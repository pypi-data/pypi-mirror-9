#include <Python.h>
#include <structmember.h>

/*
Persistent/Immutable/Functional vector and helper types. 

Please note that they are anything but immutable at this level since
there is a whole lot of reference counting going on. That's the way
CPython works though and the GIL makes them appear immutable.

To the programmer using them from Python they appear immutable and
behave immutably at least.

Naming conventions
------------------
initpyrsistentc - This is the method that initializes the whole module
pyrsistent_* -    Methods part of the interface
<typename>_* -    Instance methods of types. For examle PVector_append(...)

All other methods are camel cased without prefix. All methods are static, none should
require to be exposed outside of this module. 
*/

#define BRANCH_FACTOR 32
#define BIT_MASK (BRANCH_FACTOR - 1)

static PyTypeObject PVectorType;
static PyTypeObject PVectorEvolverType;

int SHIFT = 0;

typedef struct {
  void *items[BRANCH_FACTOR];
  unsigned int refCount;
} VNode;

#define NODE_CACHE_MAX_SIZE 1024

typedef struct {
  unsigned int size;
  VNode* nodes[NODE_CACHE_MAX_SIZE];
} vNodeCache;

static vNodeCache nodeCache;

typedef struct {
  PyObject_HEAD
  unsigned int count;   // Perhaps ditch this one in favor of ob_size/Py_SIZE()
  unsigned int shift;
  VNode *root;
  VNode *tail;
} PVector;

typedef struct {
  PyObject_HEAD
  PVector* originalVector;
  PVector* newVector;
  PyObject* appendList;
} PVectorEvolver;


static PVector* EMPTY_VECTOR = NULL;
static PyObject* pmap_factory_fn = NULL;
static PyObject* set_in_fn_name = NULL;

static PyObject* setInPmap(PyObject* keySequence, Py_ssize_t keySize, PyObject* value) {
  if(pmap_factory_fn == NULL) {
    // Lazy import pmap factory to avoid circular import problems
    pmap_factory_fn = PyObject_GetAttrString(PyImport_ImportModule("pyrsistent"), "pmap");
  }

  PyObject* emptyMap = PyObject_CallFunctionObjArgs(pmap_factory_fn, NULL);
  PyObject* newSequence = PySequence_GetSlice(keySequence, 1, keySize);
  PyObject* newMap = PyObject_CallMethodObjArgs(emptyMap,
						set_in_fn_name,
						newSequence,
						value,
						NULL);
  Py_DECREF(emptyMap);
  Py_DECREF(newSequence);
  return newMap;
}

// No access to internal members
static PyMemberDef PVector_members[] = {
	{NULL}  /* Sentinel */
};

#define debug(...)
// #define debug printf

#define NODE_REF_COUNT(n) ((n)->refCount)
#define SET_NODE_REF_COUNT(n, c) (NODE_REF_COUNT(n) = (c))
#define INC_NODE_REF_COUNT(n) (NODE_REF_COUNT(n)++)
#define DEC_NODE_REF_COUNT(n) (NODE_REF_COUNT(n)--)

static VNode* allocNode(void) {
  if(nodeCache.size > 0) {
    nodeCache.size--;
    return nodeCache.nodes[nodeCache.size];
  }

  return PyMem_Malloc(sizeof(VNode));
}

static void freeNode(VNode *node) {
  if(nodeCache.size < NODE_CACHE_MAX_SIZE) {
    nodeCache.nodes[nodeCache.size] = node;
    nodeCache.size++;
  } else {
    PyMem_Free(node);
  }
}

static VNode* newNode(void) {
  VNode* result = allocNode();
  memset(result, 0x0, sizeof(VNode));
  SET_NODE_REF_COUNT(result, 1);
  debug("newNode() %p\n", result);
  return result;
}

static VNode* copyNode(VNode* source) {
  /* NB: Only to be used for internal nodes, eg. nodes that do not
         hold direct references to python objects but only to other nodes. */
  int i;
  VNode* result = allocNode();
  debug("copyNode() %p\n", result);
  memcpy(result->items, source->items, sizeof(source->items));
  
  for(i = 0; i < BRANCH_FACTOR; i++) {
    if(result->items[i] != NULL) {
      INC_NODE_REF_COUNT((VNode*)result->items[i]);
    }
  }

  SET_NODE_REF_COUNT(result, 1);
  return result;
}

static PVector* emptyNewPvec(void);
static PVector* copyPVector(PVector *original);
static void extendWithItem(PVector *newVec, PyObject *item);

static PyObject *PVectorEvolver_pvector(PVectorEvolver *);
static int PVectorEvolver_set_item(PVectorEvolver *, PyObject*, PyObject*);

static Py_ssize_t PVector_len(PVector *self) {
  return self->count;
}

/* Convenience macros */
#define ROOT_NODE_FULL(vec) ((vec->count >> SHIFT) > (1 << vec->shift))
#define TAIL_OFF(vec) ((vec->count < BRANCH_FACTOR) ? 0 : (((vec->count - 1) >> SHIFT) << SHIFT))
#define TAIL_SIZE(vec) (vec->count - TAIL_OFF(vec))
#define PVector_CheckExact(op) (Py_TYPE(op) == &PVectorType)

static VNode* nodeFor(PVector *self, int i){
  int level;
  if((i >= 0) && (i < self->count)) {
    if(i >= TAIL_OFF(self)) {
      return self->tail;
    }

    VNode* node = self->root;
    for(level = self->shift; level > 0; level -= SHIFT) {
      node = (VNode*) node->items[(i >> level) & BIT_MASK];
    }

    return node;
  }

  PyErr_SetString(PyExc_IndexError, "Index out of range");
  return NULL;
}

static PyObject* _get_item(PVector *self, Py_ssize_t pos) {
  VNode* node = nodeFor((PVector*)self, pos);
  PyObject *result = NULL;
  if(node != NULL) {
    result = node->items[pos & BIT_MASK];
  }
  return result;
}

/*
 Returns a new reference as specified by the PySequence_GetItem function.
*/
static PyObject* PVector_get_item(PVector *self, Py_ssize_t pos) {
  if (pos < 0) {
    pos += self->count;
  }

  PyObject* obj = _get_item(self, pos);
  Py_XINCREF(obj);
  return obj;  
}

static void releaseNode(int level, VNode *node) {
  if(node == NULL) {
    return;
  }

  debug("releaseNode(): node=%p, level=%i, refCount=%i\n", node, level, NODE_REF_COUNT(node));

  int i;

  DEC_NODE_REF_COUNT(node);
  debug("Refcount when trying to release: %u\n", NODE_REF_COUNT(node));
  if(NODE_REF_COUNT(node) == 0) {
    if(level > 0) {
      for(i = 0; i < BRANCH_FACTOR; i++) {
        if(node->items[i] != NULL) {
          releaseNode(level - SHIFT, node->items[i]);
        }
      }
      freeNode(node);
    } else {
      for(i = 0; i < BRANCH_FACTOR; i++) {
         Py_XDECREF(node->items[i]);
      }
      freeNode(node);
    }
  }

  debug("releaseNode(): Done! node=%p!\n", node);
}

/*
 Returns all references to PyObjects that have been stolen. Also decrements
 the internal reference counts used for shared memory structures and deallocates
 those if needed.
*/
static void PVector_dealloc(PVector *self) {
  debug("Dealloc(): self=%p, self->count=%u, tail->refCount=%u, root->refCount=%u, self->shift=%u, self->tail=%p, self->root=%p\n",
        self, self->count, NODE_REF_COUNT(self->tail), NODE_REF_COUNT(self->root), self->shift, self->tail, self->root);

  PyObject_GC_UnTrack((PyObject*)self);
  Py_TRASHCAN_SAFE_BEGIN(self);

  releaseNode(0, self->tail);
  releaseNode(self->shift, self->root);
  
  PyObject_GC_Del(self);
  Py_TRASHCAN_SAFE_END(self);
}

static PyObject *toList(PVector *self) {
  Py_ssize_t i;
  PyObject *list = PyList_New(self->count);
  for (i = 0; i < self->count; ++i) {
    PyObject *o = _get_item(self, i);
    Py_INCREF(o);
    PyList_SET_ITEM(list, i, o);
  }

  return list;
}

static PyObject *PVector_repr(PVector *self) {
  // Reuse the list repr code, a bit less efficient but saves some code
  PyObject *list = toList(self);
  PyObject *list_repr = PyObject_Repr(list);
  Py_DECREF(list);

  // Repr for list implemented differently in python 2 and 3. Need to
  // handle this or core dump will occur.
#if PY_MAJOR_VERSION >= 3
  PyObject *s = PyUnicode_FromFormat("%s%U%s", "pvector(", list_repr, ")");
  Py_DECREF(list_repr);
#else
  PyObject *s = PyString_FromString("pvector(");
  PyString_ConcatAndDel(&s, list_repr);
  PyString_ConcatAndDel(&s, PyString_FromString(")"));
#endif

  return s;
}


static long PVector_hash(PVector *self) {
  // Follows the pattern of the tuple hash
  long x, y;
  Py_ssize_t i;
  long mult = 1000003L;
  x = 0x456789L;
  for(i=0; i<self->count; i++) {
      y = PyObject_Hash(_get_item(self, i));
      if (y == -1) {
        return -1;
      }
      x = (x ^ y) * mult;
      mult += (long)(82520L + i + i);
  }

  x += 97531L;
  if(x == -1) {
    x = -2;
  }

  return x;
}

static PyObject* compareSizes(long vlen, long wlen, int op) {
    int cmp;
    PyObject *res;
    switch (op) {
      case Py_LT: cmp = vlen <  wlen; break;
      case Py_LE: cmp = vlen <= wlen; break;
      case Py_EQ: cmp = vlen == wlen; break;
      case Py_NE: cmp = vlen != wlen; break;
      case Py_GT: cmp = vlen >  wlen; break;
      case Py_GE: cmp = vlen >= wlen; break;
      default: return NULL; /* cannot happen */
    }

    if (cmp) {
      res = Py_True;
    } else {
      res = Py_False;
    }

    Py_INCREF(res);
    return res;
}

static PyObject* PVector_richcompare(PyObject *v, PyObject *w, int op) {
    // Follows the principles of the tuple comparison
    PVector *vt, *wt;
    Py_ssize_t i;
    Py_ssize_t vlen, wlen;

    if(!PVector_CheckExact(v) || !PVector_CheckExact(w)) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    if((op == Py_EQ) && (v == w)) {
        Py_INCREF(Py_True);
        return Py_True;
    }

    vt = (PVector *)v;
    wt = (PVector *)w;

    vlen = vt->count;
    wlen = wt->count;

    /* Search for the first index where items are different. */
    PyObject *left = NULL;
    PyObject *right = NULL;
    for (i = 0; i < vlen && i < wlen; i++) {
        left = _get_item(vt, i);
        right = _get_item(wt, i);
        int k = PyObject_RichCompareBool(left, right, Py_EQ);
        if (k < 0) {
            return NULL;
        }
        if (!k) {
            break;
        }
    }

    if (i >= vlen || i >= wlen) {
        /* No more items to compare -- compare sizes */
        return compareSizes(vlen, wlen, op);
    }

    /* We have an item that differs -- shortcuts for EQ/NE */
    if (op == Py_EQ) {
        Py_INCREF(Py_False);
        return Py_False;
    } else if (op == Py_NE) {
        Py_INCREF(Py_True);
        return Py_True;
    } else {
      /* Compare the final item again using the proper operator */
      return PyObject_RichCompare(left, right, op);
    }
}


static PyObject* PVector_repeat(PVector *self, Py_ssize_t n) {
  if (n < 0) {
      n = 0;
  }

  if ((n == 0) || (self->count == 0)) {
    Py_INCREF(EMPTY_VECTOR);
    return (PyObject *)EMPTY_VECTOR;
  } else if (n == 1) {
    Py_INCREF(self);
    return (PyObject *)self;
  } else if ((self->count * n)/self->count != n) {
    return PyErr_NoMemory();
  } else {
    int i, j;
    PVector *newVec = copyPVector(self);
    for(i=0; i<(n-1); i++) {
      for(j=0; j<self->count; j++) {
        extendWithItem(newVec, PVector_get_item(self, j));
      }
    }
    return (PyObject*)newVec;
  }
}

static int PVector_traverse(PVector *o, visitproc visit, void *arg) {
    // Naive traverse
    Py_ssize_t i;
    for (i = o->count; --i >= 0; ) {
      Py_VISIT(_get_item(o, i));
    }

    return 0;
}


static PyObject* PVector_index(PVector *self, PyObject *args) {
  // A direct rip-off of the tuple version
  Py_ssize_t i, start=0, stop=self->count;
  PyObject *value;
  
  if (!PyArg_ParseTuple(args, "O|O&O&:index", &value,
			_PyEval_SliceIndex, &start,
			_PyEval_SliceIndex, &stop)) {
    return NULL;
  }
  
  if (start < 0) {
    start += self->count;
    if (start < 0) {
      start = 0;
    }
  }
  
  if (stop < 0) {
    stop += self->count;
      if (stop < 0) {
	stop = 0;
      }
  }
  
  for (i = start; i < stop && i < self->count; i++) {
    int cmp = PyObject_RichCompareBool(_get_item(self, i), value, Py_EQ);
    if (cmp > 0) {
#if PY_MAJOR_VERSION >= 3
      return PyLong_FromSsize_t(i);
#else
      return PyInt_FromSsize_t(i);
#endif
    } else if (cmp < 0) {
      return NULL;
    }
  }

  PyErr_SetString(PyExc_ValueError, "PVector.index(x): x not in vector");
  return NULL;
}

static PyObject* PVector_count(PVector *self, PyObject *value) {
  Py_ssize_t count = 0;
  Py_ssize_t i;

  for (i = 0; i < self->count; i++) {
    int cmp = PyObject_RichCompareBool(_get_item(self, i), value, Py_EQ);
    if (cmp > 0) {
      count++;
    } else if (cmp < 0) {
      return NULL;
    }
  }

#if PY_MAJOR_VERSION >= 3
      return PyLong_FromSsize_t(count);
#else
      return PyInt_FromSsize_t(count);
#endif
}

static PyObject* PVector_pickle_reduce(PVector *self) {

  PyObject* module = PyImport_ImportModule("pvectorc");
  PyObject* pvector_fn = PyObject_GetAttrString(module, "pvector");
  Py_DECREF(module);

  PyObject *list = toList(self);
  PyObject *arg_tuple = PyTuple_New(1);
  PyTuple_SET_ITEM(arg_tuple, 0, list);

  PyObject *result_tuple = PyTuple_New(2);
  PyTuple_SET_ITEM(result_tuple, 0, pvector_fn);
  PyTuple_SET_ITEM(result_tuple, 1, arg_tuple);

  return result_tuple;
}

static PVector* rawCopyPVector(PVector* vector) {
  PVector* newVector = PyObject_GC_New(PVector, &PVectorType);
  newVector->count = vector->count;
  newVector->shift = vector->shift;
  newVector->root = vector->root;
  newVector->tail = vector->tail;
  PyObject_GC_Track((PyObject*)newVector);
  return newVector;
}

static void initializeEvolver(PVectorEvolver* evolver, PVector* vector, PyObject* appendList) {
  // Need to hold a reference to the underlying vector to manage
  // the ref counting properly.
  evolver->originalVector = vector;
  evolver->newVector = vector;

  if(appendList == NULL) {
    evolver->appendList = PyList_New(0);
  } else {
    evolver->appendList = appendList;
  }
}

static PyObject * PVector_evolver(PVector *self) {
  PVectorEvolver *evolver = PyObject_GC_New(PVectorEvolver, &PVectorEvolverType);
  if (evolver == NULL) {
    return NULL;
  }
  
  PyObject_GC_Track(evolver);
  initializeEvolver(evolver, self, NULL);
  Py_INCREF(self);
  return (PyObject *)evolver;
}


static void copyInsert(void** dest, void** src, Py_ssize_t pos, void *obj) {
  memcpy(dest, src, BRANCH_FACTOR * sizeof(void*));
  dest[pos] = obj;
}

static PyObject* PVector_append(PVector *self, PyObject *obj);

static PyObject* PVector_set_in(PVector *self, PyObject *obj);

static PyObject* PVector_set(PVector *self, PyObject *obj);

static PyObject* PVector_mset(PVector *self, PyObject *args);

static PyObject* PVector_subscript(PVector* self, PyObject* item);

static PyObject* PVector_extend(PVector *self, PyObject *args);

static PySequenceMethods PVector_sequence_methods = {
    (lenfunc)PVector_len,            /* sq_length */
    (binaryfunc)PVector_extend,      /* sq_concat */
    (ssizeargfunc)PVector_repeat,    /* sq_repeat */
    (ssizeargfunc)PVector_get_item,  /* sq_item */
    // TODO might want to move the slice function to here
    NULL,                            /* sq_slice */
    NULL,                            /* sq_ass_item */
    NULL,                            /* sq_ass_slice */
    NULL,                            /* sq_contains */
    NULL,                            /* sq_inplace_concat */
    NULL,                            /* sq_inplace_repeat */
};

static PyMappingMethods PVector_mapping_methods = {
    (lenfunc)PVector_len,
    (binaryfunc)PVector_subscript,
    NULL
};


static PyMethodDef PVector_methods[] = {
	{"append",      (PyCFunction)PVector_append, METH_O,       "Appends an element"},
	{"set",         (PyCFunction)PVector_set, METH_VARARGS, "Inserts an element at the specified position"},
	{"extend",      (PyCFunction)PVector_extend, METH_O|METH_COEXIST, "Extend"},
	{"set_in",      (PyCFunction)PVector_set_in, METH_VARARGS, "Insert an element in a nested structure"},
	{"index",       (PyCFunction)PVector_index, METH_VARARGS, "Return first index of value"},
	{"count",       (PyCFunction)PVector_count, METH_O, "Return number of occurrences of value"},
        {"__reduce__",  (PyCFunction)PVector_pickle_reduce, METH_NOARGS, "Pickle support method"},
        {"evolver",     (PyCFunction)PVector_evolver, METH_NOARGS, "Return new evolver for pvector"},
	{"mset",        (PyCFunction)PVector_mset, METH_VARARGS, "Inserts multiple elements at the specified positions"},
	{NULL}
};

static PyObject * PVectorIter_iter(PyObject *seq);

static PyTypeObject PVectorType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "pvectorc.PVector",                         /* tp_name        */
  sizeof(PVector),                            /* tp_basicsize   */
  0,		                              /* tp_itemsize    */
  (destructor)PVector_dealloc,                /* tp_dealloc     */
  0,                                          /* tp_print       */
  0,                                          /* tp_getattr     */
  0,                                          /* tp_setattr     */
  0,                                          /* tp_compare     */
  (reprfunc)PVector_repr,                     /* tp_repr        */
  0,                                          /* tp_as_number   */
  &PVector_sequence_methods,                  /* tp_as_sequence */
  &PVector_mapping_methods,                   /* tp_as_mapping  */
  (hashfunc)PVector_hash,                     /* tp_hash        */
  0,                                          /* tp_call        */
  0,                                          /* tp_str         */
  0,                                          /* tp_getattro    */
  0,                                          /* tp_setattro    */
  0,                                          /* tp_as_buffer   */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags       */
  "Persistent vector",   	              /* tp_doc         */
  (traverseproc)PVector_traverse,             /* tp_traverse       */
  0,                                          /* tp_clear          */
  PVector_richcompare,                        /* tp_richcompare    */
  0,                                          /* tp_weaklistoffset */
  PVectorIter_iter,                           /* tp_iter           */
  0,                                          /* tp_iternext       */
  PVector_methods,                            /* tp_methods        */
  PVector_members,                            /* tp_members        */
  0,                                          /* tp_getset         */
  0,                                          /* tp_base           */
  0,                                          /* tp_dict           */
  0,                                          /* tp_descr_get      */
  0,                                          /* tp_descr_set      */
  0,                                          /* tp_dictoffset     */
};

static PyObject* pyrsistent_pvec(PyObject *self, PyObject *args) {
    debug("pyrsistent_pvec(): %x\n", args);

    PyObject *argObj = NULL;  /* list of arguments */

    if(!PyArg_ParseTuple(args, "|O", &argObj)) {
      return NULL;
    }

    if(argObj == NULL) {
      Py_INCREF(EMPTY_VECTOR);
      return (PyObject*)EMPTY_VECTOR;
    }

    return PVector_extend(EMPTY_VECTOR, argObj);
}

static PVector* emptyNewPvec(void) {
  PVector *pvec = PyObject_GC_New(PVector, &PVectorType);
  debug("pymem alloc_new %x, ref cnt: %u\n", pvec, pvec->ob_refcnt);
  pvec->count = (Py_ssize_t)0;
  pvec->shift = SHIFT;
  pvec->root = newNode();
  pvec->tail = newNode();
  PyObject_GC_Track((PyObject*)pvec);
  return pvec;
}

static void incRefs(PyObject **obj) {
  int i;
  for(i = 0; i < BRANCH_FACTOR; i++) {
    Py_XINCREF(obj[i]);
  }
}


static PVector* newPvec(unsigned int count, unsigned int shift, VNode *root) {
  PVector *pvec = PyObject_GC_New(PVector, &PVectorType);
  debug("pymem alloc_copy %x, ref cnt: %u\n", pvec, pvec->ob_refcnt);
  pvec->count = count;
  pvec->shift = shift;
  pvec->root = root;
  pvec->tail = newNode();
  PyObject_GC_Track((PyObject*)pvec);
  return pvec;
}

static VNode* newPath(unsigned int level, VNode* node){
  if(level == 0) {
    INC_NODE_REF_COUNT(node);
    return node;
  }
  
  VNode* result = newNode();
  result->items[0] = newPath(level - SHIFT, node);
  return result;
}

static VNode* pushTail(unsigned int level, unsigned int count, VNode* parent, VNode* tail) {
  int subIndex = ((count - 1) >> level) & BIT_MASK;
  VNode* result = copyNode(parent);
  VNode* nodeToInsert;
  VNode* child;
  debug("pushTail(): count = %i, subIndex = %i\n", count, subIndex);

  if(level == SHIFT) {
    // We're at the bottom
    INC_NODE_REF_COUNT(tail);
    nodeToInsert = tail;
  } else {
    // More levels available in the tree
    child = parent->items[subIndex];

    if(child != NULL) {
      nodeToInsert = pushTail(level - SHIFT, count, child, tail);

      // Need to make an adjustment of the ref COUNT for the child node here since
      // it was incremented in an earlier stage when the node was copied. Now the child
      // node will be part of the path copy so the number of references to the original
      // child will not increase at all.
      DEC_NODE_REF_COUNT(child);
    } else {
      nodeToInsert = newPath(level - SHIFT, tail);
    }
  }
  
  result->items[subIndex] = nodeToInsert;
  return result;
}

static PVector* copyPVector(PVector *original) {
  PVector *newVec = newPvec(original->count, original->shift, original->root);
  INC_NODE_REF_COUNT(original->root);
  memcpy(newVec->tail->items, original->tail->items, TAIL_SIZE(original) * sizeof(void*));
  incRefs((PyObject**)newVec->tail->items);
  return newVec;
}

/* Does not steal a reference, this must be managed outside of this function */
static void extendWithItem(PVector *newVec, PyObject *item) {
  unsigned int tail_size = TAIL_SIZE(newVec);

  if(tail_size >= BRANCH_FACTOR) {
    VNode* new_root;
    if(ROOT_NODE_FULL(newVec)) {
      new_root = newNode();
      new_root->items[0] = newVec->root;
      new_root->items[1] = newPath(newVec->shift, newVec->tail);
      newVec->shift += SHIFT;
    } else {
      new_root = pushTail(newVec->shift, newVec->count, newVec->root, newVec->tail);
      releaseNode(newVec->shift, newVec->root);
    }

    newVec->root = new_root;

    // Need to adjust the ref count of the old tail here since no new references were
    // actually created, we just moved the tail.
    DEC_NODE_REF_COUNT(newVec->tail);
    newVec->tail = newNode();
    tail_size = 0;
  }

  newVec->tail->items[tail_size] = item;    
  newVec->count++;
}


#if PY_MAJOR_VERSION >= 3
// This was changed in 3.2 but we do not claim compatibility with any older version of python 3.
#define SLICE_CAST
#else
#define SLICE_CAST (PySliceObject *)
#endif

static PyObject *PVector_subscript(PVector* self, PyObject* item) {
  if (PyIndex_Check(item)) {
    Py_ssize_t i = PyNumber_AsSsize_t(item, PyExc_IndexError);
    if (i == -1 && PyErr_Occurred()) {
      return NULL;
    }
    
    return PVector_get_item(self, i);
  } else if (PySlice_Check(item)) {
    Py_ssize_t start, stop, step, slicelength, cur, i;
    if (PySlice_GetIndicesEx(SLICE_CAST item, self->count,
                             &start, &stop, &step, &slicelength) < 0) {
      return NULL;
    }
    
    debug("start=%i, stop=%i, step=%i\n", start, stop, step);
    
    if (slicelength <= 0) {
      Py_INCREF(EMPTY_VECTOR);
      return (PyObject*)EMPTY_VECTOR;
    } else if((slicelength == self->count) && (step > 0)) {
      Py_INCREF(self);
      return (PyObject*)self;
    } else {
      PVector *newVec = copyPVector(EMPTY_VECTOR);
      for (cur=start, i=0; i<slicelength; cur += (size_t)step, i++) {
        extendWithItem(newVec, PVector_get_item(self, cur));
      }
      
      return (PyObject*)newVec;
    }
  } else {
    PyErr_Format(PyExc_TypeError, "pvector indices must be integers, not %.200s", Py_TYPE(item)->tp_name);
    return NULL;
  }
} 

/* A hack to get some of the error handling code away from the function
   doing the actual work */
#define HANDLE_ITERATION_ERROR()                         \
    if (PyErr_Occurred()) {                              \
      if (PyErr_ExceptionMatches(PyExc_StopIteration)) { \
        PyErr_Clear();                                   \
      } else {                                           \
        return NULL;                                     \
      }                                                  \
    }


/* Returns a new vector that is extended with the iterable b.
   Takes a copy of the original vector and performs the extension in place on this
   one for efficiency. 

   These are some optimizations that could be done to this function,
   these are not considered important enough yet though.
   - Use the PySequence_Fast ops if the iterable is a list or a tuple (which it
     whould probably often be)
   - Only copy the original tail if it is not full
   - No need to try to increment ref count in tail for the whole tail
*/
static PyObject* PVector_extend(PVector *self, PyObject *iterable) {
    PyObject *it;
    PyObject *(*iternext)(PyObject *);

    it = PyObject_GetIter(iterable);
    if (it == NULL) {
        return NULL;
    }
    
    iternext = *Py_TYPE(it)->tp_iternext;
    PyObject *item = iternext(it);
    if (item == NULL) {
      Py_DECREF(it);
      HANDLE_ITERATION_ERROR()
      Py_INCREF(self);
      return (PyObject *)self;
    } else {
      PVector *newVec = copyPVector(self);
      while(item != NULL) {
        extendWithItem(newVec, item);
        item = iternext(it);
      }

      Py_DECREF(it);
      HANDLE_ITERATION_ERROR()
      return (PyObject*)newVec;
    }
}

/*
 Steals a reference to the object that is appended to the list.
*/
static PyObject* PVector_append(PVector *self, PyObject *obj) {
  assert (obj != NULL);

  unsigned int tail_size = TAIL_SIZE(self);
  debug("append(): count = %u, tail_size = %u\n", self->count, tail_size);

  // Does the new object fit in the tail? If so, take a copy of the tail and
  // insert the new element in that.
  if(tail_size < BRANCH_FACTOR) {
    INC_NODE_REF_COUNT(self->root);
    PVector *new_pvec = newPvec(self->count + 1, self->shift, self->root);
    copyInsert(new_pvec->tail->items, self->tail->items, tail_size, obj);
    incRefs((PyObject**)new_pvec->tail->items);
    debug("append(): new_pvec=%p, new_pvec->tail=%p, new_pvec->root=%p\n",
    new_pvec, new_pvec->tail, new_pvec->root);

    return (PyObject*)new_pvec;
  }

  // Tail is full, need to push it into the tree  
  VNode* new_root;
  unsigned int new_shift;
  if(ROOT_NODE_FULL(self)) {
    new_root = newNode();
    new_root->items[0] = self->root;
    INC_NODE_REF_COUNT(self->root);
    new_root->items[1] = newPath(self->shift, self->tail);
    new_shift = self->shift + SHIFT;
  } else {
    new_root = pushTail(self->shift, self->count, self->root, self->tail);
    new_shift = self->shift;
  }

  PVector* pvec = newPvec(self->count + 1, new_shift, new_root);
  pvec->tail->items[0] = obj;
  Py_XINCREF(obj);
  debug("append_push(): pvec=%p, pvec->tail=%p, pvec->root=%p\n", pvec, pvec->tail, pvec->root);
  return (PyObject*)pvec;
}

static VNode* doSet(VNode* node, unsigned int level, unsigned int position, PyObject* value) {
  debug("doSet(): level == %i\n", level);
  if(level == 0) {
    VNode* theNewNode = newNode();
    copyInsert(theNewNode->items, node->items, position & BIT_MASK, value);
    incRefs((PyObject**)theNewNode->items);
    return theNewNode;
  } else {
    VNode* theNewNode = copyNode(node);
    Py_ssize_t index = (position >> level) & BIT_MASK;

    // Drop reference to this node since we're about to replace it
    DEC_NODE_REF_COUNT((VNode*)theNewNode->items[index]);
    theNewNode->items[index] = doSet(node->items[index], level - SHIFT, position, value); 
    return theNewNode;
  }
}


static PyObject* internalSet(PVector *self, Py_ssize_t position, PyObject *argObj) {
  if(position < 0) {
    position += self->count;
  }

  if((0 <= position) && (position < self->count)) {
    if(position >= TAIL_OFF(self)) {
      // Reuse the root, replace the tail
      INC_NODE_REF_COUNT(self->root);
      PVector *new_pvec = newPvec(self->count, self->shift, self->root);
      copyInsert(new_pvec->tail->items, self->tail->items, position & BIT_MASK, argObj);
      incRefs((PyObject**)new_pvec->tail->items);
      return (PyObject*)new_pvec;
    } else {
      // Keep the tail, replace the root
      VNode *newRoot = doSet(self->root, self->shift, position, argObj);
      PVector *new_pvec = newPvec(self->count, self->shift, newRoot);

      // Free the tail and replace it with a reference to the tail of the original vector
      freeNode(new_pvec->tail);
      new_pvec->tail = self->tail;
      INC_NODE_REF_COUNT(self->tail);
      return (PyObject*)new_pvec;
    }
  } else if (position == self->count) {
    // TODO Remove this case?
    return PVector_append(self, argObj);
  } else {
    PyErr_SetString(PyExc_IndexError, "Index out of range");
    return NULL;
  }
}

static PyObject* PVector_set_in(PVector *self, PyObject *args) {
  PyObject *keySequence = NULL;
  PyObject *value = NULL;

  if(!PyArg_ParseTuple(args, "OO", &keySequence, &value)) {
    return NULL;
  }

  Py_ssize_t keySize = PySequence_Size(keySequence);
  if(keySize == 0) {
    Py_INCREF(self);
    return (PyObject*)self;
  } else {
    PyObject *index = PySequence_GetItem(keySequence, 0);
    Py_DECREF(index);
    Py_ssize_t keyIndex = PyNumber_AsSsize_t(index, NULL);
    if (keyIndex == -1 && PyErr_Occurred()) {
      return NULL;
    }

    if(keySize == 1) {
      return internalSet(self, keyIndex, value);
    } else if(keyIndex == self->count) {
      PyObject* newMap = setInPmap(keySequence, keySize, value);
      if(newMap == NULL) {
      	return NULL;
      }

      PyObject* newVector = PVector_append(self, newMap);
      Py_DECREF(newMap);
      return newVector;
    } else {
      PyObject* currentItem = PVector_get_item(self, keyIndex);
      if(currentItem == NULL) {
	return NULL;
      }

      // This is slightly scary calling out to Python code. Could
      // there be concurrency issues if the GIL is released?
      PyObject* newSequence = PySequence_GetSlice(keySequence, 1, keySize);
      PyObject* newItem = PyObject_CallMethodObjArgs(currentItem, set_in_fn_name, newSequence, value, NULL);
      Py_DECREF(currentItem);
      Py_DECREF(newSequence);
      if(newItem == NULL) {
	return NULL;
      }
      
      PyObject* newVector = internalSet(self, keyIndex, newItem);
      Py_DECREF(newItem);
      return newVector;
    }
  }
}

/*
 Steals a reference to the object that is inserted in the vector.
*/
static PyObject* PVector_set(PVector *self, PyObject *args) {
  PyObject *argObj = NULL;  /* argument to insert */
  Py_ssize_t position;

  /* The n parses for size, the O parses for a Python object */
  if(!PyArg_ParseTuple(args, "nO", &position, &argObj)) {
    return NULL;
  }

  return internalSet(self, position, argObj);
}

static PyObject* PVector_mset(PVector *self, PyObject *args) {
  Py_ssize_t size = PyTuple_Size(args);
  if(size % 2) {
    PyErr_SetString(PyExc_TypeError, "mset expected an even number of arguments");
    return NULL;
  }

  PVectorEvolver* evolver = (PVectorEvolver*)PVector_evolver(self);
  Py_ssize_t i;
  for(i=0; i<size; i+=2) {
    if(PVectorEvolver_set_item(evolver, PyTuple_GetItem(args, i), PyTuple_GetItem(args, i + 1)) < 0) {
      Py_DECREF(evolver);
      return NULL;
    }
  }

  PyObject* vector = PVectorEvolver_pvector(evolver);
  Py_DECREF(evolver);
  return vector;
}


static PyMethodDef PyrsistentMethods[] = {
  {"pvector", pyrsistent_pvec, METH_VARARGS, "Factory method for persistent vectors"},
  {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "pvectorc",          /* m_name */
    "Persistent vector", /* m_doc */
    -1,                  /* m_size */
    PyrsistentMethods,   /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };
#endif

PyObject* moduleinit(void) {
  PyObject* m;
  
  // Only allow creation/initialization through factory method pvec
  PVectorType.tp_init = NULL;
  PVectorType.tp_new = NULL;

  if (PyType_Ready(&PVectorType) < 0) {
    return NULL;
  }

  // Register with Sequence to appear as a proper sequence to the outside world
  PyObject* c = PyObject_GetAttrString(PyImport_ImportModule("collections"), "Sequence");

  if (PyType_Ready(Py_TYPE(c)) < 0) {
    printf("Failed to initialize Sequence!\n");
    return NULL;
  }

  if(c == NULL) {
    debug("Was NULL!\n");
  }
  
  PyObject_CallMethod(c, "register", "O", &PVectorType);

#if PY_MAJOR_VERSION >= 3
  m = PyModule_Create(&moduledef);
#else
  m = Py_InitModule3("pvectorc", PyrsistentMethods, "Persistent vector");  
#endif

  if (m == NULL) {
    return NULL;
  }

  SHIFT = __builtin_popcount(BIT_MASK);
  
  if(EMPTY_VECTOR == NULL) {
    EMPTY_VECTOR = emptyNewPvec();
  }

  nodeCache.size = 0;

  Py_INCREF(&PVectorType);
  PyModule_AddObject(m, "PVector", (PyObject *)&PVectorType);


  set_in_fn_name = PyUnicode_FromString("set_in");

  return m;
}

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_pvectorc(void) {
  return moduleinit();
}
#else
PyMODINIT_FUNC initpvectorc(void) {
  moduleinit();
}
#endif


/*********************** PVector Iterator **************************/

/* 
The Sequence class provides us with a default iterator but the runtime
overhead of using that compared to the iterator below is huge.
*/

typedef struct {
    PyObject_HEAD
    Py_ssize_t it_index;
    PVector *it_seq; /* Set to NULL when iterator is exhausted */
} PVectorIter;

static void PVectorIter_dealloc(PVectorIter *);
static int PVectorIter_traverse(PVectorIter *, visitproc, void *);
static PyObject *PVectorIter_next(PVectorIter *);

static PyMethodDef PVectorIter_methods[] = {
    {NULL,              NULL}           /* sentinel */
};

static PyTypeObject PVectorIterType = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "pvector_iterator",                         /* tp_name */
    sizeof(PVectorIter),                        /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)PVectorIter_dealloc,            /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)PVectorIter_traverse,         /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    (iternextfunc)PVectorIter_next,             /* tp_iternext */
    PVectorIter_methods,                        /* tp_methods */
    0,                                          /* tp_members */
};

static PyObject *PVectorIter_iter(PyObject *seq) {
    PVectorIter *it = PyObject_GC_New(PVectorIter, &PVectorIterType);
    if (it == NULL) {
        return NULL;
    }

    it->it_index = 0;
    Py_INCREF(seq);
    it->it_seq = (PVector *)seq;
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

static void PVectorIter_dealloc(PVectorIter *it) {
    PyObject_GC_UnTrack(it);
    Py_XDECREF(it->it_seq);
    PyObject_GC_Del(it);
}

static int PVectorIter_traverse(PVectorIter *it, visitproc visit, void *arg) {
    Py_VISIT(it->it_seq);
    return 0;
}

static PyObject *PVectorIter_next(PVectorIter *it) {
    assert(it != NULL);
    PVector *seq = it->it_seq;
    if (seq == NULL) {
        return NULL;
    }

    if (it->it_index < seq->count) {
        PyObject *item = _get_item(seq, it->it_index);
        ++it->it_index;
        Py_INCREF(item);
        return item;
    }

    Py_DECREF(seq);
    it->it_seq = NULL;
    return NULL;
}


/*********************** PVector Evolver **************************/

/* 
Evolver to make multi updates easier to work with and more efficient.
*/

static void PVectorEvolver_dealloc(PVectorEvolver *);
static PyObject *PVectorEvolver_append(PVectorEvolver *, PyObject *);
static PyObject *PVectorEvolver_extend(PVectorEvolver *, PyObject *);
static PyObject *PVectorEvolver_subscript(PVectorEvolver *, PyObject *);
static PyObject *PVectorEvolver_pvector(PVectorEvolver *);
static Py_ssize_t PVectorEvolver_len(PVectorEvolver *);
static PyObject *PVectorEvolver_is_dirty(PVectorEvolver *);
static int PVectorEvolver_traverse(PVectorEvolver *self, visitproc visit, void *arg);

static PyMappingMethods PVectorEvolver_mapping_methods = {
  (lenfunc)PVectorEvolver_len,
  (binaryfunc)PVectorEvolver_subscript,
  (objobjargproc)PVectorEvolver_set_item,
};


static PyMethodDef PVectorEvolver_methods[] = {
	{"append",      (PyCFunction)PVectorEvolver_append, METH_O,       "Appends an element"},
	{"extend",      (PyCFunction)PVectorEvolver_extend, METH_O|METH_COEXIST, "Extend"},
        {"pvector",     (PyCFunction)PVectorEvolver_pvector, METH_NOARGS, "Create PVector from evolver"},
        {"is_dirty",    (PyCFunction)PVectorEvolver_is_dirty, METH_NOARGS, "Check if evolver contains modifications"},
        {NULL,              NULL}           /* sentinel */
};

static PyTypeObject PVectorEvolverType = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "pvector_evolver",                          /* tp_name */
    sizeof(PVectorEvolver),                     /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)PVectorEvolver_dealloc,         /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    &PVectorEvolver_mapping_methods,             /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)PVectorEvolver_traverse,      /* tp_traverse       */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    PVectorEvolver_methods,                     /* tp_methods */
    0,                                          /* tp_members */
};


// Indicate that a node is "dirty" (has been updated by the evolver)
// by setting the MSB of the refCount. This will be cleared when
// creating a pvector from the evolver (cleaning it).
#define DIRTY_BIT 0x80000000
#define REF_COUNT_MASK (~DIRTY_BIT)
#define IS_DIRTY(node) ((node)->refCount & DIRTY_BIT)
#define SET_DIRTY(node) ((node)->refCount |= DIRTY_BIT)
#define CLEAR_DIRTY(node) ((node)->refCount &= REF_COUNT_MASK)


static void cleanNodeRecursively(VNode *node, int level) {
  debug("Freezing recursively node=%p, level=%u\n", node, level);

  int i;
  CLEAR_DIRTY(node);
  SET_NODE_REF_COUNT(node, 1);
  if(level > 0) {
    for(i = 0; i < BRANCH_FACTOR; i++) {
      VNode *nextNode = (VNode*)node->items[i];
      if((nextNode != NULL) && IS_DIRTY(nextNode)) {
        cleanNodeRecursively(nextNode, level - SHIFT);
      }
    }
  }
}

static void cleanVector(PVector *vector) {
  // Freezing the vector means that all dirty indications are cleared
  // and that the nodes that were dirty get a ref count of 1 since
  // they are brand new. Once frozen the vector can be released into
  // the wild.
  if(IS_DIRTY(vector->tail)) {
    cleanNodeRecursively(vector->tail, 0);
  } else {
    INC_NODE_REF_COUNT(vector->tail);
  }

  if(IS_DIRTY(vector->root)) {
    cleanNodeRecursively(vector->root, vector->shift);
  } else {
    INC_NODE_REF_COUNT(vector->root);
  }
}

static void PVectorEvolver_dealloc(PVectorEvolver *self) {
  PyObject_GC_UnTrack(self);
  Py_TRASHCAN_SAFE_BEGIN(self);

  if(self->originalVector != self->newVector) {
    cleanVector(self->newVector);
    Py_DECREF(self->newVector);
  }

  Py_DECREF(self->originalVector);
  Py_DECREF(self->appendList);

  PyObject_GC_Del(self);
  Py_TRASHCAN_SAFE_END(self);
}

static PyObject *PVectorEvolver_append(PVectorEvolver *self, PyObject *args) {
  if (PyList_Append(self->appendList, args) == 0) {
    Py_RETURN_NONE;
  }

  return NULL;
}

static PyObject *PVectorEvolver_extend(PVectorEvolver *self, PyObject *args) {
  return _PyList_Extend((PyListObject *)self->appendList, args);
}

static PyObject *PVectorEvolver_subscript(PVectorEvolver *self, PyObject *item) {
  if (PyIndex_Check(item)) {
    Py_ssize_t position = PyNumber_AsSsize_t(item, PyExc_IndexError);
    if (position == -1 && PyErr_Occurred()) {
      return NULL;
    }

    if (position < 0) {
      position += self->newVector->count + PyList_GET_SIZE(self->appendList);
    }

    if(0 <= position && position < self->newVector->count) {
      PyObject *result = _get_item(self->newVector, position);
      Py_XINCREF(result);
      return result;
    } else if (0 <= position && position < (self->newVector->count + PyList_GET_SIZE(self->appendList))) {
      PyObject *result = PyList_GetItem(self->appendList, position - self->newVector->count);
      Py_INCREF(result);
      return result;
    } else {
      PyErr_SetString(PyExc_IndexError, "Index out of range");
    }
  } else {
    PyErr_Format(PyExc_TypeError, "Indices must be integers, not %.200s", item->ob_type->tp_name);
  }

  return NULL;
}

static VNode* doSetWithDirty(VNode* node, unsigned int level, unsigned int position, PyObject* value) {
  VNode* resultNode;
  debug("doSetWithDirty(): level == %i\n", level);
  if(level == 0) {
    if(!IS_DIRTY(node)) {
      resultNode = allocNode();
      copyInsert(resultNode->items, node->items, position & BIT_MASK, value);
      incRefs((PyObject**)resultNode->items);
      SET_DIRTY(resultNode);
    } else {
      resultNode = node;
      Py_INCREF(value);
      Py_DECREF(resultNode->items[position & BIT_MASK]);
      resultNode->items[position & BIT_MASK] = value;
    }
  } else {
    if(!IS_DIRTY(node)) {
      resultNode = copyNode(node);
      SET_DIRTY(resultNode);
    } else {
      resultNode = node;
    }    

    Py_ssize_t index = (position >> level) & BIT_MASK;
    VNode* oldNode = (VNode*)resultNode->items[index];
    resultNode->items[index] = doSetWithDirty(resultNode->items[index], level - SHIFT, position, value);

    if(resultNode->items[index] != oldNode) {
      // Node replaced, drop references to old node
      DEC_NODE_REF_COUNT(oldNode);
    }
  }

  return resultNode;
}

static int PVectorEvolver_set_item(PVectorEvolver *self, PyObject* item, PyObject* value) {
  if (PyIndex_Check(item)) {
    Py_ssize_t position = PyNumber_AsSsize_t(item, PyExc_IndexError);
    if (position == -1 && PyErr_Occurred()) {
      return -1;
    }
         
    if (position < 0) {
      position += self->newVector->count + PyList_GET_SIZE(self->appendList);
    }

    if((0 <= position) && (position < self->newVector->count)) {
      if(self->originalVector == self->newVector) {
        // Create new vector since we're about to modify the original
        self->newVector = rawCopyPVector(self->originalVector);
      }

      if(position < TAIL_OFF(self->newVector)) {
        self->newVector->root = doSetWithDirty(self->newVector->root, self->newVector->shift, position, value);
      } else {
        self->newVector->tail = doSetWithDirty(self->newVector->tail, 0, position, value);
      }
      
      return 0;
    } else if((0 <= position) && (position < (self->newVector->count + PyList_GET_SIZE(self->appendList)))) {
      int result = PyList_SetItem(self->appendList, position - self->newVector->count, value); 
      if(result == 0) {
        Py_INCREF(value);
      }
      return result;
    } else if((0 <= position) && (position < (self->newVector->count + PyList_GET_SIZE(self->appendList) + 1))) {
      return PyList_Append(self->appendList, value); 
    } else {
      PyErr_SetString(PyExc_IndexError, "Index out of range");
    }
  } else {
    PyErr_Format(PyExc_TypeError, "Indices must be integers, not %.200s", item->ob_type->tp_name);
  }
  return -1;
}

static PyObject *PVectorEvolver_pvector(PVectorEvolver *self) {
  PVector *resultVector;
  if(self->newVector == self->originalVector) {
    resultVector = self->newVector;
  } else {
    cleanVector(self->newVector);
    resultVector = self->newVector;
    Py_DECREF(self->originalVector);
  }

  if(PyList_GET_SIZE(self->appendList)) {
    PVector *oldVector = resultVector;
    resultVector = (PVector*)PVector_extend(resultVector, self->appendList);
    Py_DECREF(oldVector);
    Py_DECREF(self->appendList);
    self->appendList = NULL;
  }

  initializeEvolver(self, resultVector, self->appendList);
  Py_INCREF(resultVector);  
  return (PyObject*)resultVector;
}

static Py_ssize_t PVectorEvolver_len(PVectorEvolver *self) {
  return self->newVector->count + PyList_GET_SIZE(self->appendList);
}

static PyObject* PVectorEvolver_is_dirty(PVectorEvolver *self) {
  if((self->newVector != self->originalVector) || (PyList_GET_SIZE(self->appendList) > 0)) {
    Py_INCREF(Py_True);
    return Py_True;
  }

  Py_INCREF(Py_False);
  return Py_False;
}

static int PVectorEvolver_traverse(PVectorEvolver *self, visitproc visit, void *arg) {
  Py_VISIT(self->newVector);
  Py_VISIT(self->originalVector);
  Py_VISIT(self->appendList);
  return 0;
}

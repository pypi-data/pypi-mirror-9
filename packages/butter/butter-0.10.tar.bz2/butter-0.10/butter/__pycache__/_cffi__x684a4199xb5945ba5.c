
#include <Python.h>
#include <stddef.h>

/* this block of #ifs should be kept exactly identical between
   c/_cffi_backend.c, cffi/vengine_cpy.py, cffi/vengine_gen.py */
#if defined(_MSC_VER)
# include <malloc.h>   /* for alloca() */
# if _MSC_VER < 1600   /* MSVC < 2010 */
   typedef __int8 int8_t;
   typedef __int16 int16_t;
   typedef __int32 int32_t;
   typedef __int64 int64_t;
   typedef unsigned __int8 uint8_t;
   typedef unsigned __int16 uint16_t;
   typedef unsigned __int32 uint32_t;
   typedef unsigned __int64 uint64_t;
   typedef __int8 int_least8_t;
   typedef __int16 int_least16_t;
   typedef __int32 int_least32_t;
   typedef __int64 int_least64_t;
   typedef unsigned __int8 uint_least8_t;
   typedef unsigned __int16 uint_least16_t;
   typedef unsigned __int32 uint_least32_t;
   typedef unsigned __int64 uint_least64_t;
   typedef __int8 int_fast8_t;
   typedef __int16 int_fast16_t;
   typedef __int32 int_fast32_t;
   typedef __int64 int_fast64_t;
   typedef unsigned __int8 uint_fast8_t;
   typedef unsigned __int16 uint_fast16_t;
   typedef unsigned __int32 uint_fast32_t;
   typedef unsigned __int64 uint_fast64_t;
   typedef __int64 intmax_t;
   typedef unsigned __int64 uintmax_t;
# else
#  include <stdint.h>
# endif
# if _MSC_VER < 1800   /* MSVC < 2013 */
   typedef unsigned char _Bool;
# endif
#else
# include <stdint.h>
# if (defined (__SVR4) && defined (__sun)) || defined(_AIX)
#  include <alloca.h>
# endif
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_CheckExact
# undef PyCapsule_GetPointer
# define PyCapsule_CheckExact(capsule) (PyCObject_Check(capsule))
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_ulong PyLong_FromUnsignedLong
#define _cffi_from_c_longlong PyLong_FromLongLong
#define _cffi_from_c_ulonglong PyLong_FromUnsignedLongLong

#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_from_c_int_const(x)                                        \
    (((x) > 0) ?                                                         \
        ((unsigned long long)(x) <= (unsigned long long)LONG_MAX) ?      \
            PyInt_FromLong((long)(x)) :                                  \
            PyLong_FromUnsignedLongLong((unsigned long long)(x)) :       \
        ((long long)(x) >= (long long)LONG_MIN) ?                        \
            PyInt_FromLong((long)(x)) :                                  \
            PyLong_FromLongLong((long long)(x)))

#define _cffi_from_c_int(x, type)                                        \
    (((type)-1) > 0 ? /* unsigned */                                     \
        (sizeof(type) < sizeof(long) ?                                   \
            PyInt_FromLong((long)x) :                                    \
         sizeof(type) == sizeof(long) ?                                  \
            PyLong_FromUnsignedLong((unsigned long)x) :                  \
            PyLong_FromUnsignedLongLong((unsigned long long)x)) :        \
        (sizeof(type) <= sizeof(long) ?                                  \
            PyInt_FromLong((long)x) :                                    \
            PyLong_FromLongLong((long long)x)))

#define _cffi_to_c_int(o, type)                                          \
    (sizeof(type) == 1 ? (((type)-1) > 0 ? (type)_cffi_to_c_u8(o)        \
                                         : (type)_cffi_to_c_i8(o)) :     \
     sizeof(type) == 2 ? (((type)-1) > 0 ? (type)_cffi_to_c_u16(o)       \
                                         : (type)_cffi_to_c_i16(o)) :    \
     sizeof(type) == 4 ? (((type)-1) > 0 ? (type)_cffi_to_c_u32(o)       \
                                         : (type)_cffi_to_c_i32(o)) :    \
     sizeof(type) == 8 ? (((type)-1) > 0 ? (type)_cffi_to_c_u64(o)       \
                                         : (type)_cffi_to_c_i64(o)) :    \
     (Py_FatalError("unsupported size for type " #type), (type)0))

#define _cffi_to_c_i8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_u8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_i16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_u16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[4])
#define _cffi_to_c_i32                                                   \
                 ((int(*)(PyObject *))_cffi_exports[5])
#define _cffi_to_c_u32                                                   \
                 ((unsigned int(*)(PyObject *))_cffi_exports[6])
#define _cffi_to_c_i64                                                   \
                 ((long long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_u64                                                   \
                 ((unsigned long long(*)(PyObject *))_cffi_exports[8])
#define _cffi_to_c_char                                                  \
                 ((int(*)(PyObject *))_cffi_exports[9])
#define _cffi_from_c_pointer                                             \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[10])
#define _cffi_to_c_pointer                                               \
    ((char *(*)(PyObject *, CTypeDescrObject *))_cffi_exports[11])
#define _cffi_get_struct_layout                                          \
    ((PyObject *(*)(Py_ssize_t[]))_cffi_exports[12])
#define _cffi_restore_errno                                              \
    ((void(*)(void))_cffi_exports[13])
#define _cffi_save_errno                                                 \
    ((void(*)(void))_cffi_exports[14])
#define _cffi_from_c_char                                                \
    ((PyObject *(*)(char))_cffi_exports[15])
#define _cffi_from_c_deref                                               \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[16])
#define _cffi_to_c                                                       \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[17])
#define _cffi_from_c_struct                                              \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[18])
#define _cffi_to_c_wchar_t                                               \
    ((wchar_t(*)(PyObject *))_cffi_exports[19])
#define _cffi_from_c_wchar_t                                             \
    ((PyObject *(*)(wchar_t))_cffi_exports[20])
#define _cffi_to_c_long_double                                           \
    ((long double(*)(PyObject *))_cffi_exports[21])
#define _cffi_to_c__Bool                                                 \
    ((_Bool(*)(PyObject *))_cffi_exports[22])
#define _cffi_prepare_pointer_call_argument                              \
    ((Py_ssize_t(*)(CTypeDescrObject *, PyObject *, char **))_cffi_exports[23])
#define _cffi_convert_array_from_object                                  \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[24])
#define _CFFI_NUM_EXPORTS 25

typedef struct _ctypedescr CTypeDescrObject;

static void *_cffi_exports[_CFFI_NUM_EXPORTS];
static PyObject *_cffi_types, *_cffi_VerificationError;

static int _cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    int was_alive = (_cffi_types != NULL);
    (void)self; /* unused */
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    if (_cffi_setup_custom(library) < 0)
        return NULL;
    return PyBool_FromLong(was_alive);
}

static int _cffi_init(void)
{
    PyObject *module, *c_api_object = NULL;

    module = PyImport_ImportModule("_cffi_backend");
    if (module == NULL)
        goto failure;

    c_api_object = PyObject_GetAttrString(module, "_C_API");
    if (c_api_object == NULL)
        goto failure;
    if (!PyCapsule_CheckExact(c_api_object)) {
        PyErr_SetNone(PyExc_ImportError);
        goto failure;
    }
    memcpy(_cffi_exports, PyCapsule_GetPointer(c_api_object, "cffi"),
           _CFFI_NUM_EXPORTS * sizeof(void *));

    Py_DECREF(module);
    Py_DECREF(c_api_object);
    return 0;

  failure:
    Py_XDECREF(module);
    Py_XDECREF(c_api_object);
    return -1;
}

#define _cffi_type(num) ((CTypeDescrObject *)PyList_GET_ITEM(_cffi_types, num))

/**********/



#include <linux/fcntl.h>
#include <sys/fanotify.h>


static PyObject *
_cffi_f_fanotify_init(PyObject *self, PyObject *args)
{
  unsigned int x0;
  unsigned int x1;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fanotify_init", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, unsigned int);
  if (x0 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fanotify_init(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fanotify_mark(PyObject *self, PyObject *args)
{
  int x0;
  unsigned int x1;
  uint64_t x2;
  int x3;
  char const * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:fanotify_mark", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2, uint64_t);
  if (x2 == (uint64_t)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_int(arg3, int);
  if (x3 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(0), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fanotify_mark(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static int _cffi_const_FAN_ACCESS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_ACCESS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_ACCESS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return ((void)lib,0);
}

static int _cffi_const_FAN_ACCESS_PERM(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_ACCESS_PERM);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_ACCESS_PERM", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_ACCESS(lib);
}

static int _cffi_const_FAN_ALLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_ALLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_ALLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_ACCESS_PERM(lib);
}

static int _cffi_const_FAN_ALL_MARK_FLAGS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_ALL_MARK_FLAGS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_ALL_MARK_FLAGS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_ALLOW(lib);
}

static int _cffi_const_FAN_CLASS_CONTENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLASS_CONTENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLASS_CONTENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_ALL_MARK_FLAGS(lib);
}

static int _cffi_const_FAN_CLASS_NOTIF(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLASS_NOTIF);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLASS_NOTIF", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLASS_CONTENT(lib);
}

static int _cffi_const_FAN_CLASS_PRE_CONTENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLASS_PRE_CONTENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLASS_PRE_CONTENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLASS_NOTIF(lib);
}

static int _cffi_const_FAN_CLOEXEC(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLOEXEC);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLOEXEC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLASS_PRE_CONTENT(lib);
}

static int _cffi_const_FAN_CLOSE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLOSE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLOSE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLOEXEC(lib);
}

static int _cffi_const_FAN_CLOSE_NOWRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLOSE_NOWRITE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLOSE_NOWRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLOSE(lib);
}

static int _cffi_const_FAN_CLOSE_WRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_CLOSE_WRITE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_CLOSE_WRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLOSE_NOWRITE(lib);
}

static int _cffi_const_FAN_DENY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_DENY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_DENY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_CLOSE_WRITE(lib);
}

static int _cffi_const_FAN_EVENT_ON_CHILD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_EVENT_ON_CHILD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_EVENT_ON_CHILD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_DENY(lib);
}

static int _cffi_const_FAN_MARK_ADD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_ADD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_ADD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_EVENT_ON_CHILD(lib);
}

static int _cffi_const_FAN_MARK_DONT_FOLLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_DONT_FOLLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_DONT_FOLLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_ADD(lib);
}

static int _cffi_const_FAN_MARK_FLUSH(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_FLUSH);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_FLUSH", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_DONT_FOLLOW(lib);
}

static int _cffi_const_FAN_MARK_IGNORED_MASK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_IGNORED_MASK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_IGNORED_MASK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_FLUSH(lib);
}

static int _cffi_const_FAN_MARK_IGNORED_SURV_MODIFY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_IGNORED_SURV_MODIFY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_IGNORED_SURV_MODIFY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_IGNORED_MASK(lib);
}

static int _cffi_const_FAN_MARK_MOUNT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_MOUNT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_MOUNT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_IGNORED_SURV_MODIFY(lib);
}

static int _cffi_const_FAN_MARK_ONLYDIR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_ONLYDIR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_ONLYDIR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_MOUNT(lib);
}

static int _cffi_const_FAN_MARK_REMOVE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MARK_REMOVE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MARK_REMOVE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_ONLYDIR(lib);
}

static int _cffi_const_FAN_MODIFY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_MODIFY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_MODIFY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MARK_REMOVE(lib);
}

static int _cffi_const_FAN_NONBLOCK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_NONBLOCK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_NONBLOCK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_MODIFY(lib);
}

static int _cffi_const_FAN_ONDIR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_ONDIR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_ONDIR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_NONBLOCK(lib);
}

static int _cffi_const_FAN_OPEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_OPEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_OPEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_ONDIR(lib);
}

static int _cffi_const_FAN_OPEN_PERM(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_OPEN_PERM);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_OPEN_PERM", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_OPEN(lib);
}

static int _cffi_const_FAN_Q_OVERFLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_Q_OVERFLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_Q_OVERFLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_OPEN_PERM(lib);
}

static int _cffi_const_FAN_UNLIMITED_MARKS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_UNLIMITED_MARKS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_UNLIMITED_MARKS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_Q_OVERFLOW(lib);
}

static int _cffi_const_FAN_UNLIMITED_QUEUE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(FAN_UNLIMITED_QUEUE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FAN_UNLIMITED_QUEUE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FAN_UNLIMITED_MARKS(lib);
}

static void _cffi_check_struct_fanotify_event_metadata(struct fanotify_event_metadata *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->event_len) << 1);
  (void)((p->vers) << 1);
  (void)((p->reserved) << 1);
  (void)((p->metadata_len) << 1);
  (void)((p->mask) << 1);
  (void)((p->fd) << 1);
  (void)((p->pid) << 1);
}
static PyObject *
_cffi_layout_struct_fanotify_event_metadata(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct fanotify_event_metadata y; };
  static Py_ssize_t nums[] = {
    sizeof(struct fanotify_event_metadata),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct fanotify_event_metadata, event_len),
    sizeof(((struct fanotify_event_metadata *)0)->event_len),
    offsetof(struct fanotify_event_metadata, vers),
    sizeof(((struct fanotify_event_metadata *)0)->vers),
    offsetof(struct fanotify_event_metadata, reserved),
    sizeof(((struct fanotify_event_metadata *)0)->reserved),
    offsetof(struct fanotify_event_metadata, metadata_len),
    sizeof(((struct fanotify_event_metadata *)0)->metadata_len),
    offsetof(struct fanotify_event_metadata, mask),
    sizeof(((struct fanotify_event_metadata *)0)->mask),
    offsetof(struct fanotify_event_metadata, fd),
    sizeof(((struct fanotify_event_metadata *)0)->fd),
    offsetof(struct fanotify_event_metadata, pid),
    sizeof(((struct fanotify_event_metadata *)0)->pid),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_fanotify_event_metadata(0);
}

static void _cffi_check_struct_fanotify_response(struct fanotify_response *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->fd) << 1);
  (void)((p->response) << 1);
}
static PyObject *
_cffi_layout_struct_fanotify_response(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct fanotify_response y; };
  static Py_ssize_t nums[] = {
    sizeof(struct fanotify_response),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct fanotify_response, fd),
    sizeof(((struct fanotify_response *)0)->fd),
    offsetof(struct fanotify_response, response),
    sizeof(((struct fanotify_response *)0)->response),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_fanotify_response(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_FAN_UNLIMITED_QUEUE(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"fanotify_init", _cffi_f_fanotify_init, METH_VARARGS, NULL},
  {"fanotify_mark", _cffi_f_fanotify_mark, METH_VARARGS, NULL},
  {"_cffi_layout_struct_fanotify_event_metadata", _cffi_layout_struct_fanotify_event_metadata, METH_NOARGS, NULL},
  {"_cffi_layout_struct_fanotify_response", _cffi_layout_struct_fanotify_response, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__x684a4199xb5945ba5",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__x684a4199xb5945ba5(void)
{
  PyObject *lib;
  lib = PyModule_Create(&_cffi_module_def);
  if (lib == NULL)
    return NULL;
  if (((void)lib,0) < 0 || _cffi_init() < 0) {
    Py_DECREF(lib);
    return NULL;
  }
  return lib;
}

#else

PyMODINIT_FUNC
init_cffi__x684a4199xb5945ba5(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x684a4199xb5945ba5", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

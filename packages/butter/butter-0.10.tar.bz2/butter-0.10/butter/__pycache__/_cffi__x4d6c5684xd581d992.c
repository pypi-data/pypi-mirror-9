
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



#include <sys/inotify.h>
#include <sys/ioctl.h>


static PyObject *
_cffi_f_inotify_add_watch(PyObject *self, PyObject *args)
{
  int x0;
  char const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:inotify_add_watch", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(0), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = inotify_add_watch(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_inotify_init(PyObject *self, PyObject *noarg)
{
  int result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = inotify_init(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_inotify_init1(PyObject *self, PyObject *arg0)
{
  int x0;
  int result;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = inotify_init1(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_inotify_rm_watch(PyObject *self, PyObject *args)
{
  int x0;
  int x1;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:inotify_rm_watch", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = inotify_rm_watch(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static int _cffi_const_IN_ACCESS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_ACCESS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_ACCESS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return ((void)lib,0);
}

static int _cffi_const_IN_ALL_EVENTS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_ALL_EVENTS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_ALL_EVENTS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_ACCESS(lib);
}

static int _cffi_const_IN_ATTRIB(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_ATTRIB);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_ATTRIB", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_ALL_EVENTS(lib);
}

static int _cffi_const_IN_CLOEXEC(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_CLOEXEC);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_CLOEXEC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_ATTRIB(lib);
}

static int _cffi_const_IN_CLOSE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_CLOSE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_CLOSE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_CLOEXEC(lib);
}

static int _cffi_const_IN_CLOSE_NOWRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_CLOSE_NOWRITE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_CLOSE_NOWRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_CLOSE(lib);
}

static int _cffi_const_IN_CLOSE_WRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_CLOSE_WRITE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_CLOSE_WRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_CLOSE_NOWRITE(lib);
}

static int _cffi_const_IN_CREATE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_CREATE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_CREATE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_CLOSE_WRITE(lib);
}

static int _cffi_const_IN_DELETE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_DELETE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_DELETE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_CREATE(lib);
}

static int _cffi_const_IN_DELETE_SELF(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_DELETE_SELF);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_DELETE_SELF", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_DELETE(lib);
}

static int _cffi_const_IN_DONT_FOLLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_DONT_FOLLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_DONT_FOLLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_DELETE_SELF(lib);
}

static int _cffi_const_IN_EXCL_UNLINK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_EXCL_UNLINK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_EXCL_UNLINK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_DONT_FOLLOW(lib);
}

static int _cffi_const_IN_IGNORED(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_IGNORED);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_IGNORED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_EXCL_UNLINK(lib);
}

static int _cffi_const_IN_ISDIR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_ISDIR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_ISDIR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_IGNORED(lib);
}

static int _cffi_const_IN_MASK_ADD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_MASK_ADD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_MASK_ADD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_ISDIR(lib);
}

static int _cffi_const_IN_MODIFY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_MODIFY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_MODIFY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_MASK_ADD(lib);
}

static int _cffi_const_IN_MOVE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_MOVE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_MOVE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_MODIFY(lib);
}

static int _cffi_const_IN_MOVED_FROM(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_MOVED_FROM);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_MOVED_FROM", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_MOVE(lib);
}

static int _cffi_const_IN_MOVED_TO(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_MOVED_TO);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_MOVED_TO", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_MOVED_FROM(lib);
}

static int _cffi_const_IN_MOVE_SELF(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_MOVE_SELF);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_MOVE_SELF", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_MOVED_TO(lib);
}

static int _cffi_const_IN_NONBLOCK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_NONBLOCK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_NONBLOCK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_MOVE_SELF(lib);
}

static int _cffi_const_IN_ONESHOT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_ONESHOT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_ONESHOT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_NONBLOCK(lib);
}

static int _cffi_const_IN_ONLYDIR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_ONLYDIR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_ONLYDIR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_ONESHOT(lib);
}

static int _cffi_const_IN_OPEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_OPEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_OPEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_ONLYDIR(lib);
}

static int _cffi_const_IN_Q_OVERFLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_Q_OVERFLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_Q_OVERFLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_OPEN(lib);
}

static int _cffi_const_IN_UNMOUNT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(IN_UNMOUNT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IN_UNMOUNT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IN_Q_OVERFLOW(lib);
}

static void _cffi_check_struct_inotify_event(struct inotify_event *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->wd) << 1);
  (void)((p->mask) << 1);
  (void)((p->cookie) << 1);
  (void)((p->len) << 1);
}
static PyObject *
_cffi_layout_struct_inotify_event(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct inotify_event y; };
  static Py_ssize_t nums[] = {
    sizeof(struct inotify_event),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct inotify_event, wd),
    sizeof(((struct inotify_event *)0)->wd),
    offsetof(struct inotify_event, mask),
    sizeof(((struct inotify_event *)0)->mask),
    offsetof(struct inotify_event, cookie),
    sizeof(((struct inotify_event *)0)->cookie),
    offsetof(struct inotify_event, len),
    sizeof(((struct inotify_event *)0)->len),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_inotify_event(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_IN_UNMOUNT(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"inotify_add_watch", _cffi_f_inotify_add_watch, METH_VARARGS, NULL},
  {"inotify_init", _cffi_f_inotify_init, METH_NOARGS, NULL},
  {"inotify_init1", _cffi_f_inotify_init1, METH_O, NULL},
  {"inotify_rm_watch", _cffi_f_inotify_rm_watch, METH_VARARGS, NULL},
  {"_cffi_layout_struct_inotify_event", _cffi_layout_struct_inotify_event, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__x4d6c5684xd581d992",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__x4d6c5684xd581d992(void)
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
init_cffi__x4d6c5684xd581d992(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x4d6c5684xd581d992", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

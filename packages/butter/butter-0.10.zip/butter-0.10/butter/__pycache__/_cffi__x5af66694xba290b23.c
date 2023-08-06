
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


  
//#include <sched.h>
#include <sys/mount.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <sys/mount.h>

int32_t getpid(void){
    return syscall(SYS_getpid);
};

int32_t getppid(void){
    return syscall(SYS_getppid);
};


static PyObject *
_cffi_f_gethostname(PyObject *self, PyObject *args)
{
  char * x0;
  size_t x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:gethostname", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = gethostname(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_getpid(PyObject *self, PyObject *noarg)
{
  int32_t result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = getpid(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_int(result, int32_t);
}

static PyObject *
_cffi_f_getppid(PyObject *self, PyObject *noarg)
{
  int32_t result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = getppid(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_int(result, int32_t);
}

static PyObject *
_cffi_f_mount(PyObject *self, PyObject *args)
{
  char const * x0;
  char const * x1;
  char const * x2;
  unsigned long x3;
  void const * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:mount", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(1), arg2) < 0)
      return NULL;
  }

  x3 = _cffi_to_c_int(arg3, unsigned long);
  if (x3 == (unsigned long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(2), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = mount(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_pivot_root(PyObject *self, PyObject *args)
{
  char const * x0;
  char const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:pivot_root", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = pivot_root(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_sethostname(PyObject *self, PyObject *args)
{
  char const * x0;
  size_t x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:sethostname", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = sethostname(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_umount2(PyObject *self, PyObject *args)
{
  char const * x0;
  int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:umount2", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = umount2(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static int _cffi_const_HOST_NAME_MAX(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(HOST_NAME_MAX);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "HOST_NAME_MAX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return ((void)lib,0);
}

static int _cffi_const_MNT_DETACH(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MNT_DETACH);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MNT_DETACH", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_HOST_NAME_MAX(lib);
}

static int _cffi_const_MNT_EXPIRE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MNT_EXPIRE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MNT_EXPIRE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MNT_DETACH(lib);
}

static int _cffi_const_MNT_FORCE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MNT_FORCE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MNT_FORCE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MNT_EXPIRE(lib);
}

static int _cffi_const_MS_BIND(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_BIND);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_BIND", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MNT_FORCE(lib);
}

static int _cffi_const_MS_DIRSYNC(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_DIRSYNC);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_DIRSYNC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_BIND(lib);
}

static int _cffi_const_MS_MANDLOCK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_MANDLOCK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_MANDLOCK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_DIRSYNC(lib);
}

static int _cffi_const_MS_MOVE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_MOVE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_MOVE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_MANDLOCK(lib);
}

static int _cffi_const_MS_NOATIME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_NOATIME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_NOATIME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_MOVE(lib);
}

static int _cffi_const_MS_NODEV(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_NODEV);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_NODEV", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_NOATIME(lib);
}

static int _cffi_const_MS_NODIRATIME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_NODIRATIME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_NODIRATIME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_NODEV(lib);
}

static int _cffi_const_MS_NOEXEC(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_NOEXEC);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_NOEXEC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_NODIRATIME(lib);
}

static int _cffi_const_MS_NOSUID(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_NOSUID);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_NOSUID", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_NOEXEC(lib);
}

static int _cffi_const_MS_RDONLY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_RDONLY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_RDONLY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_NOSUID(lib);
}

static int _cffi_const_MS_RELATIME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_RELATIME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_RELATIME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_RDONLY(lib);
}

static int _cffi_const_MS_REMOUNT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_REMOUNT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_REMOUNT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_RELATIME(lib);
}

static int _cffi_const_MS_SILENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_SILENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_SILENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_REMOUNT(lib);
}

static int _cffi_const_MS_STRICTATIME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_STRICTATIME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_STRICTATIME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_SILENT(lib);
}

static int _cffi_const_MS_SYNCHRONOUS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(MS_SYNCHRONOUS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "MS_SYNCHRONOUS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_STRICTATIME(lib);
}

static int _cffi_const_UMOUNT_NOFOLLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(UMOUNT_NOFOLLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UMOUNT_NOFOLLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_MS_SYNCHRONOUS(lib);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_UMOUNT_NOFOLLOW(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"gethostname", _cffi_f_gethostname, METH_VARARGS, NULL},
  {"getpid", _cffi_f_getpid, METH_NOARGS, NULL},
  {"getppid", _cffi_f_getppid, METH_NOARGS, NULL},
  {"mount", _cffi_f_mount, METH_VARARGS, NULL},
  {"pivot_root", _cffi_f_pivot_root, METH_VARARGS, NULL},
  {"sethostname", _cffi_f_sethostname, METH_VARARGS, NULL},
  {"umount2", _cffi_f_umount2, METH_VARARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__x5af66694xba290b23",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__x5af66694xba290b23(void)
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
init_cffi__x5af66694xba290b23(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x5af66694xba290b23", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

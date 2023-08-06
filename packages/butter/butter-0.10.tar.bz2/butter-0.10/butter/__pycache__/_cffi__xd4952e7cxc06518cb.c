
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



#include <seccomp.h>

uint64_t _SCMP_ACT_ERRNO(uint64_t code) {
    return 0x7ff00000U | (code & 0x0000ffffU);
}
uint64_t _SCMP_ACT_TRACE(uint64_t code) {
    return 0x00050000U | (code & 0x0000ffffU);
}



static int _cffi_e_enum_scmp_compare(PyObject *lib)
{
  return ((void)lib,0);
}

static PyObject *
_cffi_f__SCMP_ACT_ERRNO(PyObject *self, PyObject *arg0)
{
  uint64_t x0;
  uint64_t result;

  x0 = _cffi_to_c_int(arg0, uint64_t);
  if (x0 == (uint64_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = _SCMP_ACT_ERRNO(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, uint64_t);
}

static PyObject *
_cffi_f__SCMP_ACT_TRACE(PyObject *self, PyObject *arg0)
{
  uint64_t x0;
  uint64_t result;

  x0 = _cffi_to_c_int(arg0, uint64_t);
  if (x0 == (uint64_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = _SCMP_ACT_TRACE(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, uint64_t);
}

static PyObject *
_cffi_f_seccomp_init(PyObject *self, PyObject *arg0)
{
  uint32_t x0;
  void * result;

  x0 = _cffi_to_c_int(arg0, uint32_t);
  if (x0 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = seccomp_init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(0));
}

static PyObject *
_cffi_f_seccomp_load(PyObject *self, PyObject *arg0)
{
  void * x0;
  Py_ssize_t datasize;
  int result;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = seccomp_load(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_seccomp_merge(PyObject *self, PyObject *args)
{
  void * x0;
  void * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:seccomp_merge", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = seccomp_merge(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_seccomp_release(PyObject *self, PyObject *arg0)
{
  void * x0;
  Py_ssize_t datasize;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { seccomp_release(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_seccomp_reset(PyObject *self, PyObject *args)
{
  void * x0;
  uint32_t x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:seccomp_reset", &arg0, &arg1))
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

  x1 = _cffi_to_c_int(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = seccomp_reset(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static int _cffi_const_seccomp_rule_add(PyObject *lib)
{
  PyObject *o;
  int res;
  int(* i)(void *, uint32_t, int, unsigned int, ...);
  i = (seccomp_rule_add);
  o = _cffi_from_c_pointer((char *)i, _cffi_type(2));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "seccomp_rule_add", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_e_enum_scmp_compare(lib);
}

static PyObject *
_cffi_f_seccomp_rule_add_array(PyObject *self, PyObject *args)
{
  void * x0;
  uint32_t x1;
  int x2;
  unsigned int x3;
  struct scmp_arg_cmp const * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:seccomp_rule_add_array", &arg0, &arg1, &arg2, &arg3, &arg4))
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

  x1 = _cffi_to_c_int(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_int(arg3, unsigned int);
  if (x3 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(3), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = seccomp_rule_add_array(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static int _cffi_const_seccomp_rule_add_exact(PyObject *lib)
{
  PyObject *o;
  int res;
  int(* i)(void *, uint32_t, int, unsigned int, ...);
  i = (seccomp_rule_add_exact);
  o = _cffi_from_c_pointer((char *)i, _cffi_type(2));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "seccomp_rule_add_exact", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_seccomp_rule_add(lib);
}

static PyObject *
_cffi_f_seccomp_rule_add_exact_array(PyObject *self, PyObject *args)
{
  void * x0;
  uint32_t x1;
  int x2;
  unsigned int x3;
  struct scmp_arg_cmp const * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:seccomp_rule_add_exact_array", &arg0, &arg1, &arg2, &arg3, &arg4))
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

  x1 = _cffi_to_c_int(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_int(arg3, unsigned int);
  if (x3 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(3), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = seccomp_rule_add_exact_array(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static int _cffi_const_SCMP_ACT_ALLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_ACT_ALLOW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_ACT_ALLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_seccomp_rule_add_exact(lib);
}

static int _cffi_const_SCMP_ACT_KILL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_ACT_KILL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_ACT_KILL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_ACT_ALLOW(lib);
}

static int _cffi_const_SCMP_ACT_TRAP(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_ACT_TRAP);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_ACT_TRAP", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_ACT_KILL(lib);
}

static int _cffi_const_SCMP_CMP_EQ(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_EQ);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_EQ", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_ACT_TRAP(lib);
}

static int _cffi_const_SCMP_CMP_GE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_GE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_GE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_EQ(lib);
}

static int _cffi_const_SCMP_CMP_GT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_GT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_GT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_GE(lib);
}

static int _cffi_const_SCMP_CMP_LE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_LE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_LE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_GT(lib);
}

static int _cffi_const_SCMP_CMP_LT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_LT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_LT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_LE(lib);
}

static int _cffi_const_SCMP_CMP_MASKED_EQ(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_MASKED_EQ);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_MASKED_EQ", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_LT(lib);
}

static int _cffi_const_SCMP_CMP_NE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SCMP_CMP_NE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SCMP_CMP_NE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_MASKED_EQ(lib);
}

static int _cffi_const___NR_SCMP_ERROR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_SCMP_ERROR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_SCMP_ERROR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_SCMP_CMP_NE(lib);
}

static int _cffi_const___NR__llseek(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR__llseek);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR__llseek", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_SCMP_ERROR(lib);
}

static int _cffi_const___NR__newselect(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR__newselect);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR__newselect", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR__llseek(lib);
}

static int _cffi_const___NR__sysctl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR__sysctl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR__sysctl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR__newselect(lib);
}

static int _cffi_const___NR_accept(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_accept);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_accept", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR__sysctl(lib);
}

static int _cffi_const___NR_accept4(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_accept4);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_accept4", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_accept(lib);
}

static int _cffi_const___NR_afs_syscall(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_afs_syscall);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_afs_syscall", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_accept4(lib);
}

static int _cffi_const___NR_arch_prctl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_arch_prctl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_arch_prctl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_afs_syscall(lib);
}

static int _cffi_const___NR_arm_fadvise64_64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_arm_fadvise64_64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_arm_fadvise64_64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_arch_prctl(lib);
}

static int _cffi_const___NR_arm_sync_file_range(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_arm_sync_file_range);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_arm_sync_file_range", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_arm_fadvise64_64(lib);
}

static int _cffi_const___NR_bdflush(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_bdflush);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_bdflush", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_arm_sync_file_range(lib);
}

static int _cffi_const___NR_bind(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_bind);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_bind", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_bdflush(lib);
}

static int _cffi_const___NR_break(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_break);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_break", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_bind(lib);
}

static int _cffi_const___NR_chown32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_chown32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_chown32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_break(lib);
}

static int _cffi_const___NR_connect(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_connect);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_connect", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_chown32(lib);
}

static int _cffi_const___NR_create_module(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_create_module);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_create_module", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_connect(lib);
}

static int _cffi_const___NR_epoll_ctl_old(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_epoll_ctl_old);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_epoll_ctl_old", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_create_module(lib);
}

static int _cffi_const___NR_epoll_wait_old(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_epoll_wait_old);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_epoll_wait_old", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_epoll_ctl_old(lib);
}

static int _cffi_const___NR_fadvise64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fadvise64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fadvise64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_epoll_wait_old(lib);
}

static int _cffi_const___NR_fadvise64_64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fadvise64_64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fadvise64_64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fadvise64(lib);
}

static int _cffi_const___NR_fchown32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fchown32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fchown32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fadvise64_64(lib);
}

static int _cffi_const___NR_fcntl64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fcntl64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fcntl64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fchown32(lib);
}

static int _cffi_const___NR_finit_module(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_finit_module);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_finit_module", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fcntl64(lib);
}

static int _cffi_const___NR_fstat64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fstat64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fstat64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_finit_module(lib);
}

static int _cffi_const___NR_fstatat64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fstatat64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fstatat64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fstat64(lib);
}

static int _cffi_const___NR_fstatfs64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_fstatfs64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_fstatfs64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fstatat64(lib);
}

static int _cffi_const___NR_ftime(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ftime);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ftime", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_fstatfs64(lib);
}

static int _cffi_const___NR_ftruncate64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ftruncate64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ftruncate64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ftime(lib);
}

static int _cffi_const___NR_get_kernel_syms(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_get_kernel_syms);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_get_kernel_syms", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ftruncate64(lib);
}

static int _cffi_const___NR_get_thread_area(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_get_thread_area);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_get_thread_area", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_get_kernel_syms(lib);
}

static int _cffi_const___NR_getegid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getegid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getegid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_get_thread_area(lib);
}

static int _cffi_const___NR_geteuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_geteuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_geteuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getegid32(lib);
}

static int _cffi_const___NR_getgid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getgid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getgid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_geteuid32(lib);
}

static int _cffi_const___NR_getgroups32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getgroups32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getgroups32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getgid32(lib);
}

static int _cffi_const___NR_getpeername(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getpeername);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getpeername", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getgroups32(lib);
}

static int _cffi_const___NR_getpmsg(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getpmsg);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getpmsg", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getpeername(lib);
}

static int _cffi_const___NR_getresgid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getresgid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getresgid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getpmsg(lib);
}

static int _cffi_const___NR_getresuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getresuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getresuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getresgid32(lib);
}

static int _cffi_const___NR_getsockname(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getsockname);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getsockname", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getresuid32(lib);
}

static int _cffi_const___NR_getsockopt(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getsockopt);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getsockopt", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getsockname(lib);
}

static int _cffi_const___NR_getuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_getuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_getuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getsockopt(lib);
}

static int _cffi_const___NR_gtty(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_gtty);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_gtty", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_getuid32(lib);
}

static int _cffi_const___NR_idle(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_idle);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_idle", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_gtty(lib);
}

static int _cffi_const___NR_ioperm(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ioperm);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ioperm", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_idle(lib);
}

static int _cffi_const___NR_iopl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_iopl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_iopl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ioperm(lib);
}

static int _cffi_const___NR_ipc(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ipc);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ipc", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_iopl(lib);
}

static int _cffi_const___NR_kcmp(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_kcmp);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_kcmp", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ipc(lib);
}

static int _cffi_const___NR_lchown32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_lchown32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_lchown32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_kcmp(lib);
}

static int _cffi_const___NR_listen(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_listen);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_listen", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_lchown32(lib);
}

static int _cffi_const___NR_lock(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_lock);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_lock", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_listen(lib);
}

static int _cffi_const___NR_lstat64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_lstat64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_lstat64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_lock(lib);
}

static int _cffi_const___NR_migrate_pages(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_migrate_pages);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_migrate_pages", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_lstat64(lib);
}

static int _cffi_const___NR_mmap2(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_mmap2);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_mmap2", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_migrate_pages(lib);
}

static int _cffi_const___NR_modify_ldt(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_modify_ldt);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_modify_ldt", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_mmap2(lib);
}

static int _cffi_const___NR_mpx(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_mpx);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_mpx", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_modify_ldt(lib);
}

static int _cffi_const___NR_msgctl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_msgctl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_msgctl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_mpx(lib);
}

static int _cffi_const___NR_msgget(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_msgget);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_msgget", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_msgctl(lib);
}

static int _cffi_const___NR_msgrcv(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_msgrcv);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_msgrcv", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_msgget(lib);
}

static int _cffi_const___NR_msgsnd(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_msgsnd);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_msgsnd", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_msgrcv(lib);
}

static int _cffi_const___NR_newfstatat(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_newfstatat);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_newfstatat", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_msgsnd(lib);
}

static int _cffi_const___NR_nfsservctl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_nfsservctl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_nfsservctl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_newfstatat(lib);
}

static int _cffi_const___NR_nice(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_nice);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_nice", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_nfsservctl(lib);
}

static int _cffi_const___NR_oldfstat(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_oldfstat);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_oldfstat", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_nice(lib);
}

static int _cffi_const___NR_oldlstat(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_oldlstat);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_oldlstat", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_oldfstat(lib);
}

static int _cffi_const___NR_oldolduname(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_oldolduname);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_oldolduname", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_oldlstat(lib);
}

static int _cffi_const___NR_oldstat(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_oldstat);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_oldstat", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_oldolduname(lib);
}

static int _cffi_const___NR_olduname(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_olduname);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_olduname", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_oldstat(lib);
}

static int _cffi_const___NR_pciconfig_iobase(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_pciconfig_iobase);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_pciconfig_iobase", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_olduname(lib);
}

static int _cffi_const___NR_pciconfig_read(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_pciconfig_read);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_pciconfig_read", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_pciconfig_iobase(lib);
}

static int _cffi_const___NR_pciconfig_write(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_pciconfig_write);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_pciconfig_write", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_pciconfig_read(lib);
}

static int _cffi_const___NR_prof(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_prof);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_prof", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_pciconfig_write(lib);
}

static int _cffi_const___NR_profil(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_profil);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_profil", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_prof(lib);
}

static int _cffi_const___NR_putpmsg(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_putpmsg);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_putpmsg", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_profil(lib);
}

static int _cffi_const___NR_query_module(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_query_module);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_query_module", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_putpmsg(lib);
}

static int _cffi_const___NR_readdir(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_readdir);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_readdir", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_query_module(lib);
}

static int _cffi_const___NR_recv(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_recv);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_recv", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_readdir(lib);
}

static int _cffi_const___NR_recvfrom(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_recvfrom);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_recvfrom", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_recv(lib);
}

static int _cffi_const___NR_recvmmsg(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_recvmmsg);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_recvmmsg", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_recvfrom(lib);
}

static int _cffi_const___NR_recvmsg(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_recvmsg);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_recvmsg", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_recvmmsg(lib);
}

static int _cffi_const___NR_security(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_security);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_security", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_recvmsg(lib);
}

static int _cffi_const___NR_semctl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_semctl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_semctl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_security(lib);
}

static int _cffi_const___NR_semget(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_semget);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_semget", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_semctl(lib);
}

static int _cffi_const___NR_semop(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_semop);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_semop", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_semget(lib);
}

static int _cffi_const___NR_semtimedop(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_semtimedop);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_semtimedop", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_semop(lib);
}

static int _cffi_const___NR_send(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_send);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_send", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_semtimedop(lib);
}

static int _cffi_const___NR_sendfile64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sendfile64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sendfile64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_send(lib);
}

static int _cffi_const___NR_sendmmsg(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sendmmsg);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sendmmsg", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sendfile64(lib);
}

static int _cffi_const___NR_sendmsg(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sendmsg);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sendmsg", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sendmmsg(lib);
}

static int _cffi_const___NR_sendto(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sendto);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sendto", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sendmsg(lib);
}

static int _cffi_const___NR_set_thread_area(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_set_thread_area);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_set_thread_area", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sendto(lib);
}

static int _cffi_const___NR_setfsgid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setfsgid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setfsgid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_set_thread_area(lib);
}

static int _cffi_const___NR_setfsuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setfsuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setfsuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setfsgid32(lib);
}

static int _cffi_const___NR_setgid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setgid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setgid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setfsuid32(lib);
}

static int _cffi_const___NR_setgroups32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setgroups32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setgroups32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setgid32(lib);
}

static int _cffi_const___NR_setregid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setregid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setregid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setgroups32(lib);
}

static int _cffi_const___NR_setresgid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setresgid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setresgid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setregid32(lib);
}

static int _cffi_const___NR_setresuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setresuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setresuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setresgid32(lib);
}

static int _cffi_const___NR_setreuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setreuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setreuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setresuid32(lib);
}

static int _cffi_const___NR_setsockopt(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setsockopt);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setsockopt", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setreuid32(lib);
}

static int _cffi_const___NR_setuid32(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_setuid32);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_setuid32", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setsockopt(lib);
}

static int _cffi_const___NR_sgetmask(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sgetmask);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sgetmask", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_setuid32(lib);
}

static int _cffi_const___NR_shmat(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_shmat);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_shmat", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sgetmask(lib);
}

static int _cffi_const___NR_shmctl(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_shmctl);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_shmctl", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_shmat(lib);
}

static int _cffi_const___NR_shmdt(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_shmdt);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_shmdt", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_shmctl(lib);
}

static int _cffi_const___NR_shmget(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_shmget);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_shmget", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_shmdt(lib);
}

static int _cffi_const___NR_shutdown(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_shutdown);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_shutdown", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_shmget(lib);
}

static int _cffi_const___NR_sigaction(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sigaction);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sigaction", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_shutdown(lib);
}

static int _cffi_const___NR_signal(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_signal);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_signal", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sigaction(lib);
}

static int _cffi_const___NR_sigpending(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sigpending);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sigpending", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_signal(lib);
}

static int _cffi_const___NR_sigprocmask(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sigprocmask);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sigprocmask", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sigpending(lib);
}

static int _cffi_const___NR_sigreturn(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sigreturn);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sigreturn", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sigprocmask(lib);
}

static int _cffi_const___NR_sigsuspend(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sigsuspend);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sigsuspend", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sigreturn(lib);
}

static int _cffi_const___NR_socket(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_socket);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_socket", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sigsuspend(lib);
}

static int _cffi_const___NR_socketcall(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_socketcall);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_socketcall", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_socket(lib);
}

static int _cffi_const___NR_socketpair(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_socketpair);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_socketpair", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_socketcall(lib);
}

static int _cffi_const___NR_ssetmask(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ssetmask);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ssetmask", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_socketpair(lib);
}

static int _cffi_const___NR_stat64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_stat64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_stat64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ssetmask(lib);
}

static int _cffi_const___NR_statfs64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_statfs64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_statfs64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_stat64(lib);
}

static int _cffi_const___NR_stime(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_stime);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_stime", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_statfs64(lib);
}

static int _cffi_const___NR_stty(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_stty);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_stty", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_stime(lib);
}

static int _cffi_const___NR_sync_file_range(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sync_file_range);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sync_file_range", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_stty(lib);
}

static int _cffi_const___NR_sync_file_range2(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_sync_file_range2);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_sync_file_range2", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sync_file_range(lib);
}

static int _cffi_const___NR_syscall(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_syscall);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_syscall", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_sync_file_range2(lib);
}

static int _cffi_const___NR_truncate64(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_truncate64);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_truncate64", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_syscall(lib);
}

static int _cffi_const___NR_tuxcall(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_tuxcall);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_tuxcall", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_truncate64(lib);
}

static int _cffi_const___NR_ugetrlimit(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ugetrlimit);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ugetrlimit", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_tuxcall(lib);
}

static int _cffi_const___NR_ulimit(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_ulimit);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_ulimit", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ugetrlimit(lib);
}

static int _cffi_const___NR_umount(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_umount);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_umount", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_ulimit(lib);
}

static int _cffi_const___NR_uselib(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_uselib);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_uselib", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_umount(lib);
}

static int _cffi_const___NR_vm86(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_vm86);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_vm86", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_uselib(lib);
}

static int _cffi_const___NR_vm86old(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_vm86old);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_vm86old", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_vm86(lib);
}

static int _cffi_const___NR_vserver(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_vserver);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_vserver", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_vm86old(lib);
}

static int _cffi_const___NR_waitpid(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(__NR_waitpid);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__NR_waitpid", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___NR_vserver(lib);
}

static void _cffi_check_struct_scmp_arg_cmp(struct scmp_arg_cmp *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->arg) << 1);
  { enum scmp_compare *tmp = &p->op; (void)tmp; }
  (void)((p->datum_a) << 1);
  (void)((p->datum_b) << 1);
}
static PyObject *
_cffi_layout_struct_scmp_arg_cmp(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct scmp_arg_cmp y; };
  static Py_ssize_t nums[] = {
    sizeof(struct scmp_arg_cmp),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct scmp_arg_cmp, arg),
    sizeof(((struct scmp_arg_cmp *)0)->arg),
    offsetof(struct scmp_arg_cmp, op),
    sizeof(((struct scmp_arg_cmp *)0)->op),
    offsetof(struct scmp_arg_cmp, datum_a),
    sizeof(((struct scmp_arg_cmp *)0)->datum_a),
    offsetof(struct scmp_arg_cmp, datum_b),
    sizeof(((struct scmp_arg_cmp *)0)->datum_b),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_scmp_arg_cmp(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const___NR_waitpid(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"_SCMP_ACT_ERRNO", _cffi_f__SCMP_ACT_ERRNO, METH_O, NULL},
  {"_SCMP_ACT_TRACE", _cffi_f__SCMP_ACT_TRACE, METH_O, NULL},
  {"seccomp_init", _cffi_f_seccomp_init, METH_O, NULL},
  {"seccomp_load", _cffi_f_seccomp_load, METH_O, NULL},
  {"seccomp_merge", _cffi_f_seccomp_merge, METH_VARARGS, NULL},
  {"seccomp_release", _cffi_f_seccomp_release, METH_O, NULL},
  {"seccomp_reset", _cffi_f_seccomp_reset, METH_VARARGS, NULL},
  {"seccomp_rule_add_array", _cffi_f_seccomp_rule_add_array, METH_VARARGS, NULL},
  {"seccomp_rule_add_exact_array", _cffi_f_seccomp_rule_add_exact_array, METH_VARARGS, NULL},
  {"_cffi_layout_struct_scmp_arg_cmp", _cffi_layout_struct_scmp_arg_cmp, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__xd4952e7cxc06518cb",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__xd4952e7cxc06518cb(void)
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
init_cffi__xd4952e7cxc06518cb(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__xd4952e7cxc06518cb", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif


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



#include <sys/types.h>
#include <sys/errno.h>
#include <sys/capability.h>


static int _cffi_const___cap_rights_clear(PyObject *lib)
{
  PyObject *o;
  int res;
  cap_rights_t *(* i)(cap_rights_t *, ...);
  i = (__cap_rights_clear);
  o = _cffi_from_c_pointer((char *)i, _cffi_type(0));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__cap_rights_clear", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return ((void)lib,0);
}

static int _cffi_const___cap_rights_init(PyObject *lib)
{
  PyObject *o;
  int res;
  cap_rights_t *(* i)(int, cap_rights_t *, ...);
  i = (__cap_rights_init);
  o = _cffi_from_c_pointer((char *)i, _cffi_type(1));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__cap_rights_init", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___cap_rights_clear(lib);
}

static int _cffi_const___cap_rights_is_set(PyObject *lib)
{
  PyObject *o;
  int res;
  _Bool(* i)(cap_rights_t const *, ...);
  i = (__cap_rights_is_set);
  o = _cffi_from_c_pointer((char *)i, _cffi_type(2));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__cap_rights_is_set", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___cap_rights_init(lib);
}

static int _cffi_const___cap_rights_set(PyObject *lib)
{
  PyObject *o;
  int res;
  cap_rights_t *(* i)(cap_rights_t *, ...);
  i = (__cap_rights_set);
  o = _cffi_from_c_pointer((char *)i, _cffi_type(0));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "__cap_rights_set", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___cap_rights_is_set(lib);
}

static PyObject *
_cffi_f_cap_enter(PyObject *self, PyObject *noarg)
{
  int result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_enter(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_fcntls_get(PyObject *self, PyObject *args)
{
  int x0;
  uint32_t * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_fcntls_get", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(3), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_fcntls_get(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_fcntls_limit(PyObject *self, PyObject *args)
{
  int x0;
  uint32_t x1;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_fcntls_limit", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_fcntls_limit(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_getmode(PyObject *self, PyObject *arg0)
{
  unsigned int * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_getmode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_ioctls_get(PyObject *self, PyObject *args)
{
  int x0;
  unsigned long * x1;
  size_t x2;
  Py_ssize_t datasize;
  ssize_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:cap_ioctls_get", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(5), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_ioctls_get(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, ssize_t);
}

static PyObject *
_cffi_f_cap_ioctls_limit(PyObject *self, PyObject *args)
{
  int x0;
  unsigned long const * x1;
  size_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:cap_ioctls_limit", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(6), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_ioctls_limit(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_rights_contains(PyObject *self, PyObject *args)
{
  cap_rights_t const * x0;
  cap_rights_t const * x1;
  Py_ssize_t datasize;
  _Bool result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_rights_contains", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_rights_contains(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, _Bool);
}

static PyObject *
_cffi_f_cap_rights_get(PyObject *self, PyObject *args)
{
  int x0;
  cap_rights_t * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_rights_get", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(8), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_rights_get(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_rights_is_valid(PyObject *self, PyObject *arg0)
{
  cap_rights_t const * x0;
  Py_ssize_t datasize;
  _Bool result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_rights_is_valid(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, _Bool);
}

static PyObject *
_cffi_f_cap_rights_limit(PyObject *self, PyObject *args)
{
  int x0;
  cap_rights_t const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_rights_limit", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_rights_limit(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cap_rights_merge(PyObject *self, PyObject *args)
{
  cap_rights_t * x0;
  cap_rights_t const * x1;
  Py_ssize_t datasize;
  cap_rights_t * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_rights_merge", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(8), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_rights_merge(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(8));
}

static PyObject *
_cffi_f_cap_rights_remove(PyObject *self, PyObject *args)
{
  cap_rights_t * x0;
  cap_rights_t const * x1;
  Py_ssize_t datasize;
  cap_rights_t * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:cap_rights_remove", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(8), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = cap_rights_remove(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(8));
}

static int _cffi_const_CAP_ACCEPT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_ACCEPT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_ACCEPT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const___cap_rights_set(lib);
}

static int _cffi_const_CAP_ACL_CHECK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_ACL_CHECK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_ACL_CHECK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_ACCEPT(lib);
}

static int _cffi_const_CAP_ACL_DELETE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_ACL_DELETE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_ACL_DELETE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_ACL_CHECK(lib);
}

static int _cffi_const_CAP_ACL_GET(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_ACL_GET);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_ACL_GET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_ACL_DELETE(lib);
}

static int _cffi_const_CAP_ACL_SET(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_ACL_SET);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_ACL_SET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_ACL_GET(lib);
}

static int _cffi_const_CAP_BIND(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_BIND);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_BIND", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_ACL_SET(lib);
}

static int _cffi_const_CAP_BINDAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_BINDAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_BINDAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_BIND(lib);
}

static int _cffi_const_CAP_CHFLAGSAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_CHFLAGSAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_CHFLAGSAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_BINDAT(lib);
}

static int _cffi_const_CAP_CONNECT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_CONNECT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_CONNECT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_CHFLAGSAT(lib);
}

static int _cffi_const_CAP_CONNECTAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_CONNECTAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_CONNECTAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_CONNECT(lib);
}

static int _cffi_const_CAP_CREATE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_CREATE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_CREATE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_CONNECTAT(lib);
}

static int _cffi_const_CAP_EVENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_EVENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_EVENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_CREATE(lib);
}

static int _cffi_const_CAP_EXTATTR_DELETE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_EXTATTR_DELETE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_EXTATTR_DELETE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_EVENT(lib);
}

static int _cffi_const_CAP_EXTATTR_GET(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_EXTATTR_GET);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_EXTATTR_GET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_EXTATTR_DELETE(lib);
}

static int _cffi_const_CAP_EXTATTR_LIST(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_EXTATTR_LIST);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_EXTATTR_LIST", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_EXTATTR_GET(lib);
}

static int _cffi_const_CAP_EXTATTR_SET(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_EXTATTR_SET);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_EXTATTR_SET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_EXTATTR_LIST(lib);
}

static int _cffi_const_CAP_FCHDIR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCHDIR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCHDIR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_EXTATTR_SET(lib);
}

static int _cffi_const_CAP_FCHFLAGS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCHFLAGS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCHFLAGS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCHDIR(lib);
}

static int _cffi_const_CAP_FCHMOD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCHMOD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCHMOD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCHFLAGS(lib);
}

static int _cffi_const_CAP_FCHMODAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCHMODAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCHMODAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCHMOD(lib);
}

static int _cffi_const_CAP_FCHOWN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCHOWN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCHOWN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCHMODAT(lib);
}

static int _cffi_const_CAP_FCHOWNAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCHOWNAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCHOWNAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCHOWN(lib);
}

static int _cffi_const_CAP_FCNTL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCNTL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCNTL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCHOWNAT(lib);
}

static int _cffi_const_CAP_FCNTL_GETFL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCNTL_GETFL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCNTL_GETFL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCNTL(lib);
}

static int _cffi_const_CAP_FCNTL_GETOWN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCNTL_GETOWN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCNTL_GETOWN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCNTL_GETFL(lib);
}

static int _cffi_const_CAP_FCNTL_SETFL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCNTL_SETFL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCNTL_SETFL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCNTL_GETOWN(lib);
}

static int _cffi_const_CAP_FCNTL_SETOWN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FCNTL_SETOWN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FCNTL_SETOWN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCNTL_SETFL(lib);
}

static int _cffi_const_CAP_FEXECVE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FEXECVE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FEXECVE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FCNTL_SETOWN(lib);
}

static int _cffi_const_CAP_FLOCK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FLOCK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FLOCK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FEXECVE(lib);
}

static int _cffi_const_CAP_FPATHCONF(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FPATHCONF);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FPATHCONF", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FLOCK(lib);
}

static int _cffi_const_CAP_FSCK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FSCK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FSCK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FPATHCONF(lib);
}

static int _cffi_const_CAP_FSTAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FSTAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FSTAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FSCK(lib);
}

static int _cffi_const_CAP_FSTATAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FSTATAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FSTATAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FSTAT(lib);
}

static int _cffi_const_CAP_FSTATFS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FSTATFS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FSTATFS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FSTATAT(lib);
}

static int _cffi_const_CAP_FSYNC(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FSYNC);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FSYNC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FSTATFS(lib);
}

static int _cffi_const_CAP_FTRUNCATE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FTRUNCATE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FTRUNCATE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FSYNC(lib);
}

static int _cffi_const_CAP_FUTIMES(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FUTIMES);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FUTIMES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FTRUNCATE(lib);
}

static int _cffi_const_CAP_FUTIMESAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_FUTIMESAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_FUTIMESAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FUTIMES(lib);
}

static int _cffi_const_CAP_GETPEERNAME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_GETPEERNAME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_GETPEERNAME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_FUTIMESAT(lib);
}

static int _cffi_const_CAP_GETSOCKNAME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_GETSOCKNAME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_GETSOCKNAME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_GETPEERNAME(lib);
}

static int _cffi_const_CAP_GETSOCKOPT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_GETSOCKOPT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_GETSOCKOPT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_GETSOCKNAME(lib);
}

static int _cffi_const_CAP_IOCTL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_IOCTL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_IOCTL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_GETSOCKOPT(lib);
}

static int _cffi_const_CAP_IOCTLS_ALL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_IOCTLS_ALL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_IOCTLS_ALL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_IOCTL(lib);
}

static int _cffi_const_CAP_KQUEUE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_KQUEUE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_KQUEUE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_IOCTLS_ALL(lib);
}

static int _cffi_const_CAP_KQUEUE_CHANGE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_KQUEUE_CHANGE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_KQUEUE_CHANGE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_KQUEUE(lib);
}

static int _cffi_const_CAP_KQUEUE_EVENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_KQUEUE_EVENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_KQUEUE_EVENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_KQUEUE_CHANGE(lib);
}

static int _cffi_const_CAP_LINKAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_LINKAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_LINKAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_KQUEUE_EVENT(lib);
}

static int _cffi_const_CAP_LISTEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_LISTEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_LISTEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_LINKAT(lib);
}

static int _cffi_const_CAP_LOOKUP(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_LOOKUP);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_LOOKUP", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_LISTEN(lib);
}

static int _cffi_const_CAP_MAC_GET(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MAC_GET);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MAC_GET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_LOOKUP(lib);
}

static int _cffi_const_CAP_MAC_SET(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MAC_SET);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MAC_SET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MAC_GET(lib);
}

static int _cffi_const_CAP_MKDIRAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MKDIRAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MKDIRAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MAC_SET(lib);
}

static int _cffi_const_CAP_MKFIFOAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MKFIFOAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MKFIFOAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MKDIRAT(lib);
}

static int _cffi_const_CAP_MKNODAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MKNODAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MKNODAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MKFIFOAT(lib);
}

static int _cffi_const_CAP_MMAP(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MKNODAT(lib);
}

static int _cffi_const_CAP_MMAP_R(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_R);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_R", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP(lib);
}

static int _cffi_const_CAP_MMAP_RW(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_RW);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_RW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_R(lib);
}

static int _cffi_const_CAP_MMAP_RWX(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_RWX);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_RWX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_RW(lib);
}

static int _cffi_const_CAP_MMAP_RX(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_RX);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_RX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_RWX(lib);
}

static int _cffi_const_CAP_MMAP_W(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_W);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_W", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_RX(lib);
}

static int _cffi_const_CAP_MMAP_WX(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_WX);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_WX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_W(lib);
}

static int _cffi_const_CAP_MMAP_X(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_MMAP_X);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_MMAP_X", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_WX(lib);
}

static int _cffi_const_CAP_PDGETPID(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_PDGETPID);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_PDGETPID", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_MMAP_X(lib);
}

static int _cffi_const_CAP_PDKILL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_PDKILL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_PDKILL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_PDGETPID(lib);
}

static int _cffi_const_CAP_PDWAIT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_PDWAIT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_PDWAIT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_PDKILL(lib);
}

static int _cffi_const_CAP_PEELOFF(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_PEELOFF);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_PEELOFF", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_PDWAIT(lib);
}

static int _cffi_const_CAP_PREAD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_PREAD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_PREAD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_PEELOFF(lib);
}

static int _cffi_const_CAP_PWRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_PWRITE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_PWRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_PREAD(lib);
}

static int _cffi_const_CAP_READ(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_READ);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_READ", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_PWRITE(lib);
}

static int _cffi_const_CAP_RECV(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_RECV);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_RECV", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_READ(lib);
}

static int _cffi_const_CAP_RENAMEAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_RENAMEAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_RENAMEAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_RECV(lib);
}

static int _cffi_const_CAP_RIGHTS_VERSION(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_RIGHTS_VERSION);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_RIGHTS_VERSION", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_RENAMEAT(lib);
}

static int _cffi_const_CAP_SEEK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SEEK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SEEK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_RIGHTS_VERSION(lib);
}

static int _cffi_const_CAP_SEM_GETVALUE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SEM_GETVALUE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SEM_GETVALUE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SEEK(lib);
}

static int _cffi_const_CAP_SEM_POST(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SEM_POST);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SEM_POST", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SEM_GETVALUE(lib);
}

static int _cffi_const_CAP_SEM_WAIT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SEM_WAIT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SEM_WAIT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SEM_POST(lib);
}

static int _cffi_const_CAP_SEND(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SEND);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SEND", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SEM_WAIT(lib);
}

static int _cffi_const_CAP_SETSOCKOPT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SETSOCKOPT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SETSOCKOPT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SEND(lib);
}

static int _cffi_const_CAP_SHUTDOWN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SHUTDOWN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SHUTDOWN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SETSOCKOPT(lib);
}

static int _cffi_const_CAP_SYMLINKAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_SYMLINKAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_SYMLINKAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SHUTDOWN(lib);
}

static int _cffi_const_CAP_TTYHOOK(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_TTYHOOK);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_TTYHOOK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_SYMLINKAT(lib);
}

static int _cffi_const_CAP_UNLINKAT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_UNLINKAT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_UNLINKAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_TTYHOOK(lib);
}

static int _cffi_const_CAP_WRITE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(CAP_WRITE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CAP_WRITE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_UNLINKAT(lib);
}

static int _cffi_const_ECAPMODE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(ECAPMODE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ECAPMODE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CAP_WRITE(lib);
}

static int _cffi_const_ENOTCAPABLE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(ENOTCAPABLE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ENOTCAPABLE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ECAPMODE(lib);
}

static int _cffi_const_ENOTRECOVERABLE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(ENOTRECOVERABLE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ENOTRECOVERABLE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ENOTCAPABLE(lib);
}

static int _cffi_const_EOWNERDEAD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EOWNERDEAD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EOWNERDEAD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ENOTRECOVERABLE(lib);
}

static void _cffi_check_struct_cap_rights(struct cap_rights *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
}
static PyObject *
_cffi_layout_struct_cap_rights(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct cap_rights y; };
  static Py_ssize_t nums[] = {
    sizeof(struct cap_rights),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_cap_rights(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_EOWNERDEAD(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"cap_enter", _cffi_f_cap_enter, METH_NOARGS, NULL},
  {"cap_fcntls_get", _cffi_f_cap_fcntls_get, METH_VARARGS, NULL},
  {"cap_fcntls_limit", _cffi_f_cap_fcntls_limit, METH_VARARGS, NULL},
  {"cap_getmode", _cffi_f_cap_getmode, METH_O, NULL},
  {"cap_ioctls_get", _cffi_f_cap_ioctls_get, METH_VARARGS, NULL},
  {"cap_ioctls_limit", _cffi_f_cap_ioctls_limit, METH_VARARGS, NULL},
  {"cap_rights_contains", _cffi_f_cap_rights_contains, METH_VARARGS, NULL},
  {"cap_rights_get", _cffi_f_cap_rights_get, METH_VARARGS, NULL},
  {"cap_rights_is_valid", _cffi_f_cap_rights_is_valid, METH_O, NULL},
  {"cap_rights_limit", _cffi_f_cap_rights_limit, METH_VARARGS, NULL},
  {"cap_rights_merge", _cffi_f_cap_rights_merge, METH_VARARGS, NULL},
  {"cap_rights_remove", _cffi_f_cap_rights_remove, METH_VARARGS, NULL},
  {"_cffi_layout_struct_cap_rights", _cffi_layout_struct_cap_rights, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__x368c86e1x65aaebc5",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__x368c86e1x65aaebc5(void)
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
init_cffi__x368c86e1x65aaebc5(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x368c86e1x65aaebc5", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

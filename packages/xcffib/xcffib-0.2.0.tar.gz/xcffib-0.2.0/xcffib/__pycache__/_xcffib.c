
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
    (((type)-1) > 0 ?   /* unsigned */                                   \
        (sizeof(type) < sizeof(long) ? PyInt_FromLong(x) :               \
         sizeof(type) == sizeof(long) ? PyLong_FromUnsignedLong(x) :     \
                                        PyLong_FromUnsignedLongLong(x))  \
      : (sizeof(type) <= sizeof(long) ? PyInt_FromLong(x) :              \
                                        PyLong_FromLongLong(x)))

#define _cffi_to_c_int(o, type)                                          \
    (sizeof(type) == 1 ? (((type)-1) > 0 ? (type)_cffi_to_c_u8(o)        \
                                         : (type)_cffi_to_c_i8(o)) :     \
     sizeof(type) == 2 ? (((type)-1) > 0 ? (type)_cffi_to_c_u16(o)       \
                                         : (type)_cffi_to_c_i16(o)) :    \
     sizeof(type) == 4 ? (((type)-1) > 0 ? (type)_cffi_to_c_u32(o)       \
                                         : (type)_cffi_to_c_i32(o)) :    \
     sizeof(type) == 8 ? (((type)-1) > 0 ? (type)_cffi_to_c_u64(o)       \
                                         : (type)_cffi_to_c_i64(o)) :    \
     (Py_FatalError("unsupported size for type " #type), 0))

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



    #include <stdlib.h>
    #include <xcb/xcb.h>
    #include <xcb/xcbext.h>
    #include <xcb/render.h>


static void _cffi_check__xcb_generic_error_t(xcb_generic_error_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->response_type) << 1);
  (void)((p->error_code) << 1);
  (void)((p->sequence) << 1);
  (void)((p->resource_id) << 1);
  (void)((p->minor_code) << 1);
  (void)((p->major_code) << 1);
  (void)((p->pad0) << 1);
  { uint32_t(*tmp)[5] = &p->pad; (void)tmp; }
  (void)((p->full_sequence) << 1);
}
static PyObject *
_cffi_layout__xcb_generic_error_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; xcb_generic_error_t y; };
  static Py_ssize_t nums[] = {
    sizeof(xcb_generic_error_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(xcb_generic_error_t, response_type),
    sizeof(((xcb_generic_error_t *)0)->response_type),
    offsetof(xcb_generic_error_t, error_code),
    sizeof(((xcb_generic_error_t *)0)->error_code),
    offsetof(xcb_generic_error_t, sequence),
    sizeof(((xcb_generic_error_t *)0)->sequence),
    offsetof(xcb_generic_error_t, resource_id),
    sizeof(((xcb_generic_error_t *)0)->resource_id),
    offsetof(xcb_generic_error_t, minor_code),
    sizeof(((xcb_generic_error_t *)0)->minor_code),
    offsetof(xcb_generic_error_t, major_code),
    sizeof(((xcb_generic_error_t *)0)->major_code),
    offsetof(xcb_generic_error_t, pad0),
    sizeof(((xcb_generic_error_t *)0)->pad0),
    offsetof(xcb_generic_error_t, pad),
    sizeof(((xcb_generic_error_t *)0)->pad),
    offsetof(xcb_generic_error_t, full_sequence),
    sizeof(((xcb_generic_error_t *)0)->full_sequence),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__xcb_generic_error_t(0);
}

static void _cffi_check__xcb_generic_event_t(xcb_generic_event_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->response_type) << 1);
  (void)((p->pad0) << 1);
  (void)((p->sequence) << 1);
  { uint32_t(*tmp)[7] = &p->pad; (void)tmp; }
  (void)((p->full_sequence) << 1);
}
static PyObject *
_cffi_layout__xcb_generic_event_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; xcb_generic_event_t y; };
  static Py_ssize_t nums[] = {
    sizeof(xcb_generic_event_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(xcb_generic_event_t, response_type),
    sizeof(((xcb_generic_event_t *)0)->response_type),
    offsetof(xcb_generic_event_t, pad0),
    sizeof(((xcb_generic_event_t *)0)->pad0),
    offsetof(xcb_generic_event_t, sequence),
    sizeof(((xcb_generic_event_t *)0)->sequence),
    offsetof(xcb_generic_event_t, pad),
    sizeof(((xcb_generic_event_t *)0)->pad),
    offsetof(xcb_generic_event_t, full_sequence),
    sizeof(((xcb_generic_event_t *)0)->full_sequence),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__xcb_generic_event_t(0);
}

static void _cffi_check__xcb_generic_reply_t(xcb_generic_reply_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->response_type) << 1);
  (void)((p->pad0) << 1);
  (void)((p->sequence) << 1);
  (void)((p->length) << 1);
}
static PyObject *
_cffi_layout__xcb_generic_reply_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; xcb_generic_reply_t y; };
  static Py_ssize_t nums[] = {
    sizeof(xcb_generic_reply_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(xcb_generic_reply_t, response_type),
    sizeof(((xcb_generic_reply_t *)0)->response_type),
    offsetof(xcb_generic_reply_t, pad0),
    sizeof(((xcb_generic_reply_t *)0)->pad0),
    offsetof(xcb_generic_reply_t, sequence),
    sizeof(((xcb_generic_reply_t *)0)->sequence),
    offsetof(xcb_generic_reply_t, length),
    sizeof(((xcb_generic_reply_t *)0)->length),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__xcb_generic_reply_t(0);
}

static void _cffi_check__xcb_protocol_request_t(xcb_protocol_request_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->count) << 1);
  { xcb_extension_t * *tmp = &p->ext; (void)tmp; }
  (void)((p->opcode) << 1);
  (void)((p->isvoid) << 1);
}
static PyObject *
_cffi_layout__xcb_protocol_request_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; xcb_protocol_request_t y; };
  static Py_ssize_t nums[] = {
    sizeof(xcb_protocol_request_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(xcb_protocol_request_t, count),
    sizeof(((xcb_protocol_request_t *)0)->count),
    offsetof(xcb_protocol_request_t, ext),
    sizeof(((xcb_protocol_request_t *)0)->ext),
    offsetof(xcb_protocol_request_t, opcode),
    sizeof(((xcb_protocol_request_t *)0)->opcode),
    offsetof(xcb_protocol_request_t, isvoid),
    sizeof(((xcb_protocol_request_t *)0)->isvoid),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__xcb_protocol_request_t(0);
}

static void _cffi_check__xcb_void_cookie_t(xcb_void_cookie_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->sequence) << 1);
}
static PyObject *
_cffi_layout__xcb_void_cookie_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; xcb_void_cookie_t y; };
  static Py_ssize_t nums[] = {
    sizeof(xcb_void_cookie_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(xcb_void_cookie_t, sequence),
    sizeof(((xcb_void_cookie_t *)0)->sequence),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__xcb_void_cookie_t(0);
}

static PyObject *
_cffi_f_free(PyObject *self, PyObject *arg0)
{
  void * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_xcb_connect(PyObject *self, PyObject *args)
{
  char const * x0;
  int * x1;
  Py_ssize_t datasize;
  xcb_connection_t * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:xcb_connect", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(3), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_connect(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_xcb_connect_to_display_with_auth_info(PyObject *self, PyObject *args)
{
  char const * x0;
  xcb_auth_info_t * x1;
  int * x2;
  Py_ssize_t datasize;
  xcb_connection_t * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:xcb_connect_to_display_with_auth_info", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(5), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_connect_to_display_with_auth_info(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_xcb_connect_to_fd(PyObject *self, PyObject *args)
{
  int x0;
  xcb_auth_info_t * x1;
  Py_ssize_t datasize;
  xcb_connection_t * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:xcb_connect_to_fd", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(5), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_connect_to_fd(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_xcb_connection_has_error(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_connection_has_error(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_xcb_disconnect(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { xcb_disconnect(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_xcb_flush(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_flush(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_xcb_generate_id(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  uint32_t result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_generate_id(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, uint32_t);
}

static PyObject *
_cffi_f_xcb_get_extension_data(PyObject *self, PyObject *args)
{
  xcb_connection_t * x0;
  xcb_extension_t * x1;
  Py_ssize_t datasize;
  xcb_query_extension_reply_t const * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:xcb_get_extension_data", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(6), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_get_extension_data(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(7));
}

static PyObject *
_cffi_f_xcb_get_file_descriptor(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_get_file_descriptor(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_xcb_get_maximum_request_length(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  uint32_t result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_get_maximum_request_length(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, uint32_t);
}

static PyObject *
_cffi_f_xcb_get_setup(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  xcb_setup_t const * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_get_setup(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(8));
}

static PyObject *
_cffi_f_xcb_parse_display(PyObject *self, PyObject *args)
{
  char const * x0;
  char * * x1;
  int * x2;
  int * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:xcb_parse_display", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(9), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_parse_display(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_xcb_poll_for_event(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  xcb_generic_event_t * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_poll_for_event(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(10));
}

static PyObject *
_cffi_f_xcb_poll_for_reply(PyObject *self, PyObject *args)
{
  xcb_connection_t * x0;
  unsigned int x1;
  void * * x2;
  xcb_generic_error_t * * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:xcb_poll_for_reply", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(11), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(11), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(12), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_poll_for_reply(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_xcb_prefetch_maximum_request_length(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { xcb_prefetch_maximum_request_length(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_xcb_request_check(PyObject *self, PyObject *args)
{
  xcb_connection_t * x0;
  xcb_void_cookie_t x1;
  Py_ssize_t datasize;
  xcb_generic_error_t * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:xcb_request_check", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  if (_cffi_to_c((char *)&x1, _cffi_type(13), arg1) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_request_check(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(14));
}

static PyObject *
_cffi_f_xcb_send_request(PyObject *self, PyObject *args)
{
  xcb_connection_t * x0;
  int x1;
  struct iovec * x2;
  xcb_protocol_request_t const * x3;
  Py_ssize_t datasize;
  unsigned int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:xcb_send_request", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(15), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(15), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(16), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_send_request(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, unsigned int);
}

static PyObject *
_cffi_f_xcb_wait_for_event(PyObject *self, PyObject *arg0)
{
  xcb_connection_t * x0;
  Py_ssize_t datasize;
  xcb_generic_event_t * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_wait_for_event(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(10));
}

static PyObject *
_cffi_f_xcb_wait_for_reply(PyObject *self, PyObject *args)
{
  xcb_connection_t * x0;
  unsigned int x1;
  xcb_generic_error_t * * x2;
  Py_ssize_t datasize;
  void * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:xcb_wait_for_reply", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(4), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(12), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = xcb_wait_for_reply(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(0));
}

static int _cffi_const_XCB_CONN_CLOSED_EXT_NOTSUPPORTED(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_CONN_CLOSED_EXT_NOTSUPPORTED);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_CONN_CLOSED_EXT_NOTSUPPORTED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_XCB_CONN_CLOSED_MEM_INSUFFICIENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_CONN_CLOSED_MEM_INSUFFICIENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_CONN_CLOSED_MEM_INSUFFICIENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_CONN_CLOSED_EXT_NOTSUPPORTED(lib);
}

static int _cffi_const_XCB_CONN_CLOSED_PARSE_ERR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_CONN_CLOSED_PARSE_ERR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_CONN_CLOSED_PARSE_ERR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_CONN_CLOSED_MEM_INSUFFICIENT(lib);
}

static int _cffi_const_XCB_CONN_CLOSED_REQ_LEN_EXCEED(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_CONN_CLOSED_REQ_LEN_EXCEED);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_CONN_CLOSED_REQ_LEN_EXCEED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_CONN_CLOSED_PARSE_ERR(lib);
}

static int _cffi_const_XCB_CONN_ERROR(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_CONN_ERROR);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_CONN_ERROR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_CONN_CLOSED_REQ_LEN_EXCEED(lib);
}

static int _cffi_const_XCB_COPY_FROM_PARENT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_COPY_FROM_PARENT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_COPY_FROM_PARENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_CONN_ERROR(lib);
}

static int _cffi_const_XCB_CURRENT_TIME(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_CURRENT_TIME);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_CURRENT_TIME", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_COPY_FROM_PARENT(lib);
}

static int _cffi_const_XCB_NONE(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_NONE);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_NONE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_CURRENT_TIME(lib);
}

static int _cffi_const_XCB_NO_SYMBOL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_NO_SYMBOL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_NO_SYMBOL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_NONE(lib);
}

static int _cffi_const_XCB_REQUEST_CHECKED(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(XCB_REQUEST_CHECKED);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "XCB_REQUEST_CHECKED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_NO_SYMBOL(lib);
}

static int _cffi_const_X_PROTOCOL(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(X_PROTOCOL);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "X_PROTOCOL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_XCB_REQUEST_CHECKED(lib);
}

static int _cffi_const_X_PROTOCOL_REVISION(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(X_PROTOCOL_REVISION);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "X_PROTOCOL_REVISION", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_X_PROTOCOL(lib);
}

static int _cffi_const_X_TCP_PORT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(X_TCP_PORT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "X_TCP_PORT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_X_PROTOCOL_REVISION(lib);
}

static void _cffi_check_struct_iovec(struct iovec *p)
{
  /* only to generate compile-time warnings or errors */
  { void * *tmp = &p->iov_base; (void)tmp; }
  (void)((p->iov_len) << 1);
}
static PyObject *
_cffi_layout_struct_iovec(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct iovec y; };
  static Py_ssize_t nums[] = {
    sizeof(struct iovec),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct iovec, iov_base),
    sizeof(((struct iovec *)0)->iov_base),
    offsetof(struct iovec, iov_len),
    sizeof(((struct iovec *)0)->iov_len),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_iovec(0);
}

static void _cffi_check_struct_xcb_auth_info_t(struct xcb_auth_info_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->namelen) << 1);
  { char * *tmp = &p->name; (void)tmp; }
  (void)((p->datalen) << 1);
  { char * *tmp = &p->data; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_xcb_auth_info_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_auth_info_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_auth_info_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_auth_info_t, namelen),
    sizeof(((struct xcb_auth_info_t *)0)->namelen),
    offsetof(struct xcb_auth_info_t, name),
    sizeof(((struct xcb_auth_info_t *)0)->name),
    offsetof(struct xcb_auth_info_t, datalen),
    sizeof(((struct xcb_auth_info_t *)0)->datalen),
    offsetof(struct xcb_auth_info_t, data),
    sizeof(((struct xcb_auth_info_t *)0)->data),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_auth_info_t(0);
}

static void _cffi_check_struct_xcb_extension_t(struct xcb_extension_t *p)
{
  /* only to generate compile-time warnings or errors */
  { char const * *tmp = &p->name; (void)tmp; }
  (void)((p->global_id) << 1);
}
static PyObject *
_cffi_layout_struct_xcb_extension_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_extension_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_extension_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_extension_t, name),
    sizeof(((struct xcb_extension_t *)0)->name),
    offsetof(struct xcb_extension_t, global_id),
    sizeof(((struct xcb_extension_t *)0)->global_id),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_extension_t(0);
}

static void _cffi_check_struct_xcb_query_extension_reply_t(struct xcb_query_extension_reply_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->response_type) << 1);
  (void)((p->pad0) << 1);
  (void)((p->sequence) << 1);
  (void)((p->length) << 1);
  (void)((p->present) << 1);
  (void)((p->major_opcode) << 1);
  (void)((p->first_event) << 1);
  (void)((p->first_error) << 1);
}
static PyObject *
_cffi_layout_struct_xcb_query_extension_reply_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_query_extension_reply_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_query_extension_reply_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_query_extension_reply_t, response_type),
    sizeof(((struct xcb_query_extension_reply_t *)0)->response_type),
    offsetof(struct xcb_query_extension_reply_t, pad0),
    sizeof(((struct xcb_query_extension_reply_t *)0)->pad0),
    offsetof(struct xcb_query_extension_reply_t, sequence),
    sizeof(((struct xcb_query_extension_reply_t *)0)->sequence),
    offsetof(struct xcb_query_extension_reply_t, length),
    sizeof(((struct xcb_query_extension_reply_t *)0)->length),
    offsetof(struct xcb_query_extension_reply_t, present),
    sizeof(((struct xcb_query_extension_reply_t *)0)->present),
    offsetof(struct xcb_query_extension_reply_t, major_opcode),
    sizeof(((struct xcb_query_extension_reply_t *)0)->major_opcode),
    offsetof(struct xcb_query_extension_reply_t, first_event),
    sizeof(((struct xcb_query_extension_reply_t *)0)->first_event),
    offsetof(struct xcb_query_extension_reply_t, first_error),
    sizeof(((struct xcb_query_extension_reply_t *)0)->first_error),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_query_extension_reply_t(0);
}

static void _cffi_check_struct_xcb_render_directformat_t(struct xcb_render_directformat_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->red_shift) << 1);
  (void)((p->red_mask) << 1);
  (void)((p->green_shift) << 1);
  (void)((p->green_mask) << 1);
  (void)((p->blue_shift) << 1);
  (void)((p->blue_mask) << 1);
  (void)((p->alpha_shift) << 1);
  (void)((p->alpha_mask) << 1);
}
static PyObject *
_cffi_layout_struct_xcb_render_directformat_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_render_directformat_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_render_directformat_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_render_directformat_t, red_shift),
    sizeof(((struct xcb_render_directformat_t *)0)->red_shift),
    offsetof(struct xcb_render_directformat_t, red_mask),
    sizeof(((struct xcb_render_directformat_t *)0)->red_mask),
    offsetof(struct xcb_render_directformat_t, green_shift),
    sizeof(((struct xcb_render_directformat_t *)0)->green_shift),
    offsetof(struct xcb_render_directformat_t, green_mask),
    sizeof(((struct xcb_render_directformat_t *)0)->green_mask),
    offsetof(struct xcb_render_directformat_t, blue_shift),
    sizeof(((struct xcb_render_directformat_t *)0)->blue_shift),
    offsetof(struct xcb_render_directformat_t, blue_mask),
    sizeof(((struct xcb_render_directformat_t *)0)->blue_mask),
    offsetof(struct xcb_render_directformat_t, alpha_shift),
    sizeof(((struct xcb_render_directformat_t *)0)->alpha_shift),
    offsetof(struct xcb_render_directformat_t, alpha_mask),
    sizeof(((struct xcb_render_directformat_t *)0)->alpha_mask),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_render_directformat_t(0);
}

static void _cffi_check_struct_xcb_render_pictforminfo_t(struct xcb_render_pictforminfo_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->id) << 1);
  (void)((p->type) << 1);
  (void)((p->depth) << 1);
  { uint8_t(*tmp)[2] = &p->pad0; (void)tmp; }
  { xcb_render_directformat_t *tmp = &p->direct; (void)tmp; }
  (void)((p->colormap) << 1);
}
static PyObject *
_cffi_layout_struct_xcb_render_pictforminfo_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_render_pictforminfo_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_render_pictforminfo_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_render_pictforminfo_t, id),
    sizeof(((struct xcb_render_pictforminfo_t *)0)->id),
    offsetof(struct xcb_render_pictforminfo_t, type),
    sizeof(((struct xcb_render_pictforminfo_t *)0)->type),
    offsetof(struct xcb_render_pictforminfo_t, depth),
    sizeof(((struct xcb_render_pictforminfo_t *)0)->depth),
    offsetof(struct xcb_render_pictforminfo_t, pad0),
    sizeof(((struct xcb_render_pictforminfo_t *)0)->pad0),
    offsetof(struct xcb_render_pictforminfo_t, direct),
    sizeof(((struct xcb_render_pictforminfo_t *)0)->direct),
    offsetof(struct xcb_render_pictforminfo_t, colormap),
    sizeof(((struct xcb_render_pictforminfo_t *)0)->colormap),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_render_pictforminfo_t(0);
}

static void _cffi_check_struct_xcb_screen_t(struct xcb_screen_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->root) << 1);
  (void)((p->default_colormap) << 1);
  (void)((p->white_pixel) << 1);
  (void)((p->black_pixel) << 1);
  (void)((p->current_input_masks) << 1);
  (void)((p->width_in_pixels) << 1);
  (void)((p->height_in_pixels) << 1);
  (void)((p->width_in_millimeters) << 1);
  (void)((p->height_in_millimeters) << 1);
  (void)((p->min_installed_maps) << 1);
  (void)((p->max_installed_maps) << 1);
  (void)((p->root_visual) << 1);
  (void)((p->backing_stores) << 1);
  (void)((p->save_unders) << 1);
  (void)((p->root_depth) << 1);
  (void)((p->allowed_depths_len) << 1);
}
static PyObject *
_cffi_layout_struct_xcb_screen_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_screen_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_screen_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_screen_t, root),
    sizeof(((struct xcb_screen_t *)0)->root),
    offsetof(struct xcb_screen_t, default_colormap),
    sizeof(((struct xcb_screen_t *)0)->default_colormap),
    offsetof(struct xcb_screen_t, white_pixel),
    sizeof(((struct xcb_screen_t *)0)->white_pixel),
    offsetof(struct xcb_screen_t, black_pixel),
    sizeof(((struct xcb_screen_t *)0)->black_pixel),
    offsetof(struct xcb_screen_t, current_input_masks),
    sizeof(((struct xcb_screen_t *)0)->current_input_masks),
    offsetof(struct xcb_screen_t, width_in_pixels),
    sizeof(((struct xcb_screen_t *)0)->width_in_pixels),
    offsetof(struct xcb_screen_t, height_in_pixels),
    sizeof(((struct xcb_screen_t *)0)->height_in_pixels),
    offsetof(struct xcb_screen_t, width_in_millimeters),
    sizeof(((struct xcb_screen_t *)0)->width_in_millimeters),
    offsetof(struct xcb_screen_t, height_in_millimeters),
    sizeof(((struct xcb_screen_t *)0)->height_in_millimeters),
    offsetof(struct xcb_screen_t, min_installed_maps),
    sizeof(((struct xcb_screen_t *)0)->min_installed_maps),
    offsetof(struct xcb_screen_t, max_installed_maps),
    sizeof(((struct xcb_screen_t *)0)->max_installed_maps),
    offsetof(struct xcb_screen_t, root_visual),
    sizeof(((struct xcb_screen_t *)0)->root_visual),
    offsetof(struct xcb_screen_t, backing_stores),
    sizeof(((struct xcb_screen_t *)0)->backing_stores),
    offsetof(struct xcb_screen_t, save_unders),
    sizeof(((struct xcb_screen_t *)0)->save_unders),
    offsetof(struct xcb_screen_t, root_depth),
    sizeof(((struct xcb_screen_t *)0)->root_depth),
    offsetof(struct xcb_screen_t, allowed_depths_len),
    sizeof(((struct xcb_screen_t *)0)->allowed_depths_len),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_screen_t(0);
}

static void _cffi_check_struct_xcb_setup_t(struct xcb_setup_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->status) << 1);
  (void)((p->pad0) << 1);
  (void)((p->protocol_major_version) << 1);
  (void)((p->protocol_minor_version) << 1);
  (void)((p->length) << 1);
  (void)((p->release_number) << 1);
  (void)((p->resource_id_base) << 1);
  (void)((p->resource_id_mask) << 1);
  (void)((p->motion_buffer_size) << 1);
  (void)((p->vendor_len) << 1);
  (void)((p->maximum_request_length) << 1);
  (void)((p->roots_len) << 1);
  (void)((p->pixmap_formats_len) << 1);
  (void)((p->image_byte_order) << 1);
  (void)((p->bitmap_format_bit_order) << 1);
  (void)((p->bitmap_format_scanline_unit) << 1);
  (void)((p->bitmap_format_scanline_pad) << 1);
  (void)((p->min_keycode) << 1);
  (void)((p->max_keycode) << 1);
  { uint8_t(*tmp)[4] = &p->pad1; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_xcb_setup_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_setup_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_setup_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_setup_t, status),
    sizeof(((struct xcb_setup_t *)0)->status),
    offsetof(struct xcb_setup_t, pad0),
    sizeof(((struct xcb_setup_t *)0)->pad0),
    offsetof(struct xcb_setup_t, protocol_major_version),
    sizeof(((struct xcb_setup_t *)0)->protocol_major_version),
    offsetof(struct xcb_setup_t, protocol_minor_version),
    sizeof(((struct xcb_setup_t *)0)->protocol_minor_version),
    offsetof(struct xcb_setup_t, length),
    sizeof(((struct xcb_setup_t *)0)->length),
    offsetof(struct xcb_setup_t, release_number),
    sizeof(((struct xcb_setup_t *)0)->release_number),
    offsetof(struct xcb_setup_t, resource_id_base),
    sizeof(((struct xcb_setup_t *)0)->resource_id_base),
    offsetof(struct xcb_setup_t, resource_id_mask),
    sizeof(((struct xcb_setup_t *)0)->resource_id_mask),
    offsetof(struct xcb_setup_t, motion_buffer_size),
    sizeof(((struct xcb_setup_t *)0)->motion_buffer_size),
    offsetof(struct xcb_setup_t, vendor_len),
    sizeof(((struct xcb_setup_t *)0)->vendor_len),
    offsetof(struct xcb_setup_t, maximum_request_length),
    sizeof(((struct xcb_setup_t *)0)->maximum_request_length),
    offsetof(struct xcb_setup_t, roots_len),
    sizeof(((struct xcb_setup_t *)0)->roots_len),
    offsetof(struct xcb_setup_t, pixmap_formats_len),
    sizeof(((struct xcb_setup_t *)0)->pixmap_formats_len),
    offsetof(struct xcb_setup_t, image_byte_order),
    sizeof(((struct xcb_setup_t *)0)->image_byte_order),
    offsetof(struct xcb_setup_t, bitmap_format_bit_order),
    sizeof(((struct xcb_setup_t *)0)->bitmap_format_bit_order),
    offsetof(struct xcb_setup_t, bitmap_format_scanline_unit),
    sizeof(((struct xcb_setup_t *)0)->bitmap_format_scanline_unit),
    offsetof(struct xcb_setup_t, bitmap_format_scanline_pad),
    sizeof(((struct xcb_setup_t *)0)->bitmap_format_scanline_pad),
    offsetof(struct xcb_setup_t, min_keycode),
    sizeof(((struct xcb_setup_t *)0)->min_keycode),
    offsetof(struct xcb_setup_t, max_keycode),
    sizeof(((struct xcb_setup_t *)0)->max_keycode),
    offsetof(struct xcb_setup_t, pad1),
    sizeof(((struct xcb_setup_t *)0)->pad1),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_setup_t(0);
}

static void _cffi_check_struct_xcb_visualtype_t(struct xcb_visualtype_t *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->visual_id) << 1);
  (void)((p->_class) << 1);
  (void)((p->bits_per_rgb_value) << 1);
  (void)((p->colormap_entries) << 1);
  (void)((p->red_mask) << 1);
  (void)((p->green_mask) << 1);
  (void)((p->blue_mask) << 1);
  { uint8_t(*tmp)[4] = &p->pad0; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_xcb_visualtype_t(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct xcb_visualtype_t y; };
  static Py_ssize_t nums[] = {
    sizeof(struct xcb_visualtype_t),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct xcb_visualtype_t, visual_id),
    sizeof(((struct xcb_visualtype_t *)0)->visual_id),
    offsetof(struct xcb_visualtype_t, _class),
    sizeof(((struct xcb_visualtype_t *)0)->_class),
    offsetof(struct xcb_visualtype_t, bits_per_rgb_value),
    sizeof(((struct xcb_visualtype_t *)0)->bits_per_rgb_value),
    offsetof(struct xcb_visualtype_t, colormap_entries),
    sizeof(((struct xcb_visualtype_t *)0)->colormap_entries),
    offsetof(struct xcb_visualtype_t, red_mask),
    sizeof(((struct xcb_visualtype_t *)0)->red_mask),
    offsetof(struct xcb_visualtype_t, green_mask),
    sizeof(((struct xcb_visualtype_t *)0)->green_mask),
    offsetof(struct xcb_visualtype_t, blue_mask),
    sizeof(((struct xcb_visualtype_t *)0)->blue_mask),
    offsetof(struct xcb_visualtype_t, pad0),
    sizeof(((struct xcb_visualtype_t *)0)->pad0),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_xcb_visualtype_t(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_X_TCP_PORT(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout__xcb_generic_error_t", _cffi_layout__xcb_generic_error_t, METH_NOARGS, NULL},
  {"_cffi_layout__xcb_generic_event_t", _cffi_layout__xcb_generic_event_t, METH_NOARGS, NULL},
  {"_cffi_layout__xcb_generic_reply_t", _cffi_layout__xcb_generic_reply_t, METH_NOARGS, NULL},
  {"_cffi_layout__xcb_protocol_request_t", _cffi_layout__xcb_protocol_request_t, METH_NOARGS, NULL},
  {"_cffi_layout__xcb_void_cookie_t", _cffi_layout__xcb_void_cookie_t, METH_NOARGS, NULL},
  {"free", _cffi_f_free, METH_O, NULL},
  {"xcb_connect", _cffi_f_xcb_connect, METH_VARARGS, NULL},
  {"xcb_connect_to_display_with_auth_info", _cffi_f_xcb_connect_to_display_with_auth_info, METH_VARARGS, NULL},
  {"xcb_connect_to_fd", _cffi_f_xcb_connect_to_fd, METH_VARARGS, NULL},
  {"xcb_connection_has_error", _cffi_f_xcb_connection_has_error, METH_O, NULL},
  {"xcb_disconnect", _cffi_f_xcb_disconnect, METH_O, NULL},
  {"xcb_flush", _cffi_f_xcb_flush, METH_O, NULL},
  {"xcb_generate_id", _cffi_f_xcb_generate_id, METH_O, NULL},
  {"xcb_get_extension_data", _cffi_f_xcb_get_extension_data, METH_VARARGS, NULL},
  {"xcb_get_file_descriptor", _cffi_f_xcb_get_file_descriptor, METH_O, NULL},
  {"xcb_get_maximum_request_length", _cffi_f_xcb_get_maximum_request_length, METH_O, NULL},
  {"xcb_get_setup", _cffi_f_xcb_get_setup, METH_O, NULL},
  {"xcb_parse_display", _cffi_f_xcb_parse_display, METH_VARARGS, NULL},
  {"xcb_poll_for_event", _cffi_f_xcb_poll_for_event, METH_O, NULL},
  {"xcb_poll_for_reply", _cffi_f_xcb_poll_for_reply, METH_VARARGS, NULL},
  {"xcb_prefetch_maximum_request_length", _cffi_f_xcb_prefetch_maximum_request_length, METH_O, NULL},
  {"xcb_request_check", _cffi_f_xcb_request_check, METH_VARARGS, NULL},
  {"xcb_send_request", _cffi_f_xcb_send_request, METH_VARARGS, NULL},
  {"xcb_wait_for_event", _cffi_f_xcb_wait_for_event, METH_O, NULL},
  {"xcb_wait_for_reply", _cffi_f_xcb_wait_for_reply, METH_VARARGS, NULL},
  {"_cffi_layout_struct_iovec", _cffi_layout_struct_iovec, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_auth_info_t", _cffi_layout_struct_xcb_auth_info_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_extension_t", _cffi_layout_struct_xcb_extension_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_query_extension_reply_t", _cffi_layout_struct_xcb_query_extension_reply_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_render_directformat_t", _cffi_layout_struct_xcb_render_directformat_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_render_pictforminfo_t", _cffi_layout_struct_xcb_render_pictforminfo_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_screen_t", _cffi_layout_struct_xcb_screen_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_setup_t", _cffi_layout_struct_xcb_setup_t, METH_NOARGS, NULL},
  {"_cffi_layout_struct_xcb_visualtype_t", _cffi_layout_struct_xcb_visualtype_t, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_xcffib",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__xcffib(void)
{
  PyObject *lib;
  lib = PyModule_Create(&_cffi_module_def);
  if (lib == NULL)
    return NULL;
  if (0 < 0 || _cffi_init() < 0) {
    Py_DECREF(lib);
    return NULL;
  }
  return lib;
}

#else

PyMODINIT_FUNC
init_xcffib(void)
{
  PyObject *lib;
  lib = Py_InitModule("_xcffib", _cffi_methods);
  if (lib == NULL)
    return;
  if (0 < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

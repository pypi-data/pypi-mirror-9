
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



#include <openssl/bn.h>
#include <openssl/ec.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/ecdsa.h>

#define BN_num_bytes(a) ((BN_num_bits(a)+7)/8)


int bn_num_bytes(BIGNUM * a){
    return BN_num_bytes(a);
}

int bn_is_odd(BIGNUM * a){
    return BN_is_odd(a);
}

size_t hmac_ctx_size(void){
    return sizeof(HMAC_CTX);
}


extern void ERR_load_crypto_strings(void);
extern void OPENSSL_config(void*);
extern void ERR_free_strings(void);

void init_ciphers(void){

    /* Load the human readable error strings for libcrypto */
    ERR_load_crypto_strings();

    /* Load all digest and cipher algorithms */
    OpenSSL_add_all_algorithms();

    /* Load config file, and other important initialisation */
    OPENSSL_config(NULL);

}

void cleanup_ciphers(void){

    /* Removes all digests and ciphers */
    EVP_cleanup();

    /* if you omit the next, a small leak may be left when you make use of the BIO (low level API) for e.g. base64 transformations */
    CRYPTO_cleanup_all_ex_data();

    /* Remove error strings */
    ERR_free_strings();

}



static void _cffi_check__EC_builtin_curve(EC_builtin_curve *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->nid) << 1);
  { char const * *tmp = &p->comment; (void)tmp; }
}
static PyObject *
_cffi_layout__EC_builtin_curve(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; EC_builtin_curve y; };
  static Py_ssize_t nums[] = {
    sizeof(EC_builtin_curve),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(EC_builtin_curve, nid),
    sizeof(((EC_builtin_curve *)0)->nid),
    offsetof(EC_builtin_curve, comment),
    sizeof(((EC_builtin_curve *)0)->comment),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__EC_builtin_curve(0);
}

static void _cffi_check__HMAC_CTX(HMAC_CTX *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
}
static PyObject *
_cffi_layout__HMAC_CTX(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; HMAC_CTX y; };
  static Py_ssize_t nums[] = {
    sizeof(HMAC_CTX),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__HMAC_CTX(0);
}

static int _cffi_e__point_conversion_form_t(PyObject *lib)
{
  if ((POINT_CONVERSION_COMPRESSED) <= 0 || (unsigned long)(POINT_CONVERSION_COMPRESSED) != 2UL) {
    char buf[64];
    if ((POINT_CONVERSION_COMPRESSED) <= 0)
        snprintf(buf, 63, "%ld", (long)(POINT_CONVERSION_COMPRESSED));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(POINT_CONVERSION_COMPRESSED));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum point_conversion_form_t: ", "POINT_CONVERSION_COMPRESSED", buf, "2");
    return -1;
  }
  if ((POINT_CONVERSION_UNCOMPRESSED) <= 0 || (unsigned long)(POINT_CONVERSION_UNCOMPRESSED) != 4UL) {
    char buf[64];
    if ((POINT_CONVERSION_UNCOMPRESSED) <= 0)
        snprintf(buf, 63, "%ld", (long)(POINT_CONVERSION_UNCOMPRESSED));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(POINT_CONVERSION_UNCOMPRESSED));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum point_conversion_form_t: ", "POINT_CONVERSION_UNCOMPRESSED", buf, "4");
    return -1;
  }
  if ((POINT_CONVERSION_HYBRID) <= 0 || (unsigned long)(POINT_CONVERSION_HYBRID) != 6UL) {
    char buf[64];
    if ((POINT_CONVERSION_HYBRID) <= 0)
        snprintf(buf, 63, "%ld", (long)(POINT_CONVERSION_HYBRID));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(POINT_CONVERSION_HYBRID));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum point_conversion_form_t: ", "POINT_CONVERSION_HYBRID", buf, "6");
    return -1;
  }
  return ((void)lib,0);
}

static PyObject *
_cffi_f_BN_CTX_free(PyObject *self, PyObject *arg0)
{
  BN_CTX * x0;
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
  { BN_CTX_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_BN_CTX_new(PyObject *self, PyObject *noarg)
{
  BN_CTX * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_CTX_new(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(0));
}

static PyObject *
_cffi_f_BN_add(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:BN_add", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_add(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_bin2bn(PyObject *self, PyObject *args)
{
  unsigned char const * x0;
  int x1;
  BIGNUM * x2;
  Py_ssize_t datasize;
  BIGNUM * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:BN_bin2bn", &arg0, &arg1, &arg2))
    return NULL;

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

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(2), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_bin2bn(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_BN_bn2bin(PyObject *self, PyObject *args)
{
  BIGNUM const * x0;
  unsigned char * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_bn2bin", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_bn2bin(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_bn2dec(PyObject *self, PyObject *arg0)
{
  BIGNUM const * x0;
  Py_ssize_t datasize;
  char * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_bn2dec(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(6));
}

static PyObject *
_cffi_f_BN_bn2hex(PyObject *self, PyObject *arg0)
{
  BIGNUM const * x0;
  Py_ssize_t datasize;
  char * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_bn2hex(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(6));
}

static PyObject *
_cffi_f_BN_clear_free(PyObject *self, PyObject *arg0)
{
  BIGNUM * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { BN_clear_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_BN_cmp(PyObject *self, PyObject *args)
{
  BIGNUM const * x0;
  BIGNUM const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_cmp", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

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
  { result = BN_cmp(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_copy(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  Py_ssize_t datasize;
  BIGNUM * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_copy", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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
  { result = BN_copy(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_BN_dec2bn(PyObject *self, PyObject *args)
{
  BIGNUM * * x0;
  char const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_dec2bn", &arg0, &arg1))
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
  { result = BN_dec2bn(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_div(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM * x1;
  BIGNUM const * x2;
  BIGNUM const * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:BN_div", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

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
  { result = BN_div(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_exp(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:BN_exp", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_exp(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_generate_prime_ex(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  int x1;
  int x2;
  BIGNUM const * x3;
  BIGNUM const * x4;
  BN_GENCB * x5;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:BN_generate_prime_ex", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca((size_t)datasize);
    memset((void *)x5, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(9), arg5) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_generate_prime_ex(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_hex2bn(PyObject *self, PyObject *args)
{
  BIGNUM * * x0;
  char const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_hex2bn", &arg0, &arg1))
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
  { result = BN_hex2bn(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_init(PyObject *self, PyObject *arg0)
{
  BIGNUM * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { BN_init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_BN_is_bit_set(PyObject *self, PyObject *args)
{
  BIGNUM const * x0;
  int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_is_bit_set", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_is_bit_set(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_is_prime_ex(PyObject *self, PyObject *args)
{
  BIGNUM const * x0;
  int x1;
  BN_CTX * x2;
  BN_GENCB * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:BN_is_prime_ex", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(9), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_is_prime_ex(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_mod_add(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM * x1;
  BIGNUM * x2;
  BIGNUM const * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:BN_mod_add", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(2), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

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
  { result = BN_mod_add(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_mod_exp(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  BIGNUM const * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:BN_mod_exp", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

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
  { result = BN_mod_exp(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_mod_inverse(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  BIGNUM * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:BN_mod_inverse", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_mod_inverse(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_BN_mod_mul(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM * x1;
  BIGNUM * x2;
  BIGNUM const * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:BN_mod_mul", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(2), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

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
  { result = BN_mod_mul(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_mod_sub(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM * x1;
  BIGNUM * x2;
  BIGNUM const * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:BN_mod_sub", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(2), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

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
  { result = BN_mod_sub(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_mul(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:BN_mul", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_mul(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_new(PyObject *self, PyObject *noarg)
{
  BIGNUM * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_new(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(2));
}

static PyObject *
_cffi_f_BN_nnmod(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:BN_nnmod", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_nnmod(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_num_bits(PyObject *self, PyObject *arg0)
{
  BIGNUM const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_num_bits(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_rand_range(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_rand_range", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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
  { result = BN_rand_range(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_set_negative(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  int x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_set_negative", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { BN_set_negative(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_BN_set_word(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_set_word", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_set_word(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_sub(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM const * x1;
  BIGNUM const * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:BN_sub", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = BN_sub(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_BN_swap(PyObject *self, PyObject *args)
{
  BIGNUM * x0;
  BIGNUM * x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:BN_swap", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { BN_swap(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_CRYPTO_memcmp(PyObject *self, PyObject *args)
{
  void const * x0;
  void const * x1;
  size_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CRYPTO_memcmp", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(10), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CRYPTO_memcmp(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_ECDSA_SIG_free(PyObject *self, PyObject *arg0)
{
  ECDSA_SIG * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(11), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(11), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { ECDSA_SIG_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_ECDSA_SIG_new(PyObject *self, PyObject *noarg)
{
  ECDSA_SIG * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ECDSA_SIG_new(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(11));
}

static PyObject *
_cffi_f_ECDSA_do_sign(PyObject *self, PyObject *args)
{
  unsigned char const * x0;
  int x1;
  EC_KEY * x2;
  Py_ssize_t datasize;
  ECDSA_SIG * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ECDSA_do_sign", &arg0, &arg1, &arg2))
    return NULL;

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

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(12), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ECDSA_do_sign(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(11));
}

static PyObject *
_cffi_f_ECDSA_do_verify(PyObject *self, PyObject *args)
{
  unsigned char const * x0;
  int x1;
  ECDSA_SIG const * x2;
  EC_KEY * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:ECDSA_do_verify", &arg0, &arg1, &arg2, &arg3))
    return NULL;

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

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(13), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(12), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ECDSA_do_verify(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_ECDSA_size(PyObject *self, PyObject *arg0)
{
  EC_KEY const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(14), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ECDSA_size(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_clear_free(PyObject *self, PyObject *arg0)
{
  EC_GROUP * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(15), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(15), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EC_GROUP_clear_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EC_GROUP_cmp(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_GROUP const * x1;
  BN_CTX * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EC_GROUP_cmp", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(16), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_cmp(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_free(PyObject *self, PyObject *arg0)
{
  EC_GROUP * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(15), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(15), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EC_GROUP_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EC_GROUP_get0_generator(PyObject *self, PyObject *arg0)
{
  EC_GROUP const * x0;
  Py_ssize_t datasize;
  EC_POINT const * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_get0_generator(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(17));
}

static PyObject *
_cffi_f_EC_GROUP_get_cofactor(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  BIGNUM * x1;
  BN_CTX * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EC_GROUP_get_cofactor", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_get_cofactor(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_get_curve_GFp(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  BIGNUM * x1;
  BIGNUM * x2;
  BIGNUM * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EC_GROUP_get_curve_GFp", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(2), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(2), arg3) < 0)
      return NULL;
  }

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
  { result = EC_GROUP_get_curve_GFp(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_get_curve_name(PyObject *self, PyObject *arg0)
{
  EC_GROUP const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_get_curve_name(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_get_order(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  BIGNUM * x1;
  BN_CTX * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EC_GROUP_get_order", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_get_order(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_have_precompute_mult(PyObject *self, PyObject *arg0)
{
  EC_GROUP const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_have_precompute_mult(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_GROUP_new_by_curve_name(PyObject *self, PyObject *arg0)
{
  int x0;
  EC_GROUP * result;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_GROUP_new_by_curve_name(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(15));
}

static PyObject *
_cffi_f_EC_GROUP_precompute_mult(PyObject *self, PyObject *args)
{
  EC_GROUP * x0;
  BN_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_GROUP_precompute_mult", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(15), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(15), arg0) < 0)
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
  { result = EC_GROUP_precompute_mult(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_KEY_free(PyObject *self, PyObject *arg0)
{
  EC_KEY * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(12), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EC_KEY_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EC_KEY_new(PyObject *self, PyObject *noarg)
{
  EC_KEY * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_KEY_new(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(12));
}

static PyObject *
_cffi_f_EC_KEY_set_group(PyObject *self, PyObject *args)
{
  EC_KEY * x0;
  EC_GROUP const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_KEY_set_group", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(12), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(16), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_KEY_set_group(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_KEY_set_private_key(PyObject *self, PyObject *args)
{
  EC_KEY * x0;
  BIGNUM const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_KEY_set_private_key", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(12), arg0) < 0)
      return NULL;
  }

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
  { result = EC_KEY_set_private_key(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_KEY_set_public_key(PyObject *self, PyObject *args)
{
  EC_KEY * x0;
  EC_POINT const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_KEY_set_public_key", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(12), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_KEY_set_public_key(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_add(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  EC_POINT const * x2;
  EC_POINT const * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EC_POINT_add", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(17), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(17), arg3) < 0)
      return NULL;
  }

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
  { result = EC_POINT_add(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_clear_free(PyObject *self, PyObject *arg0)
{
  EC_POINT * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(18), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EC_POINT_clear_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EC_POINT_cmp(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT const * x1;
  EC_POINT const * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:EC_POINT_cmp", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(17), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_cmp(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_copy(PyObject *self, PyObject *args)
{
  EC_POINT * x0;
  EC_POINT const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_POINT_copy", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(18), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_copy(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_dbl(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  EC_POINT const * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:EC_POINT_dbl", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(17), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_dbl(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_dup(PyObject *self, PyObject *args)
{
  EC_POINT const * x0;
  EC_GROUP const * x1;
  Py_ssize_t datasize;
  EC_POINT * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_POINT_dup", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(17), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(16), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_dup(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(18));
}

static PyObject *
_cffi_f_EC_POINT_free(PyObject *self, PyObject *arg0)
{
  EC_POINT * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(18), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EC_POINT_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EC_POINT_get_affine_coordinates_GFp(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT const * x1;
  BIGNUM * x2;
  BIGNUM * x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EC_POINT_get_affine_coordinates_GFp", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(2), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(2), arg3) < 0)
      return NULL;
  }

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
  { result = EC_POINT_get_affine_coordinates_GFp(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_invert(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  BN_CTX * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EC_POINT_invert", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_invert(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_is_at_infinity(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_POINT_is_at_infinity", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_is_at_infinity(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_is_on_curve(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT const * x1;
  BN_CTX * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EC_POINT_is_on_curve", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_is_on_curve(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_make_affine(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  BN_CTX * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EC_POINT_make_affine", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_make_affine(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_mul(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  BIGNUM const * x2;
  EC_POINT const * x3;
  BIGNUM const * x4;
  BN_CTX * x5;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:EC_POINT_mul", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(17), arg3) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca((size_t)datasize);
    memset((void *)x5, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(0), arg5) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_mul(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_new(PyObject *self, PyObject *arg0)
{
  EC_GROUP const * x0;
  Py_ssize_t datasize;
  EC_POINT * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_new(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(18));
}

static PyObject *
_cffi_f_EC_POINT_oct2point(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  unsigned char const * x2;
  size_t x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EC_POINT_oct2point", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(4), arg2) < 0)
      return NULL;
  }

  x3 = _cffi_to_c_int(arg3, size_t);
  if (x3 == (size_t)-1 && PyErr_Occurred())
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
  { result = EC_POINT_oct2point(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_point2oct(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT const * x1;
  point_conversion_form_t x2;
  unsigned char * x3;
  size_t x4;
  BN_CTX * x5;
  Py_ssize_t datasize;
  size_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:EC_POINT_point2oct", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(17), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(17), arg1) < 0)
      return NULL;
  }

  if (_cffi_to_c((char *)&x2, _cffi_type(19), arg2) < 0)
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(5), arg3) < 0)
      return NULL;
  }

  x4 = _cffi_to_c_int(arg4, size_t);
  if (x4 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca((size_t)datasize);
    memset((void *)x5, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(0), arg5) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_point2oct(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, size_t);
}

static PyObject *
_cffi_f_EC_POINT_set_compressed_coordinates_GFp(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  BIGNUM const * x2;
  int x3;
  BN_CTX * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EC_POINT_set_compressed_coordinates_GFp", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

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
  { result = EC_POINT_set_compressed_coordinates_GFp(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINT_set_to_infinity(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_POINT_set_to_infinity", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINT_set_to_infinity(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINTs_make_affine(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  size_t x1;
  EC_POINT * * x2;
  BN_CTX * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:EC_POINTs_make_affine", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(20), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(20), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINTs_make_affine(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_POINTs_mul(PyObject *self, PyObject *args)
{
  EC_GROUP const * x0;
  EC_POINT * x1;
  BIGNUM const * x2;
  size_t x3;
  EC_POINT const * * x4;
  BIGNUM const * * x5;
  BN_CTX * x6;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;

  if (!PyArg_ParseTuple(args, "OOOOOOO:EC_POINTs_mul", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(16), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(16), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(18), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(18), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  x3 = _cffi_to_c_int(arg3, size_t);
  if (x3 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(21), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(21), arg4) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(22), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca((size_t)datasize);
    memset((void *)x5, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(22), arg5) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca((size_t)datasize);
    memset((void *)x6, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(0), arg6) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_POINTs_mul(x0, x1, x2, x3, x4, x5, x6); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EC_get_builtin_curves(PyObject *self, PyObject *args)
{
  EC_builtin_curve * x0;
  size_t x1;
  Py_ssize_t datasize;
  size_t result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EC_get_builtin_curves", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(23), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(23), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EC_get_builtin_curves(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, size_t);
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_cleanup(PyObject *self, PyObject *arg0)
{
  EVP_CIPHER_CTX * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CIPHER_CTX_cleanup(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_ctrl(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  int x1;
  int x2;
  void * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:EVP_CIPHER_CTX_ctrl", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(25), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(25), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CIPHER_CTX_ctrl(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_free(PyObject *self, PyObject *arg0)
{
  EVP_CIPHER_CTX * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EVP_CIPHER_CTX_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_init(PyObject *self, PyObject *arg0)
{
  EVP_CIPHER_CTX * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { EVP_CIPHER_CTX_init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_new(PyObject *self, PyObject *noarg)
{
  EVP_CIPHER_CTX * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CIPHER_CTX_new(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(24));
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_rand_key(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EVP_CIPHER_CTX_rand_key", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CIPHER_CTX_rand_key(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_set_key_length(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EVP_CIPHER_CTX_set_key_length", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CIPHER_CTX_set_key_length(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CIPHER_CTX_set_padding(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:EVP_CIPHER_CTX_set_padding", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CIPHER_CTX_set_padding(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CipherFinal_ex(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  int * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EVP_CipherFinal_ex", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(26), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(26), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CipherFinal_ex(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CipherInit_ex(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  EVP_CIPHER const * x1;
  ENGINE * x2;
  unsigned char const * x3;
  unsigned char const * x4;
  int x5;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:EVP_CipherInit_ex", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(27), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(27), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(28), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(28), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(4), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(4), arg4) < 0)
      return NULL;
  }

  x5 = _cffi_to_c_int(arg5, int);
  if (x5 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CipherInit_ex(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_CipherUpdate(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  int * x2;
  unsigned char const * x3;
  int x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EVP_CipherUpdate", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(26), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(26), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(4), arg3) < 0)
      return NULL;
  }

  x4 = _cffi_to_c_int(arg4, int);
  if (x4 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_CipherUpdate(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_DecryptFinal_ex(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  int * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EVP_DecryptFinal_ex", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(26), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(26), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_DecryptFinal_ex(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_DecryptInit_ex(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  EVP_CIPHER const * x1;
  ENGINE * x2;
  unsigned char * x3;
  unsigned char * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EVP_DecryptInit_ex", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(27), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(27), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(28), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(28), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(5), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(5), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_DecryptInit_ex(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_DecryptUpdate(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  int * x2;
  unsigned char * x3;
  int x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EVP_DecryptUpdate", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(26), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(26), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(5), arg3) < 0)
      return NULL;
  }

  x4 = _cffi_to_c_int(arg4, int);
  if (x4 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_DecryptUpdate(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_EncryptFinal_ex(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  int * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:EVP_EncryptFinal_ex", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(26), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(26), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_EncryptFinal_ex(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_EncryptInit_ex(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  EVP_CIPHER const * x1;
  ENGINE * x2;
  unsigned char * x3;
  unsigned char * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EVP_EncryptInit_ex", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(27), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(27), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(28), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(28), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(5), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(5), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_EncryptInit_ex(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_EncryptUpdate(PyObject *self, PyObject *args)
{
  EVP_CIPHER_CTX * x0;
  unsigned char * x1;
  int * x2;
  unsigned char * x3;
  int x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:EVP_EncryptUpdate", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(24), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(24), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(26), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(26), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(5), arg3) < 0)
      return NULL;
  }

  x4 = _cffi_to_c_int(arg4, int);
  if (x4 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_EncryptUpdate(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_MD_block_size(PyObject *self, PyObject *arg0)
{
  EVP_MD const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(29), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(29), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_MD_block_size(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_MD_size(PyObject *self, PyObject *arg0)
{
  EVP_MD const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(29), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(29), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_MD_size(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_EVP_aes_128_gcm(PyObject *self, PyObject *noarg)
{
  EVP_CIPHER const * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_aes_128_gcm(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(27));
}

static PyObject *
_cffi_f_EVP_aes_192_gcm(PyObject *self, PyObject *noarg)
{
  EVP_CIPHER const * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_aes_192_gcm(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(27));
}

static PyObject *
_cffi_f_EVP_aes_256_gcm(PyObject *self, PyObject *noarg)
{
  EVP_CIPHER const * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_aes_256_gcm(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(27));
}

static PyObject *
_cffi_f_EVP_get_cipherbyname(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  EVP_CIPHER const * result;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_get_cipherbyname(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(27));
}

static PyObject *
_cffi_f_EVP_get_digestbyname(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  EVP_MD const * result;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = EVP_get_digestbyname(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(29));
}

static PyObject *
_cffi_f_HMAC_CTX_cleanup(PyObject *self, PyObject *arg0)
{
  HMAC_CTX * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(30), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(30), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { HMAC_CTX_cleanup(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_HMAC_CTX_init(PyObject *self, PyObject *arg0)
{
  HMAC_CTX * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(30), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(30), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { HMAC_CTX_init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_HMAC_Final(PyObject *self, PyObject *args)
{
  HMAC_CTX * x0;
  unsigned char * x1;
  unsigned int * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:HMAC_Final", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(30), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(30), arg0) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(31), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(31), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = HMAC_Final(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_HMAC_Init_ex(PyObject *self, PyObject *args)
{
  HMAC_CTX * x0;
  void const * x1;
  int x2;
  EVP_MD const * x3;
  ENGINE * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:HMAC_Init_ex", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(30), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(30), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(10), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(29), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(29), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(28), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(28), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = HMAC_Init_ex(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_HMAC_Update(PyObject *self, PyObject *args)
{
  HMAC_CTX * x0;
  unsigned char const * x1;
  int x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:HMAC_Update", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(30), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(30), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(4), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = HMAC_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_OPENSSL_free(PyObject *self, PyObject *arg0)
{
  void * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(25), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(25), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { OPENSSL_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_SSLeay_version(PyObject *self, PyObject *arg0)
{
  int x0;
  char const * result;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = SSLeay_version(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(8));
}

static PyObject *
_cffi_f_bn_is_odd(PyObject *self, PyObject *arg0)
{
  BIGNUM * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = bn_is_odd(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_bn_num_bytes(PyObject *self, PyObject *arg0)
{
  BIGNUM * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = bn_num_bytes(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_cleanup_ciphers(PyObject *self, PyObject *noarg)
{

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { cleanup_ciphers(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_hmac_ctx_size(PyObject *self, PyObject *noarg)
{
  size_t result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = hmac_ctx_size(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_from_c_int(result, size_t);
}

static PyObject *
_cffi_f_init_ciphers(PyObject *self, PyObject *noarg)
{

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { init_ciphers(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static int _cffi_const_EVP_CTRL_AEAD_SET_MAC_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_AEAD_SET_MAC_KEY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_AEAD_SET_MAC_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_e__point_conversion_form_t(lib);
}

static int _cffi_const_EVP_CTRL_AEAD_TLS1_AAD(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_AEAD_TLS1_AAD);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_AEAD_TLS1_AAD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_AEAD_SET_MAC_KEY(lib);
}

static int _cffi_const_EVP_CTRL_CCM_GET_TAG(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_CCM_GET_TAG);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_CCM_GET_TAG", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_AEAD_TLS1_AAD(lib);
}

static int _cffi_const_EVP_CTRL_CCM_SET_IVLEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_CCM_SET_IVLEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_CCM_SET_IVLEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_CCM_GET_TAG(lib);
}

static int _cffi_const_EVP_CTRL_CCM_SET_L(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_CCM_SET_L);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_CCM_SET_L", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_CCM_SET_IVLEN(lib);
}

static int _cffi_const_EVP_CTRL_CCM_SET_MSGLEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_CCM_SET_MSGLEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_CCM_SET_MSGLEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_CCM_SET_L(lib);
}

static int _cffi_const_EVP_CTRL_CCM_SET_TAG(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_CCM_SET_TAG);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_CCM_SET_TAG", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_CCM_SET_MSGLEN(lib);
}

static int _cffi_const_EVP_CTRL_COPY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_COPY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_COPY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_CCM_SET_TAG(lib);
}

static int _cffi_const_EVP_CTRL_GCM_GET_TAG(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GCM_GET_TAG);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GCM_GET_TAG", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_COPY(lib);
}

static int _cffi_const_EVP_CTRL_GCM_IV_GEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GCM_IV_GEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GCM_IV_GEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GCM_GET_TAG(lib);
}

static int _cffi_const_EVP_CTRL_GCM_SET_IVLEN(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GCM_SET_IVLEN);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GCM_SET_IVLEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GCM_IV_GEN(lib);
}

static int _cffi_const_EVP_CTRL_GCM_SET_IV_FIXED(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GCM_SET_IV_FIXED);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GCM_SET_IV_FIXED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GCM_SET_IVLEN(lib);
}

static int _cffi_const_EVP_CTRL_GCM_SET_IV_INV(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GCM_SET_IV_INV);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GCM_SET_IV_INV", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GCM_SET_IV_FIXED(lib);
}

static int _cffi_const_EVP_CTRL_GCM_SET_TAG(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GCM_SET_TAG);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GCM_SET_TAG", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GCM_SET_IV_INV(lib);
}

static int _cffi_const_EVP_CTRL_GET_RC2_KEY_BITS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GET_RC2_KEY_BITS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GET_RC2_KEY_BITS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GCM_SET_TAG(lib);
}

static int _cffi_const_EVP_CTRL_GET_RC5_ROUNDS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_GET_RC5_ROUNDS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_GET_RC5_ROUNDS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GET_RC2_KEY_BITS(lib);
}

static int _cffi_const_EVP_CTRL_INIT(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_INIT);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_INIT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_GET_RC5_ROUNDS(lib);
}

static int _cffi_const_EVP_CTRL_PBE_PRF_NID(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_PBE_PRF_NID);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_PBE_PRF_NID", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_INIT(lib);
}

static int _cffi_const_EVP_CTRL_RAND_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_RAND_KEY);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_RAND_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_PBE_PRF_NID(lib);
}

static int _cffi_const_EVP_CTRL_SET_KEY_LENGTH(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_SET_KEY_LENGTH);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_SET_KEY_LENGTH", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_RAND_KEY(lib);
}

static int _cffi_const_EVP_CTRL_SET_RC2_KEY_BITS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_SET_RC2_KEY_BITS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_SET_RC2_KEY_BITS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_SET_KEY_LENGTH(lib);
}

static int _cffi_const_EVP_CTRL_SET_RC5_ROUNDS(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(EVP_CTRL_SET_RC5_ROUNDS);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "EVP_CTRL_SET_RC5_ROUNDS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_SET_RC2_KEY_BITS(lib);
}

static int _cffi_const_SSLEAY_VERSION(PyObject *lib)
{
  PyObject *o;
  int res;
  o = _cffi_from_c_int_const(SSLEAY_VERSION);
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "SSLEAY_VERSION", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_EVP_CTRL_SET_RC5_ROUNDS(lib);
}

static void _cffi_check_struct_ECDSA_SIG_st(struct ECDSA_SIG_st *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  { BIGNUM * *tmp = &p->r; (void)tmp; }
  { BIGNUM * *tmp = &p->s; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_ECDSA_SIG_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct ECDSA_SIG_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct ECDSA_SIG_st),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct ECDSA_SIG_st, r),
    sizeof(((struct ECDSA_SIG_st *)0)->r),
    offsetof(struct ECDSA_SIG_st, s),
    sizeof(((struct ECDSA_SIG_st *)0)->s),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_ECDSA_SIG_st(0);
}

static void _cffi_check_struct_evp_cipher_ctx_st(struct evp_cipher_ctx_st *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  { EVP_CIPHER const * *tmp = &p->cipher; (void)tmp; }
  (void)((p->encrypt) << 1);
  (void)((p->buf_len) << 1);
  (void)((p->num) << 1);
  (void)((p->key_len) << 1);
  (void)((p->flags) << 1);
  (void)((p->final_used) << 1);
  (void)((p->block_mask) << 1);
}
static PyObject *
_cffi_layout_struct_evp_cipher_ctx_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct evp_cipher_ctx_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct evp_cipher_ctx_st),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct evp_cipher_ctx_st, cipher),
    sizeof(((struct evp_cipher_ctx_st *)0)->cipher),
    offsetof(struct evp_cipher_ctx_st, encrypt),
    sizeof(((struct evp_cipher_ctx_st *)0)->encrypt),
    offsetof(struct evp_cipher_ctx_st, buf_len),
    sizeof(((struct evp_cipher_ctx_st *)0)->buf_len),
    offsetof(struct evp_cipher_ctx_st, num),
    sizeof(((struct evp_cipher_ctx_st *)0)->num),
    offsetof(struct evp_cipher_ctx_st, key_len),
    sizeof(((struct evp_cipher_ctx_st *)0)->key_len),
    offsetof(struct evp_cipher_ctx_st, flags),
    sizeof(((struct evp_cipher_ctx_st *)0)->flags),
    offsetof(struct evp_cipher_ctx_st, final_used),
    sizeof(((struct evp_cipher_ctx_st *)0)->final_used),
    offsetof(struct evp_cipher_ctx_st, block_mask),
    sizeof(((struct evp_cipher_ctx_st *)0)->block_mask),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_evp_cipher_ctx_st(0);
}

static void _cffi_check_struct_evp_cipher_st(struct evp_cipher_st *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->nid) << 1);
  (void)((p->block_size) << 1);
  (void)((p->key_len) << 1);
  (void)((p->iv_len) << 1);
  (void)((p->flags) << 1);
}
static PyObject *
_cffi_layout_struct_evp_cipher_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct evp_cipher_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct evp_cipher_st),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct evp_cipher_st, nid),
    sizeof(((struct evp_cipher_st *)0)->nid),
    offsetof(struct evp_cipher_st, block_size),
    sizeof(((struct evp_cipher_st *)0)->block_size),
    offsetof(struct evp_cipher_st, key_len),
    sizeof(((struct evp_cipher_st *)0)->key_len),
    offsetof(struct evp_cipher_st, iv_len),
    sizeof(((struct evp_cipher_st *)0)->iv_len),
    offsetof(struct evp_cipher_st, flags),
    sizeof(((struct evp_cipher_st *)0)->flags),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_evp_cipher_st(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_SSLEAY_VERSION(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout__EC_builtin_curve", _cffi_layout__EC_builtin_curve, METH_NOARGS, NULL},
  {"_cffi_layout__HMAC_CTX", _cffi_layout__HMAC_CTX, METH_NOARGS, NULL},
  {"BN_CTX_free", _cffi_f_BN_CTX_free, METH_O, NULL},
  {"BN_CTX_new", _cffi_f_BN_CTX_new, METH_NOARGS, NULL},
  {"BN_add", _cffi_f_BN_add, METH_VARARGS, NULL},
  {"BN_bin2bn", _cffi_f_BN_bin2bn, METH_VARARGS, NULL},
  {"BN_bn2bin", _cffi_f_BN_bn2bin, METH_VARARGS, NULL},
  {"BN_bn2dec", _cffi_f_BN_bn2dec, METH_O, NULL},
  {"BN_bn2hex", _cffi_f_BN_bn2hex, METH_O, NULL},
  {"BN_clear_free", _cffi_f_BN_clear_free, METH_O, NULL},
  {"BN_cmp", _cffi_f_BN_cmp, METH_VARARGS, NULL},
  {"BN_copy", _cffi_f_BN_copy, METH_VARARGS, NULL},
  {"BN_dec2bn", _cffi_f_BN_dec2bn, METH_VARARGS, NULL},
  {"BN_div", _cffi_f_BN_div, METH_VARARGS, NULL},
  {"BN_exp", _cffi_f_BN_exp, METH_VARARGS, NULL},
  {"BN_generate_prime_ex", _cffi_f_BN_generate_prime_ex, METH_VARARGS, NULL},
  {"BN_hex2bn", _cffi_f_BN_hex2bn, METH_VARARGS, NULL},
  {"BN_init", _cffi_f_BN_init, METH_O, NULL},
  {"BN_is_bit_set", _cffi_f_BN_is_bit_set, METH_VARARGS, NULL},
  {"BN_is_prime_ex", _cffi_f_BN_is_prime_ex, METH_VARARGS, NULL},
  {"BN_mod_add", _cffi_f_BN_mod_add, METH_VARARGS, NULL},
  {"BN_mod_exp", _cffi_f_BN_mod_exp, METH_VARARGS, NULL},
  {"BN_mod_inverse", _cffi_f_BN_mod_inverse, METH_VARARGS, NULL},
  {"BN_mod_mul", _cffi_f_BN_mod_mul, METH_VARARGS, NULL},
  {"BN_mod_sub", _cffi_f_BN_mod_sub, METH_VARARGS, NULL},
  {"BN_mul", _cffi_f_BN_mul, METH_VARARGS, NULL},
  {"BN_new", _cffi_f_BN_new, METH_NOARGS, NULL},
  {"BN_nnmod", _cffi_f_BN_nnmod, METH_VARARGS, NULL},
  {"BN_num_bits", _cffi_f_BN_num_bits, METH_O, NULL},
  {"BN_rand_range", _cffi_f_BN_rand_range, METH_VARARGS, NULL},
  {"BN_set_negative", _cffi_f_BN_set_negative, METH_VARARGS, NULL},
  {"BN_set_word", _cffi_f_BN_set_word, METH_VARARGS, NULL},
  {"BN_sub", _cffi_f_BN_sub, METH_VARARGS, NULL},
  {"BN_swap", _cffi_f_BN_swap, METH_VARARGS, NULL},
  {"CRYPTO_memcmp", _cffi_f_CRYPTO_memcmp, METH_VARARGS, NULL},
  {"ECDSA_SIG_free", _cffi_f_ECDSA_SIG_free, METH_O, NULL},
  {"ECDSA_SIG_new", _cffi_f_ECDSA_SIG_new, METH_NOARGS, NULL},
  {"ECDSA_do_sign", _cffi_f_ECDSA_do_sign, METH_VARARGS, NULL},
  {"ECDSA_do_verify", _cffi_f_ECDSA_do_verify, METH_VARARGS, NULL},
  {"ECDSA_size", _cffi_f_ECDSA_size, METH_O, NULL},
  {"EC_GROUP_clear_free", _cffi_f_EC_GROUP_clear_free, METH_O, NULL},
  {"EC_GROUP_cmp", _cffi_f_EC_GROUP_cmp, METH_VARARGS, NULL},
  {"EC_GROUP_free", _cffi_f_EC_GROUP_free, METH_O, NULL},
  {"EC_GROUP_get0_generator", _cffi_f_EC_GROUP_get0_generator, METH_O, NULL},
  {"EC_GROUP_get_cofactor", _cffi_f_EC_GROUP_get_cofactor, METH_VARARGS, NULL},
  {"EC_GROUP_get_curve_GFp", _cffi_f_EC_GROUP_get_curve_GFp, METH_VARARGS, NULL},
  {"EC_GROUP_get_curve_name", _cffi_f_EC_GROUP_get_curve_name, METH_O, NULL},
  {"EC_GROUP_get_order", _cffi_f_EC_GROUP_get_order, METH_VARARGS, NULL},
  {"EC_GROUP_have_precompute_mult", _cffi_f_EC_GROUP_have_precompute_mult, METH_O, NULL},
  {"EC_GROUP_new_by_curve_name", _cffi_f_EC_GROUP_new_by_curve_name, METH_O, NULL},
  {"EC_GROUP_precompute_mult", _cffi_f_EC_GROUP_precompute_mult, METH_VARARGS, NULL},
  {"EC_KEY_free", _cffi_f_EC_KEY_free, METH_O, NULL},
  {"EC_KEY_new", _cffi_f_EC_KEY_new, METH_NOARGS, NULL},
  {"EC_KEY_set_group", _cffi_f_EC_KEY_set_group, METH_VARARGS, NULL},
  {"EC_KEY_set_private_key", _cffi_f_EC_KEY_set_private_key, METH_VARARGS, NULL},
  {"EC_KEY_set_public_key", _cffi_f_EC_KEY_set_public_key, METH_VARARGS, NULL},
  {"EC_POINT_add", _cffi_f_EC_POINT_add, METH_VARARGS, NULL},
  {"EC_POINT_clear_free", _cffi_f_EC_POINT_clear_free, METH_O, NULL},
  {"EC_POINT_cmp", _cffi_f_EC_POINT_cmp, METH_VARARGS, NULL},
  {"EC_POINT_copy", _cffi_f_EC_POINT_copy, METH_VARARGS, NULL},
  {"EC_POINT_dbl", _cffi_f_EC_POINT_dbl, METH_VARARGS, NULL},
  {"EC_POINT_dup", _cffi_f_EC_POINT_dup, METH_VARARGS, NULL},
  {"EC_POINT_free", _cffi_f_EC_POINT_free, METH_O, NULL},
  {"EC_POINT_get_affine_coordinates_GFp", _cffi_f_EC_POINT_get_affine_coordinates_GFp, METH_VARARGS, NULL},
  {"EC_POINT_invert", _cffi_f_EC_POINT_invert, METH_VARARGS, NULL},
  {"EC_POINT_is_at_infinity", _cffi_f_EC_POINT_is_at_infinity, METH_VARARGS, NULL},
  {"EC_POINT_is_on_curve", _cffi_f_EC_POINT_is_on_curve, METH_VARARGS, NULL},
  {"EC_POINT_make_affine", _cffi_f_EC_POINT_make_affine, METH_VARARGS, NULL},
  {"EC_POINT_mul", _cffi_f_EC_POINT_mul, METH_VARARGS, NULL},
  {"EC_POINT_new", _cffi_f_EC_POINT_new, METH_O, NULL},
  {"EC_POINT_oct2point", _cffi_f_EC_POINT_oct2point, METH_VARARGS, NULL},
  {"EC_POINT_point2oct", _cffi_f_EC_POINT_point2oct, METH_VARARGS, NULL},
  {"EC_POINT_set_compressed_coordinates_GFp", _cffi_f_EC_POINT_set_compressed_coordinates_GFp, METH_VARARGS, NULL},
  {"EC_POINT_set_to_infinity", _cffi_f_EC_POINT_set_to_infinity, METH_VARARGS, NULL},
  {"EC_POINTs_make_affine", _cffi_f_EC_POINTs_make_affine, METH_VARARGS, NULL},
  {"EC_POINTs_mul", _cffi_f_EC_POINTs_mul, METH_VARARGS, NULL},
  {"EC_get_builtin_curves", _cffi_f_EC_get_builtin_curves, METH_VARARGS, NULL},
  {"EVP_CIPHER_CTX_cleanup", _cffi_f_EVP_CIPHER_CTX_cleanup, METH_O, NULL},
  {"EVP_CIPHER_CTX_ctrl", _cffi_f_EVP_CIPHER_CTX_ctrl, METH_VARARGS, NULL},
  {"EVP_CIPHER_CTX_free", _cffi_f_EVP_CIPHER_CTX_free, METH_O, NULL},
  {"EVP_CIPHER_CTX_init", _cffi_f_EVP_CIPHER_CTX_init, METH_O, NULL},
  {"EVP_CIPHER_CTX_new", _cffi_f_EVP_CIPHER_CTX_new, METH_NOARGS, NULL},
  {"EVP_CIPHER_CTX_rand_key", _cffi_f_EVP_CIPHER_CTX_rand_key, METH_VARARGS, NULL},
  {"EVP_CIPHER_CTX_set_key_length", _cffi_f_EVP_CIPHER_CTX_set_key_length, METH_VARARGS, NULL},
  {"EVP_CIPHER_CTX_set_padding", _cffi_f_EVP_CIPHER_CTX_set_padding, METH_VARARGS, NULL},
  {"EVP_CipherFinal_ex", _cffi_f_EVP_CipherFinal_ex, METH_VARARGS, NULL},
  {"EVP_CipherInit_ex", _cffi_f_EVP_CipherInit_ex, METH_VARARGS, NULL},
  {"EVP_CipherUpdate", _cffi_f_EVP_CipherUpdate, METH_VARARGS, NULL},
  {"EVP_DecryptFinal_ex", _cffi_f_EVP_DecryptFinal_ex, METH_VARARGS, NULL},
  {"EVP_DecryptInit_ex", _cffi_f_EVP_DecryptInit_ex, METH_VARARGS, NULL},
  {"EVP_DecryptUpdate", _cffi_f_EVP_DecryptUpdate, METH_VARARGS, NULL},
  {"EVP_EncryptFinal_ex", _cffi_f_EVP_EncryptFinal_ex, METH_VARARGS, NULL},
  {"EVP_EncryptInit_ex", _cffi_f_EVP_EncryptInit_ex, METH_VARARGS, NULL},
  {"EVP_EncryptUpdate", _cffi_f_EVP_EncryptUpdate, METH_VARARGS, NULL},
  {"EVP_MD_block_size", _cffi_f_EVP_MD_block_size, METH_O, NULL},
  {"EVP_MD_size", _cffi_f_EVP_MD_size, METH_O, NULL},
  {"EVP_aes_128_gcm", _cffi_f_EVP_aes_128_gcm, METH_NOARGS, NULL},
  {"EVP_aes_192_gcm", _cffi_f_EVP_aes_192_gcm, METH_NOARGS, NULL},
  {"EVP_aes_256_gcm", _cffi_f_EVP_aes_256_gcm, METH_NOARGS, NULL},
  {"EVP_get_cipherbyname", _cffi_f_EVP_get_cipherbyname, METH_O, NULL},
  {"EVP_get_digestbyname", _cffi_f_EVP_get_digestbyname, METH_O, NULL},
  {"HMAC_CTX_cleanup", _cffi_f_HMAC_CTX_cleanup, METH_O, NULL},
  {"HMAC_CTX_init", _cffi_f_HMAC_CTX_init, METH_O, NULL},
  {"HMAC_Final", _cffi_f_HMAC_Final, METH_VARARGS, NULL},
  {"HMAC_Init_ex", _cffi_f_HMAC_Init_ex, METH_VARARGS, NULL},
  {"HMAC_Update", _cffi_f_HMAC_Update, METH_VARARGS, NULL},
  {"OPENSSL_free", _cffi_f_OPENSSL_free, METH_O, NULL},
  {"SSLeay_version", _cffi_f_SSLeay_version, METH_O, NULL},
  {"bn_is_odd", _cffi_f_bn_is_odd, METH_O, NULL},
  {"bn_num_bytes", _cffi_f_bn_num_bytes, METH_O, NULL},
  {"cleanup_ciphers", _cffi_f_cleanup_ciphers, METH_NOARGS, NULL},
  {"hmac_ctx_size", _cffi_f_hmac_ctx_size, METH_NOARGS, NULL},
  {"init_ciphers", _cffi_f_init_ciphers, METH_NOARGS, NULL},
  {"_cffi_layout_struct_ECDSA_SIG_st", _cffi_layout_struct_ECDSA_SIG_st, METH_NOARGS, NULL},
  {"_cffi_layout_struct_evp_cipher_ctx_st", _cffi_layout_struct_evp_cipher_ctx_st, METH_NOARGS, NULL},
  {"_cffi_layout_struct_evp_cipher_st", _cffi_layout_struct_evp_cipher_st, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__xe4596063x2ad35c4b",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__xe4596063x2ad35c4b(void)
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
init_cffi__xe4596063x2ad35c4b(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__xe4596063x2ad35c4b", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

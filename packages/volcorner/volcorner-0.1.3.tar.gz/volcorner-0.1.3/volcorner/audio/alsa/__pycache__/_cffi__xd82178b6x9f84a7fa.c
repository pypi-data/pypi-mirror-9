
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


#include <alsa/asoundlib.h>

static int _cffi_e_enum__snd_mixer_selem_channel_id(PyObject *lib)
{
  if ((SND_MIXER_SCHN_UNKNOWN) > 0 || (long)(SND_MIXER_SCHN_UNKNOWN) != -1L) {
    char buf[64];
    if ((SND_MIXER_SCHN_UNKNOWN) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_UNKNOWN));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_UNKNOWN));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_UNKNOWN", buf, "-1");
    return -1;
  }
  if ((SND_MIXER_SCHN_FRONT_LEFT) > 0 || (long)(SND_MIXER_SCHN_FRONT_LEFT) != 0L) {
    char buf[64];
    if ((SND_MIXER_SCHN_FRONT_LEFT) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_FRONT_LEFT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_FRONT_LEFT));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_FRONT_LEFT", buf, "0");
    return -1;
  }
  if ((SND_MIXER_SCHN_FRONT_RIGHT) <= 0 || (unsigned long)(SND_MIXER_SCHN_FRONT_RIGHT) != 1UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_FRONT_RIGHT) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_FRONT_RIGHT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_FRONT_RIGHT));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_FRONT_RIGHT", buf, "1");
    return -1;
  }
  if ((SND_MIXER_SCHN_REAR_LEFT) <= 0 || (unsigned long)(SND_MIXER_SCHN_REAR_LEFT) != 2UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_REAR_LEFT) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_REAR_LEFT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_REAR_LEFT));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_REAR_LEFT", buf, "2");
    return -1;
  }
  if ((SND_MIXER_SCHN_REAR_RIGHT) <= 0 || (unsigned long)(SND_MIXER_SCHN_REAR_RIGHT) != 3UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_REAR_RIGHT) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_REAR_RIGHT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_REAR_RIGHT));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_REAR_RIGHT", buf, "3");
    return -1;
  }
  if ((SND_MIXER_SCHN_FRONT_CENTER) <= 0 || (unsigned long)(SND_MIXER_SCHN_FRONT_CENTER) != 4UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_FRONT_CENTER) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_FRONT_CENTER));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_FRONT_CENTER));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_FRONT_CENTER", buf, "4");
    return -1;
  }
  if ((SND_MIXER_SCHN_WOOFER) <= 0 || (unsigned long)(SND_MIXER_SCHN_WOOFER) != 5UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_WOOFER) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_WOOFER));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_WOOFER));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_WOOFER", buf, "5");
    return -1;
  }
  if ((SND_MIXER_SCHN_SIDE_LEFT) <= 0 || (unsigned long)(SND_MIXER_SCHN_SIDE_LEFT) != 6UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_SIDE_LEFT) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_SIDE_LEFT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_SIDE_LEFT));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_SIDE_LEFT", buf, "6");
    return -1;
  }
  if ((SND_MIXER_SCHN_SIDE_RIGHT) <= 0 || (unsigned long)(SND_MIXER_SCHN_SIDE_RIGHT) != 7UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_SIDE_RIGHT) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_SIDE_RIGHT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_SIDE_RIGHT));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_SIDE_RIGHT", buf, "7");
    return -1;
  }
  if ((SND_MIXER_SCHN_REAR_CENTER) <= 0 || (unsigned long)(SND_MIXER_SCHN_REAR_CENTER) != 8UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_REAR_CENTER) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_REAR_CENTER));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_REAR_CENTER));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_REAR_CENTER", buf, "8");
    return -1;
  }
  if ((SND_MIXER_SCHN_LAST) <= 0 || (unsigned long)(SND_MIXER_SCHN_LAST) != 31UL) {
    char buf[64];
    if ((SND_MIXER_SCHN_LAST) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_LAST));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_LAST));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_LAST", buf, "31");
    return -1;
  }
  if ((SND_MIXER_SCHN_MONO) > 0 || (long)(SND_MIXER_SCHN_MONO) != 0L) {
    char buf[64];
    if ((SND_MIXER_SCHN_MONO) <= 0)
        snprintf(buf, 63, "%ld", (long)(SND_MIXER_SCHN_MONO));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(SND_MIXER_SCHN_MONO));
    PyErr_Format(_cffi_VerificationError,
                 "%s%s has the real value %s, not %s",
                 "enum _snd_mixer_selem_channel_id: ", "SND_MIXER_SCHN_MONO", buf, "0");
    return -1;
  }
  return ((void)lib,0);
}

static PyObject *
_cffi_f_snd_mixer_attach(PyObject *self, PyObject *args)
{
  snd_mixer_t * x0;
  char const * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:snd_mixer_attach", &arg0, &arg1))
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
  { result = snd_mixer_attach(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_find_selem(PyObject *self, PyObject *args)
{
  snd_mixer_t * x0;
  snd_mixer_selem_id_t const * x1;
  Py_ssize_t datasize;
  snd_mixer_elem_t * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:snd_mixer_find_selem", &arg0, &arg1))
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
  { result = snd_mixer_find_selem(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_snd_mixer_handle_events(PyObject *self, PyObject *arg0)
{
  snd_mixer_t * x0;
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
  { result = snd_mixer_handle_events(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_load(PyObject *self, PyObject *arg0)
{
  snd_mixer_t * x0;
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
  { result = snd_mixer_load(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_open(PyObject *self, PyObject *args)
{
  snd_mixer_t * * x0;
  int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:snd_mixer_open", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_open(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_poll_descriptors(PyObject *self, PyObject *args)
{
  snd_mixer_t * x0;
  struct pollfd * x1;
  unsigned int x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_poll_descriptors", &arg0, &arg1, &arg2))
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
      _cffi_type(5), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(5), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, unsigned int);
  if (x2 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_poll_descriptors(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_poll_descriptors_count(PyObject *self, PyObject *arg0)
{
  snd_mixer_t * x0;
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
  { result = snd_mixer_poll_descriptors_count(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_poll_descriptors_revents(PyObject *self, PyObject *args)
{
  snd_mixer_t * x0;
  struct pollfd * x1;
  unsigned int x2;
  unsigned short * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:snd_mixer_poll_descriptors_revents", &arg0, &arg1, &arg2, &arg3))
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
      _cffi_type(5), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(5), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_int(arg2, unsigned int);
  if (x2 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca((size_t)datasize);
    memset((void *)x3, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(6), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_poll_descriptors_revents(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_get_playback_dB(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  snd_mixer_selem_channel_id_t x1;
  long * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_get_playback_dB", &arg0, &arg1, &arg2))
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

  if (_cffi_to_c((char *)&x1, _cffi_type(7), arg1) < 0)
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(8), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_get_playback_dB(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_get_playback_dB_range(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  long * x1;
  long * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_get_playback_dB_range", &arg0, &arg1, &arg2))
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
      _cffi_type(8), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(8), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(8), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_get_playback_dB_range(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_get_playback_volume(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  snd_mixer_selem_channel_id_t x1;
  long * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_get_playback_volume", &arg0, &arg1, &arg2))
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

  if (_cffi_to_c((char *)&x1, _cffi_type(7), arg1) < 0)
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(8), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_get_playback_volume(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_get_playback_volume_range(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  long * x1;
  long * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_get_playback_volume_range", &arg0, &arg1, &arg2))
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
      _cffi_type(8), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(8), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(8), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_get_playback_volume_range(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_id_free(PyObject *self, PyObject *arg0)
{
  snd_mixer_selem_id_t * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(9), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { snd_mixer_selem_id_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_snd_mixer_selem_id_malloc(PyObject *self, PyObject *arg0)
{
  snd_mixer_selem_id_t * * x0;
  Py_ssize_t datasize;
  int result;

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
  { result = snd_mixer_selem_id_malloc(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_id_set_name(PyObject *self, PyObject *args)
{
  snd_mixer_selem_id_t * x0;
  char const * x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:snd_mixer_selem_id_set_name", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca((size_t)datasize);
    memset((void *)x0, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(9), arg0) < 0)
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
  { snd_mixer_selem_id_set_name(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_snd_mixer_selem_register(PyObject *self, PyObject *args)
{
  snd_mixer_t * x0;
  struct snd_mixer_selem_regopt * x1;
  snd_mixer_class_t * * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_register", &arg0, &arg1, &arg2))
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
      _cffi_type(12), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca((size_t)datasize);
    memset((void *)x1, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(12), arg1) < 0)
      return NULL;
  }

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_register(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_set_playback_dB(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  snd_mixer_selem_channel_id_t x1;
  long x2;
  int x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:snd_mixer_selem_set_playback_dB", &arg0, &arg1, &arg2, &arg3))
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

  if (_cffi_to_c((char *)&x1, _cffi_type(7), arg1) < 0)
    return NULL;

  x2 = _cffi_to_c_int(arg2, long);
  if (x2 == (long)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_int(arg3, int);
  if (x3 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_set_playback_dB(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_set_playback_dB_all(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  long x1;
  int x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_set_playback_dB_all", &arg0, &arg1, &arg2))
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

  x1 = _cffi_to_c_int(arg1, long);
  if (x1 == (long)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_set_playback_dB_all(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_set_playback_volume(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  snd_mixer_selem_channel_id_t x1;
  long x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:snd_mixer_selem_set_playback_volume", &arg0, &arg1, &arg2))
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

  if (_cffi_to_c((char *)&x1, _cffi_type(7), arg1) < 0)
    return NULL;

  x2 = _cffi_to_c_int(arg2, long);
  if (x2 == (long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_set_playback_volume(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_snd_mixer_selem_set_playback_volume_all(PyObject *self, PyObject *args)
{
  snd_mixer_elem_t * x0;
  long x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:snd_mixer_selem_set_playback_volume_all", &arg0, &arg1))
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

  x1 = _cffi_to_c_int(arg1, long);
  if (x1 == (long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = snd_mixer_selem_set_playback_volume_all(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static void _cffi_check_struct_pollfd(struct pollfd *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->fd) << 1);
  (void)((p->events) << 1);
  (void)((p->revents) << 1);
}
static PyObject *
_cffi_layout_struct_pollfd(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct pollfd y; };
  static Py_ssize_t nums[] = {
    sizeof(struct pollfd),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct pollfd, fd),
    sizeof(((struct pollfd *)0)->fd),
    offsetof(struct pollfd, events),
    sizeof(((struct pollfd *)0)->events),
    offsetof(struct pollfd, revents),
    sizeof(((struct pollfd *)0)->revents),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_pollfd(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_e_enum__snd_mixer_selem_channel_id(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"snd_mixer_attach", _cffi_f_snd_mixer_attach, METH_VARARGS, NULL},
  {"snd_mixer_find_selem", _cffi_f_snd_mixer_find_selem, METH_VARARGS, NULL},
  {"snd_mixer_handle_events", _cffi_f_snd_mixer_handle_events, METH_O, NULL},
  {"snd_mixer_load", _cffi_f_snd_mixer_load, METH_O, NULL},
  {"snd_mixer_open", _cffi_f_snd_mixer_open, METH_VARARGS, NULL},
  {"snd_mixer_poll_descriptors", _cffi_f_snd_mixer_poll_descriptors, METH_VARARGS, NULL},
  {"snd_mixer_poll_descriptors_count", _cffi_f_snd_mixer_poll_descriptors_count, METH_O, NULL},
  {"snd_mixer_poll_descriptors_revents", _cffi_f_snd_mixer_poll_descriptors_revents, METH_VARARGS, NULL},
  {"snd_mixer_selem_get_playback_dB", _cffi_f_snd_mixer_selem_get_playback_dB, METH_VARARGS, NULL},
  {"snd_mixer_selem_get_playback_dB_range", _cffi_f_snd_mixer_selem_get_playback_dB_range, METH_VARARGS, NULL},
  {"snd_mixer_selem_get_playback_volume", _cffi_f_snd_mixer_selem_get_playback_volume, METH_VARARGS, NULL},
  {"snd_mixer_selem_get_playback_volume_range", _cffi_f_snd_mixer_selem_get_playback_volume_range, METH_VARARGS, NULL},
  {"snd_mixer_selem_id_free", _cffi_f_snd_mixer_selem_id_free, METH_O, NULL},
  {"snd_mixer_selem_id_malloc", _cffi_f_snd_mixer_selem_id_malloc, METH_O, NULL},
  {"snd_mixer_selem_id_set_name", _cffi_f_snd_mixer_selem_id_set_name, METH_VARARGS, NULL},
  {"snd_mixer_selem_register", _cffi_f_snd_mixer_selem_register, METH_VARARGS, NULL},
  {"snd_mixer_selem_set_playback_dB", _cffi_f_snd_mixer_selem_set_playback_dB, METH_VARARGS, NULL},
  {"snd_mixer_selem_set_playback_dB_all", _cffi_f_snd_mixer_selem_set_playback_dB_all, METH_VARARGS, NULL},
  {"snd_mixer_selem_set_playback_volume", _cffi_f_snd_mixer_selem_set_playback_volume, METH_VARARGS, NULL},
  {"snd_mixer_selem_set_playback_volume_all", _cffi_f_snd_mixer_selem_set_playback_volume_all, METH_VARARGS, NULL},
  {"_cffi_layout_struct_pollfd", _cffi_layout_struct_pollfd, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__xd82178b6x9f84a7fa",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__xd82178b6x9f84a7fa(void)
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
init_cffi__xd82178b6x9f84a7fa(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__xd82178b6x9f84a7fa", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif


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



#include "fourd.h"


static void _cffi_check__FOURD(FOURD *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->socket) << 1);
  (void)((p->init) << 1);
  (void)((p->connected) << 1);
  (void)((p->status) << 1);
  (void)((p->error_code) << 1);
  { char(*tmp)[2048] = &p->error_string; (void)tmp; }
  (void)((p->updated_row) << 1);
  { char * *tmp = &p->preferred_image_types; (void)tmp; }
  (void)((p->timeout) << 1);
}
static PyObject *
_cffi_layout__FOURD(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD, socket),
    sizeof(((FOURD *)0)->socket),
    offsetof(FOURD, init),
    sizeof(((FOURD *)0)->init),
    offsetof(FOURD, connected),
    sizeof(((FOURD *)0)->connected),
    offsetof(FOURD, status),
    sizeof(((FOURD *)0)->status),
    offsetof(FOURD, error_code),
    sizeof(((FOURD *)0)->error_code),
    offsetof(FOURD, error_string),
    sizeof(((FOURD *)0)->error_string),
    offsetof(FOURD, updated_row),
    sizeof(((FOURD *)0)->updated_row),
    offsetof(FOURD, preferred_image_types),
    sizeof(((FOURD *)0)->preferred_image_types),
    offsetof(FOURD, timeout),
    sizeof(((FOURD *)0)->timeout),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD(0);
}

static void _cffi_check__FOURD_BLOB(FOURD_BLOB *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->length) << 1);
  { void * *tmp = &p->data; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_BLOB(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_BLOB y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_BLOB),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_BLOB, length),
    sizeof(((FOURD_BLOB *)0)->length),
    offsetof(FOURD_BLOB, data),
    sizeof(((FOURD_BLOB *)0)->data),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_BLOB(0);
}

static void _cffi_check__FOURD_COLUMN(FOURD_COLUMN *p)
{
  /* only to generate compile-time warnings or errors */
  { char(*tmp)[255] = &p->sType; (void)tmp; }
  { FOURD_TYPE *tmp = &p->type; (void)tmp; }
  { char(*tmp)[255] = &p->sColumnName; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_COLUMN(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_COLUMN y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_COLUMN),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_COLUMN, sType),
    sizeof(((FOURD_COLUMN *)0)->sType),
    offsetof(FOURD_COLUMN, type),
    sizeof(((FOURD_COLUMN *)0)->type),
    offsetof(FOURD_COLUMN, sColumnName),
    sizeof(((FOURD_COLUMN *)0)->sColumnName),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_COLUMN(0);
}

static void _cffi_check__FOURD_ELEMENT(FOURD_ELEMENT *p)
{
  /* only to generate compile-time warnings or errors */
  { FOURD_TYPE *tmp = &p->type; (void)tmp; }
  { char *tmp = &p->null; (void)tmp; }
  { void * *tmp = &p->pValue; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_ELEMENT(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_ELEMENT y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_ELEMENT),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_ELEMENT, type),
    sizeof(((FOURD_ELEMENT *)0)->type),
    offsetof(FOURD_ELEMENT, null),
    sizeof(((FOURD_ELEMENT *)0)->null),
    offsetof(FOURD_ELEMENT, pValue),
    sizeof(((FOURD_ELEMENT *)0)->pValue),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_ELEMENT(0);
}

static void _cffi_check__FOURD_FLOAT(FOURD_FLOAT *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->exp) << 1);
  (void)((p->sign) << 1);
  (void)((p->data_length) << 1);
  { void * *tmp = &p->data; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_FLOAT(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_FLOAT y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_FLOAT),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_FLOAT, exp),
    sizeof(((FOURD_FLOAT *)0)->exp),
    offsetof(FOURD_FLOAT, sign),
    sizeof(((FOURD_FLOAT *)0)->sign),
    offsetof(FOURD_FLOAT, data_length),
    sizeof(((FOURD_FLOAT *)0)->data_length),
    offsetof(FOURD_FLOAT, data),
    sizeof(((FOURD_FLOAT *)0)->data),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_FLOAT(0);
}

static void _cffi_check__FOURD_RESULT(FOURD_RESULT *p)
{
  /* only to generate compile-time warnings or errors */
  { FOURD * *tmp = &p->cnx; (void)tmp; }
  { char(*tmp)[2048] = &p->header; (void)tmp; }
  (void)((p->header_size) << 1);
  (void)((p->status) << 1);
  (void)((p->error_code) << 1);
  { char(*tmp)[2048] = &p->error_string; (void)tmp; }
  { FOURD_RESULT_TYPE *tmp = &p->resultType; (void)tmp; }
  (void)((p->id_statement) << 1);
  (void)((p->id_commande) << 1);
  (void)((p->updateability) << 1);
  (void)((p->row_count) << 1);
  (void)((p->row_count_sent) << 1);
  (void)((p->first_row) << 1);
  { FOURD_ROW_TYPE *tmp = &p->row_type; (void)tmp; }
  { FOURD_ELEMENT * *tmp = &p->elmt; (void)tmp; }
  (void)((p->numRow) << 1);
}
static PyObject *
_cffi_layout__FOURD_RESULT(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_RESULT y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_RESULT),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_RESULT, cnx),
    sizeof(((FOURD_RESULT *)0)->cnx),
    offsetof(FOURD_RESULT, header),
    sizeof(((FOURD_RESULT *)0)->header),
    offsetof(FOURD_RESULT, header_size),
    sizeof(((FOURD_RESULT *)0)->header_size),
    offsetof(FOURD_RESULT, status),
    sizeof(((FOURD_RESULT *)0)->status),
    offsetof(FOURD_RESULT, error_code),
    sizeof(((FOURD_RESULT *)0)->error_code),
    offsetof(FOURD_RESULT, error_string),
    sizeof(((FOURD_RESULT *)0)->error_string),
    offsetof(FOURD_RESULT, resultType),
    sizeof(((FOURD_RESULT *)0)->resultType),
    offsetof(FOURD_RESULT, id_statement),
    sizeof(((FOURD_RESULT *)0)->id_statement),
    offsetof(FOURD_RESULT, id_commande),
    sizeof(((FOURD_RESULT *)0)->id_commande),
    offsetof(FOURD_RESULT, updateability),
    sizeof(((FOURD_RESULT *)0)->updateability),
    offsetof(FOURD_RESULT, row_count),
    sizeof(((FOURD_RESULT *)0)->row_count),
    offsetof(FOURD_RESULT, row_count_sent),
    sizeof(((FOURD_RESULT *)0)->row_count_sent),
    offsetof(FOURD_RESULT, first_row),
    sizeof(((FOURD_RESULT *)0)->first_row),
    offsetof(FOURD_RESULT, row_type),
    sizeof(((FOURD_RESULT *)0)->row_type),
    offsetof(FOURD_RESULT, elmt),
    sizeof(((FOURD_RESULT *)0)->elmt),
    offsetof(FOURD_RESULT, numRow),
    sizeof(((FOURD_RESULT *)0)->numRow),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_RESULT(0);
}

static int _cffi_e__FOURD_RESULT_TYPE(PyObject *lib)
{
  if ((UNKNOW) < 0 || (unsigned long)(UNKNOW) != 0UL) {
    char buf[64];
    if ((UNKNOW) < 0)
        snprintf(buf, 63, "%ld", (long)(UNKNOW));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(UNKNOW));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_RESULT_TYPE", "UNKNOW", buf, "0");
    return -1;
  }
  if ((UPDATE_COUNT) < 0 || (unsigned long)(UPDATE_COUNT) != 1UL) {
    char buf[64];
    if ((UPDATE_COUNT) < 0)
        snprintf(buf, 63, "%ld", (long)(UPDATE_COUNT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(UPDATE_COUNT));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_RESULT_TYPE", "UPDATE_COUNT", buf, "1");
    return -1;
  }
  if ((RESULT_SET) < 0 || (unsigned long)(RESULT_SET) != 2UL) {
    char buf[64];
    if ((RESULT_SET) < 0)
        snprintf(buf, 63, "%ld", (long)(RESULT_SET));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(RESULT_SET));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_RESULT_TYPE", "RESULT_SET", buf, "2");
    return -1;
  }
  return 0;
}

static void _cffi_check__FOURD_ROW_TYPE(FOURD_ROW_TYPE *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->nbColumn) << 1);
  { FOURD_COLUMN * *tmp = &p->Column; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_ROW_TYPE(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_ROW_TYPE y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_ROW_TYPE),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_ROW_TYPE, nbColumn),
    sizeof(((FOURD_ROW_TYPE *)0)->nbColumn),
    offsetof(FOURD_ROW_TYPE, Column),
    sizeof(((FOURD_ROW_TYPE *)0)->Column),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_ROW_TYPE(0);
}

static void _cffi_check__FOURD_STATEMENT(FOURD_STATEMENT *p)
{
  /* only to generate compile-time warnings or errors */
  { FOURD * *tmp = &p->cnx; (void)tmp; }
  { char * *tmp = &p->query; (void)tmp; }
  (void)((p->nb_element) << 1);
  (void)((p->nbAllocElement) << 1);
  { FOURD_ELEMENT * *tmp = &p->elmt; (void)tmp; }
  { char * *tmp = &p->preferred_image_types; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_STATEMENT(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_STATEMENT y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_STATEMENT),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_STATEMENT, cnx),
    sizeof(((FOURD_STATEMENT *)0)->cnx),
    offsetof(FOURD_STATEMENT, query),
    sizeof(((FOURD_STATEMENT *)0)->query),
    offsetof(FOURD_STATEMENT, nb_element),
    sizeof(((FOURD_STATEMENT *)0)->nb_element),
    offsetof(FOURD_STATEMENT, nbAllocElement),
    sizeof(((FOURD_STATEMENT *)0)->nbAllocElement),
    offsetof(FOURD_STATEMENT, elmt),
    sizeof(((FOURD_STATEMENT *)0)->elmt),
    offsetof(FOURD_STATEMENT, preferred_image_types),
    sizeof(((FOURD_STATEMENT *)0)->preferred_image_types),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_STATEMENT(0);
}

static void _cffi_check__FOURD_STRING(FOURD_STRING *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->length) << 1);
  { char * *tmp = &p->data; (void)tmp; }
}
static PyObject *
_cffi_layout__FOURD_STRING(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_STRING y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_STRING),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_STRING, length),
    sizeof(((FOURD_STRING *)0)->length),
    offsetof(FOURD_STRING, data),
    sizeof(((FOURD_STRING *)0)->data),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_STRING(0);
}

static void _cffi_check__FOURD_TIMESTAMP(FOURD_TIMESTAMP *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->year) << 1);
  (void)((p->mounth) << 1);
  (void)((p->day) << 1);
  (void)((p->milli) << 1);
}
static PyObject *
_cffi_layout__FOURD_TIMESTAMP(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; FOURD_TIMESTAMP y; };
  static Py_ssize_t nums[] = {
    sizeof(FOURD_TIMESTAMP),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(FOURD_TIMESTAMP, year),
    sizeof(((FOURD_TIMESTAMP *)0)->year),
    offsetof(FOURD_TIMESTAMP, mounth),
    sizeof(((FOURD_TIMESTAMP *)0)->mounth),
    offsetof(FOURD_TIMESTAMP, day),
    sizeof(((FOURD_TIMESTAMP *)0)->day),
    offsetof(FOURD_TIMESTAMP, milli),
    sizeof(((FOURD_TIMESTAMP *)0)->milli),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__FOURD_TIMESTAMP(0);
}

static int _cffi_e__FOURD_TYPE(PyObject *lib)
{
  if ((VK_UNKNOW) < 0 || (unsigned long)(VK_UNKNOW) != 0UL) {
    char buf[64];
    if ((VK_UNKNOW) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_UNKNOW));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_UNKNOW));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_UNKNOW", buf, "0");
    return -1;
  }
  if ((VK_BOOLEAN) < 0 || (unsigned long)(VK_BOOLEAN) != 1UL) {
    char buf[64];
    if ((VK_BOOLEAN) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_BOOLEAN));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_BOOLEAN));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_BOOLEAN", buf, "1");
    return -1;
  }
  if ((VK_BYTE) < 0 || (unsigned long)(VK_BYTE) != 2UL) {
    char buf[64];
    if ((VK_BYTE) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_BYTE));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_BYTE));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_BYTE", buf, "2");
    return -1;
  }
  if ((VK_WORD) < 0 || (unsigned long)(VK_WORD) != 3UL) {
    char buf[64];
    if ((VK_WORD) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_WORD));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_WORD));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_WORD", buf, "3");
    return -1;
  }
  if ((VK_LONG) < 0 || (unsigned long)(VK_LONG) != 4UL) {
    char buf[64];
    if ((VK_LONG) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_LONG));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_LONG));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_LONG", buf, "4");
    return -1;
  }
  if ((VK_LONG8) < 0 || (unsigned long)(VK_LONG8) != 5UL) {
    char buf[64];
    if ((VK_LONG8) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_LONG8));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_LONG8));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_LONG8", buf, "5");
    return -1;
  }
  if ((VK_REAL) < 0 || (unsigned long)(VK_REAL) != 6UL) {
    char buf[64];
    if ((VK_REAL) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_REAL));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_REAL));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_REAL", buf, "6");
    return -1;
  }
  if ((VK_FLOAT) < 0 || (unsigned long)(VK_FLOAT) != 7UL) {
    char buf[64];
    if ((VK_FLOAT) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_FLOAT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_FLOAT));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_FLOAT", buf, "7");
    return -1;
  }
  if ((VK_TIME) < 0 || (unsigned long)(VK_TIME) != 8UL) {
    char buf[64];
    if ((VK_TIME) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_TIME));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_TIME));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_TIME", buf, "8");
    return -1;
  }
  if ((VK_TIMESTAMP) < 0 || (unsigned long)(VK_TIMESTAMP) != 9UL) {
    char buf[64];
    if ((VK_TIMESTAMP) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_TIMESTAMP));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_TIMESTAMP));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_TIMESTAMP", buf, "9");
    return -1;
  }
  if ((VK_DURATION) < 0 || (unsigned long)(VK_DURATION) != 10UL) {
    char buf[64];
    if ((VK_DURATION) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_DURATION));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_DURATION));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_DURATION", buf, "10");
    return -1;
  }
  if ((VK_TEXT) < 0 || (unsigned long)(VK_TEXT) != 11UL) {
    char buf[64];
    if ((VK_TEXT) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_TEXT));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_TEXT));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_TEXT", buf, "11");
    return -1;
  }
  if ((VK_STRING) < 0 || (unsigned long)(VK_STRING) != 12UL) {
    char buf[64];
    if ((VK_STRING) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_STRING));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_STRING));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_STRING", buf, "12");
    return -1;
  }
  if ((VK_BLOB) < 0 || (unsigned long)(VK_BLOB) != 13UL) {
    char buf[64];
    if ((VK_BLOB) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_BLOB));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_BLOB));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_BLOB", buf, "13");
    return -1;
  }
  if ((VK_IMAGE) < 0 || (unsigned long)(VK_IMAGE) != 14UL) {
    char buf[64];
    if ((VK_IMAGE) < 0)
        snprintf(buf, 63, "%ld", (long)(VK_IMAGE));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(VK_IMAGE));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "FOURD_TYPE", "VK_IMAGE", buf, "14");
    return -1;
  }
  return _cffi_e__FOURD_RESULT_TYPE(lib);
}

static PyObject *
_cffi_f_fourd_affected_rows(PyObject *self, PyObject *arg0)
{
  FOURD * x0;
  Py_ssize_t datasize;
  long long result;

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
  { result = fourd_affected_rows(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, long long);
}

static PyObject *
_cffi_f_fourd_bind_param(PyObject *self, PyObject *args)
{
  FOURD_STATEMENT * x0;
  unsigned int x1;
  FOURD_TYPE x2;
  void * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:fourd_bind_param", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, unsigned int);
  if (x1 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  if (_cffi_to_c((char *)&x2, _cffi_type(2), arg2) < 0)
    return NULL;

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
  { result = fourd_bind_param(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_close(PyObject *self, PyObject *arg0)
{
  FOURD * x0;
  Py_ssize_t datasize;
  int result;

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
  { result = fourd_close(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_close_statement(PyObject *self, PyObject *arg0)
{
  FOURD_RESULT * x0;
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
  { result = fourd_close_statement(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_connect(PyObject *self, PyObject *args)
{
  FOURD * x0;
  char const * x1;
  char const * x2;
  char const * x3;
  char const * x4;
  unsigned int x5;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:fourd_connect", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
    return NULL;

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
      _cffi_type(5), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(5), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(5), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(5), arg4) < 0)
      return NULL;
  }

  x5 = _cffi_to_c_int(arg5, unsigned int);
  if (x5 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_connect(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_errno(PyObject *self, PyObject *arg0)
{
  FOURD * x0;
  Py_ssize_t datasize;
  int result;

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
  { result = fourd_errno(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_error(PyObject *self, PyObject *arg0)
{
  FOURD * x0;
  Py_ssize_t datasize;
  char const * result;

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
  { result = fourd_error(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_fourd_exec_statement(PyObject *self, PyObject *args)
{
  FOURD_STATEMENT * x0;
  int x1;
  Py_ssize_t datasize;
  FOURD_RESULT * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_exec_statement", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_exec_statement(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_fourd_field(PyObject *self, PyObject *args)
{
  FOURD_RESULT * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  void * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_field", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_field(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_fourd_field_long(PyObject *self, PyObject *args)
{
  FOURD_RESULT * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  int * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_field_long", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_field_long(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(6));
}

static PyObject *
_cffi_f_fourd_field_string(PyObject *self, PyObject *args)
{
  FOURD_RESULT * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  FOURD_STRING * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_field_string", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_field_string(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(7));
}

static PyObject *
_cffi_f_fourd_field_to_string(PyObject *self, PyObject *args)
{
  FOURD_RESULT * x0;
  unsigned int x1;
  char * * x2;
  size_t * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:fourd_field_to_string", &arg0, &arg1, &arg2, &arg3))
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
      _cffi_type(8), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(8), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(9), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_field_to_string(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_free(PyObject *self, PyObject *arg0)
{
  FOURD * x0;
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
  { fourd_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_fourd_free_result(PyObject *self, PyObject *arg0)
{
  FOURD_RESULT * x0;
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
  { fourd_free_result(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_fourd_get_column_name(PyObject *self, PyObject *args)
{
  FOURD_RESULT * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  char const * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_get_column_name", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_get_column_name(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_fourd_get_column_type(PyObject *self, PyObject *args)
{
  FOURD_RESULT * x0;
  unsigned int x1;
  Py_ssize_t datasize;
  FOURD_TYPE result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_get_column_type", &arg0, &arg1))
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_get_column_type(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_deref((char *)&result, _cffi_type(2));
}

static PyObject *
_cffi_f_fourd_init(PyObject *self, PyObject *no_arg)
{
  FOURD * result;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fourd_init(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(0));
}

static PyObject *
_cffi_f_fourd_next_row(PyObject *self, PyObject *arg0)
{
  FOURD_RESULT * x0;
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
  { result = fourd_next_row(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_num_columns(PyObject *self, PyObject *arg0)
{
  FOURD_RESULT * x0;
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
  { result = fourd_num_columns(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_fourd_num_rows(PyObject *self, PyObject *arg0)
{
  FOURD_RESULT * x0;
  Py_ssize_t datasize;
  long long result;

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
  { result = fourd_num_rows(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, long long);
}

static PyObject *
_cffi_f_fourd_prepare_statement(PyObject *self, PyObject *args)
{
  FOURD * x0;
  char const * x1;
  Py_ssize_t datasize;
  FOURD_STATEMENT * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_prepare_statement", &arg0, &arg1))
    return NULL;

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
  { result = fourd_prepare_statement(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(1));
}

static PyObject *
_cffi_f_fourd_query(PyObject *self, PyObject *args)
{
  FOURD * x0;
  char const * x1;
  Py_ssize_t datasize;
  FOURD_RESULT * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:fourd_query", &arg0, &arg1))
    return NULL;

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
  { result = fourd_query(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(4));
}

static PyObject *
_cffi_f_free(PyObject *self, PyObject *arg0)
{
  void * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
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
_cffi_f_resultTypeFromString(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  FOURD_RESULT_TYPE result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(5), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = resultTypeFromString(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_deref((char *)&result, _cffi_type(11));
}

static PyObject *
_cffi_f_stringFromResultType(PyObject *self, PyObject *arg0)
{
  FOURD_RESULT_TYPE x0;
  char const * result;

  if (_cffi_to_c((char *)&x0, _cffi_type(11), arg0) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = stringFromResultType(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_stringFromType(PyObject *self, PyObject *arg0)
{
  FOURD_TYPE x0;
  char const * result;

  if (_cffi_to_c((char *)&x0, _cffi_type(2), arg0) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = stringFromType(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_typeFromString(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  FOURD_TYPE result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(5), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = typeFromString(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_deref((char *)&result, _cffi_type(2));
}

static PyObject *
_cffi_f_vk_sizeof(PyObject *self, PyObject *arg0)
{
  FOURD_TYPE x0;
  int result;

  if (_cffi_to_c((char *)&x0, _cffi_type(2), arg0) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = vk_sizeof(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_e__FOURD_TYPE(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout__FOURD", _cffi_layout__FOURD, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_BLOB", _cffi_layout__FOURD_BLOB, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_COLUMN", _cffi_layout__FOURD_COLUMN, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_ELEMENT", _cffi_layout__FOURD_ELEMENT, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_FLOAT", _cffi_layout__FOURD_FLOAT, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_RESULT", _cffi_layout__FOURD_RESULT, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_ROW_TYPE", _cffi_layout__FOURD_ROW_TYPE, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_STATEMENT", _cffi_layout__FOURD_STATEMENT, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_STRING", _cffi_layout__FOURD_STRING, METH_NOARGS, NULL},
  {"_cffi_layout__FOURD_TIMESTAMP", _cffi_layout__FOURD_TIMESTAMP, METH_NOARGS, NULL},
  {"fourd_affected_rows", _cffi_f_fourd_affected_rows, METH_O, NULL},
  {"fourd_bind_param", _cffi_f_fourd_bind_param, METH_VARARGS, NULL},
  {"fourd_close", _cffi_f_fourd_close, METH_O, NULL},
  {"fourd_close_statement", _cffi_f_fourd_close_statement, METH_O, NULL},
  {"fourd_connect", _cffi_f_fourd_connect, METH_VARARGS, NULL},
  {"fourd_errno", _cffi_f_fourd_errno, METH_O, NULL},
  {"fourd_error", _cffi_f_fourd_error, METH_O, NULL},
  {"fourd_exec_statement", _cffi_f_fourd_exec_statement, METH_VARARGS, NULL},
  {"fourd_field", _cffi_f_fourd_field, METH_VARARGS, NULL},
  {"fourd_field_long", _cffi_f_fourd_field_long, METH_VARARGS, NULL},
  {"fourd_field_string", _cffi_f_fourd_field_string, METH_VARARGS, NULL},
  {"fourd_field_to_string", _cffi_f_fourd_field_to_string, METH_VARARGS, NULL},
  {"fourd_free", _cffi_f_fourd_free, METH_O, NULL},
  {"fourd_free_result", _cffi_f_fourd_free_result, METH_O, NULL},
  {"fourd_get_column_name", _cffi_f_fourd_get_column_name, METH_VARARGS, NULL},
  {"fourd_get_column_type", _cffi_f_fourd_get_column_type, METH_VARARGS, NULL},
  {"fourd_init", _cffi_f_fourd_init, METH_NOARGS, NULL},
  {"fourd_next_row", _cffi_f_fourd_next_row, METH_O, NULL},
  {"fourd_num_columns", _cffi_f_fourd_num_columns, METH_O, NULL},
  {"fourd_num_rows", _cffi_f_fourd_num_rows, METH_O, NULL},
  {"fourd_prepare_statement", _cffi_f_fourd_prepare_statement, METH_VARARGS, NULL},
  {"fourd_query", _cffi_f_fourd_query, METH_VARARGS, NULL},
  {"free", _cffi_f_free, METH_O, NULL},
  {"resultTypeFromString", _cffi_f_resultTypeFromString, METH_O, NULL},
  {"stringFromResultType", _cffi_f_stringFromResultType, METH_O, NULL},
  {"stringFromType", _cffi_f_stringFromType, METH_O, NULL},
  {"typeFromString", _cffi_f_typeFromString, METH_O, NULL},
  {"vk_sizeof", _cffi_f_vk_sizeof, METH_O, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_Py4d_cffi_c9d3f55ex6d324386",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__Py4d_cffi_c9d3f55ex6d324386(void)
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
init_Py4d_cffi_c9d3f55ex6d324386(void)
{
  PyObject *lib;
  lib = Py_InitModule("_Py4d_cffi_c9d3f55ex6d324386", _cffi_methods);
  if (lib == NULL)
    return;
  if (0 < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

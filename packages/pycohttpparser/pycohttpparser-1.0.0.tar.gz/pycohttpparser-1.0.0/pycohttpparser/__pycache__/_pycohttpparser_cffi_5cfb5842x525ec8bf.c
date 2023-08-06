
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
/*
 * Copyright (c) 2009-2014 Kazuho Oku, Tokuhiro Matsuno, Daisuke Murase,
 *                         Shigeo Mitsunari
 *
 * The software is licensed under either the MIT License (below) or the Perl
 * license.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#include <assert.h>
#include <stddef.h>
#include <string.h>
#ifdef __SSE4_2__
# ifdef _MSC_VER
#  include <nmmintrin.h>
# else
#  include <x86intrin.h>
# endif
#endif
#include "picohttpparser.h"

/* $Id$ */

#if __GNUC__ >= 3
# define likely(x) __builtin_expect(!!(x), 1)
# define unlikely(x) __builtin_expect(!!(x), 0)
#else
# define likely(x) (x)
# define unlikely(x) (x)
#endif

#ifdef _MSC_VER
# define ALIGNED(n) _declspec(align(n))
#else
# define ALIGNED(n) __attribute__((aligned(n)))
#endif

#define IS_PRINTABLE_ASCII(c) ((unsigned char)(c) - 040u < 0137u)

#define CHECK_EOF() \
  if (buf == buf_end) { \
    *ret = -2; \
    return NULL; \
  }

#define EXPECT_CHAR(ch) \
  CHECK_EOF(); \
  if (*buf++ != ch) { \
    *ret = -1; \
    return NULL; \
  }

#define ADVANCE_TOKEN(tok, toklen) do { \
    const char* tok_start = buf; \
    static const char ALIGNED(16) ranges2[] = "\000\040\177\177"; \
    int found2; \
    buf = findchar_fast(buf, buf_end, ranges2, sizeof(ranges2) - 1, &found2); \
    if (! found2) { \
      CHECK_EOF(); \
    } \
    while (1) { \
      if (*buf == ' ') { \
        break; \
      } else if (unlikely(! IS_PRINTABLE_ASCII(*buf))) { \
        if ((unsigned char)*buf < '\040' || *buf == '\177') { \
          *ret = -1; \
          return NULL; \
        } \
      } \
      ++buf; \
      CHECK_EOF(); \
    } \
    tok = tok_start; \
    toklen = buf - tok_start; \
  } while (0)

static const char* token_char_map =
  "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
  "\0\1\1\1\1\1\1\1\0\0\1\1\0\1\1\0\1\1\1\1\1\1\1\1\1\1\0\0\0\0\0\0"
  "\0\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\0\0\1\1"
  "\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\1\0\1\0\1\0"
  "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
  "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
  "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
  "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0";

static const char* findchar_fast(const char* buf, const char* buf_end, const char *ranges, size_t ranges_size, int* found)
{
  *found = 0;
#if __SSE4_2__
  if (likely(buf_end - buf >= 16)) {
    __m128i ranges16 = _mm_loadu_si128((const __m128i*)ranges);

    size_t left = (buf_end - buf) & ~15;
    do {
      __m128i b16 = _mm_loadu_si128((void*)buf);
      int r = _mm_cmpestri(ranges16, ranges_size, b16, 16, _SIDD_LEAST_SIGNIFICANT | _SIDD_CMP_RANGES | _SIDD_UBYTE_OPS);
      if (unlikely(r != 16)) {
        buf += r;
        *found = 1;
        break;
      }
      buf += 16;
      left -= 16;
    } while (likely(left != 0));
  }
#endif
  return buf;
}

static const char* get_token_to_eol(const char* buf, const char* buf_end,
                                    const char** token, size_t* token_len,
                                    int* ret)
{
  const char* token_start = buf;
  
#ifdef __SSE4_2__
  static const char ranges1[] =
    "\0\010"
    /* allow HT */
    "\012\037"
    /* allow SP and up to but not including DEL */
    "\177\177"
    /* allow chars w. MSB set */
    ;
  int found;
  buf = findchar_fast(buf, buf_end, ranges1, sizeof(ranges1) - 1, &found);
  if (found)
    goto FOUND_CTL;
#else
  /* find non-printable char within the next 8 bytes, this is the hottest code; manually inlined */
  while (likely(buf_end - buf >= 8)) {
#define DOIT() if (unlikely(! IS_PRINTABLE_ASCII(*buf))) goto NonPrintable; ++buf
    DOIT(); DOIT(); DOIT(); DOIT();
    DOIT(); DOIT(); DOIT(); DOIT();
#undef DOIT
    continue;
  NonPrintable:
    if ((likely((unsigned char)*buf < '\040') && likely(*buf != '\011')) || unlikely(*buf == '\177')) {
      goto FOUND_CTL;
    }
    ++buf;
  }
#endif
  for (; ; ++buf) {
    CHECK_EOF();
    if (unlikely(! IS_PRINTABLE_ASCII(*buf))) {
      if ((likely((unsigned char)*buf < '\040') && likely(*buf != '\011')) || unlikely(*buf == '\177')) {
        goto FOUND_CTL;
      }
    }
  }
 FOUND_CTL:
  if (likely(*buf == '\015')) {
    ++buf;
    EXPECT_CHAR('\012');
    *token_len = buf - 2 - token_start;
  } else if (*buf == '\012') {
    *token_len = buf - token_start;
    ++buf;
  } else {
    *ret = -1;
    return NULL;
  }
  *token = token_start;
  
  return buf;
}
  
static const char* is_complete(const char* buf, const char* buf_end,
                               size_t last_len, int* ret)
{
  int ret_cnt = 0;
  buf = last_len < 3 ? buf : buf + last_len - 3;
  
  while (1) {
    CHECK_EOF();
    if (*buf == '\015') {
      ++buf;
      CHECK_EOF();
      EXPECT_CHAR('\012');
      ++ret_cnt;
    } else if (*buf == '\012') {
      ++buf;
      ++ret_cnt;
    } else {
      ++buf;
      ret_cnt = 0;
    }
    if (ret_cnt == 2) {
      return buf;
    }
  }
  
  *ret = -2;
  return NULL;
}

/* *_buf is always within [buf, buf_end) upon success */
static const char* parse_int(const char* buf, const char* buf_end, int* value,
                             int* ret)
{
  int v;
  CHECK_EOF();
  if (! ('0' <= *buf && *buf <= '9')) {
    *ret = -1;
    return NULL;
  }
  v = 0;
  for (; ; ++buf) {
    CHECK_EOF();
    if ('0' <= *buf && *buf <= '9') {
      v = v * 10 + *buf - '0';
    } else {
      break;
    }
  }
  
  *value = v;
  return buf;
}

/* returned pointer is always within [buf, buf_end), or null */
static const char* parse_http_version(const char* buf, const char* buf_end,
                                      int* minor_version, int* ret)
{
  EXPECT_CHAR('H'); EXPECT_CHAR('T'); EXPECT_CHAR('T'); EXPECT_CHAR('P');
  EXPECT_CHAR('/'); EXPECT_CHAR('1'); EXPECT_CHAR('.');
  return parse_int(buf, buf_end, minor_version, ret);
}

static const char* parse_headers(const char* buf, const char* buf_end,
                                 struct phr_header* headers,
                                 size_t* num_headers, size_t max_headers,
                                 int* ret)
{
  for (; ; ++*num_headers) {
    CHECK_EOF();
    if (*buf == '\015') {
      ++buf;
      EXPECT_CHAR('\012');
      break;
    } else if (*buf == '\012') {
      ++buf;
      break;
    }
    if (*num_headers == max_headers) {
      *ret = -1;
      return NULL;
    }
    if (! (*num_headers != 0 && (*buf == ' ' || *buf == '\t'))) {
      if (! token_char_map[(unsigned char)*buf]) {
        *ret = -1;
        return NULL;
      }
      /* parsing name, but do not discard SP before colon, see
       * http://www.mozilla.org/security/announce/2006/mfsa2006-33.html */
      headers[*num_headers].name = buf;
      static const char ALIGNED(16) ranges1[] = "::\x00\037";
      int found;
      buf = findchar_fast(buf, buf_end, ranges1, sizeof(ranges1) - 1, &found);
      if (! found) {
        CHECK_EOF();
      }
      while (1) {
        if (*buf == ':') {
          break;
        } else if (*buf < ' ') {
          *ret = -1;
          return NULL;
        }
        ++buf;
        CHECK_EOF();
      }
      headers[*num_headers].name_len = buf - headers[*num_headers].name;
      ++buf;
      for (; ; ++buf) {
        CHECK_EOF();
        if (! (*buf == ' ' || *buf == '\t')) {
          break;
        }
      }
    } else {
      headers[*num_headers].name = NULL;
      headers[*num_headers].name_len = 0;
    }
    if ((buf = get_token_to_eol(buf, buf_end, &headers[*num_headers].value,
                                &headers[*num_headers].value_len, ret))
        == NULL) {
      return NULL;
    }
  }
  return buf;
}

static const char* parse_request(const char* buf, const char* buf_end,
                                 const char** method, size_t* method_len,
                                 const char** path, size_t* path_len,
                                 int* minor_version, struct phr_header* headers,
                                 size_t* num_headers, size_t max_headers,
                                 int* ret)
{
  /* skip first empty line (some clients add CRLF after POST content) */
  CHECK_EOF();
  if (*buf == '\015') {
    ++buf;
    EXPECT_CHAR('\012');
  } else if (*buf == '\012') {
    ++buf;
  }
  
  /* parse request line */
  ADVANCE_TOKEN(*method, *method_len);
  ++buf;
  ADVANCE_TOKEN(*path, *path_len);
  ++buf;
  if ((buf = parse_http_version(buf, buf_end, minor_version, ret)) == NULL) {
    return NULL;
  }
  if (*buf == '\015') {
    ++buf;
    EXPECT_CHAR('\012');
  } else if (*buf == '\012') {
    ++buf;
  } else {
    *ret = -1;
    return NULL;
  }
  
  return parse_headers(buf, buf_end, headers, num_headers, max_headers, ret);
}

int phr_parse_request(const char* buf_start, size_t len, const char** method,
                      size_t* method_len, const char** path, size_t* path_len,
                      int* minor_version, struct phr_header* headers,
                      size_t* num_headers, size_t last_len)
{
  const char * buf = buf_start, * buf_end = buf_start + len;
  size_t max_headers = *num_headers;
  int r;
  
  *method = NULL;
  *method_len = 0;
  *path = NULL;
  *path_len = 0;
  *minor_version = -1;
  *num_headers = 0;
  
  /* if last_len != 0, check if the request is complete (a fast countermeasure
     againt slowloris */
  if (last_len != 0 && is_complete(buf, buf_end, last_len, &r) == NULL) {
    return r;
  }
  
  if ((buf = parse_request(buf, buf_end, method, method_len, path, path_len,
                           minor_version, headers, num_headers, max_headers,
                           &r))
      == NULL) {
    return r;
  }
  
  return (int)(buf - buf_start);
}

static const char* parse_response(const char* buf, const char* buf_end,
                                  int* minor_version, int* status,
                                  const char** msg, size_t* msg_len,
                                  struct phr_header* headers,
                                  size_t* num_headers, size_t max_headers,
                                  int* ret)
{
  /* parse "HTTP/1.x" */
  if ((buf = parse_http_version(buf, buf_end, minor_version, ret)) == NULL) {
    return NULL;
  }
  /* skip space */
  if (*buf++ != ' ') {
    *ret = -1;
    return NULL;
  }
  /* parse status code */
  if ((buf = parse_int(buf, buf_end, status, ret)) == NULL) {
    return NULL;
  }
  /* skip space */
  if (*buf++ != ' ') {
    *ret = -1;
    return NULL;
  }
  /* get message */
  if ((buf = get_token_to_eol(buf, buf_end, msg, msg_len, ret)) == NULL) {
    return NULL;
  }
  
  return parse_headers(buf, buf_end, headers, num_headers, max_headers, ret);
}

int phr_parse_response(const char* buf_start, size_t len, int* minor_version,
                       int* status, const char** msg, size_t* msg_len,
                       struct phr_header* headers, size_t* num_headers,
                       size_t last_len)
{
  const char * buf = buf_start, * buf_end = buf + len;
  size_t max_headers = *num_headers;
  int r;
  
  *minor_version = -1;
  *status = 0;
  *msg = NULL;
  *msg_len = 0;
  *num_headers = 0;
  
  /* if last_len != 0, check if the response is complete (a fast countermeasure
     against slowloris */
  if (last_len != 0 && is_complete(buf, buf_end, last_len, &r) == NULL) {
    return r;
  }
  
  if ((buf = parse_response(buf, buf_end, minor_version, status, msg, msg_len,
                            headers, num_headers, max_headers, &r))
      == NULL) {
    return r;
  }
  
  return (int)(buf - buf_start);
}

int phr_parse_headers(const char* buf_start, size_t len,
                      struct phr_header* headers, size_t* num_headers,
                      size_t last_len)
{
  const char* buf = buf_start, * buf_end = buf + len;
  size_t max_headers = *num_headers;
  int r;

  *num_headers = 0;

  /* if last_len != 0, check if the response is complete (a fast countermeasure
     against slowloris */
  if (last_len != 0 && is_complete(buf, buf_end, last_len, &r) == NULL) {
    return r;
  }

  if ((buf = parse_headers(buf, buf_end, headers, num_headers, max_headers, &r))
      == NULL) {
    return r;
  }

  return (int)(buf - buf_start);
}

enum {
  CHUNKED_IN_CHUNK_SIZE,
  CHUNKED_IN_CHUNK_EXT,
  CHUNKED_IN_CHUNK_DATA,
  CHUNKED_IN_CHUNK_CRLF,
  CHUNKED_IN_TRAILERS_LINE_HEAD,
  CHUNKED_IN_TRAILERS_LINE_MIDDLE
};

static int decode_hex(int ch)
{
  if ('0' <= ch && ch <= '9') {
    return ch - '0';
  } else if ('A' <= ch && ch <= 'F') {
    return ch - 'A' + 0xa;
  } else if ('a' <= ch && ch <= 'f') {
    return ch - 'a' + 0xa;
  } else {
    return -1;
  }
}

ssize_t phr_decode_chunked(struct phr_chunked_decoder *decoder, char *buf,
                           size_t *_bufsz)
{
  size_t dst = 0, src = 0, bufsz = *_bufsz;
  ssize_t ret = -2; /* incomplete */

  while (1) {
    switch (decoder->_state) {
    case CHUNKED_IN_CHUNK_SIZE:
      for (; ; ++src) {
        int v;
        if (src == bufsz)
          goto Exit;
        if ((v = decode_hex(buf[src])) == -1) {
          if (decoder->_hex_count == 0) {
            ret = -1;
            goto Exit;
          }
          break;
        }
        if (decoder->_hex_count == sizeof(size_t) * 2) {
          ret = -1;
          goto Exit;
        }
        decoder->bytes_left_in_chunk = decoder->bytes_left_in_chunk * 16 + v;
        ++decoder->_hex_count;
      }
      decoder->_hex_count = 0;
      decoder->_state = CHUNKED_IN_CHUNK_EXT;
      /* fallthru */
    case CHUNKED_IN_CHUNK_EXT:
      /* RFC 7230 A.2 "Line folding in chunk extensions is disallowed" */
      for (; ; ++src) {
        if (src == bufsz)
          goto Exit;
        if (buf[src] == '\012')
          break;
      }
      ++src;
      if (decoder->bytes_left_in_chunk == 0) {
        if (decoder->consume_trailer) {
          decoder->_state = CHUNKED_IN_TRAILERS_LINE_HEAD;
          break;
        } else {
          goto Complete;
        }
      }
      decoder->_state = CHUNKED_IN_CHUNK_DATA;
      /* fallthru */
    case CHUNKED_IN_CHUNK_DATA:
      {
        size_t avail = bufsz - src;
        if (avail < decoder->bytes_left_in_chunk) {
          if (dst != src)
            memmove(buf + dst, buf + src, avail);
          src += avail;
          dst += avail;
          decoder->bytes_left_in_chunk -= avail;
          goto Exit;
        }
        if (dst != src)
          memmove(buf + dst, buf + src, decoder->bytes_left_in_chunk);
        src += decoder->bytes_left_in_chunk;
        dst += decoder->bytes_left_in_chunk;
        decoder->bytes_left_in_chunk = 0;
        decoder->_state = CHUNKED_IN_CHUNK_CRLF;
      }
      /* fallthru */
    case CHUNKED_IN_CHUNK_CRLF:
      for (; ; ++src) {
        if (src == bufsz)
          goto Exit;
        if (buf[src] != '\015')
          break;
      }
      if (buf[src] != '\012') {
        ret = -1;
        goto Exit;
      }
      ++src;
      decoder->_state = CHUNKED_IN_CHUNK_SIZE;
      break;
    case CHUNKED_IN_TRAILERS_LINE_HEAD:
      for (; ; ++src) {
        if (src == bufsz)
          goto Exit;
        if (buf[src] != '\015')
          break;
      }
      if (buf[src++] == '\012')
        goto Complete;
      decoder->_state = CHUNKED_IN_TRAILERS_LINE_MIDDLE;
      /* fallthru */
    case CHUNKED_IN_TRAILERS_LINE_MIDDLE:
      for (; ; ++src) {
        if (src == bufsz)
          goto Exit;
        if (buf[src] == '\012')
          break;
      }
      ++src;
      decoder->_state = CHUNKED_IN_TRAILERS_LINE_HEAD;
      break;
    default:
      assert(!"decoder is corrupt");
    }
  }

Complete:
  ret = bufsz - src;
Exit:
  if (dst != src)
    memmove(buf + dst, buf + src, bufsz - src);
  *_bufsz = dst;
  return ret;
}

#undef CHECK_EOF
#undef EXPECT_CHAR
#undef ADVANCE_TOKEN


static PyObject *
_cffi_f_phr_decode_chunked(PyObject *self, PyObject *args)
{
  struct phr_chunked_decoder * x0;
  char * x1;
  size_t * x2;
  Py_ssize_t datasize;
  ssize_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:phr_decode_chunked", &arg0, &arg1, &arg2))
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
  { result = phr_decode_chunked(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, ssize_t);
}

static PyObject *
_cffi_f_phr_parse_headers(PyObject *self, PyObject *args)
{
  char const * x0;
  size_t x1;
  struct phr_header * x2;
  size_t * x3;
  size_t x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:phr_parse_headers", &arg0, &arg1, &arg2, &arg3, &arg4))
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

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

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

  x4 = _cffi_to_c_int(arg4, size_t);
  if (x4 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = phr_parse_headers(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_phr_parse_request(PyObject *self, PyObject *args)
{
  char const * x0;
  size_t x1;
  char const * * x2;
  size_t * x3;
  char const * * x4;
  size_t * x5;
  int * x6;
  struct phr_header * x7;
  size_t * x8;
  size_t x9;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;
  PyObject *arg7;
  PyObject *arg8;
  PyObject *arg9;

  if (!PyArg_ParseTuple(args, "OOOOOOOOOO:phr_parse_request", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6, &arg7, &arg8, &arg9))
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

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(5), arg2) < 0)
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
      _cffi_type(5), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca((size_t)datasize);
    memset((void *)x4, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(5), arg4) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca((size_t)datasize);
    memset((void *)x5, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(2), arg5) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca((size_t)datasize);
    memset((void *)x6, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(6), arg6) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg7, (char **)&x7);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x7 = alloca((size_t)datasize);
    memset((void *)x7, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x7, _cffi_type(4), arg7) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg8, (char **)&x8);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x8 = alloca((size_t)datasize);
    memset((void *)x8, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x8, _cffi_type(2), arg8) < 0)
      return NULL;
  }

  x9 = _cffi_to_c_int(arg9, size_t);
  if (x9 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = phr_parse_request(x0, x1, x2, x3, x4, x5, x6, x7, x8, x9); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_phr_parse_response(PyObject *self, PyObject *args)
{
  char const * x0;
  size_t x1;
  int * x2;
  int * x3;
  char const * * x4;
  size_t * x5;
  struct phr_header * x6;
  size_t * x7;
  size_t x8;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;
  PyObject *arg7;
  PyObject *arg8;

  if (!PyArg_ParseTuple(args, "OOOOOOOOO:phr_parse_response", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6, &arg7, &arg8))
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

  x1 = _cffi_to_c_int(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca((size_t)datasize);
    memset((void *)x2, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(6), arg2) < 0)
      return NULL;
  }

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca((size_t)datasize);
    memset((void *)x5, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(2), arg5) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca((size_t)datasize);
    memset((void *)x6, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(4), arg6) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg7, (char **)&x7);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x7 = alloca((size_t)datasize);
    memset((void *)x7, 0, (size_t)datasize);
    if (_cffi_convert_array_from_object((char *)x7, _cffi_type(2), arg7) < 0)
      return NULL;
  }

  x8 = _cffi_to_c_int(arg8, size_t);
  if (x8 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = phr_parse_response(x0, x1, x2, x3, x4, x5, x6, x7, x8); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  return _cffi_from_c_int(result, int);
}

static void _cffi_check_struct_phr_chunked_decoder(struct phr_chunked_decoder *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  (void)((p->bytes_left_in_chunk) << 1);
  { char *tmp = &p->consume_trailer; (void)tmp; }
  { char *tmp = &p->_hex_count; (void)tmp; }
  { char *tmp = &p->_state; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_phr_chunked_decoder(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct phr_chunked_decoder y; };
  static Py_ssize_t nums[] = {
    sizeof(struct phr_chunked_decoder),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct phr_chunked_decoder, bytes_left_in_chunk),
    sizeof(((struct phr_chunked_decoder *)0)->bytes_left_in_chunk),
    offsetof(struct phr_chunked_decoder, consume_trailer),
    sizeof(((struct phr_chunked_decoder *)0)->consume_trailer),
    offsetof(struct phr_chunked_decoder, _hex_count),
    sizeof(((struct phr_chunked_decoder *)0)->_hex_count),
    offsetof(struct phr_chunked_decoder, _state),
    sizeof(((struct phr_chunked_decoder *)0)->_state),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_phr_chunked_decoder(0);
}

static void _cffi_check_struct_phr_header(struct phr_header *p)
{
  /* only to generate compile-time warnings or errors */
  (void)p;
  { char const * *tmp = &p->name; (void)tmp; }
  (void)((p->name_len) << 1);
  { char const * *tmp = &p->value; (void)tmp; }
  (void)((p->value_len) << 1);
}
static PyObject *
_cffi_layout_struct_phr_header(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct phr_header y; };
  static Py_ssize_t nums[] = {
    sizeof(struct phr_header),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct phr_header, name),
    sizeof(((struct phr_header *)0)->name),
    offsetof(struct phr_header, name_len),
    sizeof(((struct phr_header *)0)->name_len),
    offsetof(struct phr_header, value),
    sizeof(((struct phr_header *)0)->value),
    offsetof(struct phr_header, value_len),
    sizeof(((struct phr_header *)0)->value_len),
    -1
  };
  (void)self; /* unused */
  (void)noarg; /* unused */
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_phr_header(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return ((void)lib,0);
}

static PyMethodDef _cffi_methods[] = {
  {"phr_decode_chunked", _cffi_f_phr_decode_chunked, METH_VARARGS, NULL},
  {"phr_parse_headers", _cffi_f_phr_parse_headers, METH_VARARGS, NULL},
  {"phr_parse_request", _cffi_f_phr_parse_request, METH_VARARGS, NULL},
  {"phr_parse_response", _cffi_f_phr_parse_response, METH_VARARGS, NULL},
  {"_cffi_layout_struct_phr_chunked_decoder", _cffi_layout_struct_phr_chunked_decoder, METH_NOARGS, NULL},
  {"_cffi_layout_struct_phr_header", _cffi_layout_struct_phr_header, METH_NOARGS, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_pycohttpparser_cffi_5cfb5842x525ec8bf",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__pycohttpparser_cffi_5cfb5842x525ec8bf(void)
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
init_pycohttpparser_cffi_5cfb5842x525ec8bf(void)
{
  PyObject *lib;
  lib = Py_InitModule("_pycohttpparser_cffi_5cfb5842x525ec8bf", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif

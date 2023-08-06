#ifndef __PYX_HAVE__SnapPy
#define __PYX_HAVE__SnapPy


#ifndef __PYX_HAVE_API__SnapPy

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#ifndef DL_IMPORT
  #define DL_IMPORT(_T) _T
#endif

__PYX_EXTERN_C DL_IMPORT(PyObject) *UCS2_hack(char *, Py_ssize_t, char *);
__PYX_EXTERN_C DL_IMPORT(void) uFatalError(const char*, const char*);
__PYX_EXTERN_C DL_IMPORT(void) uLongComputationBegins(const char*, Boolean);
__PYX_EXTERN_C DL_IMPORT(FuncResult) uLongComputationContinues(void);
__PYX_EXTERN_C DL_IMPORT(void) uLongComputationEnds(void);
__PYX_EXTERN_C DL_IMPORT(void) uAcknowledge(const char*);
__PYX_EXTERN_C DL_IMPORT(void) uAbortMemoryFull(void);
__PYX_EXTERN_C DL_IMPORT(int) uQuery(const char*, const int, const char* *, const int);

__PYX_EXTERN_C DL_IMPORT(int) SnapPy_test_flag;
__PYX_EXTERN_C DL_IMPORT(Boolean) gLongComputationInProgress;
__PYX_EXTERN_C DL_IMPORT(Boolean) gLongComputationCancelled;
__PYX_EXTERN_C DL_IMPORT(PyObject) *gLongComputationTicker;

#endif /* !__PYX_HAVE_API__SnapPy */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initSnapPy(void);
#else
PyMODINIT_FUNC PyInit_SnapPy(void);
#endif

#endif /* !__PYX_HAVE__SnapPy */

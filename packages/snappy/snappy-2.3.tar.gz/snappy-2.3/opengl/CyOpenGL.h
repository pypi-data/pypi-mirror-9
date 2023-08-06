#ifndef __PYX_HAVE__CyOpenGL
#define __PYX_HAVE__CyOpenGL


#ifndef __PYX_HAVE_API__CyOpenGL

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

#endif /* !__PYX_HAVE_API__CyOpenGL */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initCyOpenGL(void);
#else
PyMODINIT_FUNC PyInit_CyOpenGL(void);
#endif

#endif /* !__PYX_HAVE__CyOpenGL */

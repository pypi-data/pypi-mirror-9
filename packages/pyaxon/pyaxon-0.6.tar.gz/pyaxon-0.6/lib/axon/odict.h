#ifndef __PYX_HAVE__axon__odict
#define __PYX_HAVE__axon__odict

struct OrderedDictObject;

/* "axon/odict.pxd":80
 * cdef Link link_marker
 * 
 * cdef public class OrderedDict[object OrderedDictObject, type OrderedDictType]:             # <<<<<<<<<<<<<<
 * 
 *     cdef Link root
 */
struct OrderedDictObject {
  PyObject_HEAD
  struct __pyx_obj_4axon_5odict_Link *root;
  PyObject *map;
};

#ifndef __PYX_HAVE_API__axon__odict

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

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) OrderedDictType;

#endif /* !__PYX_HAVE_API__axon__odict */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initodict(void);
#else
PyMODINIT_FUNC PyInit_odict(void);
#endif

#endif /* !__PYX_HAVE__axon__odict */

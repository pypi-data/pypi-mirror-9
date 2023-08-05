#ifndef __PYX_HAVE__solvcon__parcel__fake___algorithm
#define __PYX_HAVE__solvcon__parcel__fake___algorithm

struct sc_fake_algorithm_t;
typedef struct sc_fake_algorithm_t sc_fake_algorithm_t;

/* "solvcon/parcel/fake/_algorithm.pxd":30
 * 
 * cdef public:
 *     ctypedef struct sc_fake_algorithm_t:             # <<<<<<<<<<<<<<
 *         int neq
 *         double time, time_increment
 */
struct sc_fake_algorithm_t {
  int neq;
  double time;
  double time_increment;
  double *sol;
  double *soln;
  double *dsol;
  double *dsoln;
};

#ifndef __PYX_HAVE_API__solvcon__parcel__fake___algorithm

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

#endif /* !__PYX_HAVE_API__solvcon__parcel__fake___algorithm */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_algorithm(void);
#else
PyMODINIT_FUNC PyInit__algorithm(void);
#endif

#endif /* !__PYX_HAVE__solvcon__parcel__fake___algorithm */

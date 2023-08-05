#ifndef __PYX_HAVE__solvcon__parcel__gas___algorithm
#define __PYX_HAVE__solvcon__parcel__gas___algorithm

struct sc_gas_algorithm_t;
typedef struct sc_gas_algorithm_t sc_gas_algorithm_t;

/* "solvcon/parcel/gas/_algorithm.pxd":30
 * 
 * cdef public:
 *     ctypedef struct sc_gas_algorithm_t:             # <<<<<<<<<<<<<<
 *         # equation number.
 *         int neq
 */
struct sc_gas_algorithm_t {
  int neq;
  double time;
  double time_increment;
  int alpha;
  double sigma0;
  double taylor;
  double cnbfac;
  double sftfac;
  double taumin;
  double tauscale;
  double *cecnd;
  double *cevol;
  double *sfmrc;
  int ngroup;
  int gdlen;
  double *grpda;
  int nsca;
  double *amsca;
  int nvec;
  double *amvec;
  double *sol;
  double *dsol;
  double *solt;
  double *soln;
  double *dsoln;
  double *stm;
  double *cfl;
  double *ocfl;
};

#ifndef __PYX_HAVE_API__solvcon__parcel__gas___algorithm

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

#endif /* !__PYX_HAVE_API__solvcon__parcel__gas___algorithm */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_algorithm(void);
#else
PyMODINIT_FUNC PyInit__algorithm(void);
#endif

#endif /* !__PYX_HAVE__solvcon__parcel__gas___algorithm */

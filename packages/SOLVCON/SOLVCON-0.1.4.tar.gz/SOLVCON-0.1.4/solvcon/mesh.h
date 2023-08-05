#ifndef __PYX_HAVE__solvcon__mesh
#define __PYX_HAVE__solvcon__mesh

struct sc_mesh_t;
typedef struct sc_mesh_t sc_mesh_t;
struct sc_bound_t;
typedef struct sc_bound_t sc_bound_t;

/* "solvcon/mesh.pxd":54
 *         double *value
 * 
 *     cdef enum sc_mesh_shape_enum:             # <<<<<<<<<<<<<<
 *         FCMND = 4
 *         CLMND = 8
 */
enum sc_mesh_shape_enum {
  FCMND = 4,
  CLMND = 8,
  CLMFC = 6,
  FCREL = 4,
  BFREL = 3
};

/* "solvcon/mesh.pxd":30
 * 
 * cdef public:
 *     ctypedef struct sc_mesh_t:             # <<<<<<<<<<<<<<
 *         int ndim, nnode, nface, ncell, nbound, ngstnode, ngstface, ngstcell
 *         # geometry.
 */
struct sc_mesh_t {
  int ndim;
  int nnode;
  int nface;
  int ncell;
  int nbound;
  int ngstnode;
  int ngstface;
  int ngstcell;
  double *ndcrd;
  double *fccnd;
  double *fcnml;
  double *fcara;
  double *clcnd;
  double *clvol;
  int *fctpn;
  int *cltpn;
  int *clgrp;
  int *fcnds;
  int *fccls;
  int *clnds;
  int *clfcs;
};

/* "solvcon/mesh.pxd":49
 *         int *clfcs
 * 
 *     ctypedef struct sc_bound_t:             # <<<<<<<<<<<<<<
 *         int nbound, nvalue
 *         int *facn
 */
struct sc_bound_t {
  int nbound;
  int nvalue;
  int *facn;
  double *value;
};

#ifndef __PYX_HAVE_API__solvcon__mesh

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

#endif /* !__PYX_HAVE_API__solvcon__mesh */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initmesh(void);
#else
PyMODINIT_FUNC PyInit_mesh(void);
#endif

#endif /* !__PYX_HAVE__solvcon__mesh */

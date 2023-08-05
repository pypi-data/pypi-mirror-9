
/*! @file zlaqgs.c
 * \brief Equlibrates a general sprase matrix
 *
 * <pre>
 * -- SuperLU routine (version 2.0) --
 * Univ. of California Berkeley, Xerox Palo Alto Research Center,
 * and Lawrence Berkeley National Lab.
 * November 15, 1997
 * 
 * Modified from LAPACK routine ZLAQGE
 * </pre>
 */
/*
 * File name:	zlaqgs.c
 * History:     Modified from LAPACK routine ZLAQGE
 */
#include <math.h>
#include "slu_zdefs.h"

/*! \brief
 *
 * <pre>
 *   Purpose   
 *   =======   
 *
 *   ZLAQGS equilibrates a general sparse M by N matrix A using the row and   
 *   scaling factors in the vectors R and C.   
 *
 *   See supermatrix.h for the definition of 'SuperMatrix' structure.
 *
 *   Arguments   
 *   =========   
 *
 *   A       (input/output) SuperMatrix*
 *           On exit, the equilibrated matrix.  See EQUED for the form of 
 *           the equilibrated matrix. The type of A can be:
 *	    Stype = NC; Dtype = SLU_Z; Mtype = GE.
 *	    
 *   R       (input) double*, dimension (A->nrow)
 *           The row scale factors for A.
 *	    
 *   C       (input) double*, dimension (A->ncol)
 *           The column scale factors for A.
 *	    
 *   ROWCND  (input) double
 *           Ratio of the smallest R(i) to the largest R(i).
 *	    
 *   COLCND  (input) double
 *           Ratio of the smallest C(i) to the largest C(i).
 *	    
 *   AMAX    (input) double
 *           Absolute value of largest matrix entry.
 *	    
 *   EQUED   (output) char*
 *           Specifies the form of equilibration that was done.   
 *           = 'N':  No equilibration   
 *           = 'R':  Row equilibration, i.e., A has been premultiplied by  
 *                   diag(R).   
 *           = 'C':  Column equilibration, i.e., A has been postmultiplied  
 *                   by diag(C).   
 *           = 'B':  Both row and column equilibration, i.e., A has been
 *                   replaced by diag(R) * A * diag(C).   
 *
 *   Internal Parameters   
 *   ===================   
 *
 *   THRESH is a threshold value used to decide if row or column scaling   
 *   should be done based on the ratio of the row or column scaling   
 *   factors.  If ROWCND < THRESH, row scaling is done, and if   
 *   COLCND < THRESH, column scaling is done.   
 *
 *   LARGE and SMALL are threshold values used to decide if row scaling   
 *   should be done based on the absolute size of the largest matrix   
 *   element.  If AMAX > LARGE or AMAX < SMALL, row scaling is done.   
 *
 *   ===================================================================== 
 * </pre>
 */

void
zlaqgs(SuperMatrix *A, double *r, double *c, 
	double rowcnd, double colcnd, double amax, char *equed)
{


#define THRESH    (0.1)
    
    /* Local variables */
    NCformat *Astore;
    doublecomplex   *Aval;
    int i, j, irow;
    double large, small, cj;
    double temp;


    /* Quick return if possible */
    if (A->nrow <= 0 || A->ncol <= 0) {
	*(unsigned char *)equed = 'N';
	return;
    }

    Astore = A->Store;
    Aval = Astore->nzval;
    
    /* Initialize LARGE and SMALL. */
    small = dlamch_("Safe minimum") / dlamch_("Precision");
    large = 1. / small;

    if (rowcnd >= THRESH && amax >= small && amax <= large) {
	if (colcnd >= THRESH)
	    *(unsigned char *)equed = 'N';
	else {
	    /* Column scaling */
	    for (j = 0; j < A->ncol; ++j) {
		cj = c[j];
		for (i = Astore->colptr[j]; i < Astore->colptr[j+1]; ++i) {
		    zd_mult(&Aval[i], &Aval[i], cj);
                }
	    }
	    *(unsigned char *)equed = 'C';
	}
    } else if (colcnd >= THRESH) {
	/* Row scaling, no column scaling */
	for (j = 0; j < A->ncol; ++j)
	    for (i = Astore->colptr[j]; i < Astore->colptr[j+1]; ++i) {
		irow = Astore->rowind[i];
		zd_mult(&Aval[i], &Aval[i], r[irow]);
	    }
	*(unsigned char *)equed = 'R';
    } else {
	/* Row and column scaling */
	for (j = 0; j < A->ncol; ++j) {
	    cj = c[j];
	    for (i = Astore->colptr[j]; i < Astore->colptr[j+1]; ++i) {
		irow = Astore->rowind[i];
		temp = cj * r[irow];
		zd_mult(&Aval[i], &Aval[i], temp);
	    }
	}
	*(unsigned char *)equed = 'B';
    }

    return;

} /* zlaqgs */


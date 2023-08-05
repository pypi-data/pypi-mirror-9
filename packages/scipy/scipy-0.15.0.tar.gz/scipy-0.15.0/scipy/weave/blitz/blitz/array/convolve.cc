/***************************************************************************
 * blitz/array/convolve.cc  One-dimensional convolution
 *
 * Copyright (C) 1997-2001 Todd Veldhuizen <tveldhui@oonumerics.org>
 *
 * This code was relicensed under the modified BSD license for use in SciPy
 * by Todd Veldhuizen (see LICENSE.txt in the weave directory).
 *
 *
 * Suggestions:          blitz-dev@oonumerics.org
 * Bugs:                 blitz-bugs@oonumerics.org
 *
 * For more information, please see the Blitz++ Home Page:
 *    http://oonumerics.org/blitz/
 *
 ****************************************************************************/

#ifndef BZ_ARRAY_CONVOLVE_CC
#define BZ_ARRAY_CONVOLVE_CC

BZ_NAMESPACE(blitz)

template<typename T>
Array<T,1> convolve(const Array<T,1>& B, const Array<T,1>& C)
{
    int Bl = B.lbound(0), Bh = B.ubound(0);
    int Cl = C.lbound(0), Ch = C.ubound(0);

    int lbound = Bl + Cl;
    int ubound = Bh + Ch;
    
    Array<T,1> A(Range(lbound,ubound));

    for (int i=lbound; i <= ubound; ++i)
    {
        int jl = i - Ch;
        if (jl < Bl)
            jl = Bl;

        int jh = i - Cl;
        if (jh > Bh)
            jh = Bh;

        T result = 0;
        for (int j=jl; j <= jh; ++j)
            result += B(j) * C(i-j);

        A(i) = result;
    }

    return A;
}

BZ_NAMESPACE_END

#endif // BZ_ARRAY_CONVOLVE_CC


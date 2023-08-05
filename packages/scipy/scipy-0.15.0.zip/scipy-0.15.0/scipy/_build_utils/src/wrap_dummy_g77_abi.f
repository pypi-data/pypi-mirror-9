      COMPLEX FUNCTION WCDOTC( N, CX, INCX, CY, INCY )
      INTEGER INCX, INCY, N
      COMPLEX CX(*), CY(*)
      EXTERNAL CDOTC
      COMPLEX CDOTC
      WCDOTC = CDOTC( N, CX, INCX, CY, INCY )
      END FUNCTION

      COMPLEX FUNCTION WCDOTU( N, CX, INCX, CY, INCY )
      INTEGER INCX, INCY, N
      COMPLEX CX(*), CY(*)
      EXTERNAL CDOTU
      COMPLEX CDOTU
      WCDOTU = CDOTU( N, CX, INCX, CY, INCY )
      END FUNCTION

      DOUBLE COMPLEX FUNCTION WZDOTC( N, CX, INCX, CY, INCY )
      INTEGER INCX, INCY, N
      DOUBLE COMPLEX CX(*), CY(*)
      EXTERNAL ZDOTC
      DOUBLE COMPLEX ZDOTC
      WZDOTC = ZDOTC( N, CX, INCX, CY, INCY )
      END FUNCTION

      DOUBLE COMPLEX FUNCTION WZDOTU( N, CX, INCX, CY, INCY )
      INTEGER INCX, INCY, N
      DOUBLE COMPLEX CX(*), CY(*)
      EXTERNAL ZDOTU
      DOUBLE COMPLEX ZDOTU
      WZDOTU = ZDOTU( N, CX, INCX, CY, INCY )
      END FUNCTION

      COMPLEX FUNCTION WCLADIV( X, Y )
      COMPLEX            X, Y
      EXTERNAL           CLADIV
      COMPLEX            CLADIV
      WCLADIV = CLADIV( X, Y)
      END FUNCTION

      DOUBLE COMPLEX FUNCTION WZLADIV( X, Y )
      DOUBLE COMPLEX     X, Y
      EXTERNAL           ZLADIV
      DOUBLE COMPLEX     ZLADIV
      WZLADIV = ZLADIV( X, Y)
      END FUNCTION

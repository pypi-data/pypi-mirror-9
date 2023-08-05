*DCHEX
      SUBROUTINE DCHEX(R,LDR,P,K,L,Z,LDZ,NZ,C,S,JOB)
C***BEGIN PROLOGUE  DCHEX
C***DATE WRITTEN   780814   (YYMMDD)
C***REVISION DATE  820801   (YYMMDD)
C***CATEGORY NO.  D7B
C***KEYWORDS  CHOLESKY DECOMPOSITION,DOUBLE PRECISION,EXCHANGE,
C             LINEAR ALGEBRA,LINPACK,MATRIX,POSITIVE DEFINITE
C***AUTHOR  STEWART, G. W., (U. OF MARYLAND)
C***PURPOSE  UPDATES THE CHOLESKY FACTORIZATION  A=TRANS(R)*R  OF A
C            POSITIVE DEFINITE MATRIX A OF ORDER P UNDER DIAGONAL
C            PERMUTATIONS OF THE FORM  TRANS(E)*A*E  WHERE E IS A
C            PERMUTATION MATRIX.
C***DESCRIPTION
C     DCHEX UPDATES THE CHOLESKY FACTORIZATION
C                   A = TRANS(R)*R
C     OF A POSITIVE DEFINITE MATRIX A OF ORDER P UNDER DIAGONAL
C     PERMUTATIONS OF THE FORM
C                   TRANS(E)*A*E
C     WHERE E IS A PERMUTATION MATRIX.  SPECIFICALLY, GIVEN
C     AN UPPER TRIANGULAR MATRIX R AND A PERMUTATION MATRIX
C     E (WHICH IS SPECIFIED BY K, L, AND JOB), DCHEX DETERMINES
C     AN ORTHOGONAL MATRIX U SUCH THAT
C                           U*R*E = RR,
C     WHERE RR IS UPPER TRIANGULAR.  AT THE USERS OPTION, THE
C     TRANSFORMATION U WILL BE MULTIPLIED INTO THE ARRAY Z.
C     IF A = TRANS(X)*X, SO THAT R IS THE TRIANGULAR PART OF THE
C     QR FACTORIZATION OF X, THEN RR IS THE TRIANGULAR PART OF THE
C     QR FACTORIZATION OF X*E, I.E. X WITH ITS COLUMNS PERMUTED.
C     FOR A LESS TERSE DESCRIPTION OF WHAT DCHEX DOES AND HOW
C     IT MAY BE APPLIED, SEE THE LINPACK GUIDE.
C     THE MATRIX Q IS DETERMINED AS THE PRODUCT U(L-K)*...*U(1)
C     OF PLANE ROTATIONS OF THE FORM
C                           (    C(I)       S(I) )
C                           (                    ) ,
C                           (    -S(I)      C(I) )
C     WHERE C(I) IS DOUBLE PRECISION.  THE ROWS THESE ROTATIONS OPERATE
C     ON ARE DESCRIBED BELOW.
C     THERE ARE TWO TYPES OF PERMUTATIONS, WHICH ARE DETERMINED
C     BY THE VALUE OF JOB.
C     1. RIGHT CIRCULAR SHIFT (JOB = 1).
C         THE COLUMNS ARE REARRANGED IN THE FOLLOWING ORDER.
C                1,...,K-1,L,K,K+1,...,L-1,L+1,...,P.
C         U IS THE PRODUCT OF L-K ROTATIONS U(I), WHERE U(I)
C         ACTS IN THE (L-I,L-I+1)-PLANE.
C     2. LEFT CIRCULAR SHIFT (JOB = 2).
C         THE COLUMNS ARE REARRANGED IN THE FOLLOWING ORDER
C                1,...,K-1,K+1,K+2,...,L,K,L+1,...,P.
C         U IS THE PRODUCT OF L-K ROTATIONS U(I), WHERE U(I)
C         ACTS IN THE (K+I-1,K+I)-PLANE.
C     ON ENTRY
C         R      DOUBLE PRECISION(LDR,P), WHERE LDR .GE. P.
C                R CONTAINS THE UPPER TRIANGULAR FACTOR
C                THAT IS TO BE UPDATED.  ELEMENTS OF R
C                BELOW THE DIAGONAL ARE NOT REFERENCED.
C         LDR    INTEGER.
C                LDR IS THE LEADING DIMENSION OF THE ARRAY R.
C         P      INTEGER.
C                P IS THE ORDER OF THE MATRIX R.
C         K      INTEGER.
C                K IS THE FIRST COLUMN TO BE PERMUTED.
C         L      INTEGER.
C                L IS THE LAST COLUMN TO BE PERMUTED.
C                L MUST BE STRICTLY GREATER THAN K.
C         Z      DOUBLE PRECISION(LDZ,N)Z), WHERE LDZ .GE. P.
C                Z IS AN ARRAY OF NZ P-VECTORS INTO WHICH THE
C                TRANSFORMATION U IS MULTIPLIED.  Z IS
C                NOT REFERENCED IF NZ = 0.
C         LDZ    INTEGER.
C                LDZ IS THE LEADING DIMENSION OF THE ARRAY Z.
C         NZ     INTEGER.
C                NZ IS THE NUMBER OF COLUMNS OF THE MATRIX Z.
C         JOB    INTEGER.
C                JOB DETERMINES THE TYPE OF PERMUTATION.
C                       JOB = 1  RIGHT CIRCULAR SHIFT.
C                       JOB = 2  LEFT CIRCULAR SHIFT.
C     ON RETURN
C         R      CONTAINS THE UPDATED FACTOR.
C         Z      CONTAINS THE UPDATED MATRIX Z.
C         C      DOUBLE PRECISION(P).
C                C CONTAINS THE COSINES OF THE TRANSFORMING ROTATIONS.
C         S      DOUBLE PRECISION(P).
C                S CONTAINS THE SINES OF THE TRANSFORMING ROTATIONS.
C     LINPACK.  THIS VERSION DATED 08/14/78 .
C     G. W. STEWART, UNIVERSITY OF MARYLAND, ARGONNE NATIONAL LAB.
C***REFERENCES  DONGARRA J.J., BUNCH J.R., MOLER C.B., STEWART G.W.,
C                 *LINPACK USERS  GUIDE*, SIAM, 1979.
C***ROUTINES CALLED  DROTG
C***END PROLOGUE  DCHEX

C...SCALAR ARGUMENTS
      INTEGER
     +   JOB,K,L,LDR,LDZ,NZ,P

C...ARRAY ARGUMENTS
      DOUBLE PRECISION
     +   C(*),R(LDR,*),S(*),Z(LDZ,*)

C...LOCAL SCALARS
      DOUBLE PRECISION
     +   T,T1
      INTEGER
     +   I,II,IL,IU,J,JJ,KM1,KP1,LM1,LMK

C...EXTERNAL SUBROUTINES
      EXTERNAL
     +   DROTG

C...INTRINSIC FUNCTIONS
      INTRINSIC
     +   MAX0,MIN0


C***FIRST EXECUTABLE STATEMENT  DCHEX


      KM1 = K - 1
      KP1 = K + 1
      LMK = L - K
      LM1 = L - 1

C     PERFORM THE APPROPRIATE TASK.

      GO TO (10,130), JOB

C     RIGHT CIRCULAR SHIFT.

   10 CONTINUE

C        REORDER THE COLUMNS.

         DO 20 I = 1, L
            II = L - I + 1
            S(I) = R(II,L)
   20    CONTINUE
         DO 40 JJ = K, LM1
            J = LM1 - JJ + K
            DO 30 I = 1, J
               R(I,J+1) = R(I,J)
   30       CONTINUE
            R(J+1,J+1) = 0.0D0
   40    CONTINUE
         IF (K .EQ. 1) GO TO 60
            DO 50 I = 1, KM1
               II = L - I + 1
               R(I,K) = S(II)
   50       CONTINUE
   60    CONTINUE

C        CALCULATE THE ROTATIONS.

         T = S(1)
         DO 70 I = 1, LMK
            T1 = S(I)
            CALL DROTG(S(I+1),T,C(I),T1)
            S(I) = T1
            T = S(I+1)
   70    CONTINUE
         R(K,K) = T
         DO 90 J = KP1, P
            IL = MAX0(1,L-J+1)
            DO 80 II = IL, LMK
               I = L - II
               T = C(II)*R(I,J) + S(II)*R(I+1,J)
               R(I+1,J) = C(II)*R(I+1,J) - S(II)*R(I,J)
               R(I,J) = T
   80       CONTINUE
   90    CONTINUE

C        IF REQUIRED, APPLY THE TRANSFORMATIONS TO Z.

         IF (NZ .LT. 1) GO TO 120
         DO 110 J = 1, NZ
            DO 100 II = 1, LMK
               I = L - II
               T = C(II)*Z(I,J) + S(II)*Z(I+1,J)
               Z(I+1,J) = C(II)*Z(I+1,J) - S(II)*Z(I,J)
               Z(I,J) = T
  100       CONTINUE
  110    CONTINUE
  120    CONTINUE
      GO TO 260

C     LEFT CIRCULAR SHIFT

  130 CONTINUE

C        REORDER THE COLUMNS

         DO 140 I = 1, K
            II = LMK + I
            S(II) = R(I,K)
  140    CONTINUE
         DO 160 J = K, LM1
            DO 150 I = 1, J
               R(I,J) = R(I,J+1)
  150       CONTINUE
            JJ = J - KM1
            S(JJ) = R(J+1,J+1)
  160    CONTINUE
         DO 170 I = 1, K
            II = LMK + I
            R(I,L) = S(II)
  170    CONTINUE
         DO 180 I = KP1, L
            R(I,L) = 0.0D0
  180    CONTINUE

C        REDUCTION LOOP.

         DO 220 J = K, P
            IF (J .EQ. K) GO TO 200

C              APPLY THE ROTATIONS.

               IU = MIN0(J-1,L-1)
               DO 190 I = K, IU
                  II = I - K + 1
                  T = C(II)*R(I,J) + S(II)*R(I+1,J)
                  R(I+1,J) = C(II)*R(I+1,J) - S(II)*R(I,J)
                  R(I,J) = T
  190          CONTINUE
  200       CONTINUE
            IF (J .GE. L) GO TO 210
               JJ = J - K + 1
               T = S(JJ)
               CALL DROTG(R(J,J),T,C(JJ),S(JJ))
  210       CONTINUE
  220    CONTINUE

C        APPLY THE ROTATIONS TO Z.

         IF (NZ .LT. 1) GO TO 250
         DO 240 J = 1, NZ
            DO 230 I = K, LM1
               II = I - KM1
               T = C(II)*Z(I,J) + S(II)*Z(I+1,J)
               Z(I+1,J) = C(II)*Z(I+1,J) - S(II)*Z(I,J)
               Z(I,J) = T
  230       CONTINUE
  240    CONTINUE
  250    CONTINUE
  260 CONTINUE
      RETURN
      END
*DPODI
      SUBROUTINE DPODI(A,LDA,N,DET,JOB)
C***BEGIN PROLOGUE  DPODI
C***DATE WRITTEN   780814   (YYMMDD)
C***REVISION DATE  820801   (YYMMDD)
C***CATEGORY NO.  D2B1B,D3B1B
C***KEYWORDS  DETERMINANT,DOUBLE PRECISION,FACTOR,INVERSE,
C             LINEAR ALGEBRA,LINPACK,MATRIX,POSITIVE DEFINITE
C***AUTHOR  MOLER, C. B., (U. OF NEW MEXICO)
C***PURPOSE  COMPUTES THE DETERMINANT AND INVERSE OF A CERTAIN DOUBLE
C            PRECISION SYMMETRIC POSITIVE DEFINITE MATRIX (SEE ABSTRACT)
C            USING THE FACTORS COMPUTED BY DPOCO, DPOFA OR DQRDC.
C***DESCRIPTION
C     DPODI COMPUTES THE DETERMINANT AND INVERSE OF A CERTAIN
C     DOUBLE PRECISION SYMMETRIC POSITIVE DEFINITE MATRIX (SEE BELOW)
C     USING THE FACTORS COMPUTED BY DPOCO, DPOFA OR DQRDC.
C     ON ENTRY
C        A       DOUBLE PRECISION(LDA, N)
C                THE OUTPUT  A  FROM DPOCO OR DPOFA
C                OR THE OUTPUT  X  FROM DQRDC.
C        LDA     INTEGER
C                THE LEADING DIMENSION OF THE ARRAY  A .
C        N       INTEGER
C                THE ORDER OF THE MATRIX  A .
C        JOB     INTEGER
C                = 11   BOTH DETERMINANT AND INVERSE.
C                = 01   INVERSE ONLY.
C                = 10   DETERMINANT ONLY.
C     ON RETURN
C        A       IF DPOCO OR DPOFA WAS USED TO FACTOR  A , THEN
C                DPODI PRODUCES THE UPPER HALF OF INVERSE(A) .
C                IF DQRDC WAS USED TO DECOMPOSE  X , THEN
C                DPODI PRODUCES THE UPPER HALF OF INVERSE(TRANS(X)*X)
C                WHERE TRANS(X) IS THE TRANSPOSE.
C                ELEMENTS OF  A  BELOW THE DIAGONAL ARE UNCHANGED.
C                IF THE UNITS DIGIT OF JOB IS ZERO,  A  IS UNCHANGED.
C        DET     DOUBLE PRECISION(2)
C                DETERMINANT OF  A  OR OF  TRANS(X)*X  IF REQUESTED.
C                OTHERWISE NOT REFERENCED.
C                DETERMINANT = DET(1) * 10.0**DET(2)
C                WITH  1.0 .LE. DET(1) .LT. 10.0
C                OR  DET(1) .EQ. 0.0 .
C     ERROR CONDITION
C        A DIVISION BY ZERO WILL OCCUR IF THE INPUT FACTOR CONTAINS
C        A ZERO ON THE DIAGONAL AND THE INVERSE IS REQUESTED.
C        IT WILL NOT OCCUR IF THE SUBROUTINES ARE CALLED CORRECTLY
C        AND IF DPOCO OR DPOFA HAS SET INFO .EQ. 0 .
C     LINPACK.  THIS VERSION DATED 08/14/78 .
C     CLEVE MOLER, UNIVERSITY OF NEW MEXICO, ARGONNE NATIONAL LAB.
C***REFERENCES  DONGARRA J.J., BUNCH J.R., MOLER C.B., STEWART G.W.,
C                 *LINPACK USERS  GUIDE*, SIAM, 1979.
C***ROUTINES CALLED  DAXPY,DSCAL
C***END PROLOGUE  DPODI

C...SCALAR ARGUMENTS
      INTEGER JOB,LDA,N

C...ARRAY ARGUMENTS
      DOUBLE PRECISION A(LDA,*),DET(*)

C...LOCAL SCALARS
      DOUBLE PRECISION S,T
      INTEGER I,J,JM1,K,KP1

C...EXTERNAL SUBROUTINES
      EXTERNAL DAXPY,DSCAL

C...INTRINSIC FUNCTIONS
      INTRINSIC MOD


C***FIRST EXECUTABLE STATEMENT  DPODI


      IF (JOB/10 .EQ. 0) GO TO 70
         DET(1) = 1.0D0
         DET(2) = 0.0D0
         S = 10.0D0
         DO 50 I = 1, N
            DET(1) = A(I,I)**2*DET(1)
C        ...EXIT
            IF (DET(1) .EQ. 0.0D0) GO TO 60
   10       IF (DET(1) .GE. 1.0D0) GO TO 20
               DET(1) = S*DET(1)
               DET(2) = DET(2) - 1.0D0
            GO TO 10
   20       CONTINUE
   30       IF (DET(1) .LT. S) GO TO 40
               DET(1) = DET(1)/S
               DET(2) = DET(2) + 1.0D0
            GO TO 30
   40       CONTINUE
   50    CONTINUE
   60    CONTINUE
   70 CONTINUE

C     COMPUTE INVERSE(R)

      IF (MOD(JOB,10) .EQ. 0) GO TO 140
         DO 100 K = 1, N
            A(K,K) = 1.0D0/A(K,K)
            T = -A(K,K)
            CALL DSCAL(K-1,T,A(1,K),1)
            KP1 = K + 1
            IF (N .LT. KP1) GO TO 90
            DO 80 J = KP1, N
               T = A(K,J)
               A(K,J) = 0.0D0
               CALL DAXPY(K,T,A(1,K),1,A(1,J),1)
   80       CONTINUE
   90       CONTINUE
  100    CONTINUE

C        FORM  INVERSE(R) * TRANS(INVERSE(R))

         DO 130 J = 1, N
            JM1 = J - 1
            IF (JM1 .LT. 1) GO TO 120
            DO 110 K = 1, JM1
               T = A(K,J)
               CALL DAXPY(K,T,A(1,J),1,A(1,K),1)
  110       CONTINUE
  120       CONTINUE
            T = A(J,J)
            CALL DSCAL(J,T,A(1,J),1)
  130    CONTINUE
  140 CONTINUE
      RETURN
      END
*DQRDC
      SUBROUTINE DQRDC(X,LDX,N,P,QRAUX,JPVT,WORK,JOB)
C***BEGIN PROLOGUE  DQRDC
C***DATE WRITTEN   780814   (YYMMDD)
C***REVISION DATE  820801   (YYMMDD)
C***CATEGORY NO.  D5
C***KEYWORDS  DECOMPOSITION,DOUBLE PRECISION,LINEAR ALGEBRA,LINPACK,
C             MATRIX,ORTHOGONAL TRIANGULAR
C***AUTHOR  STEWART, G. W., (U. OF MARYLAND)
C***PURPOSE  USES HOUSEHOLDER TRANSFORMATIONS TO COMPUTE THE QR FACTORI-
C            ZATION OF N BY P MATRIX X.  COLUMN PIVOTING IS OPTIONAL.
C***DESCRIPTION
C     DQRDC USES HOUSEHOLDER TRANSFORMATIONS TO COMPUTE THE QR
C     FACTORIZATION OF AN N BY P MATRIX X.  COLUMN PIVOTING
C     BASED ON THE 2-NORMS OF THE REDUCED COLUMNS MAY BE
C     PERFORMED AT THE USER'S OPTION.
C     ON ENTRY
C        X       DOUBLE PRECISION(LDX,P), WHERE LDX .GE. N.
C                X CONTAINS THE MATRIX WHOSE DECOMPOSITION IS TO BE
C                COMPUTED.
C        LDX     INTEGER.
C                LDX IS THE LEADING DIMENSION OF THE ARRAY X.
C        N       INTEGER.
C                N IS THE NUMBER OF ROWS OF THE MATRIX X.
C        P       INTEGER.
C                P IS THE NUMBER OF COLUMNS OF THE MATRIX X.
C        JPVT    INTEGER(P).
C                JPVT CONTAINS INTEGERS THAT CONTROL THE SELECTION
C                OF THE PIVOT COLUMNS.  THE K-TH COLUMN X(K) OF X
C                IS PLACED IN ONE OF THREE CLASSES ACCORDING TO THE
C                VALUE OF JPVT(K).
C                   IF JPVT(K) .GT. 0, THEN X(K) IS AN INITIAL
C                                      COLUMN.
C                   IF JPVT(K) .EQ. 0, THEN X(K) IS A FREE COLUMN.
C                   IF JPVT(K) .LT. 0, THEN X(K) IS A FINAL COLUMN.
C                BEFORE THE DECOMPOSITION IS COMPUTED, INITIAL COLUMNS
C                ARE MOVED TO THE BEGINNING OF THE ARRAY X AND FINAL
C                COLUMNS TO THE END.  BOTH INITIAL AND FINAL COLUMNS
C                ARE FROZEN IN PLACE DURING THE COMPUTATION AND ONLY
C                FREE COLUMNS ARE MOVED.  AT THE K-TH STAGE OF THE
C                REDUCTION, IF X(K) IS OCCUPIED BY A FREE COLUMN
C                IT IS INTERCHANGED WITH THE FREE COLUMN OF LARGEST
C                REDUCED NORM.  JPVT IS NOT REFERENCED IF
C                JOB .EQ. 0.
C        WORK    DOUBLE PRECISION(P).
C                WORK IS A WORK ARRAY.  WORK IS NOT REFERENCED IF
C                JOB .EQ. 0.
C        JOB     INTEGER.
C                JOB IS AN INTEGER THAT INITIATES COLUMN PIVOTING.
C                IF JOB .EQ. 0, NO PIVOTING IS DONE.
C                IF JOB .NE. 0, PIVOTING IS DONE.
C     ON RETURN
C        X       X CONTAINS IN ITS UPPER TRIANGLE THE UPPER
C                TRIANGULAR MATRIX R OF THE QR FACTORIZATION.
C                BELOW ITS DIAGONAL X CONTAINS INFORMATION FROM
C                WHICH THE ORTHOGONAL PART OF THE DECOMPOSITION
C                CAN BE RECOVERED.  NOTE THAT IF PIVOTING HAS
C                BEEN REQUESTED, THE DECOMPOSITION IS NOT THAT
C                OF THE ORIGINAL MATRIX X BUT THAT OF X
C                WITH ITS COLUMNS PERMUTED AS DESCRIBED BY JPVT.
C        QRAUX   DOUBLE PRECISION(P).
C                QRAUX CONTAINS FURTHER INFORMATION REQUIRED TO RECOVER
C                THE ORTHOGONAL PART OF THE DECOMPOSITION.
C        JPVT    JPVT(K) CONTAINS THE INDEX OF THE COLUMN OF THE
C                ORIGINAL MATRIX THAT HAS BEEN INTERCHANGED INTO
C                THE K-TH COLUMN, IF PIVOTING WAS REQUESTED.
C     LINPACK.  THIS VERSION DATED 08/14/78 .
C     G. W. STEWART, UNIVERSITY OF MARYLAND, ARGONNE NATIONAL LAB.
C***REFERENCES  DONGARRA J.J., BUNCH J.R., MOLER C.B., STEWART G.W.,
C                 *LINPACK USERS  GUIDE*, SIAM, 1979.
C***ROUTINES CALLED  DAXPY,DDOT,DNRM2,DSCAL,DSWAP
C***END PROLOGUE  DQRDC

C...SCALAR ARGUMENTS
      INTEGER
     +   JOB,LDX,N,P

C...ARRAY ARGUMENTS
      DOUBLE PRECISION
     +   QRAUX(*),WORK(*),X(LDX,*)
      INTEGER
     +   JPVT(*)

C...LOCAL SCALARS
      DOUBLE PRECISION
     +   MAXNRM,NRMXL,T,TT
      INTEGER
     +   J,JJ,JP,L,LP1,LUP,MAXJ,PL,PU
      LOGICAL
     +   NEGJ,SWAPJ

C...EXTERNAL FUNCTIONS
      DOUBLE PRECISION
     +   DDOT,DNRM2
      EXTERNAL
     +   DDOT,DNRM2

C...EXTERNAL SUBROUTINES
      EXTERNAL
     +   DAXPY,DSCAL,DSWAP

C...INTRINSIC FUNCTIONS
      INTRINSIC
     +   DABS,DMAX1,DSIGN,DSQRT,MIN0


C***FIRST EXECUTABLE STATEMENT  DQRDC


      PL = 1
      PU = 0
      IF (JOB .EQ. 0) GO TO 60

C        PIVOTING HAS BEEN REQUESTED.  REARRANGE THE COLUMNS
C        ACCORDING TO JPVT.

         DO 20 J = 1, P
            SWAPJ = JPVT(J) .GT. 0
            NEGJ = JPVT(J) .LT. 0
            JPVT(J) = J
            IF (NEGJ) JPVT(J) = -J
            IF (.NOT.SWAPJ) GO TO 10
               IF (J .NE. PL) CALL DSWAP(N,X(1,PL),1,X(1,J),1)
               JPVT(J) = JPVT(PL)
               JPVT(PL) = J
               PL = PL + 1
   10       CONTINUE
   20    CONTINUE
         PU = P
         DO 50 JJ = 1, P
            J = P - JJ + 1
            IF (JPVT(J) .GE. 0) GO TO 40
               JPVT(J) = -JPVT(J)
               IF (J .EQ. PU) GO TO 30
                  CALL DSWAP(N,X(1,PU),1,X(1,J),1)
                  JP = JPVT(PU)
                  JPVT(PU) = JPVT(J)
                  JPVT(J) = JP
   30          CONTINUE
               PU = PU - 1
   40       CONTINUE
   50    CONTINUE
   60 CONTINUE

C     COMPUTE THE NORMS OF THE FREE COLUMNS.

      IF (PU .LT. PL) GO TO 80
      DO 70 J = PL, PU
         QRAUX(J) = DNRM2(N,X(1,J),1)
         WORK(J) = QRAUX(J)
   70 CONTINUE
   80 CONTINUE

C     PERFORM THE HOUSEHOLDER REDUCTION OF X.

      LUP = MIN0(N,P)
      DO 200 L = 1, LUP
         IF (L .LT. PL .OR. L .GE. PU) GO TO 120

C           LOCATE THE COLUMN OF LARGEST NORM AND BRING IT
C           INTO THE PIVOT POSITION.

            MAXNRM = 0.0D0
            MAXJ = L
            DO 100 J = L, PU
               IF (QRAUX(J) .LE. MAXNRM) GO TO 90
                  MAXNRM = QRAUX(J)
                  MAXJ = J
   90          CONTINUE
  100       CONTINUE
            IF (MAXJ .EQ. L) GO TO 110
               CALL DSWAP(N,X(1,L),1,X(1,MAXJ),1)
               QRAUX(MAXJ) = QRAUX(L)
               WORK(MAXJ) = WORK(L)
               JP = JPVT(MAXJ)
               JPVT(MAXJ) = JPVT(L)
               JPVT(L) = JP
  110       CONTINUE
  120    CONTINUE
         QRAUX(L) = 0.0D0
         IF (L .EQ. N) GO TO 190

C           COMPUTE THE HOUSEHOLDER TRANSFORMATION FOR COLUMN L.

            NRMXL = DNRM2(N-L+1,X(L,L),1)
            IF (NRMXL .EQ. 0.0D0) GO TO 180
               IF (X(L,L) .NE. 0.0D0) NRMXL = DSIGN(NRMXL,X(L,L))
               CALL DSCAL(N-L+1,1.0D0/NRMXL,X(L,L),1)
               X(L,L) = 1.0D0 + X(L,L)

C              APPLY THE TRANSFORMATION TO THE REMAINING COLUMNS,
C              UPDATING THE NORMS.

               LP1 = L + 1
               IF (P .LT. LP1) GO TO 170
               DO 160 J = LP1, P
                  T = -DDOT(N-L+1,X(L,L),1,X(L,J),1)/X(L,L)
                  CALL DAXPY(N-L+1,T,X(L,L),1,X(L,J),1)
                  IF (J .LT. PL .OR. J .GT. PU) GO TO 150
                  IF (QRAUX(J) .EQ. 0.0D0) GO TO 150
                     TT = 1.0D0 - (DABS(X(L,J))/QRAUX(J))**2
                     TT = DMAX1(TT,0.0D0)
                     T = TT
                     TT = 1.0D0 + 0.05D0*TT*(QRAUX(J)/WORK(J))**2
                     IF (TT .EQ. 1.0D0) GO TO 130
                        QRAUX(J) = QRAUX(J)*DSQRT(T)
                     GO TO 140
  130                CONTINUE
                        QRAUX(J) = DNRM2(N-L,X(L+1,J),1)
                        WORK(J) = QRAUX(J)
  140                CONTINUE
  150             CONTINUE
  160          CONTINUE
  170          CONTINUE

C              SAVE THE TRANSFORMATION.

               QRAUX(L) = X(L,L)
               X(L,L) = -NRMXL
  180       CONTINUE
  190    CONTINUE
  200 CONTINUE
      RETURN
      END
*DQRSL
      SUBROUTINE DQRSL(X,LDX,N,K,QRAUX,Y,QY,QTY,B,RSD,XB,JOB,INFO)
C***BEGIN PROLOGUE  DQRSL
C***DATE WRITTEN   780814   (YYMMDD)
C***REVISION DATE  820801   (YYMMDD)
C***CATEGORY NO.  D9,D2A1
C***KEYWORDS  DOUBLE PRECISION,LINEAR ALGEBRA,LINPACK,MATRIX,
C             ORTHOGONAL TRIANGULAR,SOLVE
C***AUTHOR  STEWART, G. W., (U. OF MARYLAND)
C***PURPOSE  APPLIES THE OUTPUT OF DQRDC TO COMPUTE COORDINATE
C            TRANSFORMATIONS, PROJECTIONS, AND LEAST SQUARES SOLUTIONS.
C***DESCRIPTION
C     DQRSL APPLIES THE OUTPUT OF DQRDC TO COMPUTE COORDINATE
C     TRANSFORMATIONS, PROJECTIONS, AND LEAST SQUARES SOLUTIONS.
C     FOR K .LE. MIN(N,P), LET XK BE THE MATRIX
C            XK = (X(JPVT(1)),X(JPVT(2)), ... ,X(JPVT(K)))
C     FORMED FROM COLUMNNS JPVT(1), ... ,JPVT(K) OF THE ORIGINAL
C     N X P MATRIX X THAT WAS INPUT TO DQRDC (IF NO PIVOTING WAS
C     DONE, XK CONSISTS OF THE FIRST K COLUMNS OF X IN THEIR
C     ORIGINAL ORDER).  DQRDC PRODUCES A FACTORED ORTHOGONAL MATRIX Q
C     AND AN UPPER TRIANGULAR MATRIX R SUCH THAT
C              XK = Q * (R)
C                       (0)
C     THIS INFORMATION IS CONTAINED IN CODED FORM IN THE ARRAYS
C     X AND QRAUX.
C     ON ENTRY
C        X      DOUBLE PRECISION(LDX,P).
C               X CONTAINS THE OUTPUT OF DQRDC.
C        LDX    INTEGER.
C               LDX IS THE LEADING DIMENSION OF THE ARRAY X.
C        N      INTEGER.
C               N IS THE NUMBER OF ROWS OF THE MATRIX XK.  IT MUST
C               HAVE THE SAME VALUE AS N IN DQRDC.
C        K      INTEGER.
C               K IS THE NUMBER OF COLUMNS OF THE MATRIX XK.  K
C               MUST NOT BE GREATER THAN MIN(N,P), WHERE P IS THE
C               SAME AS IN THE CALLING SEQUENCE TO DQRDC.
C        QRAUX  DOUBLE PRECISION(P).
C               QRAUX CONTAINS THE AUXILIARY OUTPUT FROM DQRDC.
C        Y      DOUBLE PRECISION(N)
C               Y CONTAINS AN N-VECTOR THAT IS TO BE MANIPULATED
C               BY DQRSL.
C        JOB    INTEGER.
C               JOB SPECIFIES WHAT IS TO BE COMPUTED.  JOB HAS
C               THE DECIMAL EXPANSION ABCDE, WITH THE FOLLOWING
C               MEANING.
C                    IF A .NE. 0, COMPUTE QY.
C                    IF B,C,D, OR E .NE. 0, COMPUTE QTY.
C                    IF C .NE. 0, COMPUTE B.
C                    IF D .NE. 0, COMPUTE RSD.
C                    IF E .NE. 0, COMPUTE XB.
C               NOTE THAT A REQUEST TO COMPUTE B, RSD, OR XB
C               AUTOMATICALLY TRIGGERS THE COMPUTATION OF QTY, FOR
C               WHICH AN ARRAY MUST BE PROVIDED IN THE CALLING
C               SEQUENCE.
C     ON RETURN
C        QY     DOUBLE PRECISION(N).
C               QY CONTAINS Q*Y, IF ITS COMPUTATION HAS BEEN
C               REQUESTED.
C        QTY    DOUBLE PRECISION(N).
C               QTY CONTAINS TRANS(Q)*Y, IF ITS COMPUTATION HAS
C               BEEN REQUESTED.  HERE TRANS(Q) IS THE
C               TRANSPOSE OF THE MATRIX Q.
C        B      DOUBLE PRECISION(K)
C               B CONTAINS THE SOLUTION OF THE LEAST SQUARES PROBLEM
C                    MINIMIZE NORM2(Y - XK*B),
C               IF ITS COMPUTATION HAS BEEN REQUESTED.  (NOTE THAT
C               IF PIVOTING WAS REQUESTED IN DQRDC, THE J-TH
C               COMPONENT OF B WILL BE ASSOCIATED WITH COLUMN JPVT(J)
C               OF THE ORIGINAL MATRIX X THAT WAS INPUT INTO DQRDC.)
C        RSD    DOUBLE PRECISION(N).
C               RSD CONTAINS THE LEAST SQUARES RESIDUAL Y - XK*B,
C               IF ITS COMPUTATION HAS BEEN REQUESTED.  RSD IS
C               ALSO THE ORTHOGONAL PROJECTION OF Y ONTO THE
C               ORTHOGONAL COMPLEMENT OF THE COLUMN SPACE OF XK.
C        XB     DOUBLE PRECISION(N).
C               XB CONTAINS THE LEAST SQUARES APPROXIMATION XK*B,
C               IF ITS COMPUTATION HAS BEEN REQUESTED.  XB IS ALSO
C               THE ORTHOGONAL PROJECTION OF Y ONTO THE COLUMN SPACE
C               OF X.
C        INFO   INTEGER.
C               INFO IS ZERO UNLESS THE COMPUTATION OF B HAS
C               BEEN REQUESTED AND R IS EXACTLY SINGULAR.  IN
C               THIS CASE, INFO IS THE INDEX OF THE FIRST ZERO
C               DIAGONAL ELEMENT OF R AND B IS LEFT UNALTERED.
C     THE PARAMETERS QY, QTY, B, RSD, AND XB ARE NOT REFERENCED
C     IF THEIR COMPUTATION IS NOT REQUESTED AND IN THIS CASE
C     CAN BE REPLACED BY DUMMY VARIABLES IN THE CALLING PROGRAM.
C     TO SAVE STORAGE, THE USER MAY IN SOME CASES USE THE SAME
C     ARRAY FOR DIFFERENT PARAMETERS IN THE CALLING SEQUENCE.  A
C     FREQUENTLY OCCURING EXAMPLE IS WHEN ONE WISHES TO COMPUTE
C     ANY OF B, RSD, OR XB AND DOES NOT NEED Y OR QTY.  IN THIS
C     CASE ONE MAY IDENTIFY Y, QTY, AND ONE OF B, RSD, OR XB, WHILE
C     PROVIDING SEPARATE ARRAYS FOR ANYTHING ELSE THAT IS TO BE
C     COMPUTED.  THUS THE CALLING SEQUENCE
C          CALL DQRSL(X,LDX,N,K,QRAUX,Y,DUM,Y,B,Y,DUM,110,INFO)
C     WILL RESULT IN THE COMPUTATION OF B AND RSD, WITH RSD
C     OVERWRITING Y.  MORE GENERALLY, EACH ITEM IN THE FOLLOWING
C     LIST CONTAINS GROUPS OF PERMISSIBLE IDENTIFICATIONS FOR
C     A SINGLE CALLING SEQUENCE.
C          1. (Y,QTY,B) (RSD) (XB) (QY)
C          2. (Y,QTY,RSD) (B) (XB) (QY)
C          3. (Y,QTY,XB) (B) (RSD) (QY)
C          4. (Y,QY) (QTY,B) (RSD) (XB)
C          5. (Y,QY) (QTY,RSD) (B) (XB)
C          6. (Y,QY) (QTY,XB) (B) (RSD)
C     IN ANY GROUP THE VALUE RETURNED IN THE ARRAY ALLOCATED TO
C     THE GROUP CORRESPONDS TO THE LAST MEMBER OF THE GROUP.
C     LINPACK.  THIS VERSION DATED 08/14/78 .
C     G. W. STEWART, UNIVERSITY OF MARYLAND, ARGONNE NATIONAL LAB.
C***REFERENCES  DONGARRA J.J., BUNCH J.R., MOLER C.B., STEWART G.W.,
C                 *LINPACK USERS  GUIDE*, SIAM, 1979.
C***ROUTINES CALLED  DAXPY,DCOPY,DDOT
C***END PROLOGUE  DQRSL

C...SCALAR ARGUMENTS
      INTEGER
     +   INFO,JOB,K,LDX,N

C...ARRAY ARGUMENTS
      DOUBLE PRECISION
     +   B(*),QRAUX(*),QTY(*),QY(*),RSD(*),X(LDX,*),XB(*),
     +   Y(*)

C...LOCAL SCALARS
      DOUBLE PRECISION
     +   T,TEMP
      INTEGER
     +   I,J,JJ,JU,KP1
      LOGICAL
     +   CB,CQTY,CQY,CR,CXB

C...EXTERNAL FUNCTIONS
      DOUBLE PRECISION
     +   DDOT
      EXTERNAL
     +   DDOT

C...EXTERNAL SUBROUTINES
      EXTERNAL
     +   DAXPY,DCOPY

C...INTRINSIC FUNCTIONS
      INTRINSIC
     +   MIN0,MOD


C***FIRST EXECUTABLE STATEMENT  DQRSL


      INFO = 0

C     DETERMINE WHAT IS TO BE COMPUTED.

      CQY = JOB/10000 .NE. 0
      CQTY = MOD(JOB,10000) .NE. 0
      CB = MOD(JOB,1000)/100 .NE. 0
      CR = MOD(JOB,100)/10 .NE. 0
      CXB = MOD(JOB,10) .NE. 0
      JU = MIN0(K,N-1)

C     SPECIAL ACTION WHEN N=1.

      IF (JU .NE. 0) GO TO 40
         IF (CQY) QY(1) = Y(1)
         IF (CQTY) QTY(1) = Y(1)
         IF (CXB) XB(1) = Y(1)
         IF (.NOT.CB) GO TO 30
            IF (X(1,1) .NE. 0.0D0) GO TO 10
               INFO = 1
            GO TO 20
   10       CONTINUE
               B(1) = Y(1)/X(1,1)
   20       CONTINUE
   30    CONTINUE
         IF (CR) RSD(1) = 0.0D0
      GO TO 250
   40 CONTINUE

C        SET UP TO COMPUTE QY OR QTY.

         IF (CQY) CALL DCOPY(N,Y,1,QY,1)
         IF (CQTY) CALL DCOPY(N,Y,1,QTY,1)
         IF (.NOT.CQY) GO TO 70

C           COMPUTE QY.

            DO 60 JJ = 1, JU
               J = JU - JJ + 1
               IF (QRAUX(J) .EQ. 0.0D0) GO TO 50
                  TEMP = X(J,J)
                  X(J,J) = QRAUX(J)
                  T = -DDOT(N-J+1,X(J,J),1,QY(J),1)/X(J,J)
                  CALL DAXPY(N-J+1,T,X(J,J),1,QY(J),1)
                  X(J,J) = TEMP
   50          CONTINUE
   60       CONTINUE
   70    CONTINUE
         IF (.NOT.CQTY) GO TO 100

C           COMPUTE TRANS(Q)*Y.

            DO 90 J = 1, JU
               IF (QRAUX(J) .EQ. 0.0D0) GO TO 80
                  TEMP = X(J,J)
                  X(J,J) = QRAUX(J)
                  T = -DDOT(N-J+1,X(J,J),1,QTY(J),1)/X(J,J)
                  CALL DAXPY(N-J+1,T,X(J,J),1,QTY(J),1)
                  X(J,J) = TEMP
   80          CONTINUE
   90       CONTINUE
  100    CONTINUE

C        SET UP TO COMPUTE B, RSD, OR XB.

         IF (CB) CALL DCOPY(K,QTY,1,B,1)
         KP1 = K + 1
         IF (CXB) CALL DCOPY(K,QTY,1,XB,1)
         IF (CR .AND. K .LT. N) CALL DCOPY(N-K,QTY(KP1),1,RSD(KP1),1)
         IF (.NOT.CXB .OR. KP1 .GT. N) GO TO 120
            DO 110 I = KP1, N
               XB(I) = 0.0D0
  110       CONTINUE
  120    CONTINUE
         IF (.NOT.CR) GO TO 140
            DO 130 I = 1, K
               RSD(I) = 0.0D0
  130       CONTINUE
  140    CONTINUE
         IF (.NOT.CB) GO TO 190

C           COMPUTE B.

            DO 170 JJ = 1, K
               J = K - JJ + 1
               IF (X(J,J) .NE. 0.0D0) GO TO 150
                  INFO = J
C           ......EXIT
                  GO TO 180
  150          CONTINUE
               B(J) = B(J)/X(J,J)
               IF (J .EQ. 1) GO TO 160
                  T = -B(J)
                  CALL DAXPY(J-1,T,X(1,J),1,B,1)
  160          CONTINUE
  170       CONTINUE
  180       CONTINUE
  190    CONTINUE
         IF (.NOT.CR .AND. .NOT.CXB) GO TO 240

C           COMPUTE RSD OR XB AS REQUIRED.

            DO 230 JJ = 1, JU
               J = JU - JJ + 1
               IF (QRAUX(J) .EQ. 0.0D0) GO TO 220
                  TEMP = X(J,J)
                  X(J,J) = QRAUX(J)
                  IF (.NOT.CR) GO TO 200
                     T = -DDOT(N-J+1,X(J,J),1,RSD(J),1)/X(J,J)
                     CALL DAXPY(N-J+1,T,X(J,J),1,RSD(J),1)
  200             CONTINUE
                  IF (.NOT.CXB) GO TO 210
                     T = -DDOT(N-J+1,X(J,J),1,XB(J),1)/X(J,J)
                     CALL DAXPY(N-J+1,T,X(J,J),1,XB(J),1)
  210             CONTINUE
                  X(J,J) = TEMP
  220          CONTINUE
  230       CONTINUE
  240    CONTINUE
  250 CONTINUE
      RETURN
      END
*DTRCO
      SUBROUTINE DTRCO(T,LDT,N,RCOND,Z,JOB)
C***BEGIN PROLOGUE  DTRCO
C***DATE WRITTEN   780814   (YYMMDD)
C***REVISION DATE  820801   (YYMMDD)
C***CATEGORY NO.  D2A3
C***KEYWORDS  CONDITION,DOUBLE PRECISION,FACTOR,LINEAR ALGEBRA,LINPACK,
C             MATRIX,TRIANGULAR
C***AUTHOR  MOLER, C. B., (U. OF NEW MEXICO)
C***PURPOSE  ESTIMATES THE CONDITION OF A DOUBLE PRECISION TRIANGULAR
C            MATRIX.
C***DESCRIPTION
C     DTRCO ESTIMATES THE CONDITION OF A DOUBLE PRECISION TRIANGULAR
C     MATRIX.
C     ON ENTRY
C        T       DOUBLE PRECISION(LDT,N)
C                T CONTAINS THE TRIANGULAR MATRIX.  THE ZERO
C                ELEMENTS OF THE MATRIX ARE NOT REFERENCED, AND
C                THE CORRESPONDING ELEMENTS OF THE ARRAY CAN BE
C                USED TO STORE OTHER INFORMATION.
C        LDT     INTEGER
C                LDT IS THE LEADING DIMENSION OF THE ARRAY T.
C        N       INTEGER
C                N IS THE ORDER OF THE SYSTEM.
C        JOB     INTEGER
C                = 0         T  IS LOWER TRIANGULAR.
C                = NONZERO   T  IS UPPER TRIANGULAR.
C     ON RETURN
C        RCOND   DOUBLE PRECISION
C                AN ESTIMATE OF THE RECIPROCAL CONDITION OF  T .
C                FOR THE SYSTEM  T*X = B , RELATIVE PERTURBATIONS
C                IN  T  AND  B  OF SIZE  EPSILON  MAY CAUSE
C                RELATIVE PERTURBATIONS IN  X  OF SIZE  EPSILON/RCOND .
C                IF  RCOND  IS SO SMALL THAT THE LOGICAL EXPRESSION
C                           1.0 + RCOND .EQ. 1.0
C                IS TRUE, THEN  T  MAY BE SINGULAR TO WORKING
C                PRECISION.  IN PARTICULAR,  RCOND  IS ZERO  IF
C                EXACT SINGULARITY IS DETECTED OR THE ESTIMATE
C                UNDERFLOWS.
C        Z       DOUBLE PRECISION(N)
C                A WORK VECTOR WHOSE CONTENTS ARE USUALLY UNIMPORTANT.
C                IF  T  IS CLOSE TO A SINGULAR MATRIX, THEN  Z  IS
C                AN APPROXIMATE NULL VECTOR IN THE SENSE THAT
C                NORM(A*Z) = RCOND*NORM(A)*NORM(Z) .
C     LINPACK.  THIS VERSION DATED 08/14/78 .
C     CLEVE MOLER, UNIVERSITY OF NEW MEXICO, ARGONNE NATIONAL LAB.
C***REFERENCES  DONGARRA J.J., BUNCH J.R., MOLER C.B., STEWART G.W.,
C                 *LINPACK USERS  GUIDE*, SIAM, 1979.
C***ROUTINES CALLED  DASUM,DAXPY,DSCAL
C***END PROLOGUE  DTRCO

C...SCALAR ARGUMENTS
      DOUBLE PRECISION
     +   RCOND
      INTEGER
     +   JOB,LDT,N

C...ARRAY ARGUMENTS
      DOUBLE PRECISION
     +   T(LDT,*),Z(*)

C...LOCAL SCALARS
      DOUBLE PRECISION
     +   EK,S,SM,TNORM,W,WK,WKM,YNORM
      INTEGER
     +   I1,J,J1,J2,K,KK,L
      LOGICAL
     +   LOWER

C...EXTERNAL FUNCTIONS
      DOUBLE PRECISION
     +   DASUM
      EXTERNAL
     +   DASUM

C...EXTERNAL SUBROUTINES
      EXTERNAL
     +   DAXPY,DSCAL

C...INTRINSIC FUNCTIONS
      INTRINSIC
     +   DABS,DMAX1,DSIGN


C***FIRST EXECUTABLE STATEMENT  DTRCO


      LOWER = JOB .EQ. 0

C     COMPUTE 1-NORM OF T

      TNORM = 0.0D0
      DO 10 J = 1, N
         L = J
         IF (LOWER) L = N + 1 - J
         I1 = 1
         IF (LOWER) I1 = J
         TNORM = DMAX1(TNORM,DASUM(L,T(I1,J),1))
   10 CONTINUE

C     RCOND = 1/(NORM(T)*(ESTIMATE OF NORM(INVERSE(T)))) .
C     ESTIMATE = NORM(Z)/NORM(Y) WHERE  T*Z = Y  AND  TRANS(T)*Y = E .
C     TRANS(T)  IS THE TRANSPOSE OF T .
C     THE COMPONENTS OF  E  ARE CHOSEN TO CAUSE MAXIMUM LOCAL
C     GROWTH IN THE ELEMENTS OF Y .
C     THE VECTORS ARE FREQUENTLY RESCALED TO AVOID OVERFLOW.

C     SOLVE TRANS(T)*Y = E

      EK = 1.0D0
      DO 20 J = 1, N
         Z(J) = 0.0D0
   20 CONTINUE
      DO 100 KK = 1, N
         K = KK
         IF (LOWER) K = N + 1 - KK
         IF (Z(K) .NE. 0.0D0) EK = DSIGN(EK,-Z(K))
         IF (DABS(EK-Z(K)) .LE. DABS(T(K,K))) GO TO 30
            S = DABS(T(K,K))/DABS(EK-Z(K))
            CALL DSCAL(N,S,Z,1)
            EK = S*EK
   30    CONTINUE
         WK = EK - Z(K)
         WKM = -EK - Z(K)
         S = DABS(WK)
         SM = DABS(WKM)
         IF (T(K,K) .EQ. 0.0D0) GO TO 40
            WK = WK/T(K,K)
            WKM = WKM/T(K,K)
         GO TO 50
   40    CONTINUE
            WK = 1.0D0
            WKM = 1.0D0
   50    CONTINUE
         IF (KK .EQ. N) GO TO 90
            J1 = K + 1
            IF (LOWER) J1 = 1
            J2 = N
            IF (LOWER) J2 = K - 1
            DO 60 J = J1, J2
               SM = SM + DABS(Z(J)+WKM*T(K,J))
               Z(J) = Z(J) + WK*T(K,J)
               S = S + DABS(Z(J))
   60       CONTINUE
            IF (S .GE. SM) GO TO 80
               W = WKM - WK
               WK = WKM
               DO 70 J = J1, J2
                  Z(J) = Z(J) + W*T(K,J)
   70          CONTINUE
   80       CONTINUE
   90    CONTINUE
         Z(K) = WK
  100 CONTINUE
      S = 1.0D0/DASUM(N,Z,1)
      CALL DSCAL(N,S,Z,1)

      YNORM = 1.0D0

C     SOLVE T*Z = Y

      DO 130 KK = 1, N
         K = N + 1 - KK
         IF (LOWER) K = KK
         IF (DABS(Z(K)) .LE. DABS(T(K,K))) GO TO 110
            S = DABS(T(K,K))/DABS(Z(K))
            CALL DSCAL(N,S,Z,1)
            YNORM = S*YNORM
  110    CONTINUE
         IF (T(K,K) .NE. 0.0D0) Z(K) = Z(K)/T(K,K)
         IF (T(K,K) .EQ. 0.0D0) Z(K) = 1.0D0
         I1 = 1
         IF (LOWER) I1 = K + 1
         IF (KK .GE. N) GO TO 120
            W = -Z(K)
            CALL DAXPY(N-KK,W,T(I1,K),1,Z(I1),1)
  120    CONTINUE
  130 CONTINUE
C     MAKE ZNORM = 1.0
      S = 1.0D0/DASUM(N,Z,1)
      CALL DSCAL(N,S,Z,1)
      YNORM = S*YNORM

      IF (TNORM .NE. 0.0D0) RCOND = YNORM/TNORM
      IF (TNORM .EQ. 0.0D0) RCOND = 0.0D0
      RETURN
      END
*DTRSL
      SUBROUTINE DTRSL(T,LDT,N,B,JOB,INFO)
C***BEGIN PROLOGUE  DTRSL
C***DATE WRITTEN   780814   (YYMMDD)
C***REVISION DATE  820801   (YYMMDD)
C***CATEGORY NO.  D2A3
C***KEYWORDS  DOUBLE PRECISION,LINEAR ALGEBRA,LINPACK,MATRIX,SOLVE,
C             TRIANGULAR
C***AUTHOR  STEWART, G. W., (U. OF MARYLAND)
C***PURPOSE  SOLVES SYSTEMS OF THE FORM  T*X=B OR  TRANS(T)*X=B  WHERE T
C            IS A TRIANGULAR MATRIX OF ORDER N.
C***DESCRIPTION
C     DTRSL SOLVES SYSTEMS OF THE FORM
C                   T * X = B
C     OR
C                   TRANS(T) * X = B
C     WHERE T IS A TRIANGULAR MATRIX OF ORDER N.  HERE TRANS(T)
C     DENOTES THE TRANSPOSE OF THE MATRIX T.
C     ON ENTRY
C         T         DOUBLE PRECISION(LDT,N)
C                   T CONTAINS THE MATRIX OF THE SYSTEM.  THE ZERO
C                   ELEMENTS OF THE MATRIX ARE NOT REFERENCED, AND
C                   THE CORRESPONDING ELEMENTS OF THE ARRAY CAN BE
C                   USED TO STORE OTHER INFORMATION.
C         LDT       INTEGER
C                   LDT IS THE LEADING DIMENSION OF THE ARRAY T.
C         N         INTEGER
C                   N IS THE ORDER OF THE SYSTEM.
C         B         DOUBLE PRECISION(N).
C                   B CONTAINS THE RIGHT HAND SIDE OF THE SYSTEM.
C         JOB       INTEGER
C                   JOB SPECIFIES WHAT KIND OF SYSTEM IS TO BE SOLVED.
C                   IF JOB IS
C                        00   SOLVE T*X=B, T LOWER TRIANGULAR,
C                        01   SOLVE T*X=B, T UPPER TRIANGULAR,
C                        10   SOLVE TRANS(T)*X=B, T LOWER TRIANGULAR,
C                        11   SOLVE TRANS(T)*X=B, T UPPER TRIANGULAR.
C     ON RETURN
C         B         B CONTAINS THE SOLUTION, IF INFO .EQ. 0.
C                   OTHERWISE B IS UNALTERED.
C         INFO      INTEGER
C                   INFO CONTAINS ZERO IF THE SYSTEM IS NONSINGULAR.
C                   OTHERWISE INFO CONTAINS THE INDEX OF
C                   THE FIRST ZERO DIAGONAL ELEMENT OF T.
C     LINPACK.  THIS VERSION DATED 08/14/78 .
C     G. W. STEWART, UNIVERSITY OF MARYLAND, ARGONNE NATIONAL LAB.
C***REFERENCES  DONGARRA J.J., BUNCH J.R., MOLER C.B., STEWART G.W.,
C                 *LINPACK USERS  GUIDE*, SIAM, 1979.
C***ROUTINES CALLED  DAXPY,DDOT
C***END PROLOGUE  DTRSL

C...SCALAR ARGUMENTS
      INTEGER
     +   INFO,JOB,LDT,N

C...ARRAY ARGUMENTS
      DOUBLE PRECISION
     +   B(*),T(LDT,*)

C...LOCAL SCALARS
      DOUBLE PRECISION
     +   TEMP
      INTEGER
     +   CASE,J,JJ

C...EXTERNAL FUNCTIONS
      DOUBLE PRECISION
     +   DDOT
      EXTERNAL
     +   DDOT

C...EXTERNAL SUBROUTINES
      EXTERNAL
     +   DAXPY

C...INTRINSIC FUNCTIONS
      INTRINSIC
     +   MOD


C***FIRST EXECUTABLE STATEMENT  DTRSL


C     BEGIN BLOCK PERMITTING ...EXITS TO 150

C        CHECK FOR ZERO DIAGONAL ELEMENTS.

         DO 10 INFO = 1, N
C     ......EXIT
            IF (T(INFO,INFO) .EQ. 0.0D0) GO TO 150
   10    CONTINUE
         INFO = 0

C        DETERMINE THE TASK AND GO TO IT.

         CASE = 1
         IF (MOD(JOB,10) .NE. 0) CASE = 2
         IF (MOD(JOB,100)/10 .NE. 0) CASE = CASE + 2
         GO TO (20,50,80,110), CASE

C        SOLVE T*X=B FOR T LOWER TRIANGULAR

   20    CONTINUE
            B(1) = B(1)/T(1,1)
            IF (N .LT. 2) GO TO 40
            DO 30 J = 2, N
               TEMP = -B(J-1)
               CALL DAXPY(N-J+1,TEMP,T(J,J-1),1,B(J),1)
               B(J) = B(J)/T(J,J)
   30       CONTINUE
   40       CONTINUE
         GO TO 140

C        SOLVE T*X=B FOR T UPPER TRIANGULAR.

   50    CONTINUE
            B(N) = B(N)/T(N,N)
            IF (N .LT. 2) GO TO 70
            DO 60 JJ = 2, N
               J = N - JJ + 1
               TEMP = -B(J+1)
               CALL DAXPY(J,TEMP,T(1,J+1),1,B(1),1)
               B(J) = B(J)/T(J,J)
   60       CONTINUE
   70       CONTINUE
         GO TO 140

C        SOLVE TRANS(T)*X=B FOR T LOWER TRIANGULAR.

   80    CONTINUE
            B(N) = B(N)/T(N,N)
            IF (N .LT. 2) GO TO 100
            DO 90 JJ = 2, N
               J = N - JJ + 1
               B(J) = B(J) - DDOT(JJ-1,T(J+1,J),1,B(J+1),1)
               B(J) = B(J)/T(J,J)
   90       CONTINUE
  100       CONTINUE
         GO TO 140

C        SOLVE TRANS(T)*X=B FOR T UPPER TRIANGULAR.

  110    CONTINUE
            B(1) = B(1)/T(1,1)
            IF (N .LT. 2) GO TO 130
            DO 120 J = 2, N
               B(J) = B(J) - DDOT(J-1,T(1,J),1,B(1),1)
               B(J) = B(J)/T(J,J)
  120       CONTINUE
  130       CONTINUE
  140    CONTINUE
  150 CONTINUE
      RETURN
      END

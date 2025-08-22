# Translated Document


<!-- p002_c01 page 2 -->
# Week 1
## What is PDE?

### Analysis
- Algebra
- Geometry
- Calculculus

(IABDE, 140 ABC, 3D)

## Pot Analysis = PDE

PDE = Partial Differential Equation

ODE = Ordinary Differential Equations and its derivatives

## What is ODE?

-
An equation contains unknown function(s) of 1-variable.

x + 2x + 3 = 52X
f(x) + si f(x) = 5 (Not MODE)


<!-- p003_c01 page 3 -->
# Partial Differential Equations (PDEs)

## Definition of PDE

A partial differential equation is an equation that contains unknown functions and their partial derivatives.

## Example of a First-Order PDE

A first-order PDE can be written as:

E(X, Y, u(x, y), ux(x, y), uy(x, y)) = 0

or equivalently:

F(X, Y, U, Ux, Uy) = 0


<!-- p004_c01 page 4 -->
# Examples of PDEs
## 1. Transport Equation
- U is a function of (x, y)
- Ux + My = 0

## 2. Transport Equation
- Ux + YUy = 0

## 3. Shock Wave Equation
- Ux + UHy = 0

## 4. Laplace Equation
Table: 
| Term | Description |
| --- | --- |
| xx | Second partial derivative with respect to x |
| yy | Second partial derivative with respect to y |

## 5. Wave Equation / Interactor
- (xx + Hyy) = 0

## 6. Dispensive Equation
- Ut + UUx + Uxx = 0

## 7. Vibration Bar
- UH + Nxx = 0

## 8. Parabolic Equation (Quantum Mechanics)
- U - FU = O


<!-- p005_c01 page 5 -->
# Linear and Nonlinear Equations

## In linear algebra, T: V → W is called a linear transformation if:

- `T(u + v) = T(u) + T(v)`
- `T(au) = aT(u)`
- `T(au + bv) = aT(u) + bT(v)`

## Definition

An operator L is called linear, differential if:

`L(au) = a f(x)`

## Example: 0² = ?

`L(u)= ∂²u/∂x² = ∂²u/∂y²`
`(m) = 0`
`Ux + YUy = 0`
: Transport equation.

## A linear PDE is written as:

`2n = f(x)`
`Ax = b`


<!-- p006_c01 page 6 -->
# Linear Equations
## Homogeneous and Non-Homogeneous Systems

- **Homo**: Lu = 0, Ax = 0
- **Non-Homo**: Qu = 0, Ax = b

## General and Particular Solutions

- U = Ug + Us
- X = Xg + Xs

### Definitions

- **Ug** is a general solution of Lu = 0.
- **Us** is a special solution of Ax = b.
- **Xy** is a generax=o solution ( unclear, possibly typo).
- **Xs** is a special solution of Ax = b.

## Proposition

Let U, U , ... Un be solutions of Lu = 0. Then:

u() = (U + U + ... + Un) is also a solution of Lu = 0.


<!-- p007_c01 page 7 -->
# Using cost t
## 2X1
### A
(a , . An)

- clerest obel
x()
= f(t)
x(t)
=( f(t)d+
+ C
u()
= 0
,
x() = G
u"(+) =0
,

## Example 1
Table: (none)

- 2(f)
=
C , + + Cr

### Uxx
=0
.
(x
, y) = 0
* (ux) =0.
ux
= F(y)
(x
, y)
= F(Y)
u(x , y)
= X F(y)
+ G())


<!-- p008_c01 page 8 -->
# Example 2.

## Equation of motion

- UxX + U = 0
- u"+ u = 0

## Solution for u(x, y)

Table: Coefficients C1 and C2

| Term | Coefficient |
| --- | --- |
| cosxX | C1(y) |
| sinxX | C2(y) |

u(x, y) = C1(y)cosxX + C2(y)sinxX

## Boundary condition

- u(X, y) = 0

# Example 3.

## Equation of motion

- Uxy = 0
- uxx(x) = 0
- ux = F(X)

## Solution for u

u = ∫[F(X)]dx + H(x) + G(y)


<!-- p009_c01 page 9 -->
# List of Calculus Facts that are useful
## 1. Partial derivatives are local.

## 2. Uxy = Kyx.
### Chain rules:
#### (f(g(X . +1)) = f'(g(x, +). (x. +)
#### fgx special case of chain rule.

## 3. Assume f = f(4, %2 , ..., Yn) and Yi = gi(X , , ..., Xk) in most general form & of chain rule.

## 4. Green's formula:
Table: 
| Formula | Description |
| --- | --- |
| ∂+ ) = f(x)2) | (later) · 1 |

## 5.
- I(t) = (bH): f(x,+)dX · b
alt)
I'(t) = f(b(t), +). b'(t) - f(a(t),+)a(t)


<!-- p010_c01 page 10 -->
# 6
## Jacobian
### F : IR" - > R
#### (later)
##### where
F = (F1, ..., Fm)

# 7
## Infinite Series
#### (later)

# 8
## Directional Derivative
#### (geometry)
u(X, Y) = ∂U/∂x * u + ∂U/∂y * v as the directional derivative in direction.
 
# 9
## Familiar with Math 3D


<!-- p011_c01 page 11 -->
# Example. 1
## Transport Equations
### Method 1: (Geometry) / Gradient of u
#### Equation for the line is:
L = bx - ay = c
#### Solution is LED x(x, y) = F(bx - ay)
#### Check:
Hx = F' - b
My = F + a
aUx + buy = aFb + b · F(a) = 0

## Method 2: Change of Variable
### Let
- x = ax + by
- y = bx - ay


<!-- p012_c01 page 12 -->
# Glossary:
{}
 
# Equations
ux = Hy
- a
+ Hyb
=
allx
+ buy
My = uyb
+
Hy ( - a) = buy
- any
0 =
alx
+ buy = (a
+
+b)Ux
=
Hx)
= 0
x =
F(y)
=
F(bx - ay)

## Example 2.
Ux +yuy
= 0

It is linear
2 =
+ y52u
= 0 .

(
,y)
. (Ux
, uy) = 0

s
I -
(1 , %)
-
-
-
y = +
y = ceY


<!-- p013_c01 page 13 -->
# Along the Curve
## Equation of Motion

- *(u(x, E_x + x) = 0)*
- *u(x, y + c) = U_{10}(2y - E_x)*
- *F(x) = F(y - E_x)*
- *F(bx - ay)*


<!-- p014_c01 page 14 -->
# Review
## Example
### Equation Analysis

- allx + buy = 0
- a+b"70 
- if we consider the equation:
  y = Hx + My
  y = ux + My = 0
  u(x, x + c) = u(0, c)
  u(X ,y) = u(0 , C)
  = U(0 , y -tax)
  = F(y - Ex)
  = G(ay - bx)
  = H(bx- ay)


<!-- p015_c01 page 15 -->
# Example
2.

## Equation
ux + y Hy = 0.

## Consider
y' = - 
= Y
y =
ce"
=
c
=ye
(x, ce)
=
Ux + Hy(e"
= ux
+yuy
=0.
u(X, (e) = u(0 , C)
= u(0, ye)
= F(ye
Y)

## Example ?
In the previous example,
if 
in addition ,
210 , y) =
3.

## Solution
Then what is the solution ?

### Solution
u(x ,y) = F(ye
y= u(0
.y)
=
F(y)


<!-- p016_c01 page 16 -->
# Solution
## u(x,y) = F(ye)
u(x,y) = (ye-x)^3

## The mark : How egizy.
### ① Integrating factor
(e^(y)) = e^(-(y'-y)) = 0 .

### ② General solution
f(y) = X + C
fen
X + C
1y1
=
e
y
=
=
e
* + 6
= - e^(-ex)

## Missing solution
Y = 0 .
= y
=
c , e^X


<!-- p017_c01 page 17 -->
# Example 4.
## Equation:
Ux + 2xUy = 0.

### Solution :
y =
xy = zxyz
x = zxy^2
=
2xdx (Missing: y = 0)

- T = x + c
y = -CER
One more
y = 0
U(X . - )
=
caust
=>
u(0, -5)
y =
-
x
+ c =
- t
=>
c =
-t
-x
u(x,y)
=
u(0,
-j)
=
u(0,
x)
=
x^10,
y
= F(y)


<!-- p018_c01 page 18 -->
# 1. Equation
1 + xy = 0.

## Implicit Definition of y
y = -

## Function u(X, y) Notation
The function u(X, y) is NOT defined on the curve y = -x.

## Area I
At s &,

## General Case
In general, if a(x, y)(x + b(x, y)/ky = 0.

## ODE: Implicit Differentiation
The ODE:
y = Y(x)
is implicitly defined by the equation U(X, y) = 0.
u(x, y(x)) = 0
y = -ux + vy = 0.

## Equivalent Equation
This is equivalent to S Nx + y = 0.

## Alternative Notation
y = dis a(x-Y)


<!-- p019_c01 page 19 -->
# Ex7 of Section 1.2
## a. Solve YUx + Xy = 0, x(0,y) = g
### -6 In which region of IP is the solution uniquely determined?

- Solution: y' = y/x = yy = x + c. yx = 2C
- Rewrite: y - y = C

#### If C = 0,
y = x*

#### If so, then y^2 - x = 1

#### If co, the solution is:
y = -y = -1

#### If so, 
y = In U(x) = ulo, It) = e


<!-- p020_c01 page 20 -->
# Mathematical Physical Equations
## a, b, c
### Eqs
- Wave equations
  ①
- Heat equations (parabolic)
  Eg.1
- Laplace equations (elliptic)
  Eg.2


<!-- p021_c01 page 21 -->
# Chapter 2
## Wave and Diffusion

### 32.1 The wave equation.

Assume $U = xe^{It} , X)$, $U_t = U_{xx}$,
- $<X (@$ + > 0 .

**Theorem**

The general solutions of $U(X , t)$ are
$u(X , t) = f(X + v(t)) + g(x - v(t))$,
where $f$ and $g$ are arbitrary functions.

**Proof:**
$U_t = U_x \cdot v'(t) = 0$
- $H^+ + cU_x = V$
-
$(2v'(t))^2 + (u_{xx}) = U_{tt} + 24x$
= $(u_{xt} + u_{tx}) + ((x)^2)$
= $U_{xx} + 24xx$
If
$V = n^+ \# (U_x E V^+$,
- $CV_x = 0$
-->
$v(x,t) = h(x - 2t)$


<!-- p022_c01 page 22 -->
# General Solution of Homogeneous Equation
## Step 1: Find general solution of the homogeneous equation
- H+ + (Ux = 0
u = g(X - (t)

## Step 2: Find a particular solution
Assume u(x, t) = f(x + ct)
- Ht = cf'(X + c + )
ux = f'(x)
u+ + (ux = x f(x+ xt)
= h(x+ ct)
f(x) = ∫[h(x)dx
U = g(x - f) + f(x+ (t)x

## General Solution of Wave Equation
Alternatively, we can solve the equation by changing of variables.
We let:
- 3 = x + xt
- y = x - c

## Transformation of Variables
Ut = M(y) + H(y)(Ug-Un)
= My c + Hy(-


<!-- p023_c01 page 23 -->
# Glossary:
{} 

# Equations:

- Ug = Use + Us = cluss-Usu 
- Un = Ug + Ung = c(Ugy - Unn) 
- UH = 2(Ues + Ung) - 2cUgy 
- Ux = 4 + Yy 
- uxx = Ugg + Uny + 213 
- 0 = uH - inx = -45Ugy => KeyO 
. 

# Functions:

## ThUg()
= fixtc + gla
UH-cUxx = 0 -<XA 
? 

## u(X,o) = f(x)
uf(x , 0) = 4 (X

## Solution:
u(x , +) = f(x + (t)) + g(X - c)

## Let t = 0
& (x) = u(x ,0) = f(x) + f(x)

## U+ (x, +)
= c f'(x + (t)) - cg(x - (t))


<!-- p024_c01 page 24 -->
# D'Alembert's Formula
## Step 1: Define the problem
4(x) = (+ (x + 0) = c f(x) - 38'(x)

## Step 2: Integrate by parts
[(y()dx = f(x) - g(x)
f + y = 4
f
-g = + (4(x)dx

## Step 3: Apply the formula
f = &(k + t(y(x)dx)
g = (d - t(4(x)dx)

## Step 4: Rewrite the solution
Rewrite f(x) = za(x) + So
"4151ds
g(x) = 1P(x) - E.
"415ds

## Step 5: Apply the formula to u(x)
u(x+) = f(x + (H) + g(X - (t))

## Step 6: Simplify the expression
((d(x + (t)) + q(X - Ct)) + et()

***


## Step 7: Integrate by parts again
y1sIds = ((d(x + (t)) + q(X - Ct)) + y(s)ds

**D'Alembert's Formula**

Note: I've kept the original formatting and structure cues, including the use of Markdown headers and emphasis.


<!-- p025_c01 page 25 -->
# Assume that U is a function of XIR, where U = UIX . +
## The wave equation is given by HH - cUxx = 0.

### The general solution is given by u(X ,+) = f(x + ct) + g(x - c)

#### For the initial value problem
- UH-Uxx = 0
- x(x, 0) = 4(X)
- (+ (x , 0) = Y(X)

## Then we have the d'Alembert formula
u(x ,+) = z(f(x+ 2) + q(x - c +)) * +Ct + (x-c 4(s)ds


<!-- p026_c01 page 26 -->
# Example 1
## Assume
&\left( x \right) = 0
.
↑\left( x \right) =
cosX .
Then
u(X,+) =
24\left( 8 \right)ds
= c cos t
=
i
\int_{ - \infty }^{\infty} \left[ \sin \left( x + \left( f \right) \right) - \sin \left( x - \left( + \right) \right) \right] dx
= \frac{1}{Sin}
os
+ cos X Sict
- sin cos +
cos X Sicts
=
-
cosx Sin +
## Example
### The Plucked String
## Assume
4\left( x \right) = 0 b -
Nk
ko\left( x \right)
= 1
g
\left( x179
u\left( x, + \right)
= E\left[ d\left( x + \left( t \right) + q\left( x - c + \right) \right) \right]


<!-- p027_c01 page 27 -->
# X
,
picture P(X)
*
## Example
3
/Ex
11) .

## Find
the general solution of
3 UH + 10(x+ + 3(xx= Sin(x+ +
)

## Solution .
The linear operator
2 3 + 3
So
the equation
can be written as
2u
= sm(X+ + )
.

## To find
a special
solution
, we
assume
x(x,+)
= ( , Sm(x+ +
)
+G
+ +
)


<!-- p028_c01 page 28 -->
# General Solutions of Lu = 0
## Equation UH-Uxx = 0
### Particular Case: 3UH + 10Ux+ + 3Uxx = 0
- 2 3 ++ 3
I =
-
= Is +)(
+ 3
·
)
Let v = 
(3
+ 2)u
= 0
30+
+ Ux
= 0
.
v = f(3x - t)
#
+ + 34y
= v
= f (3x - +)
u =
g(3t - x)
+
H(3x - +)


<!-- p029_c01 page 29 -->
# 32. Causality and Energy
## Equation
TUxx = 0

### Constants
f, T
o

### Assumption
c = E

## Kinetic Energy
Emr > KE = Study = Udy
= If UEdx
= (fui)dx
= p(u+ u+ dx)
=
u+ uxx dx
= +ju
+ dux
= TT
ux
=
- T(UxUx + dX


<!-- p030_c01 page 30 -->
# Potential Energy
= (i) dx
=
- (i)uydx
Potential energy: 
Then (IE + PE)
= o
Define the
mechanical energy
to be
ITE + PE
Then
we have
the
-Mechanical
energy conservation
a
fUH
- TUxx = 0
&
u(o) =
q(x) = b
&
U+ (x, 0) = 0
E = ∫(2)(yup + TUx)dx


<!-- p031_c01 page 31 -->
# Equation Set
- T(ux) = o
- I + (d(x)/dx)b = <Xa>4(x) = 2b + t - as XO12 aOocXC P(x) = L - a < X0 IXI) aO2b2(kdx = 2 -
- u(x+) = (d(X+ (t)) + ((x - c+))
- E(f) = KE + PE
- I (i+ux]dx


<!-- p032_c01 page 32 -->
# Ut
= z(k'(x + c+) - k'(x - (t)).

## JuF
= ((k'(x + c+) - q'(x - c+))dX.

## Jux
= ((d'(x + c+) + q'(x+c))dx).

## E(t)
= (((d'(x +c+)) + (4'(x - cy))dx) = ((k'(x +CH)a - > c) ((x -())dX) & 1 '(x+ c+) dxH(, &'(y) dy = (i) dx.

## ECH
= 2c(d( dy - A).


<!-- p033_c01 page 33 -->
# The Diffusion Equation
## Cheat equation
### I. Ut = RUxx
#### U(X, t)

is a function on the rectangular domain [0,e] x To.

**Maximum Principle**

Theorem: The maximum value of u (x,t) can only be reached on lines where:

- (x,t) / ∂t = 0, for 0 ≤ x ≤ e
- (x,t) = 0, at the boundary x = 0 or x = e

**Strong Maximum Principle**

Theorem: The maximum value of u(x,t) is attained inside the domain.

**Weak Maximum Principle**

Theorem: max U(x,t) = max U(x,0).


<!-- p034_c01 page 34 -->
# Proof
## What if at 10.% in the interior of IR that reaches the maximum value of UIX .+) Then⑭ (o , Yo) = Ux(X0 , Y.) = 0. ② .

### Hessian Matrix
- **Uxx** and **UH**: incompositive definite -
- Which is equivalent to ⑭so, UH 0 at (Xo . Yo) ⑥.
- **Uxx**UH - U70. u+ = kkxx 0 = H+ 10, yo) = R(xx(X0 ,%)

## If U(o , Yo) o · We get a contradictor

### Let v(X.t) =
- u(X+) + 2x2
↳ u+= Rux = RVxx - 2kE
Vxx = Uxx + 25


<!-- p035_c01 page 35 -->
# Assume
(Xo . Yo) ERR is an interior point such that I reaches maximum.
Then 
Ut (X0, %. ) = 0
Uxx (o , %o) = 10 ·
Contradiction: 0 =
V+ 10%) = RVxx-2k25-26s0 .
Max Vixit) = max Next

Let (X0 , i) be the maximum point of vi.
Hence, Eu-ut = 20 .
v(x,+)
= u(X,+ ) +2
L
U (x .+)
=
v (X , +)
- EX
=>
Max u(x, +) < Max U(x.+)
R
R
= Max v(x. t)
Max VIX,t) - Max Ut +
3


<!-- p036_c01 page 36 -->
# Maxu(X,f)

## < Maxu(X,f) + SeR

Let 2 + 0. = Max Uf Max UIx

### Uniqueness of the Diffusion Equation.

#### Theorem

Consider Ut = RUxx ? u(x,0) = f(x)
#
u(0 .+) = g(t),
u (l .+)= h(t)

Then the solution is unique.
proof
:
Let U1 and U2 be the two solutions.
Let 2 (Xit) = U1 (X.+ ) - U2 (X,+)
-
x+ = kUxx ? u(X,0) =
0
u(0 , H) = 0,
u(l,+) =0

Max U = Max u =

Moreover,
- 1 also solves the above equation
Max(u) -
0.
=
U = O R


<!-- p037_c01 page 37 -->
# Uniqueness Theorem for Wave Equation
## Mathematical Formulation
- cUxx = 0 (wave equation)
- Initial conditions:
  - u(X, 0) = 0
  - U+(X,0) = 0
- Energy functional E(f):
  Table: Energy Functional Components
  | Component | Description |
  | --- | --- |
  | ESU | Kinetic energy term |
  | iUxo | Potential energy term |
  | o | Constant factor |
- Energy at t=0:
  - E(0) = 0
- Time derivative of energy:
  - Ut = 0
- Spatial derivatives:
  - UXEo 
- Energy conservation:
  - EU(X,+) = const

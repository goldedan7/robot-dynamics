# P3 — Derivation Notes: 2-DOF Arm Dynamics

Working notes on how the equations of motion `M(θ)θ̈ + C(θ,θ̇)θ̇ + G(θ) = τ`
were derived, and what each term physically means. Written so I (or anyone
else) can reconstruct the reasoning without re-deriving from scratch.

---

## 1. Setup

Two links, point masses at the end of each:

theta1 = shoulder angle (from horizontal)
theta2 = elbow angle (relative to link 1)

x1 = L1 cos(theta1)              y1 = L1 sin(theta1)
x2 = x1 + L2 cos(theta1+theta2)  y2 = y1 + L2 sin(theta1+theta2)

This is exactly the P2 forward-kinematics result — dynamics is built
directly on top of it.

---

## 2. Mass matrix M(θ) — where it comes from

**Goal:** find the kinetic energy T, because M is just T's coefficients.

### Velocities

For point 1: v1^2 = L1^2 * theta1_dot^2 (using sin^2+cos^2=1)

For point 2, after differentiating and squaring:
v2^2 = L1^2*th1d^2 + L2^2*(th1d+th2d)^2 + 2*L1*L2*th1d*(th1d+th2d)*cos(theta2)

The cos(theta2) comes from cos(A-B) = cosA cosB + sinA sinB applied to
the cross term. theta1 cancels entirely — only theta2 (elbow bend)
survives. Matches intuition: rotating the whole arm rigidly doesn't
change how "spread out" its mass is; only the elbow angle does.

### Kinetic energy

T = 0.5*m1*v1^2 + 0.5*m2*v2^2

Collecting terms by theta1_dot^2, theta1_dot*theta2_dot, theta2_dot^2:

m11 = (m1+m2)*L1^2 + m2*L2^2 + 2*m2*L1*L2*cos(theta2)
m12 = m2*L2^2 + m2*L1*L2*cos(theta2)
m22 = m2*L2^2

Sanity checked numerically:
theta2=0° (extended)  -> m11 = 3.592
theta2=180° (folded)  -> m11 = 1.032

A fully extended arm has more inertia than a folded one — same reason a
figure skater spins faster with arms pulled in.

m11, m22 (diagonal) = each joint's own inertia.
m12 (off-diagonal) = coupling — extra energy that only appears when
both joints move simultaneously.

---

## 3. Coriolis/centrifugal term C(θ,θ̇)

Source: Euler-Lagrange requires d/dt(∂L/∂θ̇). Since M depends on theta2,
differentiating M(θ)θ̇ pulls in a chain-rule term dM/dt * θ̇. Since
d/dtheta2[cos(theta2)] = -sin(theta2), C is proportional to sin(theta2)
times products/squares of angular velocities:

C1 = -m2*L1*L2*sin(theta2)*(2*omega1*omega2 + omega2^2)
C2 =  m2*L1*L2*sin(theta2)*omega1^2

Physical meaning: analogous to the rotating-merry-go-round example — an
effect that only appears when something moves along a rotating frame
while the frame itself is changing. Here "the frame changing" = the
arm's inertia changing as theta2 varies.

Key insight — C vanishes in two distinct situations:
1. omega1 = omega2 = 0 (not moving) — needs motion.
2. sin(theta2) = 0, i.e. fully extended or fully folded — because these
   are exactly where m11(theta2) is at a max/min, so its instantaneous
   rate of change is zero, even if the arm is moving fast.

Verified numerically:
A stationary (90°, 0,0)        -> [0, 0]
B extended+moving (0°, 5,3)    -> [0, 0]
C bent+moving (90°, 5,3)       -> [-24.96, 16.0]
D folded+moving (180°, 5,3)    -> [0, 0] (fp error only)

---

## 4. Why this matters beyond the derivation

- W3 gate (energy conservation): if C or M is wrong, simulated total
  energy (T+V) drifts instead of staying constant at zero torque/damping.
  This is the real test of whether the derivation is correct.
- P4 (computed torque, later): the controller must cancel these M/C/G
  terms. Getting C wrong here means getting that controller wrong later.

---

## 5. Tools used

sin^2(x)+cos^2(x)=1        -> simplifying v1^2, v2^2
cos(A-B)=cosAcosB+sinAsinB -> collapsing cross term to cos(theta2)

Verified symbolically with sympy (Euler-Lagrange on L=T-V) to confirm
hand-derived M, C match the automated result.

---

## 6. Gravity term G(θ) — TBD
(To be added once implemented.)

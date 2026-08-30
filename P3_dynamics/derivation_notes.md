markdown
# P3 — 2-DOF Arm Dynamics: Derivation

Deriving `M(θ)θ̈ + C(θ,θ̇)θ̇ + G(θ) = τ` for a planar two-link arm with
point masses at the end of each link.

Lagrangian rather than Newton: with two links the inter-link reaction
forces have to be tracked explicitly in a Newtonian treatment, which is
where sign errors originate. Lagrangian needs only two scalars, T and V.

**Notation.** θ₁ shoulder angle from horizontal, θ₂ elbow angle relative
to link 1. ωᵢ = θ̇ᵢ. Masses m₁, m₂ at the link ends; lengths L₁, L₂.

---

## 1. Kinematics (from P2)

x₁ = L₁cos θ₁ y₁ = L₁sin θ₁
x₂ = x₁ + L₂cos(θ₁+θ₂) y₂ = y₁ + L₂sin(θ₁+θ₂)


---

## 2. Kinetic energy → M(θ)

Differentiate, square, sum. Two identities close the algebra:
`sin²+cos² = 1`, and `cos(A−B) = cosA cosB + sinA sinB` for the cross
term.

v₁² = L₁²ω₁²
v₂² = L₁²ω₁² + L₂²(ω₁+ω₂)² + 2L₁L₂ω₁(ω₁+ω₂)cos θ₂


**θ₁ cancels identically.** Rigid rotation of the whole arm does not
change its mass distribution; only θ₂ does. Hence M = M(θ₂) only.

`T = ½m₁v₁² + ½m₂v₂²`, collected by ω₁², ω₁ω₂, ω₂²:

m₁₁ = (m₁+m₂)L₁² + m₂L₂² + 2m₂L₁L₂cos θ₂
m₁₂ = m₂L₂² + m₂L₁L₂cos θ₂ (= m₂₁, symmetric)
m₂₂ = m₂L₂²


so that `T = ½ ωᵀM(θ₂)ω`.

M is nothing more than the coefficient array of T. Diagonal = each
joint's own inertia; off-diagonal m₁₂ = coupling, the energy term
existing only when both joints move simultaneously.

**Verification**

| θ₂ | m₁₁ |
|---|---|
| 0° (extended) | 3.592 |
| 180° (folded) | 1.032 |

Ratio ≈ 3.5. Consistent with conservation of angular momentum intuition
(skater pulling arms in).

---

## 3. Coriolis / centrifugal → C(θ,θ̇)

Euler–Lagrange requires `d/dt(∂L/∂ω)`. Since M = M(θ₂):

d/dt(Mω) = Mθ̈ + (dM/dt)ω
└── origin of C


`d/dθ₂[cos θ₂] = −sin θ₂`, so every term carries sin θ₂:

C₁ = −m₂L₁L₂ sin θ₂ (2ω₁ω₂ + ω₂²)
C₂ = m₂L₁L₂ sin θ₂ ω₁²


⚠️ `coriolis_forces()` returns the product **C·θ̇**, already evaluated —
not the C matrix. Subtract directly in the EOM; multiplying by θ̇ again
double-counts.

**C = 0 in two independent cases**

1. ω₁ = ω₂ = 0 — every term is a product or square of velocities.
2. sin θ₂ = 0, i.e. θ₂ ∈ {0°, 180°} — **irrespective of speed.**

Case 2 follows from the origin of C: m₁₁(θ₂) is stationary (max at 0°,
min at 180°), so dm₁₁/dθ₂ = 0 there. C came from dM/dt; no rate of
change of inertia ⇒ no Coriolis contribution.

| θ₂ | (ω₁, ω₂) | C |
|---|---|---|
| 90° | (0, 0) | [0, 0] |
| 0° | (5, 3) | [0, 0] |
| 90° | (5, 3) | [−24.96, 16.0] |
| 180° | (5, 3) | [0, 0] |

---

## 4. Potential energy → G(θ)

V contains no velocities, so G = ∂V/∂θ is a single differentiation.

V = m₁gL₁sin θ₁ + m₂g(L₁sin θ₁ + L₂sin(θ₁+θ₂))

G₁ = (m₁+m₂)gL₁cos θ₁ + m₂gL₂cos(θ₁+θ₂)
G₂ = m₂gL₂cos(θ₁+θ₂)


| (θ₁, θ₂) | G |
|---|---|
| (0°, 0°) horizontal | [23.94, 6.28] — maximum |
| (90°, 0°) vertical | [≈0, ≈0] |

**G is a generalised torque, not a force.** At θ₁ = 90° gravity acts
along the link, collinear with the position vector from the axis ⇒ zero
moment arm. The force is unchanged; only its rotational component
vanishes. This is the unstable equilibrium.

⚠️ Initialising at `[90°, 0°, 0, 0]` gives G = 0 and ω = 0 ⇒ θ̈ = 0 for
all t. The arm never moves. Not a bug. Initialise away from equilibrium
(horizontal gives maximum gravity torque).

---

## 5. State-space form

θ̈ = M⁻¹(τ − C − G)

x = [θ₁, θ₂, ω₁, ω₂]
ẋ = [ω₁, ω₂, θ̈₁, θ̈₂]


The first two components of ẋ are definitional (dθ/dt ≡ ω) and are read
straight from x; only θ̈ requires solving the dynamics. Structurally
identical to P1's `[dtheta, domega]`, doubled.

⚠️ `M⁻¹` = `np.linalg.inv(M)`. `M**(-1)` is an elementwise reciprocal —
a different matrix, and it raises no error.

---

## 6. Validation: energy conservation

The only objective test of the derivation. With τ = 0 and zero damping,
`E = T + V` must be constant.

T = ½ ωᵀM(θ₂)ω
V = m₁gy₁ + m₂gy₂


Initial run showed E climbing monotonically from 0 to ≈0.13 J over 5 s.
Re-running the identical equations with a tightened integrator:

| Integrator setting | ΔE over 5 s |
|---|---|
| `solve_ivp` defaults | ≈ 1.3 × 10⁻¹ J |
| `rtol=1e-10, atol=1e-12` | ≈ 1 × 10⁻⁹ J |

**The derivation was correct; the default tolerance was not.** Default
tolerances target speed, not conservation. P1 never exposed this — a
single pendulum accumulates error slowly. The two-link system is
nonlinear and coupled, so local truncation error compounds far faster.

⇒ Any conserved-quantity check requires explicitly tightened rtol/atol.

Residual drift at 10⁻⁹ J is floating-point noise. **M, C, G confirmed.**

---

## 7. Damping

Viscous joint friction, opposing each joint's own velocity — the
two-joint extension of P1's `−bω`:

friction = b·[ω₁, ω₂]
θ̈ = M⁻¹(τ − C − G − friction)


Settling timescale scales as inertia/damping. With m₁₁ ≈ 3.6 and
b = 0.5 this is ≈ 7 s, so a 10 s window spans under two time constants —
amplitude visibly decays but no settled pose. Either extend the window
(≈20 s) or raise b to 1.2–2.0; the latter was used to obtain a clear
final configuration.

Settles at θ₁ ≈ −90°, θ₂ ≈ 0° — hanging vertically downward, the stable
equilibrium, antipodal to §4's unstable one.

## 7a. Undamped animation — wide swing is correct, not a bug

With more snapshots (~100), the undamped (damping=0) animation shows
theta1 swinging across a wide range (~+6° to ~−185°) rather than
settling. This is expected: with no damping, energy has nowhere to go,
so the arm never stops — it keeps swinging indefinitely. Fewer
snapshots (8) can misleadingly look like it settles, simply because it
happened to be caught mid-swing near vertical at t=5s.

---

## 8. Solver invocation

```python
solve_ivp(
    arm_dynamics_damped,     # returns state derivative
    t_span,                  # (t0, tf)
    initial_state,           # [θ₁, θ₂, ω₁, ω₂] at t0
    t_eval=t_eval_d,
    method='RK45',
    args=(torque, damping),  # order must match signature
    rtol=1e-10, atol=1e-12,  # see ## 6
)
```

`solve_ivp` supplies `(t, state)` only. Remaining parameters pass through
`args` **in signature order** — transposing them runs silently with
torque and damping exchanged.

---

## Notes to self

- Trajectory plots look plausible with or without a sign error; a
  chaotic-looking response reveals nothing. Energy conservation is the
  only diagnostic that discriminates.
- When conservation fails, rule out numerics before re-deriving. Nearly
  re-derived M over an integrator setting.
- Every trig identity used reduced to just two: `sin²+cos²=1` and
  `cos(A−B)`. If an expansion isn't collapsing, one of those two is
  probably the missing step.

# P4 - PID on the inverted pendulum

## Setup
Pendulum held at the upright position (θ = 180°), starting from 170°, with a
constant disturbance torque d = 2.0. Controller:

    torque = Kp·e + Ki·∫e dt + Kd·(−ω),   e = target − θ

The integral is carried as a third state, d(error_integral)/dt = error.

## What each term did in simulation
- **P only:** no energy is removed, so the pendulum oscillates at about 20°
  forever.
- **+D:** damping. Less overshoot, but too much D slows the settling.
- **+I:** removes the steady-state error caused by the constant disturbance,
  at the price of extra overshoot. In steady state I = −d/Ki.

## Linearisation and the characteristic equation
Near the top, let θ = π + φ. Then sin(π + φ) ≈ −φ, so

    φ̈ = (g/L)φ + τ + d

Gravity acts as a *destabilising* spring of stiffness g/L = 9.81 (L = 1 m).
This is why Kp has to exceed g/L before the controller does anything useful.
Substituting the PID torque and differentiating once more (the constant d
drops out, which is why I-action removes its effect):

    s³ + Kd·s² + (Kp − g/L)·s + Ki = 0

I checked this against the Jacobian of the full nonlinear system at the
upright point: the eigenvalues match, e.g. for (30, 10, 10) both give
−7.479, −1.762, −0.759.

## Poles and time constant
A pole s = a + jb contributes e^(at). The pole with the largest real part
(closest to zero) decays slowest and dominates the response. Time constant
τ = 1/|a|; after 1τ, 2τ, 3τ, 4τ about 37%, 14%, 5%, 2% remains.
For (30, 10, 10) the slow pole is −0.759, so τ ≈ 1.3 s and ≈ 5 s to settle
inside a 2% band (simulation: 6.5 s). A rough check, s ≈ −Ki/(Kp − g/L),
gives the right order of magnitude and shows why raising Ki speeds up the
removal of the disturbance.

## Routh–Hurwitz
Builds a table from the coefficients and counts sign changes in the first
column; each change is one root in the right half-plane.

    s³ | 1                       Kp − g/L
    s² | Kd                      Ki
    s¹ | (Kd(Kp − g/L) − Ki)/Kd  0
    s⁰ | Ki

Stable iff  Kd > 0,  Kp > g/L,  Ki > 0,  **Ki < Kd·(Kp − g/L)**.

| gains (Kp, Ki, Kd) | s¹ entry | sign changes | result |
|---|---|---|---|
| (30, 10, 10) | +19.19 | 0 | stable |
| (10, 10, 5)  | −1.81  | 2 | unstable, roots 0.159 ± 1.362j |
| (100, 150, 20) | +82.7 | 0 | stable |

If the whole s¹ row is zero there are roots on the imaginary axis. The
auxiliary polynomial from the s² row gives them: Kd·s² + Ki = 0, so
ω = √(Ki/Kd) = √(Kp − g/L). Example: Kp = 50, Kd = 4 → Ki_crit = 160.76,
ω = 6.34 rad/s; Kd = 8 doubles the limit to 321.5 but ω stays the same.

**The stability limit depends on the other gains.** Ki_crit = 201.9 only holds
for Kp = 30, Kd = 10. At Kp = 100, Kd = 20 it is 20 × 90.19 ≈ 1804, so
Ki = 150 is comfortably stable there.

## Grid search
Cost = 1.0·overshoot + 1.0·settling time + 20·|steady-state error|.
Settling = last time |θ − 180°| exceeds 0.2°.

    Kp ∈ {10, 30, 60, 100}, Ki ∈ {0, 10, …, 80, 100, 150}, Kd ∈ {2, 5, 10, 20}
    (176 combinations)

Best five (all Kp = 100, Kd = 20):

| cost | Ki | overshoot | settling |
|---|---|---|---|
| 4.762 | 150 | 3.0° | 1.74 s |
| 5.013 | 100 | 2.5° | 2.50 s |
| 5.331 | 80 | 2.3° | 3.04 s |
| 5.586 | 70 | 2.2° | 3.41 s |
| 5.937 | 60 | 2.1° | 3.88 s |

Worst three are all Kp = 10, Kd = 2 (Ki = 80, 100, 150), cost 10¹²–10¹⁷:
unstable, the oscillation grows exponentially.

## Limitations I found
- The winners sit on the **edge of the grid** (Kp = 100, Kd = 20), so the
  true optimum is outside it. Higher gains keep lowering the cost.
- The cost has **no torque term**: (1000, 500, 100) scores 2.94 but needs a
  peak torque of about 175 against about 17 for (100, 150, 20). A real motor
  could not deliver that.
- Tuning one gain at a time is misleading, because the gains interact
  through the stability condition above.
- Next: add a torque/saturation term to the cost. Choosing that trade-off
  between error and effort is exactly what LQR's Q and R formalise.

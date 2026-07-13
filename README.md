# Robot Dynamics & Control → Design Optimisation

A learning journey toward Physical AI: single pendulum → robot-arm
dynamics → control → design optimisation → co-design capstone.

## Project spine

| #  | Project             | Topic                           | Status         |
|----|----------------------|----------------------------------|----------------|
| P1 | Pendulum             | Dynamics foundations             | ✅ Complete     |
| P2 | 2-DOF robot arm       | Lagrangian dynamics + FK         | Planned        |
| P3 | Control (PID)         | Stabilisation                    | Planned        |
| P4 | Design optimisation   | ML surrogate + Bayesian opt.     | Planned        |
| P5 | Capstone               | Co-design (structure + control)  | Planned        |

## P1 — Pendulum dynamics simulation

### Goal
Build intuition for the core idea behind all robot dynamics:
**state-space representation `[θ, ω]`** integrated forward in time.

### Key points
- Nonlinear pendulum: `θ'' = -(g/L)·sin(θ) − b·ω`
- The phase portrait shows the trajectory spiralling to equilibrium.
- The damping coefficient `b` governs how quickly energy dissipates.

### Files
- `P1_pendulum/pendulum_dynamics.py` — simulation module

### Usage
```python
from pendulum_dynamics import simulate, plot_results
t, theta, omega = simulate(theta0_deg=60, damping=0.3)
plot_results(t, theta, omega)
```

## Next steps
- [ ] P2: 2-DOF robot arm dynamics (Lagrangian mechanics)
- [ ] P3: PID control for stabilisation

---
**Route:** Bristol Mechanical Engineering '25 → toward Physical AI

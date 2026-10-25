# From Pendulums to Physical AI

I'm a Mechanical Engineering graduate (Bristol '24), currently completing military service in South Korea. This repo documents my self-study route toward Physical AI — robots that act in the real world — building from classical dynamics and control up to modern robot learning.

Each project builds on the last. I write up what I learned as I go, partly so I remember it, partly in case someone walking a similar path finds it useful.

## The through-line

A robot arm is really just several pendulums connected by joints. So I started with the simplest possible dynamical system — one pendulum — and I'm scaling up along a deliberate arc:

**understand the physics → control it with theory → control it with learning.**

The point isn't to collect topics. It's to end up able to derive a Lagrangian *and* train a policy. Either skill on its own is common; the combination is rarer than either, and it's where a mechanical background stops being a gap and becomes an edge.

## Project spine

| # | Project | What it's really about | Status |
|---|---------|------------------------|--------|
| P1 | Pendulum | The core idea behind all dynamics: state + time | ✅ Done |
| P2 | 2-DOF arm — kinematics | Geometry: where is the hand? | ✅ Done |
| P3 | 2-DOF arm — dynamics | Physics: torque, gravity, Lagrangian | ✅ Done |
| P4 | Model-based control | PID vs LQR vs computed-torque | 🔄 In progress |
| P5 | Learning-based control ⭐ | The same problem, solved with RL — and compared | Planned |

**Beyond** (realistically post-discharge, mid-2027): manipulation in simulation, then a flagship project on design–control co-optimisation. Sketched at the end — deliberately, since I haven't earned the right to specify them yet.

---

## P1 — Pendulum: the first building block

**The question:** how do you simulate something that moves according to physics, on a computer?

The trick that unlocked everything is representing motion as a **state**: `[angle, angular velocity]`. Instead of solving for "where is the pendulum at t = 20 s" directly — which is hard — you ask a much easier question: *given where it is right now, where will it be a tiny instant later?* Then you repeat that question thousands of times. That's what `scipy.solve_ivp` is doing under the hood.

The most useful plot from this project wasn't angle-vs-time. It was the **phase portrait** (angle vs angular velocity). Watching the trajectory spiral into the origin as damping dissipates energy made the abstract idea of "state" suddenly feel physical.

If I were telling someone starting out one thing: don't skip the phase portrait, even when the time-series plot feels like enough. Seeing the state as a *point moving through space* is the idea everything else in robot dynamics is built on — and it's the picture I come back to in P4 and P5, where the goal shifts from letting the pendulum settle naturally to forcing it to a chosen point.

📁 `P1_pendulum/` — simulation code plus a notebook comparing undamped orbits, slow spirals, and fast spirals.

## P2 — 2-DOF arm: from one pendulum to a real arm

**The question:** if an arm is just two connected pendulums, how do I compute where its hand ends up?

I split this in two on purpose.

**Forward kinematics** — given joint angles, where's the hand? Pure geometry, chained trigonometry, no physics yet. I wanted to be comfortable with *where things are* before touching *how they move*.

**Inverse kinematics** — I want the hand *here*; what angles do I need? This is the direction that matters on a real robot, since you're rarely handed the joint angles you want — you're handed a target. I solved it analytically with the law of cosines on the triangle formed by shoulder, elbow and target, then verified every solution by feeding it back through forward kinematics to confirm the arm actually lands where it was asked to.

The detail I found most instructive was the failure case. When the target is out of reach, the function returns `None` rather than a plausible-looking wrong answer. That mirrors how real robot software has to behave: a robot should never quietly move toward a physically impossible command. Getting the maths right was the easy half; deciding what the code does when the maths has no answer was the half that taught me something.

📁 `P2_robot_arm/` — forward and inverse kinematics, numerically verified and visualised.

---

## P3 — 2-DOF robot arm dynamics

**The question:** if a robot arm is just two connected pendulums, how
does it actually move when gravity (and eventually a motor) acts on it?

I derived the equations of motion `M(θ)θ̈ + C(θ,θ̇)θ̇ + G(θ) = τ` using
Lagrangian mechanics rather than Newton's laws — with two links, tracking
inter-link reaction forces by hand is exactly where sign errors creep in.
Lagrangian only needs two scalars (kinetic and potential energy) and the
force equations fall out automatically.

**The real test, and where I got stuck:** trajectory plots for a
nonlinear, coupled system like this look plausible whether or not the
underlying algebra is right — you can't eyeball a sign error out of a
chaotic-looking swing. So the actual validation was energy conservation:
with zero torque and zero damping, total energy has to stay exactly
constant. My first attempt showed energy climbing steadily instead of
holding flat. Rather than assuming the derivation was wrong, I isolated
the cause to the ODE solver's default tolerance — tightening it
(`rtol=1e-10, atol=1e-12`) dropped the drift from ~0.13 J to ~1e-9 J
(floating-point noise). The physics was right the whole time; the solver
settings weren't.

One more thing that initially looked like a bug and wasn't: starting the
arm pointing straight up produced a simulation that never moved at all.
That's correct — straight up is an unstable equilibrium where gravity's
torque is exactly zero (it pulls along the link, not around it), so
nothing sets the arm in motion without a nudge.

📁 [`P3_dynamics/`](P3_dynamics/) — mass/Coriolis/gravity derivation,
simulation (undamped + damped), and the full derivation writeup in
[`derivation_notes.md`](P3_dynamics/derivation_notes.md)

## P4 — Model-based control (in progress)

The question: once I can simulate the physics, how do I make it do what I want, and how can I tell whether a controller will work before I run it?

Part 1: PID on an inverted pendulum ✅

Before touching the arm I went back to the single pendulum and tried to hold it upside down, starting 10° off, then again with a constant disturbance torque pushing on it. I added the three terms one at a time so I could see what each one actually does.

P alone never settles. Above a certain gain it stops the pendulum falling, but it swings ±10° forever. P adds a spring, not a brake, so nothing removes the energy. The gain it has to beat is g/L: at the top, gravity behaves like a spring pushing the pendulum away, and the controller has to overpower that before it does anything useful. D is the brake; the oscillation dies within a few seconds. Add a constant disturbance and PD still settles, but 5.67° away from the target.

Where I got it wrong: I predicted that offset as −d/Kp = −3.8°. The simulation gave +5.67°, wrong size and wrong sign. My first instinct was that the small-angle approximation had broken down. It hadn't. I'd left gravity out of the balance, and at the top gravity pushes the same way as the disturbance. With it back in, d/(Kp − g/L) gives 5.676°, within 0.004° of the simulation. I then removes the offset completely, and the integral settles at exactly the value needed to cancel the disturbance (−d/Ki, predicted −0.4, measured −0.398).

Tuning, and why intuition wasn't enough. I scored every gain combination on overshoot, settling time and steady-state error, and searched a grid of 176 combinations. Two things surprised me. The best gains kept landing on the edge of whatever grid I chose. And Ki = 150 turned out to be perfectly stable at high Kp and Kd, even though I'd calculated that the limit was about 200 at lower gains. Working out the characteristic equation and applying the Routh–Hurwitz criterion explained it: the stability limit is Ki < Kd(Kp − g/L), so it moves with the other two gains. I then checked Routh against all 176 simulations. They agreed on 165. Every one of the other 11 had its slowest pole within 0.25 of the imaginary axis, so it was growing or decaying too slowly for a 20-second simulation to decide. Simulation tells you what happened; the analysis tells you what will happen.

What PID couldn't tell me. The winners sit on the grid edge because my cost function never charged for torque: bigger gains always looked better. (1000, 500, 100) scores better than my best result but needs ten times the peak torque, which no real motor would give. Deciding how much error is worth how much effort is exactly what LQR formalises, so it's next on the list once computed torque is done.

📁 P4_control/ — notebook with P → PD → PID, the grid search, Routh vs simulation and a stability map; full writeup in derivation_notes.md
## P5 — Learning-based control ⭐ *(planned)*

The hinge of this repo. I take a problem I've already solved with theory and solve it again with reinforcement learning, then put the two side by side:

> When does a learned policy beat the LQR controller, and when does the theory win?

That comparison is the point. Running an RL tutorial is easy; saying precisely how a learned policy relates to an optimal control law you derived by hand is not.

## Beyond

Once the above is done, the natural next steps are manipulation in simulation (a Franka arm in MuJoCo, with domain randomisation for robustness) and then a flagship project treating the arm's **physical design and its controller as things to optimise jointly** — asking what structure makes a robot best-controllable, rather than accepting the structure and tuning around it.

That question is the one my background actually equips me to ask, which is why it's the destination. I'm deliberately not specifying it further until P5 is finished.

---

## About this route

I'm building toward work at the intersection of robot dynamics and control, mechanical design, and robot learning — engineers who can reason about how a robot *should* move, what structure makes that movement possible, and how modern learning methods fit in.

Everything here is done in whatever time military service leaves over, which constrains the pace but has been useful discipline about what actually matters.

**Background:** BEng Mechanical Engineering, University of Bristol ('25) · currently completing national service in South Korea.

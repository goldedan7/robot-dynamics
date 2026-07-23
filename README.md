# From Pendulums to Robot Arms: My Path to Physical AI

I'm a Mechanical Engineering graduate (Bristol '25) currently serving in
the Korean military. This repo is where I document my self-study route
toward Physical AI — combining robot dynamics/control with design
optimisation. Each project builds on the last, and I write up what I
learned along the way, partly so I remember it, partly so someone else
walking a similar path might find it useful.

**Why this order?** A robot arm is really just several pendulums
connected by joints. So I started with the simplest possible dynamical
system — one pendulum — before scaling up to a full arm, then control,
then design optimisation. Skipping the pendulum and jumping straight to
"robot arm" would have meant copying formulas without understanding them.

## Project spine

| # | Project | What it's really about | Status |
|---|---|---|---|
| P1 | Pendulum | The core idea behind *all* dynamics: state + time | ✅ Done |
| P2 | 2-DOF robot arm | Geometry first (kinematics), motion later (dynamics) | 🔄 In progress |
| P3 | PID control | Making the arm go where I actually want it to | Planned |
| P4 | Design optimisation | Which arm structure performs best? (ML as a tool) | Planned |
| P5 | Capstone | Structure + control designed together | Planned |

---

## P1 — Pendulum: the first building block

**The question I wanted to answer:** how do you even simulate something
that moves according to physics, on a computer?

The trick that unlocked everything is representing motion as a
**state**: `[angle, angular velocity]`. Instead of solving for "where is
the pendulum at t=20s" directly (which is hard), you ask a much easier
question — "given where it is *right now*, where will it be a tiny
instant later?" — and repeat that question thousands of times. That's
what `scipy.solve_ivp` does under the hood.

The most useful plot from this project wasn't the angle-vs-time graph —
it was the **phase portrait** (angle vs angular velocity). Watching the
trajectory spiral into the origin as damping dissipates energy made the
abstract idea of "state" suddenly feel physical. This is a picture I'll
come back to in P3, where the goal shifts from "let the pendulum settle
naturally" to "use a motor to force it to a chosen point."

**What I'd tell someone starting this:** don't skip visualising the
phase portrait, even if the time-series plot feels like "enough." Seeing
the state as a point moving through space is the idea that everything
else in robot dynamics is built on.

📁 [`P1_pendulum/`](P1_pendulum/) — simulation code + notebook with
damping experiments (undamped orbit vs. slow spiral vs. fast spiral)

---

## P2 — 2-DOF robot arm: from one pendulum to a real arm

**The question:** if a robot arm is just two connected pendulums, how do
I compute where its hand actually ends up?

I split this into two halves on purpose:

**1. Forward kinematics** — "given joint angles, where's the hand?"
This is pure geometry (chained trigonometry), no physics yet. I wanted
to get comfortable with *where things are* before tackling *how they
move*.

**2. Inverse kinematics** — "I want the hand *here* — what angles do I
need?" This is the direction that actually matters for a real robot
(you're rarely told the joint angles you want; you're told a target to
reach). I solved it analytically using the law of cosines on the
triangle formed by the shoulder, elbow, and target — and then verified
every solution by feeding it back through forward kinematics to confirm
the arm actually lands on the target it was asked to reach.

One detail I found genuinely important: **what happens when the target
is out of reach?** Rather than silently returning a wrong answer, the
function returns `None` — an explicit "no solution exists" signal. This
mirrors how real robot software has to behave: a robot should never
quietly move toward a physically impossible command.

📁 [`P2_robot_arm/`](P2_robot_arm/) — forward + inverse kinematics,
verified numerically and visualised

---

## What's next

- **P2 (dynamics half):** add torque and gravity so the arm actually
  *moves*, not just poses statically — using Lagrangian mechanics.
- **P3:** PID control to stabilise the arm at a target — the unstable
  equilibrium (arm held upright against gravity) is the classic hard
  case.
- **P4:** treat the arm's physical design (link lengths, etc.) as
  something to optimise, using an ML surrogate model instead of brute
  force search.

## About this route

I'm building toward roles at the intersection of robot dynamics/control
and hardware design — the people who understand both "how should this
robot move" and "what structure makes that movement possible" are rare,
and that's exactly where a mechanical engineering background is an
asset rather than a gap.

**Background:** BEng Mechanical Engineering, University of Bristol
('25) · Currently completing military service in South Korea

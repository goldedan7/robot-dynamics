# From Pendulums to Physical AI

I'm a Mechanical Engineering graduate (Bristol '25) currently serving in
the Korean military. This repo is where I document my self-study route
toward **Physical AI** — robots that act in the real world — building from
classical dynamics and control up to modern robot learning. Each project
builds on the last, and I write up what I learned along the way, partly so
I remember it, partly so someone else walking a similar path might find it
useful.

**The through-line.** A robot arm is really just several pendulums
connected by joints. So I started with the simplest possible dynamical
system — one pendulum — and I'm scaling up along a deliberate arc:

> *understand the physics → control it with theory → control it with
> learning → do a real manipulation task.*

The point isn't to collect topics. It's to become the rare kind of
engineer who can **derive a Lagrangian and train a policy** — someone who
understands both *how a robot should move* and *what makes that movement
possible*. Most ML people can't do the dynamics; most mechanical engineers
can't train the policy. That intersection is exactly where a mechanical
background stops being a gap and becomes an edge.

## Project spine

| # | Project | What it's really about | Status |
|---|---------|------------------------|--------|
| P1 | Pendulum | The core idea behind *all* dynamics: state + time | ✅ Done |
| P2 | 2-DOF arm — kinematics | Geometry: where is the hand? | ✅ Done |
| P2b | 2-DOF arm — dynamics | Physics: torque, gravity, Lagrangian | 🔄 Next |
| P3 | Model-based control | PID vs **LQR** vs computed-torque | Planned |
| P4 | **Learning-based control** ⭐ | Same problem, solved with RL — and compared | Planned |
| P5 | Manipulation in simulation | Reaching/grasping in MuJoCo, robustness | Planned |
| P6 | **Flagship** 🏆 | A full modern robot-learning pipeline | Planned |

**P4 is the hinge of the whole repo** — the moment the "control theory"
half meets the "AI" half. **P6 is the centerpiece** everything else exists
to earn the right to attempt.

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
come back to in P3 and P4, where the goal shifts from "let the pendulum
settle naturally" to "*force* it to a chosen point" — first with a
control law, then with a learned policy.

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

## The road ahead

Everything above is the classical foundation — solid, but it's still
"mechanical engineer who can code." The projects below are where this
turns into a **Physical AI** portfolio. Here's the plan, and *why each
step is where it is.*

### P2b — 2-DOF arm dynamics *(next up)*

Kinematics told me *where* the arm is; dynamics tells me *how it moves*
when torque and gravity act on it. I'll derive the equations of motion
with **Lagrangian mechanics** (kinetic minus potential energy) rather
than chasing forces directly — it scales far better to multi-joint
systems. The deliverable: given joint torques, simulate the arm actually
swinging, the same way P1 simulated the pendulum. This is the model I
need before any controller has something to control.

### P3 — Model-based control: PID vs LQR vs computed-torque

Most people stop at "I wrote a PID controller." I want to go further and
show I understand *why* one controller beats another:

- **PID** — the honest baseline; simple, model-free, surprisingly hard to
  tune well.
- **LQR** — derived from the linearised dynamics; the bridge between
  "control theory" and "optimisation," since it *minimises a cost*.
- **Computed-torque** — uses the P2b dynamics model directly to cancel
  the nonlinearities.

The interesting test case is the **unstable equilibrium** — holding the
arm upright against gravity — where a lazy controller falls over and a
good one doesn't. This project is where I prove the control-theory half
of the story.

### P4 — Learning-based control: the same problem, solved by RL ⭐

**This is the hinge of the entire repo.** I take a problem I already
solved with theory — pendulum swing-up / cart-pole balance — and solve it
*again* with **reinforcement learning** (PPO / SAC), then put the two
side by side:

> *When does the learned policy beat the LQR controller, and when does
> the theory win? What does each actually understand about the system?*

That comparison is the whole point. Anyone can run an RL tutorial; far
fewer can say precisely how the learned policy relates to the optimal
control law they derived by hand. Tooling: **Gymnasium + MuJoCo**, with a
readable single-file algorithm (CleanRL-style) so the learning is
visible, not hidden behind a library.

### P5 — Manipulation in simulation

Scaling from a toy system to something that looks like a real robot: a
manipulator (e.g. a Franka arm from MuJoCo Menagerie) learning to reach
and grasp. The engineering lesson here is **robustness** — using domain
randomisation so a policy trained in simulation doesn't fall apart the
moment the world isn't exactly what it trained on. This is the core idea
behind *sim-to-real*, which is how essentially all modern robot learning
actually reaches hardware.

### P6 — Flagship 🏆

The capstone: one project that demonstrates a **complete, modern
robot-learning pipeline** end to end. I'm choosing between two directions,
both of which play to the mechanical-engineering-plus-AI angle:

- **(A) Real low-cost arm + imitation learning.** Using the
  [LeRobot](https://github.com/huggingface/lerobot) stack with an
  affordable open-hardware arm: *teleoperate → collect demonstrations →
  train an ACT / Diffusion Policy → deploy on the real robot.* The full
  data-to-deployment loop on physical hardware — the single most
  convincing thing a portfolio can show.

- **(B) Design + control co-optimisation.** Treat the arm's *physical
  design* (link lengths, mass distribution) as something to optimise
  jointly with its controller, using an ML surrogate to search the design
  space instead of brute force. The question "*what structure makes the
  best-controllable robot?*" is one only someone with a mechanical
  background thinks to ask — which is exactly why it's mine to answer.

Direction (A) leans toward industry (a real, demonstrable system);
direction (B) leans toward research (a clear question worth writing up).
Whichever I pick, the goal is a proper technical write-up with video, not
just code.

---

## About this route

I'm building toward roles at the intersection of **robot dynamics/control
and hardware design** — and increasingly, robot *learning*. The people who
understand both "how should this robot move" and "what structure makes
that movement possible," *and* can bring modern learning methods to bear,
are rare. That intersection is the whole thesis of this repo.

**Background:** BEng Mechanical Engineering, University of Bristol
('25) · Currently completing military service in South Korea

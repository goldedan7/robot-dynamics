"""
P1 -- Pendulum Dynamics Simulation
Robot Dynamics & Control -> Design Optimisation, toward Physical AI

A single damped pendulum modelled in state-space form and integrated
numerically. This is the first building block of robot-arm dynamics:
a robot arm is a chain of pendulums connected by joints.

Author: Changhyeon
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Physical parameters
G = 9.81   # gravitational acceleration (m/s^2)
L = 1.0    # pendulum length (m)


def pendulum(t, state, damping):
    """
    Nonlinear pendulum dynamics in state-space form.

    t       : time (required by the solver's call signature; unused
              here, because the pendulum's physics do not depend on
              time directly)
    state   : [theta, omega] -- angle (rad) and angular velocity (rad/s)
    damping : friction / air-resistance coefficient

    Returns d/dt[theta, omega].
    """
    theta, omega = state
    dtheta = omega
    domega = -(G / L) * np.sin(theta) - damping * omega
    return [dtheta, domega]


def simulate(theta0_deg, omega0=0.0, t_max=20, num_points=1000, damping=0.3):
    """Simulate the pendulum from a given initial condition."""
    theta0 = np.radians(theta0_deg)
    t_eval = np.linspace(0, t_max, num_points)
    sol = solve_ivp(
        pendulum, (0, t_max), [theta0, omega0],
        t_eval=t_eval, method='RK45', args=(damping,)
    )
    return sol.t, sol.y[0], sol.y[1]


def plot_results(t, theta, omega):
    """Plot the angle over time and the phase portrait."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot(t, np.degrees(theta), 'b-', linewidth=2)
    ax1.axhline(0, color='k', linestyle='--', alpha=0.3)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Angle (deg)')
    ax1.set_title('Pendulum angle over time')
    ax1.grid(alpha=0.3)

    ax2.plot(np.degrees(theta), omega, 'b-', linewidth=2)
    ax2.plot(np.degrees(theta[0]), omega[0], 'go', markersize=13, label='Start')
    ax2.plot(np.degrees(theta[-1]), omega[-1], 'r*', markersize=20, label='End')
    ax2.axhline(0, color='k', alpha=0.2)
    ax2.axvline(0, color='k', alpha=0.2)
    ax2.set_xlabel('Angle (deg)')
    ax2.set_ylabel('Angular velocity (rad/s)')
    ax2.set_title('Phase portrait (state space)')
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    return fig


def compare_damping(theta0_deg=60, b_values=(0, 0.3, 2.0), t_max=20):
    """Compare trajectories for different damping coefficients."""
    fig, axes = plt.subplots(1, len(b_values), figsize=(5 * len(b_values), 4))
    for ax, b in zip(axes, b_values):
        t, theta, omega = simulate(theta0_deg, damping=b, t_max=t_max)
        ax.plot(np.degrees(theta), omega, 'b-', linewidth=2)
        ax.plot(np.degrees(theta[0]), omega[0], 'go', markersize=10)
        ax.plot(np.degrees(theta[-1]), omega[-1], 'r*', markersize=15)
        ax.axhline(0, color='k', alpha=0.2)
        ax.axvline(0, color='k', alpha=0.2)
        ax.set_xlabel('Angle (deg)')
        ax.set_ylabel('Angular velocity (rad/s)')
        ax.set_title(f'Damping b = {b}')
        ax.grid(alpha=0.3)
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    t, theta, omega = simulate(theta0_deg=60, damping=0.3)
    plot_results(t, theta, omega)
    compare_damping()
    plt.show()

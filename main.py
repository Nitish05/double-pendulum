import numpy as np
from simulation import DoublePendulum
from visualizer import animate_pendulum

def main():
    # Parameters
    L1 = 1.0  # length of pendulum 1 in m
    L2 = 0.5  # length of pendulum 2 in m
    M1 = 1.0  # mass of pendulum 1 in kg
    M2 = 1.0  # mass of pendulum 2 in kg
    g = 9.81  # acceleration due to gravity, in m/s^2
    damping = 0.1 # Damping coefficient (friction/air resistance)

    # Initial conditions: theta1, dtheta1/dt, theta2, dtheta2/dt
    # Angles are in radians.
    initial_state = [np.pi/2, 0, np.pi/2, 0] 

    # Time setup
    t_max = 30.0
    dt = 0.02

    # Create simulation object
    pendulum = DoublePendulum(L1, L2, M1, M2, g, damping)

    # Solve equations of motion
    print("Solving equations of motion...")
    t, y = pendulum.solve(initial_state, t_max, dt)

    # Get coordinates for animation
    x1, y1, x2, y2 = pendulum.get_coordinates(y)

    # Animate
    print("Starting animation...")
    animate_pendulum(t, x1, y1, x2, y2, L1, L2)

if __name__ == "__main__":
    main()

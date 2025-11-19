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

    # Create simulation object
    pendulum = DoublePendulum(L1, L2, M1, M2, g, damping)
    
    # Set initial state [theta1, omega1, theta2, omega2]
    # 0 means hanging straight down
    pendulum.state = np.array([0.01, 0, 0.01, 0], dtype=float) # Small offset to avoid perfect equilibrium if needed, but 0 is fine for resting

    print("Starting interactive simulation...")
    print("Click and drag the pendulum bobs to interact.")
    
    # Start interactive animation
    animate_pendulum(pendulum)

if __name__ == "__main__":
    main()

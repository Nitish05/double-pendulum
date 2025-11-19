import numpy as np
from scipy.integrate import odeint

class DoublePendulum:
    def __init__(self, L1=1.0, L2=1.0, M1=1.0, M2=1.0, g=9.81, damping=0.0):
        self.L1 = L1
        self.L2 = L2
        self.M1 = M1
        self.M2 = M2
        self.g = g
        self.damping = damping

    def derivs(self, state, t):
        """
        Calculate the derivatives of the state vector [theta1, omega1, theta2, omega2].
        Equations of motion derived from Lagrangian mechanics.
        """
        theta1, omega1, theta2, omega2 = state
        
        dtheta1 = omega1
        dtheta2 = omega2
        
        delta = theta2 - theta1
        den1 = (self.M1 + self.M2) * self.L1 - self.M2 * self.L1 * np.cos(delta) * np.cos(delta)
        den2 = (self.L2 / self.L1) * den1

        domega1 = (
            self.M2 * self.L1 * omega1 * omega1 * np.sin(delta) * np.cos(delta)
            + self.M2 * self.g * np.sin(theta2) * np.cos(delta)
            + self.M2 * self.L2 * omega2 * omega2 * np.sin(delta)
            - (self.M1 + self.M2) * self.g * np.sin(theta1)
            - self.damping * omega1  # Damping term
        ) / den1

        domega2 = (
            - self.M2 * self.L2 * omega2 * omega2 * np.sin(delta) * np.cos(delta)
            + (self.M1 + self.M2) * self.g * np.sin(theta1) * np.cos(delta)
            - (self.M1 + self.M2) * self.L1 * omega1 * omega1 * np.sin(delta)
            - (self.M1 + self.M2) * self.g * np.sin(theta2)
            - self.damping * omega2  # Damping term
        ) / den2

        return [dtheta1, domega1, dtheta2, domega2]

    def solve(self, initial_state, t_max, dt):
        """
        Solve the equations of motion.
        """
        t = np.arange(0, t_max, dt)
        y = odeint(self.derivs, initial_state, t)
        return t, y

    def get_coordinates(self, y):
        """
        Convert state vector to Cartesian coordinates (x1, y1, x2, y2).
        """
        theta1 = y[:, 0]
        theta2 = y[:, 2]

        x1 = self.L1 * np.sin(theta1)
        y1 = -self.L1 * np.cos(theta1)

        x2 = x1 + self.L2 * np.sin(theta2)
        y2 = y1 - self.L2 * np.cos(theta2)

        return x1, y1, x2, y2

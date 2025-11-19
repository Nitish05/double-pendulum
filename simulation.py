import numpy as np

class DoublePendulum:
    def __init__(self, L1=1.0, L2=1.0, M1=1.0, M2=1.0, g=9.81, damping=0.0):
        self.L1 = L1
        self.L2 = L2
        self.M1 = M1
        self.M2 = M2
        self.g = g
        self.damping = damping
        
        # State: [theta1, omega1, theta2, omega2]
        self.state = np.array([np.pi/2, 0, np.pi/2, 0], dtype=float)
        self.t = 0.0

    def derivs(self, state, t):
        """
        Calculate the derivatives of the state vector [theta1, omega1, theta2, omega2].
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
            - self.damping * omega1
        ) / den1

        domega2 = (
            - self.M2 * self.L2 * omega2 * omega2 * np.sin(delta) * np.cos(delta)
            + (self.M1 + self.M2) * self.g * np.sin(theta1) * np.cos(delta)
            - (self.M1 + self.M2) * self.L1 * omega1 * omega1 * np.sin(delta)
            - (self.M1 + self.M2) * self.g * np.sin(theta2)
            - self.damping * omega2
        ) / den2

        return np.array([dtheta1, domega1, dtheta2, domega2])

    def step(self, dt):
        """
        Perform a single integration step using Runge-Kutta 4 (RK4).
        """
        state = self.state
        t = self.t
        
        k1 = self.derivs(state, t)
        k2 = self.derivs(state + k1 * dt * 0.5, t + dt * 0.5)
        k3 = self.derivs(state + k2 * dt * 0.5, t + dt * 0.5)
        k4 = self.derivs(state + k3 * dt, t + dt)
        
        self.state = state + (k1 + 2*k2 + 2*k3 + k4) * dt / 6.0
        self.t += dt

    def get_coordinates(self):
        """
        Convert current state to Cartesian coordinates (x1, y1, x2, y2).
        """
        theta1 = self.state[0]
        theta2 = self.state[2]

        x1 = self.L1 * np.sin(theta1)
        y1 = -self.L1 * np.cos(theta1)

        x2 = x1 + self.L2 * np.sin(theta2)
        y2 = y1 - self.L2 * np.cos(theta2)

        return x1, y1, x2, y2

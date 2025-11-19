# Double Pendulum Simulation

A real-time physics simulation of a double pendulum using Python and Pygame.

## Features
- **Accurate Physics**: Solves the Lagrangian equations of motion using `scipy.integrate.odeint`.
- **Smooth Visualization**: Renders the chaotic motion at 60 FPS using `pygame`.
- **Damping**: Simulates friction and air resistance.
- **Trace Effect**: Visualizes the chaotic trajectory of the pendulum bob.

## Requirements
- Python 3.x
- `numpy`
- `scipy`
- `pygame`

## Installation
```bash
pip install numpy scipy pygame
```

## Usage
Run the simulation:
```bash
python main.py
```

You can adjust parameters like mass, length, and damping in `main.py`.

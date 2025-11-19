# Double Pendulum Simulation

A real-time physics simulation of a double pendulum using Python and Pygame.

## Features
- **Accurate Physics**: Uses Lagrangian mechanics and RK4 integration for real-time physics.
- **Smooth Animation**: Visualizes the pendulum's chaotic motion using `pygame` at 60 FPS.
- **Interactive Dragging**: Click and drag the pendulum bobs to throw them around. The simulation uses Inverse Kinematics (IK) for natural movement.
- **UI Controls**:
    - **Parameters**: Adjust lengths (`L1`, `L2`) and `Damping` in real-time.
    - **Reset**: Instantly reset the simulation to a resting state.
    - **Traces**: Toggle traces for both bobs and cycle through different colors.
    - **Visibility**: Hide the UI for a clean view of the simulation.
- **Damping**: Simulation includes friction/air resistance.
- **Dynamic Scaling**: Automatically adjusts the view to ensure the pendulum always fits within the window.

## Requirements
- Python 3.x
- `numpy`
- `scipy`
- `pygame`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Nitis05/double-pendulum.git
   ```
2. Install dependencies:
   ```bash
   pip install numpy scipy pygame
   ```

## Usage
Run the simulation:
```bash
python main.py
```

### Controls
- **Left Click & Drag**: Move the pendulum bobs.
- **UI Panel (Top Right)**:
    - Enter values for Lengths and Damping.
    - Click "Reset Simulation" to restart.
    - Click "Trace: ON/OFF" to toggle trails.
    - Click "Color" buttons to change trail colors.
    - Click "Hide UI" to toggle interface visibility.py`.

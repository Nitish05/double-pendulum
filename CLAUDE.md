# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a real-time physics simulation of a double pendulum implemented in Python using Arcade for visualization. The simulation uses Lagrangian mechanics with RK4 (Runge-Kutta 4th order) integration for accurate physics.

## Running the Simulation

```bash
python main.py
```

## Dependencies

Install required packages:
```bash
pip install numpy scipy arcade
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Architecture

### Three-Module Design

1. **main.py** - Entry point
   - Initializes pendulum parameters (lengths L1/L2, masses M1/M2, gravity g, damping)
   - Creates `DoublePendulum` instance
   - Launches the visualization via `animate_pendulum()`

2. **simulation.py** - Physics engine
   - `DoublePendulum` class handles all physics calculations
   - State vector: `[theta1, omega1, theta2, omega2]` where theta is angle, omega is angular velocity
   - `derivs()`: Computes derivatives using Lagrangian mechanics equations
   - `step()`: RK4 integration for accurate time-stepping
   - `get_coordinates()`: Converts polar (theta) to Cartesian (x, y) coordinates

3. **visualizer.py** - Rendering and interaction
   - Arcade-based visualization using `PendulumWindow` class (inherits from `arcade.Window`)
   - Interactive dragging with inverse kinematics (IK) for Bob 2
   - UI elements: `Button` and `InputBox` classes for controls
   - Dynamic scaling to keep pendulum in view
   - Trace rendering for both bobs with configurable colors
   - Event-driven architecture with `on_draw()`, `on_update()`, `on_mouse_press()`, etc.

### Key Concepts

**State Management**: The pendulum state is a 4D vector representing angles and angular velocities. When dragging:
- Bob 1 (first pendulum): Direct angle calculation from mouse position
- Bob 2 (second pendulum): Uses 2-link inverse kinematics to solve for both theta1 and theta2

**Coordinate Systems**:
- Physics coordinates: Origin at pivot point, y-axis points up
- Screen coordinates (Arcade): Origin at bottom-left, y-axis points up (same as physics!)
- Conversion uses `scale` and `offset_x/offset_y` variables for translation and scaling

**Inverse Kinematics (IK)**: When dragging Bob 2, the system solves for joint angles that place the end effector (Bob 2) at the mouse position. Uses law of cosines and angle normalization to choose the closest elbow configuration.

## Modifying Physics

To change physical behavior, edit parameters in `main.py` or adjust the equations in `DoublePendulum.derivs()` in `simulation.py`. The damping term is applied to both angular velocities.

## Modifying UI

UI elements are instantiated in the `PendulumWindow.setup_ui()` method in `visualizer.py`. Each UI element has a callback that modifies the pendulum state or visualization settings. The main entry point is `animate_pendulum()` which creates a `PendulumWindow` instance and calls `arcade.run()`.

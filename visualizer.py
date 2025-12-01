import arcade
import sys
import numpy as np
import math

# UI Classes
class Button:
    def __init__(self, x, y, w, h, text, callback, color=(200, 200, 200)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.callback = callback
        self.base_color = color
        self.hover_color = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255))
        self.text_color = (0, 0, 0)

    def draw(self, mouse_x, mouse_y):
        # Check if mouse is over button
        if (self.x <= mouse_x <= self.x + self.w and
            self.y <= mouse_y <= self.y + self.h):
            color = self.hover_color
        else:
            color = self.base_color

        # Draw filled rectangle using lrbt (left, right, bottom, top)
        arcade.draw_lrbt_rectangle_filled(
            self.x, self.x + self.w, self.y, self.y + self.h,
            color
        )
        # Draw border using lrbt (left, right, bottom, top)
        arcade.draw_lrbt_rectangle_outline(
            self.x, self.x + self.w, self.y, self.y + self.h,
            (0, 0, 0), 2
        )
        # Draw text centered in button, both horizontally and vertically
        arcade.draw_text(
            self.text,
            self.x + self.w/2, self.y + self.h/2 - 3,
            self.text_color, 14,
            anchor_x="center", anchor_y="baseline"
        )

    def is_clicked(self, x, y):
        return (self.x <= x <= self.x + self.w and
                self.y <= y <= self.y + self.h)

class InputBox:
    def __init__(self, x, y, w, h, label, initial_text, callback):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.text = str(initial_text)
        self.callback = callback
        self.color_inactive = (135, 206, 235)  # lightskyblue3
        self.color_active = (30, 144, 255)     # dodgerblue2
        self.color = self.color_inactive
        self.active = False

    def handle_click(self, x, y):
        if (self.x <= x <= self.x + self.w and
            self.y <= y <= self.y + self.h):
            self.active = not self.active
        else:
            self.active = False
        self.color = self.color_active if self.active else self.color_inactive

    def handle_key(self, key, modifiers):
        if self.active:
            if key == arcade.key.ENTER:
                try:
                    value = float(self.text)
                    self.callback(value)
                    self.active = False
                    self.color = self.color_inactive
                except ValueError:
                    pass  # Ignore invalid input
            elif key == arcade.key.BACKSPACE:
                self.text = self.text[:-1]

    def handle_text(self, text):
        if self.active:
            self.text += text

    def draw(self):
        # Draw label - position to the left of the box, vertically centered
        arcade.draw_text(
            self.label,
            self.x - 10, self.y + self.h/2 - 3,
            (0, 0, 0), 14,
            anchor_x="right", anchor_y="baseline"
        )

        # Draw box border using lrbt (left, right, bottom, top)
        arcade.draw_lrbt_rectangle_outline(
            self.x, self.x + self.w, self.y, self.y + self.h,
            self.color, 2
        )

        # Draw text inside the box, vertically centered
        arcade.draw_text(
            self.text,
            self.x + 5, self.y + self.h/2 - 3,
            (0, 0, 0), 14,
            anchor_x="left", anchor_y="baseline"
        )

class PendulumWindow(arcade.Window):
    """
    Interactive animation of the double pendulum using Arcade.
    """
    def __init__(self, pendulum):
        # Screen dimensions
        WIDTH, HEIGHT = 800, 800
        super().__init__(WIDTH, HEIGHT, "Double Pendulum Simulation - Drag to Interact")

        self.pendulum = pendulum

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREY = (100, 100, 100)

        # Trace Colors
        self.COLORS = [
            (255, 0, 0),   # Red
            (0, 255, 0),   # Green
            (0, 0, 255),   # Blue
            (255, 255, 0), # Yellow
            (255, 0, 255), # Magenta
            (0, 255, 255), # Cyan
            (0, 0, 0)      # Black
        ]
        self.COLOR_NAMES = ["Red", "Green", "Blue", "Yellow", "Magenta", "Cyan", "Black"]

        # Trace history
        self.history_len = 500
        self.trace_points1 = []
        self.trace_points2 = []

        # Trace settings
        self.show_trace1 = True
        self.show_trace2 = True
        self.color_idx1 = 1  # Green default for Bob 1
        self.color_idx2 = 0  # Red default for Bob 2

        self.ui_visible = True
        self.dragging_bob = None  # 1 or 2

        self.dt = 0.005  # Time step for physics
        self.steps_per_frame = 4  # Multiple physics steps per visual frame

        # Mouse position tracking
        self.mouse_x = 0
        self.mouse_y = 0

        # Setup UI
        self.setup_ui()

        arcade.set_background_color(self.WHITE)

    def setup_ui(self):
        """Initialize UI elements"""
        WIDTH = self.width
        HEIGHT = self.height

        # UI Elements Layout (Top Right)
        ui_x = WIDTH - 220
        ui_y = HEIGHT - 60  # Arcade y-axis starts at bottom
        spacing = -40  # Negative because we go down

        self.input_l1 = InputBox(ui_x + 80, ui_y, 60, 30, "L1 (m)", self.pendulum.L1, self.update_L1)
        self.input_l2 = InputBox(ui_x + 80, ui_y + spacing, 60, 30, "L2 (m)", self.pendulum.L2, self.update_L2)
        self.input_damp = InputBox(ui_x + 80, ui_y + spacing*2, 60, 30, "Damping", self.pendulum.damping, self.update_damping)

        self.reset_btn = Button(ui_x, ui_y + spacing*3, 140, 30, "Reset Simulation", self.reset_simulation)

        # Trace Controls
        self.btn_trace1 = Button(ui_x, ui_y + spacing*4.5, 140, 25, "Trace 1: ON", self.toggle_trace1)
        self.btn_color1 = Button(ui_x, ui_y + spacing*5.2, 140, 25, f"Color 1: {self.COLOR_NAMES[self.color_idx1]}",
                                 self.cycle_color1, self.COLORS[self.color_idx1])

        self.btn_trace2 = Button(ui_x, ui_y + spacing*6.5, 140, 25, "Trace 2: ON", self.toggle_trace2)
        self.btn_color2 = Button(ui_x, ui_y + spacing*7.2, 140, 25, f"Color 2: {self.COLOR_NAMES[self.color_idx2]}",
                                 self.cycle_color2, self.COLORS[self.color_idx2])

        # Hide UI Button
        self.btn_hide_ui = Button(WIDTH - 100, 40, 80, 30, "Hide UI", self.toggle_ui)

        self.main_ui_elements = [self.input_l1, self.input_l2, self.input_damp, self.reset_btn,
                                 self.btn_trace1, self.btn_color1, self.btn_trace2, self.btn_color2]

    # UI Callbacks
    def reset_simulation(self):
        self.pendulum.state = np.array([0.01, 0, 0.01, 0], dtype=float)
        self.trace_points1.clear()
        self.trace_points2.clear()

    def update_L1(self, val):
        self.pendulum.L1 = val
        self.trace_points1.clear()
        self.trace_points2.clear()

    def update_L2(self, val):
        self.pendulum.L2 = val
        self.trace_points2.clear()

    def update_damping(self, val):
        self.pendulum.damping = val

    def toggle_trace1(self):
        self.show_trace1 = not self.show_trace1
        self.btn_trace1.text = "Trace 1: ON" if self.show_trace1 else "Trace 1: OFF"

    def toggle_trace2(self):
        self.show_trace2 = not self.show_trace2
        self.btn_trace2.text = "Trace 2: ON" if self.show_trace2 else "Trace 2: OFF"

    def cycle_color1(self):
        self.color_idx1 = (self.color_idx1 + 1) % len(self.COLORS)
        self.btn_color1.text = f"Color 1: {self.COLOR_NAMES[self.color_idx1]}"
        self.btn_color1.base_color = self.COLORS[self.color_idx1]
        # Make text readable against color
        avg_color = sum(self.COLORS[self.color_idx1])/3
        self.btn_color1.text_color = (0,0,0) if avg_color > 128 else (255,255,255)

    def cycle_color2(self):
        self.color_idx2 = (self.color_idx2 + 1) % len(self.COLORS)
        self.btn_color2.text = f"Color 2: {self.COLOR_NAMES[self.color_idx2]}"
        self.btn_color2.base_color = self.COLORS[self.color_idx2]
        avg_color = sum(self.COLORS[self.color_idx2])/3
        self.btn_color2.text_color = (0,0,0) if avg_color > 128 else (255,255,255)

    def toggle_ui(self):
        self.ui_visible = not self.ui_visible
        self.btn_hide_ui.text = "Hide UI" if self.ui_visible else "Show UI"

    def on_update(self, delta_time):
        """Update physics"""
        if self.dragging_bob is None:
            # Physics step - multiple steps per frame for better accuracy
            for _ in range(self.steps_per_frame):
                self.pendulum.step(self.dt)

    def on_draw(self):
        """Render the frame"""
        self.clear()

        WIDTH = self.width
        HEIGHT = self.height

        # Dynamic scaling
        max_length = self.pendulum.L1 + self.pendulum.L2
        padding = 1.2
        scale = min(WIDTH, HEIGHT) / (2 * max_length * padding)
        offset_x = WIDTH // 2
        offset_y = HEIGHT // 2

        x1, y1, x2, y2 = self.pendulum.get_coordinates()

        curr_x1 = offset_x + x1 * scale
        curr_y1 = offset_y + y1 * scale  # Arcade y-axis goes up
        curr_x2 = offset_x + x2 * scale
        curr_y2 = offset_y + y2 * scale

        center_x, center_y = offset_x, offset_y

        # Update trace
        if self.dragging_bob is None:
            self.trace_points1.append((curr_x1, curr_y1))
            self.trace_points2.append((curr_x2, curr_y2))
            if len(self.trace_points1) > self.history_len:
                self.trace_points1.pop(0)
            if len(self.trace_points2) > self.history_len:
                self.trace_points2.pop(0)

        # Draw trace 1
        if self.show_trace1 and len(self.trace_points1) > 1:
            arcade.draw_line_strip(self.trace_points1, self.COLORS[self.color_idx1], 1)

        # Draw trace 2
        if self.show_trace2 and len(self.trace_points2) > 1:
            arcade.draw_line_strip(self.trace_points2, self.COLORS[self.color_idx2], 1)

        # Draw rods
        arcade.draw_line(center_x, center_y, curr_x1, curr_y1, self.BLACK, 4)
        arcade.draw_line(curr_x1, curr_y1, curr_x2, curr_y2, self.BLACK, 4)

        # Draw bobs
        c1 = self.COLORS[self.color_idx1]
        c2 = self.COLORS[self.color_idx2]
        if self.dragging_bob == 1: c1 = (255, 100, 100)  # Light red when dragging
        if self.dragging_bob == 2: c2 = (255, 100, 100)

        arcade.draw_circle_filled(curr_x1, curr_y1, 10, c1)
        arcade.draw_circle_filled(curr_x2, curr_y2, 10, c2)

        # Draw pivot
        arcade.draw_circle_filled(offset_x, offset_y, 5, self.BLACK)

        # Display time
        arcade.draw_text(
            f'Time: {self.pendulum.t:.1f}s',
            20, HEIGHT - 20,
            self.BLACK, 24,
            anchor_x="left", anchor_y="top"
        )

        arcade.draw_text(
            'Drag bobs with mouse',
            20, HEIGHT - 50,
            self.GREY, 24,
            anchor_x="left", anchor_y="top"
        )

        # Draw UI
        if self.ui_visible:
            for ui in self.main_ui_elements:
                if isinstance(ui, Button):
                    ui.draw(self.mouse_x, self.mouse_y)
                else:
                    ui.draw()

        # Always draw hide button
        self.btn_hide_ui.draw(self.mouse_x, self.mouse_y)

    def on_mouse_motion(self, x, y, dx, dy):
        """Track mouse position"""
        self.mouse_x = x
        self.mouse_y = y

        # Handle dragging
        if self.dragging_bob is not None:
            WIDTH = self.width
            HEIGHT = self.height

            # Dynamic scaling
            max_length = self.pendulum.L1 + self.pendulum.L2
            padding = 1.2
            scale = min(WIDTH, HEIGHT) / (2 * max_length * padding)
            offset_x = WIDTH // 2
            offset_y = HEIGHT // 2

            # Convert mouse to physics coords (relative to pivot)
            phys_mx = (x - offset_x) / scale
            phys_my = (y - offset_y) / scale  # No negation needed, arcade y is already upward

            if self.dragging_bob == 1:
                # Calculate angle for theta1
                self.pendulum.state[0] = math.atan2(phys_mx, -phys_my)
                self.pendulum.state[1] = 0  # Zero velocity
                self.pendulum.state[3] = 0

            elif self.dragging_bob == 2:
                # Inverse Kinematics for 2-link arm
                tx, ty = phys_mx, phys_my

                r = math.hypot(tx, ty)
                L1, L2 = self.pendulum.L1, self.pendulum.L2

                # Limit reach
                if r > (L1 + L2) * 0.999:
                    r = (L1 + L2) * 0.999
                    scale_factor = r / math.hypot(tx, ty)
                    tx *= scale_factor
                    ty *= scale_factor

                # Law of Cosines for internal angle alpha
                cos_alpha = (L1**2 + r**2 - L2**2) / (2 * L1 * r)
                cos_alpha = max(-1.0, min(1.0, cos_alpha))  # Clamp for safety
                alpha = math.acos(cos_alpha)

                # Angle to target (phi)
                phi = math.atan2(tx, -ty)

                # Two solutions for elbow
                current_theta1 = self.pendulum.state[0]

                t1_sol1 = phi - alpha
                t1_sol2 = phi + alpha

                # Normalize angles
                def normalize(angle, ref):
                    while angle - ref > np.pi: angle -= 2*np.pi
                    while angle - ref < -np.pi: angle += 2*np.pi
                    return angle

                t1_sol1 = normalize(t1_sol1, current_theta1)
                t1_sol2 = normalize(t1_sol2, current_theta1)

                if abs(t1_sol1 - current_theta1) < abs(t1_sol2 - current_theta1):
                    theta1 = t1_sol1
                else:
                    theta1 = t1_sol2

                # Calculate theta2
                # Position of elbow (Bob 1)
                ex = L1 * math.sin(theta1)
                ey = -L1 * math.cos(theta1)

                # Vector from elbow to target
                dx = tx - ex
                dy = ty - ey

                theta2 = math.atan2(dx, -dy)

                self.pendulum.state[0] = theta1
                self.pendulum.state[2] = theta2
                self.pendulum.state[1] = 0
                self.pendulum.state[3] = 0

            # Clear trace when dragging
            self.trace_points1.clear()
            self.trace_points2.clear()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse button press"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check if clicked on UI
            clicked_ui = False

            if self.btn_hide_ui.is_clicked(x, y):
                self.btn_hide_ui.callback()
                clicked_ui = True

            if self.ui_visible and not clicked_ui:
                for ui in self.main_ui_elements:
                    if isinstance(ui, Button) and ui.is_clicked(x, y):
                        ui.callback()
                        clicked_ui = True
                        break
                    elif isinstance(ui, InputBox):
                        ui.handle_click(x, y)

            if not clicked_ui:
                WIDTH = self.width
                HEIGHT = self.height

                # Dynamic scaling
                max_length = self.pendulum.L1 + self.pendulum.L2
                padding = 1.2
                scale = min(WIDTH, HEIGHT) / (2 * max_length * padding)
                offset_x = WIDTH // 2
                offset_y = HEIGHT // 2

                # Get current bob positions in screen coords
                x1, y1, x2, y2 = self.pendulum.get_coordinates()
                sx1 = offset_x + x1 * scale
                sy1 = offset_y + y1 * scale
                sx2 = offset_x + x2 * scale
                sy2 = offset_y + y2 * scale

                # Check distance
                dist1 = math.hypot(x - sx1, y - sy1)
                dist2 = math.hypot(x - sx2, y - sy2)

                if dist1 < 20:
                    self.dragging_bob = 1
                elif dist2 < 20:
                    self.dragging_bob = 2

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse button release"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.dragging_bob = None

    def on_key_press(self, key, modifiers):
        """Handle keyboard input"""
        if self.ui_visible:
            for ui in self.main_ui_elements:
                if isinstance(ui, InputBox):
                    ui.handle_key(key, modifiers)

    def on_text(self, text):
        """Handle text input for input boxes"""
        if self.ui_visible:
            for ui in self.main_ui_elements:
                if isinstance(ui, InputBox):
                    ui.handle_text(text)

def animate_pendulum(pendulum):
    """
    Interactive animation of the double pendulum using Arcade.
    """
    window = PendulumWindow(pendulum)
    arcade.run()

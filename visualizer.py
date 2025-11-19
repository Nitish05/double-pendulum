import pygame
import sys
import numpy as np
import math

# UI Classes
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = (200, 200, 200)
        self.hover_color = (170, 170, 170)
        self.text_color = (0, 0, 0)
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()

class InputBox:
    def __init__(self, x, y, w, h, label, initial_text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = str(initial_text)
        self.callback = callback
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.font = pygame.font.SysFont(None, 24)
        self.label_font = pygame.font.SysFont(None, 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    try:
                        value = float(self.text)
                        self.callback(value)
                        self.active = False
                        self.color = self.color_inactive
                    except ValueError:
                        pass # Ignore invalid input
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        # Draw label
        label_surf = self.label_font.render(self.label, True, (0, 0, 0))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 20))
        
        # Draw box
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
        # Draw text
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
        self.rect.w = max(100, text_surf.get_width() + 10)

def animate_pendulum(pendulum):
    """
    Interactive animation of the double pendulum using Pygame.
    """
    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Double Pendulum Simulation - Drag to Interact")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREY = (100, 100, 100)

    clock = pygame.time.Clock()
    
    # Trace history
    history_len = 500
    trace_points = []

    running = True
    dragging_bob = None # 1 or 2

    dt = 0.02 # Time step for physics

    # UI Callbacks
    def reset_simulation():
        pendulum.state = np.array([0.01, 0, 0.01, 0], dtype=float)
        trace_points.clear()

    def update_L1(val):
        pendulum.L1 = val
        # Need to update scaling if length changes significantly?
        # Ideally we recalculate scale every frame or just let it be.
        # For now let's keep scale dynamic in the loop.

    def update_L2(val):
        pendulum.L2 = val

    def update_damping(val):
        pendulum.damping = val

    # UI Elements
    reset_btn = Button(20, HEIGHT - 60, 100, 40, "Reset", reset_simulation)
    
    input_l1 = InputBox(140, HEIGHT - 50, 80, 30, "L1 (m)", pendulum.L1, update_L1)
    input_l2 = InputBox(240, HEIGHT - 50, 80, 30, "L2 (m)", pendulum.L2, update_L2)
    input_damp = InputBox(340, HEIGHT - 50, 80, 30, "Damping", pendulum.damping, update_damping)
    
    ui_elements = [reset_btn, input_l1, input_l2, input_damp]

    while running:
        # Dynamic scaling
        max_length = pendulum.L1 + pendulum.L2
        padding = 1.2
        scale = min(WIDTH, HEIGHT) / (2 * max_length * padding)
        offset_x = WIDTH // 2
        offset_y = HEIGHT // 2

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle UI events
            for ui in ui_elements:
                ui.handle_event(event)
            
            # Handle Dragging
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Check if clicked on UI?
                    clicked_ui = False
                    for ui in ui_elements:
                        if hasattr(ui, 'rect') and ui.rect.collidepoint(event.pos):
                            clicked_ui = True
                            break
                    
                    if not clicked_ui:
                        mx, my = pygame.mouse.get_pos()
                        
                        # Get current bob positions in screen coords
                        x1, y1, x2, y2 = pendulum.get_coordinates()
                        sx1 = offset_x + x1 * scale
                        sy1 = offset_y - y1 * scale
                        sx2 = offset_x + x2 * scale
                        sy2 = offset_y - y2 * scale
                        
                        # Check distance
                        dist1 = math.hypot(mx - sx1, my - sy1)
                        dist2 = math.hypot(mx - sx2, my - sy2)
                        
                        if dist1 < 20:
                            dragging_bob = 1
                        elif dist2 < 20:
                            dragging_bob = 2
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_bob = None

        # Mouse interaction logic
        if dragging_bob is not None:
            mx, my = pygame.mouse.get_pos()
            
            # Convert mouse to physics coords (relative to pivot)
            phys_mx = (mx - offset_x) / scale
            phys_my = (offset_y - my) / scale
            
            if dragging_bob == 1:
                # Calculate angle for theta1
                pendulum.state[0] = math.atan2(phys_mx, -phys_my)
                pendulum.state[1] = 0 # Zero velocity
                pendulum.state[3] = 0
                
            elif dragging_bob == 2:
                # Inverse Kinematics for 2-link arm
                tx, ty = phys_mx, phys_my
                
                r = math.hypot(tx, ty)
                L1, L2 = pendulum.L1, pendulum.L2
                
                # Limit reach
                if r > (L1 + L2) * 0.999:
                    r = (L1 + L2) * 0.999
                    scale_factor = r / math.hypot(tx, ty)
                    tx *= scale_factor
                    ty *= scale_factor
                
                # Law of Cosines for internal angle alpha
                cos_alpha = (L1**2 + r**2 - L2**2) / (2 * L1 * r)
                cos_alpha = max(-1.0, min(1.0, cos_alpha)) # Clamp for safety
                alpha = math.acos(cos_alpha)
                
                # Angle to target (phi)
                phi = math.atan2(tx, -ty)
                
                # Two solutions for elbow
                current_theta1 = pendulum.state[0]
                
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
                
                pendulum.state[0] = theta1
                pendulum.state[2] = theta2
                pendulum.state[1] = 0
                pendulum.state[3] = 0
                
            # Clear trace when dragging
            trace_points.clear()

        else:
            # Physics step
            pendulum.step(dt)

        # Rendering
        screen.fill(WHITE)

        x1, y1, x2, y2 = pendulum.get_coordinates()
        
        curr_x1 = offset_x + x1 * scale
        curr_y1 = offset_y - y1 * scale
        curr_x2 = offset_x + x2 * scale
        curr_y2 = offset_y - y2 * scale
        
        center_x, center_y = offset_x, offset_y

        # Update trace
        if dragging_bob is None:
            trace_points.append((curr_x2, curr_y2))
            if len(trace_points) > history_len:
                trace_points.pop(0)

        # Draw trace
        if len(trace_points) > 1:
            pygame.draw.lines(screen, RED, False, trace_points, 1)

        # Draw rods
        pygame.draw.line(screen, BLACK, (center_x, center_y), (curr_x1, curr_y1), 4)
        pygame.draw.line(screen, BLACK, (curr_x1, curr_y1), (curr_x2, curr_y2), 4)

        # Draw bobs
        color1 = RED if dragging_bob == 1 else BLUE
        color2 = RED if dragging_bob == 2 else BLUE
        
        pygame.draw.circle(screen, color1, (int(curr_x1), int(curr_y1)), 10)
        pygame.draw.circle(screen, color2, (int(curr_x2), int(curr_y2)), 10)
        
        # Draw pivot
        pygame.draw.circle(screen, BLACK, (offset_x, offset_y), 5)

        # Display time
        font = pygame.font.SysFont(None, 24)
        img = font.render(f'Time: {pendulum.t:.1f}s', True, BLACK)
        screen.blit(img, (20, 20))
        
        img2 = font.render('Drag bobs with mouse', True, GREY)
        screen.blit(img2, (20, 50))

        # Draw UI
        for ui in ui_elements:
            ui.draw(screen)

        pygame.display.flip()
        clock.tick(60) # Target 60 FPS

    pygame.quit()

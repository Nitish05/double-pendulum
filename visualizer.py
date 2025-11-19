import pygame
import sys
import numpy as np

def animate_pendulum(t, x1, y1, x2, y2, L1, L2):
    """
    Create an animation of the double pendulum using Pygame.
    """
    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Double Pendulum Simulation")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREY = (100, 100, 100)

    # Scaling and centering
    # Dynamic scaling to ensure it fits
    max_length = L1 + L2
    padding = 1.2  # 20% padding
    scale = min(WIDTH, HEIGHT) / (2 * max_length * padding)
    
    offset_x = WIDTH // 2
    offset_y = HEIGHT // 2

    clock = pygame.time.Clock()
    
    # Trace history
    history_len = 500
    trace_points = []

    running = True
    frame_idx = 0
    total_frames = len(t)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if frame_idx >= total_frames:
            # Loop animation or stop
            frame_idx = 0
            trace_points.clear()

        # Clear screen
        screen.fill(WHITE)

        # Get current coordinates
        # Note: y is inverted in screen coordinates (down is positive)
        # But our physics y is up is positive? 
        # Let's check simulation.py: y1 = -L1 * cos(theta1). Theta=0 is down.
        # So y1 is negative when hanging down.
        # Screen y: 0 is top. 
        # We want center to be (offset_x, offset_y).
        # screen_x = offset_x + x * scale
        # screen_y = offset_y - y * scale (flip y axis so up is up)
        
        # Actually, standard physics usually has y up.
        # In simulation.py: y1 = -L1 * cos(theta1).
        # If theta1=0, y1 = -L1. This is "down".
        # So if we map this to screen:
        # screen_y = offset_y - y * scale
        # Then y=-L1 becomes offset_y - (-L1)*scale = offset_y + L1*scale.
        # This puts it below the center, which is correct for screen coords.

        curr_x1 = offset_x + x1[frame_idx] * scale
        curr_y1 = offset_y - y1[frame_idx] * scale
        curr_x2 = offset_x + x2[frame_idx] * scale
        curr_y2 = offset_y - y2[frame_idx] * scale
        
        center_x, center_y = offset_x, offset_y

        # Update trace
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
        pygame.draw.circle(screen, BLUE, (int(curr_x1), int(curr_y1)), 10)
        pygame.draw.circle(screen, BLUE, (int(curr_x2), int(curr_y2)), 10)
        
        # Draw pivot
        pygame.draw.circle(screen, BLACK, (offset_x, offset_y), 5)

        # Display time
        font = pygame.font.SysFont(None, 24)
        img = font.render(f'Time: {t[frame_idx]:.1f}s', True, BLACK)
        screen.blit(img, (20, 20))

        pygame.display.flip()
        
        # Control speed
        # dt in simulation is 0.02s (50 FPS)
        # We want to match real time roughly
        clock.tick(50) 
        frame_idx += 1

    pygame.quit()

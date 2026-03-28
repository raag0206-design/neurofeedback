import pygame
import sys
import math
import random
import os
from pylsl import StreamInlet, resolve_byprop

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
FPS = 60
BG_COLOR = (5, 5, 20)

# Game States
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_WIN = "WIN"

# Gameplay Constants
ASTEROID_SPAWN_RATE = 60 
ASTEROID_SPEED_MIN = 1.5
ASTEROID_SPEED_MAX = 3.5
PLAYER_LIVES = 3
WIN_SCORE = 3000

def load_image(name, scale=None):
    # Try to find the image in the assets directory relative to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    assets_dir = os.path.join(project_root, 'assets')
    path = os.path.join(assets_dir, name)
    
    try:
        if not os.path.exists(path):
            # Fallback for when running from root or if already organized
            path = os.path.join('assets', name)
            
        image = pygame.image.load(path).convert_alpha()
        
        if scale:
            image = pygame.transform.scale(image, scale)

        return image
    except pygame.error as e:
        print(f"Unable to load image at {path}: {e}")
        surf = pygame.Surface(scale if scale else (50, 50))
        surf.fill((255, 0, 255))
        return surf

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        size = random.randint(25, 50)
        self.base_image = pygame.transform.scale(image, (size, size))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 50
        self.rect.y = random.randint(0, HEIGHT - size)
        self.speed = random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        self.rotation = 0
        self.rot_speed = random.uniform(-2, 2)

    def update(self):
        self.rect.x -= self.speed
        self.rotation += self.rot_speed
        
        # Rotate the pre-scaled base image
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        self.rect = self.image.get_rect(center=old_center)
        
        if self.rect.right < 0:
            self.kill()

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, -0.5)
        self.vy = random.uniform(-1, 1)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.color = random.choice([(255, 150, 50), (255, 100, 0), (200, 50, 0)])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

    def draw(self, screen):
        size = int(self.life * 8)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

def reset_game_state():
    """Returns fresh game state values."""
    return {
        'score': 0,
        'lives': PLAYER_LIVES,
        'current_y': float(HEIGHT // 2),
        'is_focused': False,
        'spawn_timer': 0,
        'shake_timer': 0,
        'particles': [],
    }

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neurofeedback Odyssey")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_med = pygame.font.SysFont("Arial", 30, bold=True)
    font_small = pygame.font.SysFont("Arial", 22)
    font_tiny = pygame.font.SysFont("Arial", 18)
    pygame.mouse.set_visible(False)

    # --- Assets ---
    ship_img = load_image("spaceship.png", (90, 60))
    asteroid_img = load_image("asteroid.png")
    bg_img = load_image("space_background.png", (WIDTH, HEIGHT))
    
    # --- LSL Setup ---
    # OpenViBE computes Beta/Theta ratio and threshold crossing.
    # Only 'openvibeMarkers' is used — it sends stimulation codes:
    #   33031 = Cross OVER threshold (focused)
    #   33032 = Cross UNDER threshold (unfocused)
    print("Looking for LSL stream 'openvibeMarkers'...")
    marker_streams = resolve_byprop('name', 'openvibeMarkers', timeout=5.0)
    
    marker_inlet = None
    
    if marker_streams:
        marker_inlet = StreamInlet(marker_streams[0])
        print("Connected to 'openvibeMarkers' LSL stream.")
    else:
        print("Warning: 'openvibeMarkers' not found. Using mouse fallback.")
    
    has_lsl = marker_inlet is not None

    # --- Game State ---
    game_state = STATE_START
    
    gs = reset_game_state()
    
    ship_rect = ship_img.get_rect()
    ship_rect.x = 100
    
    asteroids = pygame.sprite.Group()
    
    # Background scrolling
    bg_x1 = 0
    bg_x2 = WIDTH

    running = True
    while running:
        dt = clock.tick(FPS)
        
        # --- Input Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if game_state == STATE_START:
                    if event.key == pygame.K_SPACE:
                        game_state = STATE_PLAYING
                        gs = reset_game_state()
                        asteroids.empty()

                elif game_state in [STATE_GAME_OVER, STATE_WIN]:
                    if event.key == pygame.K_SPACE:
                        game_state = STATE_START

        if game_state == STATE_PLAYING:
            # --- LSL Data Acquisition ---
            # Read threshold crossing stimulations from OpenViBE
            if has_lsl:
                marker_chunk, _ = marker_inlet.pull_chunk(timeout=0.0)
                if marker_chunk:
                    for sample in marker_chunk:
                        stim = int(sample[0])
                        if stim == 33031:     # Cross OVER threshold = focused
                            gs['is_focused'] = True
                        elif stim == 33032:   # Cross UNDER threshold = unfocused
                            gs['is_focused'] = False
            else:
                # Mouse fallback: Y < center = focused
                gs['is_focused'] = pygame.mouse.get_pos()[1] < HEIGHT // 2

            # --- Ship Movement ---
            # Focused = propel UP, unfocused = gravity pulls DOWN
            ship_speed_up = 3.0
            gravity = 1.5
            if gs['is_focused']:
                gs['current_y'] -= ship_speed_up  # Move UP
            else:
                gs['current_y'] += gravity  # Drift DOWN
            # Clamp within screen bounds
            gs['current_y'] = max(30, min(HEIGHT - 30, gs['current_y']))
            ship_rect.centery = int(gs['current_y'])

            # --- Update Objects ---
            gs['spawn_timer'] -= 1
            if gs['spawn_timer'] <= 0:
                asteroids.add(Asteroid(asteroid_img))
                gs['spawn_timer'] = ASTEROID_SPAWN_RATE

            asteroids.update()
            
            # Particles for exhaust
            gs['particles'].append(Particle(ship_rect.left + 5, ship_rect.centery))
            for p in gs['particles'][:]:
                p.update()
                if p.life <= 0:
                    gs['particles'].remove(p)

            # Score
            gs['score'] += 1
            if gs['score'] >= WIN_SCORE:
                game_state = STATE_WIN

            # Collision detection
            hitbox = ship_rect.inflate(-15, -15)
            for asteroid in asteroids:
                if hitbox.colliderect(asteroid.rect):
                    asteroid.kill()
                    gs['lives'] -= 1
                    gs['shake_timer'] = 15
                    if gs['lives'] <= 0:
                        game_state = STATE_GAME_OVER

            # Background Scroll
            bg_x1 -= 1
            bg_x2 -= 1
            if bg_x1 <= -WIDTH: bg_x1 = WIDTH
            if bg_x2 <= -WIDTH: bg_x2 = WIDTH

        # --- Render ---
        render_offset = [0, 0]
        if gs['shake_timer'] > 0:
            render_offset = [random.randint(-5, 5), random.randint(-5, 5)]
            gs['shake_timer'] -= 1

        # Draw Background
        screen.blit(bg_img, (bg_x1 + render_offset[0], render_offset[1]))
        screen.blit(bg_img, (bg_x2 + render_offset[0], render_offset[1]))

        if game_state == STATE_PLAYING:
            # Draw Particles
            for p in gs['particles']:
                p.draw(screen)

            # Draw Asteroids
            for asteroid in asteroids:
                screen.blit(asteroid.image, (asteroid.rect.x + render_offset[0], asteroid.rect.y + render_offset[1]))

            # Draw Ship
            screen.blit(ship_img, (ship_rect.x + render_offset[0], ship_rect.y + render_offset[1]))

            # Draw UI - Score
            score_text = font_small.render(f"Score: {gs['score']}", True, (255, 255, 255))
            screen.blit(score_text, (20, 20))
            
            # Health Bar
            pygame.draw.rect(screen, (100, 0, 0), (20, 50, 150, 20))
            health_width = (gs['lives'] / PLAYER_LIVES) * 150
            if health_width > 0:
                pygame.draw.rect(screen, (255, 50, 50), (20, 50, health_width, 20))
            pygame.draw.rect(screen, (255, 255, 255), (20, 50, 150, 20), 2)

            # Focus status indicator (top-right)
            status_color = (0, 255, 100) if gs['is_focused'] else (255, 80, 80)
            status_label = "FOCUSED" if gs['is_focused'] else "UNFOCUSED"
            status_text = font_tiny.render(status_label, True, status_color)
            screen.blit(status_text, (WIDTH - status_text.get_width() - 20, 20))
            
            # LSL indicator
            lsl_color = (0, 200, 0) if has_lsl else (255, 100, 100)
            lsl_label = "LSL" if has_lsl else "MOUSE"
            lsl_text = font_tiny.render(lsl_label, True, lsl_color)
            screen.blit(lsl_text, (WIDTH - lsl_text.get_width() - 20, 45))

        elif game_state == STATE_START:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            title = font_large.render("NEUROFEEDBACK ODYSSEY", True, (0, 200, 255))
            hint = font_small.render("Focus to fly up, relax to drift down", True, (255, 255, 255))
            hint2 = font_small.render("Press SPACE to Start", True, (200, 200, 200))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2))
            screen.blit(hint2, (WIDTH//2 - hint2.get_width()//2, HEIGHT//2 + 40))
            
            # LSL status on start screen
            if has_lsl:
                lsl_status = font_tiny.render("LSL Connected (openvibeMarkers)", True, (0, 200, 0))
            else:
                lsl_status = font_tiny.render("No LSL — Mouse fallback active", True, (255, 100, 100))
            screen.blit(lsl_status, (WIDTH//2 - lsl_status.get_width()//2, HEIGHT - 60))

        elif game_state == STATE_GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            text = font_large.render("MISSION FAILED", True, (255, 255, 255))
            score_final = font_small.render(f"Final Score: {gs['score']}. Press SPACE", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3))
            screen.blit(score_final, (WIDTH//2 - score_final.get_width()//2, HEIGHT//2))

        elif game_state == STATE_WIN:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 100, 0, 180))
            screen.blit(overlay, (0, 0))
            text = font_large.render("MISSION ACCOMPLISHED", True, (255, 255, 255))
            score_final = font_small.render(f"Final Score: {gs['score']}. Press SPACE", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//3))
            screen.blit(score_final, (WIDTH//2 - score_final.get_width()//2, HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

import pygame
import random
import math
import sys

pygame.init()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 480, 720
FPS = 60
GRAVITY = 0.45
FLAP_STRENGTH = -8.5
BIRD_X = 100
BIRD_RADIUS = 16

PIPE_WIDTH = 60
PIPE_GAP = 170
PIPE_SPAWN_BASE = 90  # frames between pipes at start
PIPE_SPEED_BASE = 3.0

# Colors – neon cyberpunk palette
BG_TOP = (5, 5, 30)
BG_BOT = (15, 0, 40)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 200)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 165, 0)
NEON_YELLOW = (255, 255, 0)
NEON_RED = (255, 50, 50)
NEON_PURPLE = (180, 0, 255)
PIPE_COLOR = (0, 200, 180)
PIPE_GLOW = (0, 255, 220, 60)
WHITE = (255, 255, 255)
DIM_WHITE = (180, 180, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird – Neon Cyberpunk")
clock = pygame.time.Clock()

# Fonts
font_big = pygame.font.SysFont("Courier New", 54, bold=True)
font_med = pygame.font.SysFont("Courier New", 30, bold=True)
font_sm = pygame.font.SysFont("Courier New", 20)
font_xs = pygame.font.SysFont("Courier New", 16)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = lerp_color(BG_TOP, BG_BOT, t)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def glow_circle(surface, color, center, radius, intensity=3):
    """Draw layered transparent circles to simulate a glow."""
    s = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for i in range(intensity, 0, -1):
        alpha = max(15, 50 // i)
        r = radius + i * 4
        pygame.draw.circle(
            s,
            (*color[:3], alpha),
            (radius * 2, radius * 2),
            r,
        )
    pygame.draw.circle(s, color, (radius * 2, radius * 2), radius)
    surface.blit(s, (center[0] - radius * 2, center[1] - radius * 2))


def glow_text(surface, text, font, color, pos, glow_color=None, center=False):
    """Render text with a neon glow behind it."""
    if glow_color is None:
        glow_color = color
    rendered = font.render(text, True, color)
    glow = font.render(text, True, glow_color)
    glow_surf = pygame.Surface(
        (rendered.get_width() + 16, rendered.get_height() + 16), pygame.SRCALPHA
    )
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            glow_surf.blit(glow, (8 + dx, 8 + dy))
    # add alpha to the glow surface
    glow_surf.set_alpha(90)
    if center:
        rect = rendered.get_rect(center=pos)
        surface.blit(glow_surf, (rect.x - 8, rect.y - 8))
        surface.blit(rendered, rect)
    else:
        surface.blit(glow_surf, (pos[0] - 8, pos[1] - 8))
        surface.blit(rendered, pos)


# Pre-render background once (gradient is static)
bg_surface = pygame.Surface((WIDTH, HEIGHT))
draw_gradient_bg(bg_surface)

# Grid overlay for cyberpunk feel – drawn once
grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for x in range(0, WIDTH, 40):
    pygame.draw.line(grid_surface, (255, 255, 255, 12), (x, 0), (x, HEIGHT))
for y in range(0, HEIGHT, 40):
    pygame.draw.line(grid_surface, (255, 255, 255, 12), (0, y), (WIDTH, y))


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "radius")

    def __init__(self, x, y, color=None):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2
        self.life = random.randint(25, 55)
        self.max_life = self.life
        self.color = color or random.choice(
            [NEON_CYAN, NEON_PINK, NEON_ORANGE, NEON_YELLOW, NEON_GREEN]
        )
        self.radius = random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.vy += 0.12
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        t = self.life / self.max_life
        alpha = int(255 * t)
        r = max(1, int(self.radius * t))
        s = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (r * 2, r * 2), r)
        # outer glow
        pygame.draw.circle(s, (*self.color[:3], alpha // 4), (r * 2, r * 2), r * 2)
        surface.blit(s, (int(self.x) - r * 2, int(self.y) - r * 2))


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, x, y, count=40, color=None):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()


# ---------------------------------------------------------------------------
# Bird
# ---------------------------------------------------------------------------
class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT / 2
        self.vel = 0
        self.radius = BIRD_RADIUS
        self.angle = 0
        self.trail: list[tuple[float, float, float]] = []  # x, y, alpha

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        # target angle based on velocity
        target = max(-30, min(70, self.vel * 4))
        self.angle += (target - self.angle) * 0.15
        # trail
        self.trail.append((self.x, self.y, 1.0))
        if len(self.trail) > 14:
            self.trail.pop(0)
        # fade trail
        self.trail = [(x, y, a - 0.07) for x, y, a in self.trail if a > 0.07]

    def draw(self, surface, pulse=0):
        # Draw trail
        for i, (tx, ty, ta) in enumerate(self.trail):
            r = max(1, int(self.radius * 0.4 * ta))
            alpha = int(120 * ta)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*NEON_CYAN[:3], alpha), (r, r), r)
            surface.blit(s, (int(tx) - r, int(ty) - r))

        # Body glow
        glow_r = self.radius + 6 + int(pulse * 3)
        gs = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*NEON_CYAN[:3], 35), (glow_r * 2, glow_r * 2), glow_r)
        surface.blit(
            gs, (int(self.x) - glow_r * 2, int(self.y) - glow_r * 2)
        )

        # Main body
        pygame.draw.circle(
            surface, NEON_CYAN, (int(self.x), int(self.y)), self.radius
        )
        # Inner highlight
        pygame.draw.circle(
            surface, WHITE, (int(self.x) - 3, int(self.y) - 3), self.radius // 3
        )

        # Eye
        eye_x = int(self.x + 7)
        eye_y = int(self.y - 4)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (eye_x + 1, eye_y - 1), 2)

        # Beak
        beak_pts = [
            (int(self.x + self.radius), int(self.y)),
            (int(self.x + self.radius + 10), int(self.y + 2)),
            (int(self.x + self.radius - 2), int(self.y + 6)),
        ]
        pygame.draw.polygon(surface, NEON_ORANGE, beak_pts)

        # Wing (animated)
        wing_offset = math.sin(pygame.time.get_ticks() * 0.012) * 5
        wing_pts = [
            (int(self.x - 6), int(self.y)),
            (int(self.x - 18), int(self.y + wing_offset)),
            (int(self.x - 4), int(self.y + 8)),
        ]
        pygame.draw.polygon(surface, NEON_PINK, wing_pts)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius + 3,
            self.y - self.radius + 3,
            (self.radius - 3) * 2,
            (self.radius - 3) * 2,
        )


# ---------------------------------------------------------------------------
# Pipe
# ---------------------------------------------------------------------------
class Pipe:
    def __init__(self, x, gap_y, speed):
        self.x = x
        self.gap_y = gap_y
        self.speed = speed
        self.scored = False
        self.w = PIPE_WIDTH
        self.gap = PIPE_GAP

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        # Top pipe
        top_rect = pygame.Rect(int(self.x), 0, self.w, self.gap_y - self.gap // 2)
        # Bottom pipe
        bot_y = self.gap_y + self.gap // 2
        bot_rect = pygame.Rect(int(self.x), bot_y, self.w, HEIGHT - bot_y)

        # Glow behind pipes
        glow_s = pygame.Surface((self.w + 16, HEIGHT), pygame.SRCALPHA)
        if top_rect.height > 0:
            pygame.draw.rect(
                glow_s,
                (*PIPE_COLOR[:3], 25),
                (0, 0, self.w + 16, top_rect.height + 8),
                border_radius=6,
            )
        pygame.draw.rect(
            glow_s,
            (*PIPE_COLOR[:3], 25),
            (0, bot_y - 8, self.w + 16, HEIGHT - bot_y + 8),
            border_radius=6,
        )
        surface.blit(glow_s, (int(self.x) - 8, 0))

        # Main pipe body with gradient stripes
        for rect in (top_rect, bot_rect):
            if rect.height <= 0:
                continue
            pygame.draw.rect(surface, PIPE_COLOR, rect, border_radius=4)
            # Neon edge lines
            pygame.draw.rect(surface, NEON_GREEN, rect, width=2, border_radius=4)
            # Stripe accents
            for sy in range(rect.top + 10, rect.bottom - 4, 20):
                pygame.draw.line(
                    surface,
                    (*NEON_GREEN[:3],),
                    (rect.left + 6, sy),
                    (rect.right - 6, sy),
                    1,
                )

        # Lip / cap at gap edges
        cap_h = 12
        top_cap = pygame.Rect(int(self.x) - 4, self.gap_y - self.gap // 2 - cap_h, self.w + 8, cap_h)
        bot_cap = pygame.Rect(int(self.x) - 4, self.gap_y + self.gap // 2, self.w + 8, cap_h)
        for cap in (top_cap, bot_cap):
            pygame.draw.rect(surface, NEON_GREEN, cap, border_radius=3)
            pygame.draw.rect(surface, WHITE, cap, width=1, border_radius=3)

    def off_screen(self):
        return self.x + self.w < -10

    def get_rects(self):
        top = pygame.Rect(int(self.x), 0, self.w, self.gap_y - self.gap // 2)
        bot_y = self.gap_y + self.gap // 2
        bot = pygame.Rect(int(self.x), bot_y, self.w, HEIGHT - bot_y)
        return top, bot


# ---------------------------------------------------------------------------
# Scanline / CRT overlay (subtle)
# ---------------------------------------------------------------------------
scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 3):
    pygame.draw.line(scanline_surf, (0, 0, 0, 18), (0, y), (WIDTH, y))


# ---------------------------------------------------------------------------
# Ground "horizon" line
# ---------------------------------------------------------------------------
GROUND_Y = HEIGHT - 50


def draw_ground(surface, offset):
    # glowing ground line
    pygame.draw.line(surface, NEON_PINK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    # glow
    gs = pygame.Surface((WIDTH, 10), pygame.SRCALPHA)
    pygame.draw.rect(gs, (*NEON_PINK[:3], 30), (0, 0, WIDTH, 10))
    surface.blit(gs, (0, GROUND_Y - 3))
    # moving dashes
    dash_len = 20
    gap = 30
    ox = int(offset) % (dash_len + gap)
    for x in range(-ox, WIDTH + dash_len, dash_len + gap):
        pygame.draw.line(surface, NEON_PINK, (x, GROUND_Y + 12), (x + dash_len, GROUND_Y + 12), 1)

    # "city" silhouette (simple rectangles)
    random.seed(42)  # deterministic skyline
    for bx in range(0, WIDTH, 28):
        bh = random.randint(15, 60)
        bw = random.randint(14, 24)
        rect = pygame.Rect(bx, GROUND_Y - bh, bw, bh)
        pygame.draw.rect(surface, (10, 5, 30), rect)
        pygame.draw.rect(surface, (*NEON_PURPLE[:3],), rect, 1)
        # tiny window lights
        for wy in range(rect.top + 4, rect.bottom - 4, 8):
            for wx in range(rect.left + 3, rect.right - 3, 7):
                if random.random() < 0.4:
                    pygame.draw.rect(surface, NEON_YELLOW, (wx, wy, 3, 3))
    random.seed()  # restore randomness


# ---------------------------------------------------------------------------
# Stars (static)
# ---------------------------------------------------------------------------
stars = [(random.randint(0, WIDTH), random.randint(0, GROUND_Y - 60), random.uniform(0.5, 2)) for _ in range(60)]


def draw_stars(surface, tick):
    for sx, sy, sr in stars:
        flicker = 0.6 + 0.4 * math.sin(tick * 0.03 + sx)
        alpha = int(180 * flicker)
        r = max(1, int(sr * flicker))
        s = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (r * 2, r * 2), r)
        surface.blit(s, (sx - r * 2, sy - r * 2))


# ---------------------------------------------------------------------------
# Game class
# ---------------------------------------------------------------------------
class Game:
    STATE_MENU = 0
    STATE_PLAY = 1
    STATE_OVER = 2

    def __init__(self):
        self.state = self.STATE_MENU
        self.bird = Bird()
        self.pipes: list[Pipe] = []
        self.particles = ParticleSystem()
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.pipe_timer = 0
        self.ground_offset = 0.0
        self.tick = 0
        self.flash_alpha = 0
        self.death_cooldown = 0

        # difficulty
        self.pipe_speed = PIPE_SPEED_BASE
        self.pipe_spawn_rate = PIPE_SPAWN_BASE

    # -- difficulty helpers --
    def _update_difficulty(self):
        level = self.score // 5
        self.pipe_speed = PIPE_SPEED_BASE + level * 0.4
        self.pipe_spawn_rate = max(45, PIPE_SPAWN_BASE - level * 6)

    # -- reset for new life --
    def _respawn_bird(self):
        self.bird = Bird()
        self.pipes.clear()
        self.pipe_timer = 0
        self.death_cooldown = 30

    # -- full reset --
    def _reset(self):
        self.bird = Bird()
        self.pipes.clear()
        self.particles.clear()
        self.score = 0
        self.lives = 3
        self.pipe_timer = 0
        self.pipe_speed = PIPE_SPEED_BASE
        self.pipe_spawn_rate = PIPE_SPAWN_BASE
        self.flash_alpha = 0
        self.death_cooldown = 0

    def _handle_death(self):
        self.particles.emit(self.bird.x, self.bird.y, count=55)
        self.flash_alpha = 180
        self.lives -= 1
        if self.lives <= 0:
            self.state = self.STATE_OVER
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            self._respawn_bird()

    def _spawn_pipe(self):
        gap_y = random.randint(100 + PIPE_GAP // 2, GROUND_Y - 80 - PIPE_GAP // 2)
        self.pipes.append(Pipe(WIDTH + 20, gap_y, self.pipe_speed))

    # -- main input --
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_MENU:
                    self._reset()
                    self.state = self.STATE_PLAY
                elif self.state == self.STATE_PLAY:
                    if self.death_cooldown <= 0:
                        self.bird.flap()
                        self.particles.emit(
                            self.bird.x - 8, self.bird.y + 8, count=5, color=NEON_CYAN
                        )
                elif self.state == self.STATE_OVER:
                    self._reset()
                    self.state = self.STATE_MENU

    # -- update --
    def update(self):
        self.tick += 1
        self.particles.update()

        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 8)

        if self.state == self.STATE_PLAY:
            if self.death_cooldown > 0:
                self.death_cooldown -= 1
                return

            self.bird.update()
            self.ground_offset += self.pipe_speed

            # pipe spawn
            self.pipe_timer += 1
            if self.pipe_timer >= self.pipe_spawn_rate:
                self.pipe_timer = 0
                self._spawn_pipe()

            # update pipes
            for p in self.pipes:
                p.speed = self.pipe_speed
                p.update()

            # score
            for p in self.pipes:
                if not p.scored and p.x + p.w < self.bird.x:
                    p.scored = True
                    self.score += 1
                    self._update_difficulty()
                    self.particles.emit(
                        self.bird.x, self.bird.y, count=8, color=NEON_GREEN
                    )

            # remove off-screen
            self.pipes = [p for p in self.pipes if not p.off_screen()]

            # collision – pipes
            bird_rect = self.bird.get_rect()
            for p in self.pipes:
                top_r, bot_r = p.get_rects()
                if bird_rect.colliderect(top_r) or bird_rect.colliderect(bot_r):
                    self._handle_death()
                    return

            # collision – ceiling / ground
            if self.bird.y - self.bird.radius < 0 or self.bird.y + self.bird.radius > GROUND_Y:
                self._handle_death()
                return

        elif self.state == self.STATE_MENU:
            # gentle hover
            self.bird.y = HEIGHT / 2 + math.sin(self.tick * 0.04) * 20
            self.ground_offset += 1.5

    # -- draw --
    def draw(self):
        # Background
        screen.blit(bg_surface, (0, 0))
        screen.blit(grid_surface, (0, 0))
        draw_stars(screen, self.tick)

        # Ground + city
        draw_ground(screen, self.ground_offset)

        # Pipes
        for p in self.pipes:
            p.draw(screen)

        # Bird
        pulse = math.sin(self.tick * 0.1) * 0.5 + 0.5
        if self.state != self.STATE_OVER:
            self.bird.draw(screen, pulse)

        # Particles
        self.particles.draw(screen)

        # Flash on death
        if self.flash_alpha > 0:
            fs = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 255, 255, self.flash_alpha))
            screen.blit(fs, (0, 0))

        # HUD
        if self.state == self.STATE_PLAY:
            self._draw_hud()
        elif self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_OVER:
            self._draw_game_over()

        # Scanlines
        screen.blit(scanline_surf, (0, 0))

        pygame.display.flip()

    def _draw_hud(self):
        # Score
        glow_text(screen, str(self.score), font_big, NEON_CYAN, (WIDTH // 2, 60), center=True)
        # High score
        glow_text(screen, f"HI: {self.high_score}", font_xs, NEON_YELLOW, (WIDTH - 10, 10))
        # align right
        hi_surf = font_xs.render(f"HI: {self.high_score}", True, NEON_YELLOW)
        # Lives
        for i in range(self.lives):
            cx = 28 + i * 30
            cy = 28
            pygame.draw.circle(screen, NEON_PINK, (cx, cy), 8)
            pygame.draw.circle(screen, WHITE, (cx - 2, cy - 2), 3)

        # Level indicator
        level = self.score // 5 + 1
        glow_text(screen, f"LV {level}", font_xs, NEON_PURPLE, (WIDTH // 2, 95), center=True)

    def _draw_menu(self):
        # Title
        glow_text(
            screen, "FLAPPY BIRD", font_big, NEON_CYAN, (WIDTH // 2, HEIGHT // 4), center=True
        )
        glow_text(
            screen, "NEON EDITION", font_med, NEON_PINK, (WIDTH // 2, HEIGHT // 4 + 55), center=True
        )

        # Pulsing prompt
        alpha = int(160 + 95 * math.sin(self.tick * 0.06))
        prompt_color = (*NEON_GREEN[:3],)
        glow_text(
            screen,
            "PRESS SPACE",
            font_med,
            prompt_color,
            (WIDTH // 2, HEIGHT // 2 + 60),
            center=True,
        )

        # Instructions
        glow_text(screen, "SPACE to flap  |  3 lives", font_xs, DIM_WHITE, (WIDTH // 2, HEIGHT // 2 + 120), center=True)
        glow_text(screen, "Difficulty ramps every 5 pts", font_xs, DIM_WHITE, (WIDTH // 2, HEIGHT // 2 + 148), center=True)

        if self.high_score > 0:
            glow_text(
                screen,
                f"BEST: {self.high_score}",
                font_med,
                NEON_YELLOW,
                (WIDTH // 2, HEIGHT // 2 + 200),
                center=True,
            )

    def _draw_game_over(self):
        # Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        glow_text(screen, "GAME OVER", font_big, NEON_RED, (WIDTH // 2, HEIGHT // 3), center=True)

        glow_text(
            screen,
            f"SCORE: {self.score}",
            font_med,
            NEON_CYAN,
            (WIDTH // 2, HEIGHT // 3 + 70),
            center=True,
        )
        glow_text(
            screen,
            f"BEST:  {self.high_score}",
            font_med,
            NEON_YELLOW,
            (WIDTH // 2, HEIGHT // 3 + 110),
            center=True,
        )

        # new high score banner
        if self.score >= self.high_score and self.score > 0:
            glow_text(
                screen,
                "★ NEW HIGH SCORE ★",
                font_sm,
                NEON_ORANGE,
                (WIDTH // 2, HEIGHT // 3 + 155),
                center=True,
            )

        pulse_alpha = int(160 + 95 * math.sin(self.tick * 0.06))
        glow_text(
            screen,
            "PRESS SPACE",
            font_med,
            NEON_GREEN,
            (WIDTH // 2, HEIGHT // 2 + 130),
            center=True,
        )


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    game = Game()
    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        game.update()
        game.draw()
        clock.tick(FPS)


if __name__ == "__main__":
    main()

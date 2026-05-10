import pygame
import random
import math
import sys
import save_manager
import themes as th
from sound_engine import SoundEngine

pygame.mixer.pre_init(44100, -16, 2, 512)
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
PIPE_SPAWN_BASE = 90
PIPE_SPEED_BASE = 3.0
WHITE = (255, 255, 255)
DIM_WHITE = (180, 180, 200)
GROUND_Y = HEIGHT - 50

# ---------------------------------------------------------------------------
# Display manager
# ---------------------------------------------------------------------------
class Display:
    def __init__(self):
        self.full = False
        self.game_surf = pygame.Surface((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird – Neon Edition")

    def toggle(self):
        self.full = not self.full
        if self.full:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def present(self, surf):
        if self.full:
            sw, sh = self.screen.get_size()
            s = min(sw / WIDTH, sh / HEIGHT)
            nw, nh = int(WIDTH * s), int(HEIGHT * s)
            scaled = pygame.transform.smoothscale(surf, (nw, nh))
            self.screen.fill((0, 0, 0))
            self.screen.blit(scaled, ((sw - nw) // 2, (sh - nh) // 2))
        else:
            self.screen.blit(surf, (0, 0))
        pygame.display.flip()

display = Display()
clock = pygame.time.Clock()

# Fonts
font_big = pygame.font.SysFont("Courier New", 54, bold=True)
font_med = pygame.font.SysFont("Courier New", 30, bold=True)
font_sm = pygame.font.SysFont("Courier New", 20)
font_xs = pygame.font.SysFont("Courier New", 16)
font_xxs = pygame.font.SysFont("Courier New", 13)

# Load save & theme
save_data = save_manager.load()
current_theme = th.get_theme(save_data["selected_theme"])

# Sound
sound = SoundEngine()
sound.music_on = save_data.get("music_on", True)
sound.sfx_on = save_data.get("sfx_on", True)

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def glow_text(surface, text, font, color, pos, glow_color=None, center=False):
    if glow_color is None:
        glow_color = color
    rendered = font.render(text, True, color)
    glow = font.render(text, True, glow_color)
    gs = pygame.Surface((rendered.get_width() + 16, rendered.get_height() + 16), pygame.SRCALPHA)
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            gs.blit(glow, (8 + dx, 8 + dy))
    gs.set_alpha(90)
    if center:
        rect = rendered.get_rect(center=pos)
        surface.blit(gs, (rect.x - 8, rect.y - 8))
        surface.blit(rendered, rect)
    else:
        surface.blit(gs, (pos[0] - 8, pos[1] - 8))
        surface.blit(rendered, pos)

# ---------------------------------------------------------------------------
# Theme-dependent surfaces (rebuilt on theme change)
# ---------------------------------------------------------------------------
bg_surface = pygame.Surface((WIDTH, HEIGHT))
grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

def rebuild_surfaces():
    global bg_surface, grid_surface, scanline_surf
    T = current_theme
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = lerp_color(T.bg_top, T.bg_bot, t)
        pygame.draw.line(bg_surface, c, (0, y), (WIDTH, y))
    grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(grid_surface, (255, 255, 255, 12), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(grid_surface, (255, 255, 255, 12), (0, y), (WIDTH, y))
    scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 3):
        pygame.draw.line(scanline_surf, (0, 0, 0, 18), (0, y), (WIDTH, y))

rebuild_surfaces()

stars = [(random.randint(0, WIDTH), random.randint(0, GROUND_Y - 60), random.uniform(0.5, 2)) for _ in range(60)]

def draw_stars(surface, tick):
    for sx, sy, sr in stars:
        flicker = 0.6 + 0.4 * math.sin(tick * 0.03 + sx)
        alpha = int(180 * flicker)
        r = max(1, int(sr * flicker))
        s = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, alpha), (r * 2, r * 2), r)
        surface.blit(s, (sx - r * 2, sy - r * 2))

def draw_ground(surface, offset):
    T = current_theme
    pygame.draw.line(surface, T.ground, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    gs = pygame.Surface((WIDTH, 10), pygame.SRCALPHA)
    pygame.draw.rect(gs, (*T.ground[:3], 30), (0, 0, WIDTH, 10))
    surface.blit(gs, (0, GROUND_Y - 3))
    dash_len, gap = 20, 30
    ox = int(offset) % (dash_len + gap)
    for x in range(-ox, WIDTH + dash_len, dash_len + gap):
        pygame.draw.line(surface, T.ground, (x, GROUND_Y + 12), (x + dash_len, GROUND_Y + 12), 1)
    random.seed(42)
    for bx in range(0, WIDTH, 28):
        bh = random.randint(15, 60)
        bw = random.randint(14, 24)
        rect = pygame.Rect(bx, GROUND_Y - bh, bw, bh)
        pygame.draw.rect(surface, (10, 5, 30), rect)
        pygame.draw.rect(surface, T.accent4, rect, 1)
        for wy in range(rect.top + 4, rect.bottom - 4, 8):
            for wx in range(rect.left + 3, rect.right - 3, 7):
                if random.random() < 0.4:
                    pygame.draw.rect(surface, T.accent3, (wx, wy, 3, 3))
    random.seed()

# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "radius")
    def __init__(self, x, y, color=None):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.x, self.y = x, y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2
        self.life = random.randint(25, 55)
        self.max_life = self.life
        T = current_theme
        self.color = color or random.choice([T.bird, T.accent1, T.accent2, T.accent3, T.pipe_accent])
        self.radius = random.uniform(2, 5)
    def update(self):
        self.x += self.vx; self.vy += 0.12; self.y += self.vy; self.life -= 1
    def draw(self, surface):
        t = self.life / self.max_life
        alpha = int(255 * t)
        r = max(1, int(self.radius * t))
        s = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (r * 2, r * 2), r)
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
        for p in self.particles: p.update()
    def draw(self, surface):
        for p in self.particles: p.draw(surface)
    def clear(self):
        self.particles.clear()

# ---------------------------------------------------------------------------
# Bird
# ---------------------------------------------------------------------------
class Bird:
    def __init__(self):
        self.x, self.y = BIRD_X, HEIGHT / 2
        self.vel = 0
        self.radius = BIRD_RADIUS
        self.angle = 0
        self.trail: list[tuple[float, float, float]] = []
    def flap(self):
        self.vel = FLAP_STRENGTH
    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        target = max(-30, min(70, self.vel * 4))
        self.angle += (target - self.angle) * 0.15
        self.trail.append((self.x, self.y, 1.0))
        if len(self.trail) > 14: self.trail.pop(0)
        self.trail = [(x, y, a - 0.07) for x, y, a in self.trail if a > 0.07]
    def draw(self, surface, pulse=0):
        T = current_theme
        for _, (tx, ty, ta) in enumerate(self.trail):
            r = max(1, int(self.radius * 0.4 * ta))
            alpha = int(120 * ta)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*T.bird[:3], alpha), (r, r), r)
            surface.blit(s, (int(tx) - r, int(ty) - r))
        glow_r = self.radius + 6 + int(pulse * 3)
        gs = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*T.bird[:3], 35), (glow_r * 2, glow_r * 2), glow_r)
        surface.blit(gs, (int(self.x) - glow_r * 2, int(self.y) - glow_r * 2))
        pygame.draw.circle(surface, T.bird, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x) - 3, int(self.y) - 3), self.radius // 3)
        ex, ey = int(self.x + 7), int(self.y - 4)
        pygame.draw.circle(surface, (0, 0, 0), (ex, ey), 4)
        pygame.draw.circle(surface, WHITE, (ex + 1, ey - 1), 2)
        beak = [(int(self.x + self.radius), int(self.y)),
                (int(self.x + self.radius + 10), int(self.y + 2)),
                (int(self.x + self.radius - 2), int(self.y + 6))]
        pygame.draw.polygon(surface, T.accent2, beak)
        wo = math.sin(pygame.time.get_ticks() * 0.012) * 5
        wing = [(int(self.x - 6), int(self.y)),
                (int(self.x - 18), int(self.y + wo)),
                (int(self.x - 4), int(self.y + 8))]
        pygame.draw.polygon(surface, T.accent1, wing)
    def get_rect(self):
        return pygame.Rect(self.x - self.radius + 3, self.y - self.radius + 3,
                           (self.radius - 3) * 2, (self.radius - 3) * 2)

# ---------------------------------------------------------------------------
# Pipe
# ---------------------------------------------------------------------------
class Pipe:
    def __init__(self, x, gap_y, speed):
        self.x, self.gap_y, self.speed = x, gap_y, speed
        self.scored = False
        self.w, self.gap = PIPE_WIDTH, PIPE_GAP
    def update(self):
        self.x -= self.speed
    def draw(self, surface):
        T = current_theme
        top_rect = pygame.Rect(int(self.x), 0, self.w, self.gap_y - self.gap // 2)
        bot_y = self.gap_y + self.gap // 2
        bot_rect = pygame.Rect(int(self.x), bot_y, self.w, HEIGHT - bot_y)
        gs = pygame.Surface((self.w + 16, HEIGHT), pygame.SRCALPHA)
        if top_rect.height > 0:
            pygame.draw.rect(gs, (*T.pipe[:3], 25), (0, 0, self.w + 16, top_rect.height + 8), border_radius=6)
        pygame.draw.rect(gs, (*T.pipe[:3], 25), (0, bot_y - 8, self.w + 16, HEIGHT - bot_y + 8), border_radius=6)
        surface.blit(gs, (int(self.x) - 8, 0))
        for rect in (top_rect, bot_rect):
            if rect.height <= 0: continue
            pygame.draw.rect(surface, T.pipe, rect, border_radius=4)
            pygame.draw.rect(surface, T.pipe_accent, rect, width=2, border_radius=4)
            for sy in range(rect.top + 10, rect.bottom - 4, 20):
                pygame.draw.line(surface, T.pipe_accent, (rect.left + 6, sy), (rect.right - 6, sy), 1)
        cap_h = 12
        tc = pygame.Rect(int(self.x) - 4, self.gap_y - self.gap // 2 - cap_h, self.w + 8, cap_h)
        bc = pygame.Rect(int(self.x) - 4, self.gap_y + self.gap // 2, self.w + 8, cap_h)
        for cap in (tc, bc):
            pygame.draw.rect(surface, T.pipe_accent, cap, border_radius=3)
            pygame.draw.rect(surface, WHITE, cap, width=1, border_radius=3)
    def off_screen(self):
        return self.x + self.w < -10
    def get_rects(self):
        top = pygame.Rect(int(self.x), 0, self.w, self.gap_y - self.gap // 2)
        by = self.gap_y + self.gap // 2
        return top, pygame.Rect(int(self.x), by, self.w, HEIGHT - by)

# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    STATE_MENU, STATE_PLAY, STATE_OVER = 0, 1, 2

    def __init__(self):
        self.state = self.STATE_MENU
        self.bird = Bird()
        self.pipes: list[Pipe] = []
        self.particles = ParticleSystem()
        self.score = 0
        self.high_score = save_data["high_score"]
        self.lives = 3
        self.pipe_timer = 0
        self.ground_offset = 0.0
        self.tick = 0
        self.flash_alpha = 0
        self.death_cooldown = 0
        self.pipe_speed = PIPE_SPEED_BASE
        self.pipe_spawn_rate = PIPE_SPAWN_BASE
        self.unlock_msg = ""
        self.unlock_timer = 0
        self.theme_idx = next((i for i, t in enumerate(th.ALL_THEMES) if t.name == current_theme.name), 0)

    def _update_difficulty(self):
        level = self.score // 5
        self.pipe_speed = PIPE_SPEED_BASE + level * 0.4
        self.pipe_spawn_rate = max(45, PIPE_SPAWN_BASE - level * 6)

    def _respawn_bird(self):
        self.bird = Bird()
        self.pipes.clear()
        self.pipe_timer = 0
        self.death_cooldown = 30

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
        sound.play_death()
        if self.lives <= 0:
            self.state = self.STATE_OVER
            self._is_new_high = self.score > self.high_score
            if self._is_new_high:
                self.high_score = self.score
            save_manager.add_score(save_data, self.score, current_theme.name)
            save_manager.save(save_data)
            self._check_unlocks()
        else:
            self._respawn_bird()

    def _check_unlocks(self):
        new = th.check_unlocks(self.high_score, save_data["unlocked_themes"])
        for n in new:
            save_data["unlocked_themes"].append(n)
            t = th.get_theme(n)
            self.unlock_msg = f"UNLOCKED: {t.display}"
            self.unlock_timer = 180
            sound.play_unlock()
        if new:
            save_manager.save(save_data)

    def _spawn_pipe(self):
        gap_y = random.randint(100 + PIPE_GAP // 2, GROUND_Y - 80 - PIPE_GAP // 2)
        self.pipes.append(Pipe(WIDTH + 20, gap_y, self.pipe_speed))

    def _cycle_theme(self, d=1):
        global current_theme
        unlocked = save_data["unlocked_themes"]
        indices = [i for i, t in enumerate(th.ALL_THEMES) if t.name in unlocked]
        if len(indices) < 2:
            return
        cur = indices.index(self.theme_idx) if self.theme_idx in indices else 0
        cur = (cur + d) % len(indices)
        self.theme_idx = indices[cur]
        current_theme = th.ALL_THEMES[self.theme_idx]
        save_data["selected_theme"] = current_theme.name
        save_manager.save(save_data)
        rebuild_surfaces()

    def _save_and_quit(self):
        save_data["music_on"] = sound.music_on
        save_data["sfx_on"] = sound.sfx_on
        save_manager.save(save_data)
        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._save_and_quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_MENU:
                    self._reset()
                    self._is_new_high = False
                    self.state = self.STATE_PLAY
                elif self.state == self.STATE_PLAY and self.death_cooldown <= 0:
                    self.bird.flap()
                    self.particles.emit(self.bird.x - 8, self.bird.y + 8, count=5, color=current_theme.bird)
                    sound.play_flap()
                elif self.state == self.STATE_OVER:
                    self._reset()
                    self.state = self.STATE_MENU
            elif event.key == pygame.K_F11:
                display.toggle()
            elif event.key == pygame.K_ESCAPE and display.full:
                display.toggle()
            elif event.key == pygame.K_t and self.state == self.STATE_MENU:
                self._cycle_theme()
            elif event.key == pygame.K_m:
                sound.toggle_music()
                save_data["music_on"] = sound.music_on
                save_manager.save(save_data)

    def update(self):
        self.tick += 1
        self.particles.update()
        if self.unlock_timer > 0:
            self.unlock_timer -= 1
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 8)
        if self.state == self.STATE_PLAY:
            if self.death_cooldown > 0:
                self.death_cooldown -= 1; return
            self.bird.update()
            self.ground_offset += self.pipe_speed
            self.pipe_timer += 1
            if self.pipe_timer >= self.pipe_spawn_rate:
                self.pipe_timer = 0; self._spawn_pipe()
            for p in self.pipes:
                p.speed = self.pipe_speed; p.update()
            for p in self.pipes:
                if not p.scored and p.x + p.w < self.bird.x:
                    p.scored = True; self.score += 1
                    self._update_difficulty()
                    self.particles.emit(self.bird.x, self.bird.y, count=8, color=current_theme.pipe_accent)
                    sound.play_score()
            self.pipes = [p for p in self.pipes if not p.off_screen()]
            br = self.bird.get_rect()
            for p in self.pipes:
                tr, btr = p.get_rects()
                if br.colliderect(tr) or br.colliderect(btr):
                    self._handle_death(); return
            if self.bird.y - self.bird.radius < 0 or self.bird.y + self.bird.radius > GROUND_Y:
                self._handle_death(); return
        elif self.state == self.STATE_MENU:
            self.bird.y = HEIGHT / 2 + math.sin(self.tick * 0.04) * 20
            self.ground_offset += 1.5

    def draw(self):
        T = current_theme
        surf = display.game_surf
        surf.blit(bg_surface, (0, 0))
        surf.blit(grid_surface, (0, 0))
        draw_stars(surf, self.tick)
        draw_ground(surf, self.ground_offset)
        for p in self.pipes: p.draw(surf)
        pulse = math.sin(self.tick * 0.1) * 0.5 + 0.5
        if self.state != self.STATE_OVER:
            self.bird.draw(surf, pulse)
        self.particles.draw(surf)
        if self.flash_alpha > 0:
            fs = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 255, 255, self.flash_alpha))
            surf.blit(fs, (0, 0))
        if self.state == self.STATE_PLAY: self._draw_hud(surf)
        elif self.state == self.STATE_MENU: self._draw_menu(surf)
        elif self.state == self.STATE_OVER: self._draw_game_over(surf)
        if self.unlock_timer > 0:
            glow_text(surf, self.unlock_msg, font_sm, T.accent3, (WIDTH // 2, HEIGHT - 80), center=True)
        surf.blit(scanline_surf, (0, 0))
        # audio status indicator
        m_icon = "[M] ON" if sound.music_on else "[M] OFF"
        glow_text(surf, m_icon, font_xxs, DIM_WHITE, (WIDTH - 60, HEIGHT - 20))
        display.present(surf)

    def _draw_hud(self, surf):
        T = current_theme
        glow_text(surf, str(self.score), font_big, T.bird, (WIDTH // 2, 60), center=True)
        glow_text(surf, f"HI: {self.high_score}", font_xs, T.accent3, (WIDTH - 10, 10))
        for i in range(self.lives):
            cx, cy = 28 + i * 30, 28
            pygame.draw.circle(surf, T.accent1, (cx, cy), 8)
            pygame.draw.circle(surf, WHITE, (cx - 2, cy - 2), 3)
        level = self.score // 5 + 1
        glow_text(surf, f"LV {level}", font_xs, T.accent4, (WIDTH // 2, 95), center=True)

    def _draw_menu(self, surf):
        T = current_theme
        glow_text(surf, "FLAPPY BIRD", font_big, T.bird, (WIDTH // 2, HEIGHT // 4), center=True)
        glow_text(surf, "NEON EDITION", font_med, T.accent1, (WIDTH // 2, HEIGHT // 4 + 55), center=True)
        glow_text(surf, "PRESS SPACE", font_med, T.pipe_accent, (WIDTH // 2, HEIGHT // 2 + 60), center=True)
        glow_text(surf, "SPACE flap | 3 lives | F11 fullscreen", font_xs, DIM_WHITE, (WIDTH // 2, HEIGHT // 2 + 120), center=True)
        glow_text(surf, "Difficulty ramps every 5 pts", font_xs, DIM_WHITE, (WIDTH // 2, HEIGHT // 2 + 148), center=True)
        # Theme selector
        n_unlocked = len(save_data["unlocked_themes"])
        theme_line = f"Theme: {T.display}"
        if n_unlocked > 1:
            theme_line += "  [T] cycle"
        glow_text(surf, theme_line, font_xs, T.accent2, (WIDTH // 2, HEIGHT // 2 + 185), center=True)
        # Locked themes hint
        locked = [t for t in th.ALL_THEMES if t.name not in save_data["unlocked_themes"]]
        if locked:
            nxt = locked[0]
            glow_text(surf, f"Next unlock at score {nxt.unlock_at}", font_xxs, DIM_WHITE, (WIDTH // 2, HEIGHT // 2 + 210), center=True)
        if self.high_score > 0:
            glow_text(surf, f"BEST: {self.high_score}", font_med, T.accent3, (WIDTH // 2, HEIGHT // 2 + 245), center=True)

    def _draw_game_over(self, surf):
        T = current_theme
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        surf.blit(ov, (0, 0))
        glow_text(surf, "GAME OVER", font_big, T.danger, (WIDTH // 2, HEIGHT // 3), center=True)
        glow_text(surf, f"SCORE: {self.score}", font_med, T.bird, (WIDTH // 2, HEIGHT // 3 + 70), center=True)
        glow_text(surf, f"BEST:  {self.high_score}", font_med, T.accent3, (WIDTH // 2, HEIGHT // 3 + 110), center=True)
        if getattr(self, '_is_new_high', False) and self.score > 0:
            glow_text(surf, "★ NEW HIGH SCORE ★", font_sm, T.accent2, (WIDTH // 2, HEIGHT // 3 + 155), center=True)
        glow_text(surf, "PRESS SPACE", font_med, T.pipe_accent, (WIDTH // 2, HEIGHT // 2 + 130), center=True)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    game = Game()
    sound.start_music()
    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

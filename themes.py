"""Color themes with unlock thresholds."""


class Theme:
    def __init__(self, name, display, colors, unlock_at=0):
        self.name = name
        self.display = display
        self.unlock_at = unlock_at
        self.bg_top = colors["bg_top"]
        self.bg_bot = colors["bg_bot"]
        self.bird = colors["bird"]
        self.pipe = colors["pipe"]
        self.pipe_accent = colors["pipe_accent"]
        self.ground = colors["ground"]
        self.accent1 = colors["accent1"]      # pink equiv
        self.accent2 = colors["accent2"]      # orange equiv
        self.accent3 = colors["accent3"]      # yellow equiv
        self.accent4 = colors["accent4"]      # purple equiv
        self.danger = colors["danger"]
        self.white = (255, 255, 255)
        self.dim = (180, 180, 200)


ALL_THEMES = [
    Theme("cyberpunk", "NEON CYBERPUNK", {
        "bg_top": (5, 5, 30), "bg_bot": (15, 0, 40),
        "bird": (0, 255, 255), "pipe": (0, 200, 180),
        "pipe_accent": (57, 255, 20), "ground": (255, 0, 200),
        "accent1": (255, 0, 200), "accent2": (255, 165, 0),
        "accent3": (255, 255, 0), "accent4": (180, 0, 255),
        "danger": (255, 50, 50),
    }, unlock_at=0),

    Theme("vaporwave", "V A P O R W A V E", {
        "bg_top": (20, 0, 40), "bg_bot": (60, 0, 80),
        "bird": (255, 113, 206), "pipe": (1, 205, 254),
        "pipe_accent": (185, 103, 255), "ground": (5, 255, 161),
        "accent1": (1, 205, 254), "accent2": (255, 113, 206),
        "accent3": (5, 255, 161), "accent4": (185, 103, 255),
        "danger": (255, 50, 100),
    }, unlock_at=5),

    Theme("matrix", "THE MATRIX", {
        "bg_top": (0, 5, 0), "bg_bot": (0, 15, 5),
        "bird": (0, 255, 65), "pipe": (0, 180, 40),
        "pipe_accent": (0, 255, 0), "ground": (0, 200, 50),
        "accent1": (0, 200, 50), "accent2": (50, 255, 100),
        "accent3": (0, 255, 0), "accent4": (0, 150, 30),
        "danger": (255, 0, 0),
    }, unlock_at=10),

    Theme("sunset", "SUNSET DRIVE", {
        "bg_top": (20, 5, 30), "bg_bot": (80, 20, 10),
        "bird": (255, 200, 50), "pipe": (200, 80, 50),
        "pipe_accent": (255, 120, 0), "ground": (255, 50, 80),
        "accent1": (255, 50, 80), "accent2": (255, 200, 50),
        "accent3": (255, 255, 100), "accent4": (200, 50, 120),
        "danger": (255, 30, 30),
    }, unlock_at=20),

    Theme("arctic", "ARCTIC FROST", {
        "bg_top": (5, 10, 30), "bg_bot": (10, 20, 50),
        "bird": (150, 220, 255), "pipe": (80, 160, 200),
        "pipe_accent": (100, 200, 255), "ground": (200, 230, 255),
        "accent1": (200, 230, 255), "accent2": (150, 220, 255),
        "accent3": (220, 240, 255), "accent4": (100, 150, 220),
        "danger": (255, 100, 100),
    }, unlock_at=30),
]

THEME_MAP = {t.name: t for t in ALL_THEMES}


def get_theme(name):
    return THEME_MAP.get(name, ALL_THEMES[0])


def check_unlocks(score, already_unlocked):
    """Return list of newly unlocked theme names."""
    new = []
    for t in ALL_THEMES:
        if t.name not in already_unlocked and score >= t.unlock_at:
            new.append(t.name)
    return new

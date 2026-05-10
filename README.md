<div align="center">

# 🕹️ FLAPPY BIRD — NEON EDITION

### *The classic. Reimagined in neon.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-00D800?style=for-the-badge&logo=python&logoColor=white)](https://pygame.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/khushalv21/flappybirdgame?style=for-the-badge&color=yellow)](https://github.com/khushalv21/flappybirdgame)

<br/>

<img src="assets/gameplay.png" alt="Flappy Bird Neon Edition — Gameplay" width="480" />

<br/>

**A cyberpunk-themed Flappy Bird built from scratch in Python + Pygame.**  
Neon glow effects · Particle systems · CRT scanlines · Progressive difficulty · 3-life system

*No sprites. No assets. Every pixel is rendered in real-time.*

<br/>

[**▶ Play Now**](#-quickstart) · [**Features**](#-features) · [**How It Works**](#-architecture) · [**Contribute**](CONTRIBUTING.md)

</div>

---

## ⚡ Quickstart

Get flying in under 30 seconds:

```bash
# Clone
git clone https://github.com/khushalv21/flappybirdgame.git
cd flappybirdgame

# Setup
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

pip install -r requirements.txt

# Launch
python flappy_bird.py
```

> **That's it.** One file, one dependency, zero configuration.

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `SPACE` | Flap / Start Game / Return to Menu |

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🌆 Full Cyberpunk Aesthetic
- Navy-to-purple gradient sky
- Neon grid overlay
- Procedural city skyline with window lights
- Flickering star field
- CRT scanline post-processing

</td>
<td width="50%">

### 🐦 Expressive Bird
- Animated wing flaps
- Velocity-driven tilt angle
- Glowing cyan trail
- Neon particle burst on flap

</td>
</tr>
<tr>
<td>

### 💀 Progressive Difficulty
- Speed increases every **5 points**
- Pipe spawn rate accelerates
- Level indicator on HUD
- Gets *dangerously* fast at LV 4+

</td>
<td>

### 💖 3-Life System
- Die? Respawn and keep your score
- All 3 lives lost → Game Over
- Death flash + particle explosion
- High score tracking per session

</td>
</tr>
<tr>
<td>

### 🌈 Particle Engine
- Flap sparks (cyan)
- Score celebration (green)
- Death explosion (multicolor)
- Physics-based fade + gravity

</td>
<td>

### 🎯 Polished UX
- Neon glow text rendering
- Pulsing "PRESS SPACE" prompts
- Smooth menu → play → game over flow
- 60 FPS locked frame rate

</td>
</tr>
</table>

---

## 🏗 Architecture

The entire game is a **single 693-line Python file** — zero external assets, zero configuration files, zero build steps.

```
flappybirdgame/
├── flappy_bird.py      # The entire game
├── requirements.txt    # pygame>=2.5.0
├── assets/
│   └── gameplay.png    # Screenshot for README
├── LICENSE             # MIT
├── CONTRIBUTING.md
└── README.md
```

### Code Structure

| Section | Lines | What It Does |
|---------|-------|--------------|
| **Constants & Colors** | 1–46 | Neon palette, physics tuning, display config |
| **Utilities** | 49–111 | Gradient rendering, glow effects, grid overlay |
| **Particle System** | 114–169 | Pooled particles with alpha fade and physics |
| **Bird** | 172–255 | Player entity — trail, animation, collision rect |
| **Pipe** | 258–329 | Obstacles — glow, caps, stripe accents |
| **Environment** | 332–389 | Scanlines, ground, city skyline, stars |
| **Game** | 392–675 | State machine, input, physics, rendering |
| **Main Loop** | 678–693 | Entry point — event → update → draw @ 60 FPS |

> **Design philosophy:** Keep it in one file. No OOP ceremony. Anyone should be able to read top-to-bottom and understand the entire game in 15 minutes.

---

## 🧪 Why This Exists

Most Flappy Bird clones are sprite-based tutorials that look like homework assignments. This one asks:

> *What if Flappy Bird ran on an arcade machine in a Blade Runner alley?*

Every visual element — the glow, the particles, the scanlines, the city skyline — is **procedurally generated at runtime**. No PNGs, no spritesheets, no asset pipeline. Just `pygame.draw` and math.

This makes it:
- **Hackable** — Change a color constant and the whole aesthetic shifts
- **Educational** — See how real-time rendering effects actually work
- **Portable** — Runs anywhere Python + Pygame runs (macOS, Linux, Windows)

---

## 🔧 Customization

Want to make it yours? Tweak these constants at the top of `flappy_bird.py`:

```python
# Physics
GRAVITY = 0.45          # Higher = heavier bird
FLAP_STRENGTH = -8.5    # More negative = stronger flap
PIPE_GAP = 170          # Larger = easier
PIPE_SPEED_BASE = 3.0   # Starting scroll speed

# Palette — swap these for a totally different vibe
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 200)
NEON_GREEN = (57, 255, 20)
BG_TOP = (5, 5, 30)     # Sky gradient top
BG_BOT = (15, 0, 40)    # Sky gradient bottom
```

---

## 📋 Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.9+ |
| Pygame | 2.5+ |

No other dependencies. No build tools. No package managers beyond pip.

---

## 🚀 Roadmap

- [ ] 🎵 Sound effects & synthwave soundtrack
- [ ] 💾 Persistent high scores (JSON)
- [ ] 🎮 Gamepad support
- [ ] 🖥️ Fullscreen / resolution toggle
- [ ] 🌐 Online leaderboard
- [ ] 🎨 Unlockable color themes
- [ ] 📦 PyInstaller executable for non-developers

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Whether it's a new feature, a visual tweak, or a bug fix — PRs are open.

---

## 📄 License

MIT — do whatever you want with it. See [LICENSE](LICENSE).

---

<div align="center">

**Built with 💜 and too many neon colors**

*If this made you mass `SPACE` for 20 minutes straight, consider dropping a ⭐*

</div>

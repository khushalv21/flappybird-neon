# Contributing to Flappy Bird — Neon Edition

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

1. **Fork** the repo and clone your fork locally
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python flappy_bird.py
   ```

## Development Guidelines

- Keep the single-file architecture — the game is intentionally self-contained
- Maintain the neon cyberpunk aesthetic for any visual changes
- Test on Python 3.9+ before submitting
- Use descriptive commit messages

## Ideas for Contributions

- 🎵 Add sound effects and background music
- 🏆 Persistent high score storage (JSON/SQLite)
- 🎮 Gamepad/controller support
- 📱 Dynamic resolution / fullscreen toggle
- 🌐 Online leaderboard integration
- 🎨 Alternative visual themes (retro, minimal, pixel art)

## Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes with clear messages
3. Push to your fork and open a PR against `main`
4. Describe what you changed and why

## Code of Conduct

Be respectful, constructive, and inclusive. We're here to build cool stuff together.

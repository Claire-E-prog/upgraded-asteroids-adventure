# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
source venv/bin/activate  # optional, if using the included venv
pip install -r requirements.txt
python main.py
```

Requires Python 3.x and pygame 2.6.1.

## Controls

- `A` / `D` — rotate left / right
- `W` / `S` — move forward / backward
- `Space` — shoot (rate-limited by `PLAYER_SHOOT_COOLDOWN`)

## Architecture

This is a Pygame-based Asteroids clone. All game objects share a common base class and are managed through Pygame sprite groups.

### Class Hierarchy

```
pygame.sprite.Sprite
├── CircleShape (circleshape.py) — abstract base with position, velocity, radius, and circular collision detection
│   ├── Player (player.py) — triangle ship; handles keyboard input in update()
│   ├── Asteroid (asteroid.py) — circular obstacle; split() spawns 2 smaller asteroids at 1.2x speed
│   └── Shot (shot.py) — bullet fired by player
└── AsteroidField (asteroidfield.py) — spawns asteroids at screen edges on a timer; NOT a CircleShape
```

### Sprite Groups (main.py)

Four groups control which objects participate in each system:
- `updatable` — receives `update(dt)` each frame
- `drawable` — receives `draw(screen)` each frame
- `asteroids` — used for collision checks against player and shots
- `shots` — used for collision checks against asteroids

Classes declare their groups via class-level `containers` tuples, which are set in `main.py` before instantiation so objects automatically register themselves. `AsteroidField` sets its own containers in `__init__` rather than via `CircleShape.__init__`.

### Game Loop

Each frame: clear screen → draw all → update all → collision detection → display flip. Frame rate is capped at 60 FPS; `dt` is in seconds.

Collision outcomes:
- Player hits asteroid → `sys.exit()` (game over)
- Shot hits asteroid → `asteroid.split()` + `shot.kill()`

All collision detection uses circular hitboxes (via `CircleShape.detect_collision`), including the triangular player ship.

### Constants (constants.py)

All tunable values live here: screen dimensions, player speed/turn speed/shoot cooldown, asteroid sizes/spawn rate, and shot speed.

## Known Issues

- Player spawns at `y = SCREEN_WIDTH / 2` instead of `SCREEN_HEIGHT / 2` (`main.py:20`), which is off-center vertically on non-square screens.

## Planned Features

See `next_steps.txt` for the backlog (scoring, lives, screen wrap, explosion effects, acceleration, power-ups, etc.).

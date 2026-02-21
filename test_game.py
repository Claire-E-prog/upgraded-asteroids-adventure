"""
Unit tests for the Asteroids game.

We test game logic in isolation — no window, no event loop.
Two environment variables tell pygame to use dummy (headless) drivers
so these tests run anywhere, including CI servers with no display.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pytest
import pygame
from unittest.mock import patch, MagicMock

# pygame must be initialised before any Vector2 / Sprite work happens.
pygame.init()

from circleshape import CircleShape
from asteroid import Asteroid
from player import Player
from shot import Shot
from constants import (
    ASTEROID_MIN_RADIUS,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_COOLDOWN,
    SHOT_RADIUS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_asteroid(x=0, y=0, radius=ASTEROID_MIN_RADIUS * 2):
    """Create an Asteroid without needing sprite groups."""
    return Asteroid(x, y, radius)


def make_player(x=400, y=300):
    """Create a Player without needing sprite groups."""
    return Player(x, y)


# ---------------------------------------------------------------------------
# CircleShape — collision detection
# ---------------------------------------------------------------------------

class TestDetectCollision:
    """
    detect_collision returns True when two circles overlap.
    The condition is: distance between centres < sum of radii.
    """

    def test_overlapping_circles_collide(self):
        # Centers are 5 apart, radii sum to 20 → overlap → True
        a = Asteroid(0, 0, 10)
        b = Asteroid(5, 0, 10)
        assert a.detect_collision(b) is True

    def test_distant_circles_do_not_collide(self):
        # Centers are 100 apart, radii sum to 20 → no overlap → False
        a = Asteroid(0, 0, 10)
        b = Asteroid(100, 0, 10)
        assert a.detect_collision(b) is False

    def test_circles_touching_exactly_do_not_collide(self):
        # distance == sum of radii uses strict '<', so touching counts as False
        a = Asteroid(0, 0, 10)
        b = Asteroid(20, 0, 10)  # distance = 20, radii sum = 20
        assert a.detect_collision(b) is False

    def test_collision_is_symmetric(self):
        # a.detect_collision(b) should equal b.detect_collision(a)
        a = Asteroid(0, 0, 10)
        b = Asteroid(5, 0, 10)
        assert a.detect_collision(b) == b.detect_collision(a)

    def test_same_position_always_collides(self):
        a = Asteroid(50, 50, 10)
        b = Asteroid(50, 50, 10)
        assert a.detect_collision(b) is True


# ---------------------------------------------------------------------------
# Asteroid
# ---------------------------------------------------------------------------

class TestAsteroidUpdate:
    def test_position_moves_by_velocity_times_dt(self):
        asteroid = make_asteroid(100, 100)
        asteroid.velocity = pygame.Vector2(10, 20)
        asteroid.update(0.5)
        # Expected: (100 + 10*0.5, 100 + 20*0.5) = (105, 110)
        assert asteroid.position.x == pytest.approx(105)
        assert asteroid.position.y == pytest.approx(110)

    def test_zero_velocity_does_not_move(self):
        asteroid = make_asteroid(200, 300)
        asteroid.velocity = pygame.Vector2(0, 0)
        asteroid.update(1.0)
        assert asteroid.position.x == pytest.approx(200)
        assert asteroid.position.y == pytest.approx(300)


class TestAsteroidSplit:
    def test_split_always_kills_original(self):
        asteroid = make_asteroid(radius=ASTEROID_MIN_RADIUS * 2)
        asteroid.velocity = pygame.Vector2(10, 0)
        asteroid.split()
        assert not asteroid.alive()

    def test_split_min_radius_returns_none(self):
        # A minimum-size asteroid should vanish without spawning children.
        asteroid = make_asteroid(radius=ASTEROID_MIN_RADIUS)
        asteroid.velocity = pygame.Vector2(10, 0)
        result = asteroid.split()
        assert result is None

    def test_split_large_asteroid_returns_two_children(self):
        asteroid = make_asteroid(radius=ASTEROID_MIN_RADIUS * 2)
        asteroid.velocity = pygame.Vector2(10, 0)
        result = asteroid.split()
        assert result is not None
        assert len(result) == 2

    def test_split_children_have_smaller_radius(self):
        parent_radius = ASTEROID_MIN_RADIUS * 2
        asteroid = make_asteroid(radius=parent_radius)
        asteroid.velocity = pygame.Vector2(10, 0)
        a1, a2 = asteroid.split()
        expected_radius = parent_radius - ASTEROID_MIN_RADIUS
        assert a1.radius == pytest.approx(expected_radius)
        assert a2.radius == pytest.approx(expected_radius)

    def test_split_children_spawn_at_parent_position(self):
        asteroid = make_asteroid(x=150, y=250, radius=ASTEROID_MIN_RADIUS * 2)
        asteroid.velocity = pygame.Vector2(10, 0)
        a1, a2 = asteroid.split()
        assert a1.position.x == pytest.approx(150)
        assert a1.position.y == pytest.approx(250)
        assert a2.position.x == pytest.approx(150)
        assert a2.position.y == pytest.approx(250)

    def test_split_children_are_faster_than_parent(self):
        asteroid = make_asteroid(radius=ASTEROID_MIN_RADIUS * 2)
        asteroid.velocity = pygame.Vector2(10, 0)
        original_speed = asteroid.velocity.length()  # 10
        a1, a2 = asteroid.split()
        # Children should travel at 1.2× the parent's speed.
        assert a1.velocity.length() == pytest.approx(original_speed * 1.2, rel=1e-3)
        assert a2.velocity.length() == pytest.approx(original_speed * 1.2, rel=1e-3)

    def test_split_children_travel_in_different_directions(self):
        asteroid = make_asteroid(radius=ASTEROID_MIN_RADIUS * 2)
        asteroid.velocity = pygame.Vector2(10, 0)
        a1, a2 = asteroid.split()
        # The two velocity vectors must not be identical.
        assert a1.velocity != a2.velocity


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class TestPlayerRotate:
    def test_rotate_increases_rotation_by_turn_speed_times_dt(self):
        player = make_player()
        player.rotate(1.0)
        assert player.rotation == pytest.approx(PLAYER_TURN_SPEED * 1.0)

    def test_rotate_is_cumulative(self):
        player = make_player()
        player.rotate(0.5)
        player.rotate(0.5)
        assert player.rotation == pytest.approx(PLAYER_TURN_SPEED * 1.0)


class TestPlayerMove:
    def test_move_forward_with_zero_rotation(self):
        # rotation=0 → forward vector is (0, 1), so y increases.
        player = make_player()
        initial_y = player.position.y
        player.move(1.0)
        assert player.position.y > initial_y

    def test_move_does_not_change_x_at_zero_rotation(self):
        player = make_player()
        initial_x = player.position.x
        player.move(1.0)
        assert player.position.x == pytest.approx(initial_x)

    def test_move_distance_proportional_to_dt(self):
        player_fast = make_player()
        player_slow = make_player()
        player_fast.move(2.0)
        player_slow.move(1.0)
        # With the same rotation, twice the dt → twice the displacement.
        fast_displacement = player_fast.position.y - 300
        slow_displacement = player_slow.position.y - 300
        assert fast_displacement == pytest.approx(slow_displacement * 2, rel=1e-3)


class TestPlayerShoot:
    def test_shoot_sets_cooldown_timer(self):
        player = make_player()
        player.timer = -1  # cooldown expired → allowed to shoot
        player.shoot(dt=0.016)
        assert player.timer == pytest.approx(PLAYER_SHOOT_COOLDOWN)

    def test_shoot_creates_shot_at_player_position(self):
        player = make_player(x=400, y=300)
        player.timer = -1

        # Patch Shot inside the player module to intercept creation.
        with patch("player.Shot") as MockShot:
            mock_shot = MagicMock()
            MockShot.return_value = mock_shot
            player.shoot(dt=0.016)

        # Shot should be constructed with the player's current position.
        MockShot.assert_called_once_with(player.position, SHOT_RADIUS)

    def test_shoot_gives_shot_nonzero_velocity(self):
        player = make_player()
        player.timer = -1

        with patch("player.Shot") as MockShot:
            mock_shot = MagicMock()
            MockShot.return_value = mock_shot
            player.shoot(dt=0.016)

        # player.py does: shot.velocity = forward * PLAYER_SHOOT_SPEED
        # That assigns a real pygame.Vector2 onto the mock, so we can read it back.
        velocity = mock_shot.velocity
        assert isinstance(velocity, pygame.Vector2)
        assert velocity.length() > 0


# ---------------------------------------------------------------------------
# Shot
# ---------------------------------------------------------------------------

class TestShotUpdate:
    def test_position_moves_by_velocity_times_dt(self):
        pos = pygame.Vector2(50, 50)
        shot = Shot(pos, SHOT_RADIUS)
        shot.velocity = pygame.Vector2(0, 100)
        shot.update(0.5)
        assert shot.position.x == pytest.approx(50)
        assert shot.position.y == pytest.approx(100)  # 50 + 100*0.5

    def test_shot_does_not_decelerate(self):
        pos = pygame.Vector2(0, 0)
        shot = Shot(pos, SHOT_RADIUS)
        shot.velocity = pygame.Vector2(100, 0)
        shot.update(1.0)
        shot.update(1.0)
        # Velocity is constant — no drag, no friction.
        assert shot.velocity.x == pytest.approx(100)
        assert shot.velocity.y == pytest.approx(0)

import pygame 
from circleshape import CircleShape
from shot import Shot
from constants import *

# Base class for Players
class Player(CircleShape):
    
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.x = x
        self.y = y
        self.rotation = 0
        # self.position = pygame.Vector2(0.5, -0.5)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        return pygame.draw.polygon(screen, "white", self.triangle(), 2)
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate((dt - 0.05))
        if keys[pygame.K_d]:
            self.rotate((dt + 0.05))
        if keys[pygame.K_w]:
           self.move(dt + 0.05)
        if keys[pygame.K_s]:
            self.move(dt - 0.05) 
        if keys[pygame.K_SPACE]:
            self.shoot(dt * PLAYER_SHOOT_SPEED)
    
    
    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
    
    def shoot(self, dt):
        shot = Shot(self.position, SHOT_RADIUS)
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        shot.velocity = forward * PLAYER_SHOOT_SPEED
      




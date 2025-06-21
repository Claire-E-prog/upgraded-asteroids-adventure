
import pygame
from circleshape import CircleShape
from constants import *


class Asteroid(CircleShape):
    
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        
    def draw(self, screen):
        return pygame.draw.circle(screen, "white", (self.position), self.radius, 2)
    
    def update(self, dt):
        self.position += self.velocity * dt
    
    def split(self):
        self.kill() # splitting always kills the original asteroind for med/large asteroids
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            import random
            angle = random.uniform(20, 50) # generate random angle for new asteroid trajectory
            new_vector1 = self.velocity.rotate(angle)
            new_vector2 = self.velocity.rotate(-angle)
            
            new_radius = self.radius - ASTEROID_MIN_RADIUS

            new_asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
            new_asteroid1.velocity = (new_vector1 * 1.2)

            new_asteroid2 = Asteroid(self.position.x, self.position.y,  new_radius)
            new_asteroid2.velocity = (new_vector2 * 1.2)

            return new_asteroid1, new_asteroid2



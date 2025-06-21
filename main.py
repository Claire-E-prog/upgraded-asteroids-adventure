# this allows us to use code from
# the open-source pygame library
# throughout this file

from time import time
import pygame 
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import sys

def main():
    pygame.init()
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    x = SCREEN_WIDTH/2
    y = SCREEN_WIDTH/2
    
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)  
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)

    player = Player(x, y)
    #asteroid = Asteroid(x, y, radius=ASTEROID_MIN_RADIUS) makes just a random asteroid that will sit on the screen
    asteroid_field = AsteroidField()
    
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    dt = 0
    game_over = False
    pygame.display.set_caption("Asteroids")
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")
        for p in drawable:
            p.draw(screen)
        updatable.update(dt)
        for a in asteroids:
            if a.detect_collision(player):
                print("Game over!")
                #pygame.display.set_caption("Game Over!")
                #game_over = True
                sys.exit()
            for s in shots:
                if a.detect_collision(s):
                    a.kill()
                    s.kill()
        pygame.display.flip()
        dt = clock.tick(60)/1000

if __name__ == "__main__":
    main()

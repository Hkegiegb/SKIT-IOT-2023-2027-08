import pygame
import random

class FriendlyDrone:
    def __init__(self, x, y, speed=3):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = speed

    def chase(self, target):
        direction = target.position - self.position

        if direction.length() > 0:
            direction = direction.normalize()

        self.velocity = direction * self.speed

    def update(self):
        self.position += self.velocity
        


class HostileDrone:
    def __init__(self, x, y, speed=2.6):
        self.position = pygame.Vector2(x, y)
        self.speed = speed
        self.velocity = pygame.Vector2(random.choice([-1,1]) * speed, random.choice([-1,1]) * speed)
        

    def update(self, width, height):
        self.position += self.velocity
        if self.position.x <= 0 or self.position.x >= width:
                    self.velocity.x *= -1
        
        if self.position.y <= 0 or self.position.y >= height:
                    self.velocity.y *= -1


class Asset:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
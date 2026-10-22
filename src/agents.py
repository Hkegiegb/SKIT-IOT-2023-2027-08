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

    #SEEK AND ARRIVE FUNCTIONS ADDED TO THE FRIENDLY DRONE CLASS
    def seek(self, target):
        desired = target.position - self.position

        if desired.length() == 0:
            return

        desired = desired.normalize() * self.speed
        steering = desired - self.velocity

        max_force = 0.1
        if steering.length() > max_force:
            steering.scale_to_length(max_force)

        self.velocity += steering

        if self.velocity.length() > self.speed:
            self.velocity.scale_to_length(self.speed)

    def arrive(self, target):
        offset = target.position - self.position
        distance = offset.length()

        if distance <= 5:
            self.position = target.position.copy()
            self.velocity.update(0, 0)
            return

        arrival_radius = 80
        desired_speed = self.speed * min(1, distance / arrival_radius)
        desired = offset.normalize() * desired_speed

        steering = desired - self.velocity

        max_force = 0.1
        if steering.length() > max_force:
            steering.scale_to_length(max_force)

        self.velocity += steering

        if self.velocity.length() > self.speed:
            self.velocity.scale_to_length(self.speed)



    def update(self):
        self.position += self.velocity
        


class HostileDrone:
    def __init__(self, x, y, speed=2):
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
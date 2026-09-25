import pygame 

class FriendlyDrone:
    def __init__(self, x, y, speed=3):
        self.position = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = speed

    def chase(self, target):
        direction = (target.position - self.position)
        if direction.length() > 0:
            direction = direction.normalize()

        self.velocity = direction * self.speed
        self.position += self.velocity

    def update(self):
         self.position += self.velocity


class HostileDrone:
        def __init__(self, x, y, speed=2):
            self.position = pygame.Vector2(x,y)
            self.velocity = pygame.Vector2(0, 0)
            self.speed = speed
         
        
        def update(self):
            self.position+=self.velocity
  
        

class Asset:
        def __init__(self, x, y):
            self.position = pygame.Vector2(x, y)
      
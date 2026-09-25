import pygame
from agents import FriendlyDrone, HostileDrone, Asset
pygame.init()

#simulation window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DADSCS - Drone Swarm Simulation")

clock = pygame.time.Clock()

# simulation agents
friendly_drone = FriendlyDrone(100, 100)
hostile_drone = HostileDrone(600, 400)
asset = Asset(400, 300)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 20))

    friendly_drone.chase(hostile_drone)

    friendly_drone.update()
    hostile_drone.update()

    # Update and draw your simulation here

    pygame.draw.circle(
        screen,
        (0, 150, 255),
        (int(friendly_drone.position.x), int(friendly_drone.position.y)),
        10
    )

    pygame.draw.circle(
        screen,
        (255, 50, 50),
        (int(hostile_drone.position.x), int(hostile_drone.position.y)),
        10
    )

    pygame.draw.circle(
        screen,
        (0, 255, 0),
        (int(asset.position.x), int(asset.position.y)),
        12
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quite()
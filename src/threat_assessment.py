import math
import pygame
from agents import HostileDrone, Asset


def calculate_distance(drone, asset):
    return drone.position.distance_to(asset.position)


def calculate_direction_alignment(drone, asset):
    toward_asset = asset.position - drone.position
    distance = toward_asset.length()
    speed = drone.velocity.length()

    if distance == 0 or speed == 0:
        return 0.0

    cos_angle = drone.velocity.dot(toward_asset) / (speed * distance)
    return max(-1.0, min(1.0, cos_angle))

from dataclasses import dataclass
import pygame
from agents import HostileDrone, Asset


@dataclass
class ThreatReport:
    drone: HostileDrone
    distance: float
    alignment: float
    tti: float
    cpa_distance: float
    threat_score: float


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


def calculate_tti(drone, asset):
    distance = calculate_distance(drone, asset)
    if distance == 0:
        return 0.0

    toward_asset = asset.position - drone.position
    closing_speed = drone.velocity.dot(toward_asset) / distance

    if closing_speed <= 0:
        return float('inf')

    return distance / closing_speed


def get_nearest_threat(drones, asset):
    if not drones:
        return None
    return min(drones, key=lambda d: calculate_distance(d, asset))


def calculate_cpa(drone, asset):
    toward_asset = asset.position - drone.position
    speed_sq = drone.velocity.length_squared()

    if speed_sq == 0:
        return 0.0, toward_asset.length()

    t_cpa = toward_asset.dot(drone.velocity) / speed_sq
    if t_cpa <= 0:
        return 0.0, toward_asset.length()

    closest_pos = drone.position + drone.velocity * t_cpa
    return t_cpa, closest_pos.distance_to(asset.position)


def calculate_threat_score(drone, asset, max_range=800.0):
    dist = calculate_distance(drone, asset)
    if dist <= 0:
        return 100.0

    dist_factor = max(0.0, 1.0 - (dist / max_range))
    toward_asset = asset.position - drone.position
    closing_speed = drone.velocity.dot(toward_asset) / dist

    if closing_speed <= 0:
        return round(dist_factor * 15.0, 2)

    align_factor = max(0.0, calculate_direction_alignment(drone, asset))
    tti = dist / closing_speed
    tti_factor = 1.0 / (1.0 + (tti / 60.0))

    _, d_cpa = calculate_cpa(drone, asset)
    cpa_factor = max(0.0, 1.0 - (d_cpa / 120.0))

    score = (
        0.35 * tti_factor +
        0.30 * dist_factor +
        0.20 * align_factor +
        0.15 * cpa_factor
    ) * 100.0

    return round(score, 2)


def assess_threat(drone, asset):
    return ThreatReport(
        drone=drone,
        distance=calculate_distance(drone, asset),
        alignment=calculate_direction_alignment(drone, asset),
        tti=calculate_tti(drone, asset),
        cpa_distance=calculate_cpa(drone, asset)[1],
        threat_score=calculate_threat_score(drone, asset),
    )


def assess_threats(drones, asset):
    reports = [assess_threat(drone, asset) for drone in drones]
    reports.sort(key=lambda r: r.threat_score, reverse=True)
    return reports


def get_most_urgent_threat(drones, asset):
    if not drones:
        return None
    reports = assess_threats(drones, asset)
    return reports[0].drone

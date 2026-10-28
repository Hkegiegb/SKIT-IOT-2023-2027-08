from dataclasses import dataclass
import math
import pygame
from agents import HostileDrone, Asset


@dataclass(slots=True)
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
    dist_sq = toward_asset.length_squared()
    speed_sq = drone.velocity.length_squared()

    if dist_sq == 0 or speed_sq == 0:
        return 0.0

    dot = drone.velocity.dot(toward_asset)
    cos_angle = dot / math.sqrt(speed_sq * dist_sq)
    return max(-1.0, min(1.0, cos_angle))


def calculate_tti(drone, asset):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq == 0:
        return 0.0

    dot = drone.velocity.dot(toward_asset)
    if dot <= 0:
        return float('inf')

    return dist_sq / dot


def get_nearest_threat(drones, asset):
    if not drones:
        return None
    return min(drones, key=lambda d: d.position.distance_squared_to(asset.position))


def calculate_cpa(drone, asset):
    toward_asset = asset.position - drone.position
    speed_sq = drone.velocity.length_squared()

    if speed_sq == 0:
        return 0.0, toward_asset.length()

    dot = toward_asset.dot(drone.velocity)
    if dot <= 0:
        return 0.0, toward_asset.length()

    t_cpa = dot / speed_sq
    dist_sq = toward_asset.length_squared()
    d_cpa = math.sqrt(max(0.0, dist_sq - (dot * dot) / speed_sq))
    return t_cpa, d_cpa


def calculate_threat_score(drone, asset, max_range=800.0):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq <= 0:
        return 100.0

    dist = math.sqrt(dist_sq)
    dist_factor = max(0.0, 1.0 - (dist / max_range))

    speed_sq = drone.velocity.length_squared()
    if speed_sq == 0:
        return round(dist_factor * 15.0, 2)

    dot = drone.velocity.dot(toward_asset)
    if dot <= 0:
        return round(dist_factor * 15.0, 2)

    speed = math.sqrt(speed_sq)
    align_factor = max(0.0, min(1.0, dot / (speed * dist)))
    tti = dist_sq / dot
    tti_factor = 1.0 / (1.0 + (tti / 60.0))

    d_cpa = math.sqrt(max(0.0, dist_sq - (dot * dot) / speed_sq))
    cpa_factor = max(0.0, 1.0 - (d_cpa / 120.0))

    score = (
        0.35 * tti_factor +
        0.30 * dist_factor +
        0.20 * align_factor +
        0.15 * cpa_factor
    ) * 100.0

    return round(score, 2)


def assess_threat(drone, asset, max_range=800.0):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq <= 0:
        return ThreatReport(drone, 0.0, 0.0, 0.0, 0.0, 100.0)

    dist = math.sqrt(dist_sq)
    dist_factor = max(0.0, 1.0 - (dist / max_range))
    speed_sq = drone.velocity.length_squared()

    if speed_sq == 0:
        return ThreatReport(drone, dist, 0.0, float('inf'), dist, round(dist_factor * 15.0, 2))

    dot = drone.velocity.dot(toward_asset)
    speed = math.sqrt(speed_sq)
    alignment = max(-1.0, min(1.0, dot / (speed * dist)))

    if dot <= 0:
        return ThreatReport(drone, dist, alignment, float('inf'), dist, round(dist_factor * 15.0, 2))

    tti = dist_sq / dot
    t_cpa = dot / speed_sq
    d_cpa = math.sqrt(max(0.0, dist_sq - (dot * dot) / speed_sq))

    align_factor = max(0.0, alignment)
    tti_factor = 1.0 / (1.0 + (tti / 60.0))
    cpa_factor = max(0.0, 1.0 - (d_cpa / 120.0))

    score = (
        0.35 * tti_factor +
        0.30 * dist_factor +
        0.20 * align_factor +
        0.15 * cpa_factor
    ) * 100.0

    return ThreatReport(drone, dist, alignment, tti, d_cpa, round(score, 2))


def assess_threats(drones, asset, max_range=800.0):
    reports = [assess_threat(drone, asset, max_range) for drone in drones]
    reports.sort(key=lambda r: r.threat_score, reverse=True)
    return reports


def get_most_urgent_threat(drones, asset, max_range=800.0):
    if not drones:
        return None
    return max(drones, key=lambda d: calculate_threat_score(d, asset, max_range))

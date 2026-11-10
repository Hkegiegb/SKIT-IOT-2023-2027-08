from dataclasses import dataclass
from typing import List, Dict, Union, Optional
import math
import pygame
from agents import HostileDrone, Asset


@dataclass(slots=True)
class InitialThreatScore:
    proximity_factor: float
    closing_velocity_factor: float
    alignment_factor: float
    tti_factor: float
    cpa_factor: float
    total_score: float

    @property
    def score(self) -> float:
        return self.total_score

    @property
    def threat_score(self) -> float:
        return self.total_score

    def __float__(self) -> float:
        return float(self.total_score)

    def __lt__(self, other):
        val = other.total_score if isinstance(other, InitialThreatScore) else other
        return self.total_score < val

    def __le__(self, other):
        val = other.total_score if isinstance(other, InitialThreatScore) else other
        return self.total_score <= val

    def __gt__(self, other):
        val = other.total_score if isinstance(other, InitialThreatScore) else other
        return self.total_score > val

    def __ge__(self, other):
        val = other.total_score if isinstance(other, InitialThreatScore) else other
        return self.total_score >= val

    def __eq__(self, other):
        val = other.total_score if isinstance(other, InitialThreatScore) else other
        return self.total_score == val

    def __getitem__(self, key):
        return getattr(self, key)

    def to_dict(self):
        return {
            "proximity_factor": self.proximity_factor,
            "closing_velocity_factor": self.closing_velocity_factor,
            "alignment_factor": self.alignment_factor,
            "tti_factor": self.tti_factor,
            "cpa_factor": self.cpa_factor,
            "total_score": self.total_score,
        }


@dataclass(slots=True)
class ThreatReport:
    drone: HostileDrone
    distance: float
    alignment: float
    tti: float
    cpa_distance: float
    threat_score: float
    closing_velocity: float = 0.0
    proximity_factor: float = 0.0
    initial_score: InitialThreatScore | None = None

    @property
    def target(self) -> HostileDrone:
        return self.drone

    def bidding_utility(
        self,
        friendly_drone,
        gamma: float = 0.2,
        mu: float = 0.1,
        sensing_radius: float = 800.0,
    ) -> float:
        return compute_bidding_utility(
            friendly_drone,
            self,
            gamma=gamma,
            mu=mu,
            sensing_radius=sensing_radius,
        )


def calculate_distance(drone, asset):
    return drone.position.distance_to(asset.position)


def calculate_proximity_factor(drone, asset, max_range=800.0):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq >= max_range * max_range:
        return 0.0
    if dist_sq <= 0:
        return 1.0
    return max(0.0, 1.0 - math.sqrt(dist_sq) / max_range)


def calculate_closing_velocity(drone, asset):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq == 0:
        return 0.0

    dot = drone.velocity.dot(toward_asset)
    if dot <= 0:
        return 0.0

    return dot / math.sqrt(dist_sq)


def calculate_closing_velocity_factor(drone, asset, max_closing_speed=5.0):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq == 0 or max_closing_speed <= 0:
        return 0.0

    dot = drone.velocity.dot(toward_asset)
    if dot <= 0:
        return 0.0

    v_close = dot / math.sqrt(dist_sq)
    return min(1.0, v_close / max_closing_speed)


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


def calculate_normalized_threat_score(drone, asset, max_range=800.0) -> float:
    return round(calculate_threat_score(drone, asset, max_range) / 100.0, 4)


def assess_threat(drone, asset, max_range=800.0, max_closing_speed=5.0):
    toward_asset = asset.position - drone.position
    dist_sq = toward_asset.length_squared()
    if dist_sq <= 0:
        initial = InitialThreatScore(1.0, 0.0, 0.0, 1.0, 1.0, 100.0)
        return ThreatReport(drone, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 1.0, initial)

    dist = math.sqrt(dist_sq)
    dist_factor = max(0.0, 1.0 - (dist / max_range))
    speed_sq = drone.velocity.length_squared()

    if speed_sq == 0:
        score = round(dist_factor * 15.0, 2)
        initial = InitialThreatScore(dist_factor, 0.0, 0.0, 0.0, 0.0, score)
        return ThreatReport(drone, dist, 0.0, float('inf'), dist, score, 0.0, dist_factor, initial)

    dot = drone.velocity.dot(toward_asset)
    speed = math.sqrt(speed_sq)
    alignment = max(-1.0, min(1.0, dot / (speed * dist)))

    if dot <= 0:
        score = round(dist_factor * 15.0, 2)
        initial = InitialThreatScore(dist_factor, 0.0, max(0.0, alignment), 0.0, 0.0, score)
        return ThreatReport(drone, dist, alignment, float('inf'), dist, score, 0.0, dist_factor, initial)

    closing_velocity = dot / dist
    v_close_factor = min(1.0, closing_velocity / max_closing_speed) if max_closing_speed > 0 else 0.0

    tti = dist_sq / dot
    t_cpa = dot / speed_sq
    d_cpa = math.sqrt(max(0.0, dist_sq - (dot * dot) / speed_sq))

    align_factor = max(0.0, alignment)
    tti_factor = 1.0 / (1.0 + (tti / 60.0))
    cpa_factor = max(0.0, 1.0 - (d_cpa / 120.0))

    score = round((
        0.35 * tti_factor +
        0.30 * dist_factor +
        0.20 * align_factor +
        0.15 * cpa_factor
    ) * 100.0, 2)

    initial = InitialThreatScore(
        proximity_factor=dist_factor,
        closing_velocity_factor=v_close_factor,
        alignment_factor=align_factor,
        tti_factor=tti_factor,
        cpa_factor=cpa_factor,
        total_score=score
    )

    return ThreatReport(
        drone=drone,
        distance=dist,
        alignment=alignment,
        tti=tti,
        cpa_distance=d_cpa,
        threat_score=score,
        closing_velocity=closing_velocity,
        proximity_factor=dist_factor,
        initial_score=initial
    )


def initial_threat_score(drone, asset, max_range=800.0, max_closing_speed=5.0):
    return assess_threat(drone, asset, max_range, max_closing_speed).initial_score


calculate_initial_threat_score = initial_threat_score


def assess_threats(drones, asset, max_range=800.0) -> List[ThreatReport]:
    reports = [assess_threat(drone, asset, max_range) for drone in drones]
    reports.sort(key=lambda r: r.threat_score, reverse=True)
    return reports


def batch_threat_scores(
    drones: List[HostileDrone],
    asset: Asset,
    max_range: float = 800.0,
    normalize: bool = False,
) -> Dict[HostileDrone, float]:
    scores = {}
    for d in drones:
        score = calculate_threat_score(d, asset, max_range)
        setattr(d, "threat_score", score)
        scores[d] = score / 100.0 if normalize else score
    return scores


def assess_threats_multi_asset(
    drones: List[HostileDrone],
    assets: List[Asset],
    max_range: float = 800.0,
) -> List[ThreatReport]:
    if not assets:
        return []
    reports = []
    for d in drones:
        best_report = max(
            (assess_threat(d, a, max_range) for a in assets),
            key=lambda r: r.threat_score,
        )
        reports.append(best_report)
    reports.sort(key=lambda r: r.threat_score, reverse=True)
    return reports


def compute_bidding_utility(
    friendly_drone,
    threat: Union[HostileDrone, ThreatReport],
    asset: Optional[Asset] = None,
    gamma: float = 0.2,
    mu: float = 0.1,
    sensing_radius: float = 800.0,
) -> float:
    if isinstance(threat, ThreatReport):
        raw_score = threat.threat_score
        target_pos = threat.drone.position
    else:
        target_pos = threat.position
        if hasattr(threat, "threat_score"):
            raw_score = getattr(threat, "threat_score")
        elif asset is not None:
            raw_score = calculate_threat_score(threat, asset)
        else:
            raw_score = 50.0

    te = raw_score / 100.0 if raw_score > 1.0 else raw_score
    dist = friendly_drone.position.distance_to(target_pos)
    range_norm = sensing_radius if sensing_radius > 0 else 800.0
    dist_penalty = gamma * min(1.0, dist / range_norm)

    ebatt = getattr(friendly_drone, "battery", 1.0)
    emax = getattr(friendly_drone, "max_battery", 1.0)
    batt_penalty = mu * max(0.0, 1.0 - (ebatt / emax)) if emax > 0 else 0.0

    return max(0.0001, round(te - dist_penalty - batt_penalty, 4))


def get_most_urgent_threat(drones, asset, max_range=800.0):
    if not drones:
        return None
    return max(drones, key=lambda d: calculate_threat_score(d, asset, max_range))

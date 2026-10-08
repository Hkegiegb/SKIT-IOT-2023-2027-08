import numpy as np
from scipy.spatial import KDTree
from agents import FriendlyDrone


def find_neighbors(drones, query_drone, radius):
    positions = [drone.position for drone in drones]

    tree = KDTree(positions)

    query_index = drones.index(query_drone)

    neighbor_indices = tree.query_ball_point(
        query_drone.position, radius
    )

    neighbor_indices.remove(query_index)

    return [drones[i] for i in neighbor_indices]

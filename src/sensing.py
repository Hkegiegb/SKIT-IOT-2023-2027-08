import numpy as np
from scipy.spatial import KDTree


def find_neighbors(drones, query_drone, radius):
    positions = [drone.position for drone in drones]

    tree = KDTree(positions)

    query_index = drones.index(query_drone)

    neighbor_indices = tree.query_ball_point(
        query_drone.position, radius
    )

    neighbor_indices.remove(query_index)

    return [drones[i] for i in neighbor_indices]

class TestDrone:
    def __init__(self, x, y):
        self.position = np.array([x, y])


if __name__ == "__main__":
    drones = [
        TestDrone(100, 100),
        TestDrone(130, 120),
        TestDrone(500, 400),
        TestDrone(160, 110)
    ]

    neighbors = find_neighbors(drones, drones[0], 70)

    print("Number of neighbors:", len(neighbors))

    for drone in neighbors:
        print("Neighbor position:", drone.position)
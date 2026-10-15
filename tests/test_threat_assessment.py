import os, sys, unittest, pygame

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from agents import HostileDrone, Asset
from threat_assessment import calculate_distance, calculate_direction_alignment


class TestCalculateDistance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_known_distance(self):
        self.assertAlmostEqual(
            calculate_distance(HostileDrone(400, 300), Asset(403, 304)), 5.0, places=4
        )

    def test_zero_distance(self):
        self.assertAlmostEqual(
            calculate_distance(HostileDrone(200, 150), Asset(200, 150)), 0.0
        )


class TestDirectionAlignment(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_heading_straight_at_asset(self):
        drone = HostileDrone(200, 300)
        drone.velocity = pygame.Vector2(3.0, 0.0)
        asset = Asset(400, 300)
        self.assertAlmostEqual(calculate_direction_alignment(drone, asset), 1.0, places=4)

    def test_heading_away_from_asset(self):
        drone = HostileDrone(200, 300)
        drone.velocity = pygame.Vector2(-3.0, 0.0)
        asset = Asset(400, 300)
        self.assertAlmostEqual(calculate_direction_alignment(drone, asset), -1.0, places=4)

    def test_moving_perpendicular(self):
        drone = HostileDrone(200, 300)
        drone.velocity = pygame.Vector2(0.0, 5.0)
        asset = Asset(400, 300)
        self.assertAlmostEqual(calculate_direction_alignment(drone, asset), 0.0, places=4)

    def test_stationary_drone(self):
        drone = HostileDrone(200, 300)
        drone.velocity = pygame.Vector2(0.0, 0.0)
        asset = Asset(400, 300)
        self.assertAlmostEqual(calculate_direction_alignment(drone, asset), 0.0)


if __name__ == "__main__":
    unittest.main()

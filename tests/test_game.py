import unittest
import pygame
from src.level import Level
from src.settings import *

# Initialize pygame roughly for testing sprites
pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class TestGameMechanics(unittest.TestCase):
    def setUp(self):
        self.level = Level()
        self.player = self.level.player
        # Find a bridge object
        self.bridge = None
        for sprite in self.level.time_objects:
            self.bridge = sprite
            break

    def test_lantern_toggles_bridge(self):
        """Test that the bridge is solid when illuminated and not solid when not."""
        if not self.bridge:
            self.fail("No bridge found in level")

        # Place player near bridge
        self.player.rect.center = self.bridge.rect.center

        # 1. Lantern Active -> Bridge Solid (Past)
        self.player.lantern_active = True
        self.level.run() # Updates state
        self.assertTrue(self.bridge.is_solid, "Bridge should be solid when lantern is active and near")
        self.assertEqual(self.bridge.image, self.bridge.image_past)

        # 2. Lantern Inactive -> Bridge Not Solid (Future)
        self.player.lantern_active = False
        self.level.run() # Updates state
        self.assertFalse(self.bridge.is_solid, "Bridge should not be solid when lantern is inactive")
        self.assertEqual(self.bridge.image, self.bridge.image_future)

    def test_lantern_distance(self):
        """Test that the bridge reverts if player moves away."""
        if not self.bridge:
            self.fail("No bridge found in level")

        self.player.lantern_active = True

        # Far away
        self.player.rect.x = 0
        self.player.rect.y = 0
        # Bridge is likely at some offset. Let's make sure it's far.
        # Check bridge pos
        bridge_x = self.bridge.rect.x
        self.player.rect.x = bridge_x - 1000 # Very far

        self.level.run()
        self.assertFalse(self.bridge.is_solid, "Bridge should not be solid if player is far away, even if lantern is active")

if __name__ == '__main__':
    unittest.main()

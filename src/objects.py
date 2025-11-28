import pygame
from src.settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, color=COLOR_GROUND):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

class TimeObject(pygame.sprite.Sprite):
    """
    An object that has two states:
    - Future (Default): Dilapidated, broken, non-collidable (or different collision).
    - Past (Illuminated): Intact, solid.
    """
    def __init__(self, pos, size, type="bridge"):
        super().__init__()
        self.pos = pos
        self.size = size
        self.type = type

        # Create surfaces for both states
        self.image_past = pygame.Surface((size, size))
        self.image_past.fill(COLOR_BRIDGE_PAST) # Intact

        self.image_future = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image_future.fill((0, 0, 0, 0)) # Transparent/Broken
        # Draw some debris or outline to show where it is
        pygame.draw.rect(self.image_future, COLOR_BRIDGE_FUTURE, (0, size-10, size, 10))

        self.image = self.image_future
        self.rect = self.image.get_rect(topleft=pos)

        self.is_solid = False # Default state (Future) is broken/non-solid for a bridge

    def update_state(self, lantern_pos, lantern_radius, lantern_active):
        """
        Check if the object is within the lantern's light.
        """
        if not lantern_active:
            self._set_future()
            return

        # Calculate distance to lantern center
        # For simplicity, check if the center of the object is within radius
        # Or check if rect collides with circle.

        # Simple center distance check
        obj_center = pygame.math.Vector2(self.rect.center)
        lant_center = pygame.math.Vector2(lantern_pos)
        distance = obj_center.distance_to(lant_center)

        if distance < lantern_radius + self.size / 2: # Approximation
            self._set_past()
        else:
            self._set_future()

    def _set_past(self):
        self.image = self.image_past
        self.is_solid = True

    def _set_future(self):
        self.image = self.image_future
        self.is_solid = False

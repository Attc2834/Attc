import pygame
from settings import *
from player import Player
from objects import Tile, TimeObject

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # Sprite Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.time_objects = pygame.sprite.Group()

        self.setup_level()

    def setup_level(self):
        # Create map
        # W = Wall/Ground, P = Player, B = Bridge (TimeObject), ' ' = Air
        level_map = [
            "                        ",
            "                        ",
            "                        ",
            " P                      ",
            "WWWW   BBB   WWWWWWWW   ",
            "WWWW         WWWWWWWW   ",
            "WWWWWWWWWWWWWWWWWWWWW   ",
        ]

        for row_index, row in enumerate(level_map):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if cell == 'W':
                    tile = Tile((x, y), TILE_SIZE)
                    self.visible_sprites.add(tile)
                    self.obstacle_sprites.add(tile)
                    # Tiles are always solid
                    tile.is_solid = True
                elif cell == 'B':
                    bridge = TimeObject((x, y), TILE_SIZE, type="bridge")
                    self.visible_sprites.add(bridge)
                    self.obstacle_sprites.add(bridge) # It's in obstacle group, but solidity is checked dynamically
                    self.time_objects.add(bridge)
                elif cell == 'P':
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def run(self):
        # Update Time Objects based on Player Lantern
        for obj in self.time_objects:
            obj.update_state(self.player.rect.center, self.player.lantern_radius, self.player.lantern_active)

        self.visible_sprites.update()
        self.visible_sprites.draw(self.display_surface)

        # Draw Lantern Effect (Visual debug)
        if self.player.lantern_active:
            pygame.draw.circle(self.display_surface, (255, 255, 0), self.player.rect.center, self.player.lantern_radius, 2)

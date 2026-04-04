import pygame
from src.settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((32, 64))
        self.image.fill(COLOR_PLAYER)
        self.rect = self.image.get_rect(topleft=pos)

        # Physics
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump_speed = PLAYER_JUMP

        self.collision_sprites = collision_sprites
        self.on_ground = False

        # Lantern
        self.lantern_active = True
        self.lantern_radius = LANTERN_RADIUS

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()

        # Toggle lantern (e.g., 'F' key) - usually handled in event loop, but state is here
        # For simplicity, let's say holding 'L' keeps it off?
        # Or just toggle. We'll handle toggle in main event loop.

    def jump(self):
        self.direction.y = self.jump_speed

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def check_vertical_collisions(self):
        for sprite in self.collision_sprites:
            # Only collide if the sprite is solid
            if hasattr(sprite, 'is_solid') and not sprite.is_solid:
                continue

            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0

    def check_horizontal_collisions(self):
        for sprite in self.collision_sprites:
            if hasattr(sprite, 'is_solid') and not sprite.is_solid:
                continue

            if sprite.rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                elif self.direction.x > 0:
                    self.rect.right = sprite.rect.left

    def update(self):
        self.input()

        self.rect.x += self.direction.x * self.speed
        self.check_horizontal_collisions()

        self.apply_gravity()
        self.check_vertical_collisions()

        if self.on_ground and self.direction.y != 0:
            self.on_ground = False

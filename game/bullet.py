import pygame
from game import SCREEN_WIDTH


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, direction: int):
        super().__init__()

        # Image and rect
        self.image = pygame.surface.Surface((5, 2))
        self.image.fill("yellow")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = 10 * direction

    def update(self, tile_group: pygame.sprite.Group, scroll):
        # Move the bullet
        self.rect.x += (self.vel + scroll)

        # Disappear when offscreen
        if self.rect.right < -5 or self.rect.left > SCREEN_WIDTH + 5:
            self.kill()

        # Disappear when colliding with tiles
        for tile in tile_group.sprites():
            if self.rect.colliderect(tile.rect):
                self.kill()
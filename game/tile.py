import pygame
from game import TILE_SIZE

class Tile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, name: str, key: str | int):
        super().__init__()
        # Image and rect
        self.image = pygame.image.load(f"images/{name}/({key}).png")
        self.rect = self.image.get_rect(center=(x, y))
        offset = TILE_SIZE - self.image.get_height()
        self.rect.y = y + offset
        if self.image.get_width() != TILE_SIZE:
            self.rect.x = x + (TILE_SIZE - self.image.get_width())//2

    def update(self, scroll):
        self.rect.x += scroll
    
    def __str__(self) -> str:
        return f"Tile with {self.rect}"
    

class EditorTile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, number: int):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.number = number

    def update(self, scroll):
        self.rect.x += scroll

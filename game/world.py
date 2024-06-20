import pygame
import random
from game import TILE_SIZE, HP, SCREEN_HEIGHT, SCREEN_WIDTH
from game.tile import Tile
from game.character import Soldier


class World:
    def __init__(self, map_list):
        # Background images
        time_of_day = str(random.choice(["Day", "Night"]))
        self.bg_image_1 = pygame.image.load(f"images/Background/{time_of_day}/1.png")
        self.bg_image_2 = pygame.image.load(f"images/Background/{time_of_day}/2.png")
        self.bg_image_3 = pygame.image.load(f"images/Background/{time_of_day}/3.png")
        self.bg_image_4 = pygame.image.load(f"images/Background/{time_of_day}/4.png")
        self.bg_image_5 = pygame.image.load(f"images/Background/{time_of_day}/5.png")
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.x4 = 0
        self.x5 = 0

        self.bg_image_1 = pygame.transform.scale(self.bg_image_1, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_image_2 = pygame.transform.scale(self.bg_image_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_image_3 = pygame.transform.scale(self.bg_image_3, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_image_4 = pygame.transform.scale(self.bg_image_4, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_image_5 = pygame.transform.scale(self.bg_image_5, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Groups
        self.tile_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()  # This is for the player's bullets. I was too lazy to update this variable everywhere
        self.enemy_bullet_group = pygame.sprite.Group()  # For AI enemies
        self.objects_group = pygame.sprite.Group()
        self.check_point_group = pygame.sprite.GroupSingle()
        self.check_point = None

        # Loading the world
        for y, row in enumerate(map_list):
            for x, col in enumerate(row):
                if 1 <= col <= 13:
                    tile = Tile(x * TILE_SIZE, y * TILE_SIZE, "Tiles", col)
                    self.tile_group.add(tile)
                elif 14 <= col <= 28:
                    tile = Tile(x * TILE_SIZE, y * TILE_SIZE, "Tiles", col)
                    self.objects_group.add(tile)
                elif col == 29:
                    self.check_point = Tile(x * TILE_SIZE, y * TILE_SIZE, "Tiles", col)
                    self.check_point_group.add(self.check_point)
                elif col == 30:
                    player = Soldier(x * TILE_SIZE, y * TILE_SIZE, 4, hp=HP)
                    self.player_group.add(player)
                elif col == 31:
                    enemy = Soldier(x * TILE_SIZE, y * TILE_SIZE, 2, "Red", 40)
                    self.enemy_group.add(enemy)

    def background(self, window: pygame.surface.Surface, scroll, auto=False):
        # 1
        window.blit(self.bg_image_1, (self.x1, 0))
        # 2
        window.blit(self.bg_image_2, (self.x2, 0))
        window.blit(self.bg_image_2, (self.x2 + SCREEN_WIDTH, 0))
        # 3
        window.blit(self.bg_image_3, (self.x3, 0))
        window.blit(self.bg_image_3, (self.x3 + SCREEN_WIDTH, 0))
        # 4
        window.blit(self.bg_image_4, (self.x4, 0))
        window.blit(self.bg_image_4, (self.x4 + SCREEN_WIDTH, 0))
        # 5
        window.blit(self.bg_image_5, (self.x5, 0))
        window.blit(self.bg_image_5, (self.x5 + SCREEN_WIDTH, 0))


        # Update postions
        # If auto, just pass in 0 for scroll
        if auto:
            self.x2 -= (1/6)
            self.x3 -= (2/6)
            self.x4 -= (3/6)
            self.x5 -= (4/6)
        else:
            self.x2 += scroll * (1/6)
            self.x3 += scroll * (2/6)
            self.x4 += scroll * (3/6)
            self.x5 += scroll * (4/6)

        if abs(self.x2) >= SCREEN_WIDTH:
            self.x2 = 0
        if abs(self.x3) >= SCREEN_WIDTH:
            self.x3 = 0
        if abs(self.x4) >= SCREEN_WIDTH:
            self.x4 = 0
        if abs(self.x5) >= SCREEN_WIDTH:
            self.x5 = 0

    def get_check_point(self):
        return self.check_point

    def get_tile_group(self):
        return self.tile_group
    
    def get_player_group(self):
        return self.player_group
    
    def get_enemy_group(self):
        return self.enemy_group
    
    def get_bullet_group(self):
        return self.bullet_group
    
    def get_enemy_bullet_group(self):
        return self.enemy_bullet_group
    
    def get_objects_group(self):
        return self.objects_group
    
    def draw(self, window: pygame.surface.Surface, start: int, end: int, scroll: int):
        for tile in self.tile_group:
            if start < tile.rect.centerx < end:
                window.blit(tile.image, tile.rect)

        for obj in self.objects_group:
            if start < obj.rect.centerx < end:
                window.blit(obj.image, obj.rect)

        for enemy in self.enemy_group:
            if start < enemy.rect.centerx < end:
                enemy.update()  # If the enemy shows any weird behaviour, remove or comment out this line. 
                                # Then call the update method in the game class
                window.blit(enemy.image, enemy.rect)
                               


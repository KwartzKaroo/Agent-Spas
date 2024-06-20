# Author: KwartzKaroo
# Date created: 16 June 2024
# Agent Spas
# A first of many games and projects :)

# Image credits and sound credits:
# Soldier sprites - SecretHideout (https://secrethideout.itch.io/team-wars-platformer-battle)
# Tiles and objects - Craftpix  (https://craftpix.net/)
# Bullet sound - pixelbay (https://pixabay.com/)


import pygame
import os
import sys
from game import *
from game.world import World


pygame.init()
button_images = {
    "play": pygame.image.load("images/Buttons/play.png"),
    "restart": pygame.image.load("images/Buttons/restart.png"),
    "exit": pygame.image.load("images/Buttons/exit.png"),
    "pause": pygame.image.load("images/Buttons/pause.png"),
    "resume": pygame.image.load("images/Buttons/resume.png"),
    "more": pygame.image.load("images/Buttons/more.png"),
}

# =====================================================================================================================    

class Game:
    def __init__(self):
        pygame.display.set_caption("Agent Spas", "A")
        pygame.display.set_icon(pygame.image.load("images/Character/Blue/jump/1.png"))
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # For game levels
        self.level = 1
        self.reset_timer = 0
        self.level_complete = False
        self.player_died = False
        self.click = False

        # Create World
        self.world = World(read_level_file(self.level))
        self.scroll_x = 0
        self.camera_x = 0

        # Get groups
        self.tile_group = self.world.get_tile_group()
        self.player_group = self.world.get_player_group()
        self.ai_group = self.world.get_enemy_group()
        self.bullet_group = self.world.get_bullet_group()
        self.enemy_bullets_group = self.world.get_enemy_bullet_group()
        self.objects_group = self.world.get_objects_group()
        self.last_checkpoint = self.world.get_check_point()


        # Player 
        self.player = self.player_group.sprite

        # For UI
        self.playing = False
        self.paused = False

    def main_menu(self):
        while True:
            # Event check loop
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True

            # Mouse
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
        
            # FPS
            clock.tick(FPS)

            # Background
            self.window.fill('#5d7bf5')
            self.world.background(self.window, 0, True)

            if button(self.window, button_images["play"], (SCREEN_WIDTH//2, 160), mouse_pos, click):
                self.level = 1
                self.reset()
                self.playing = True
                self.play()
            elif button(self.window, button_images["exit"], (SCREEN_WIDTH//2, 300), mouse_pos, mouse_click[0]):
                sys.exit(0)

            # Update/refresh screen
            pygame.display.update()

    def play(self):
        while self.playing:
            # Event check loop
            click = False  # Mouse click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True  # Mouse click

            # Mouse
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
                    
            # FPS
            clock.tick(FPS)

            # Background
            self.world.background(self.window, self.scroll_x)
            
            # draw_grid(self.window)
            if button(self.window, button_images["pause"], (SCREEN_WIDTH//2, 24), mouse_pos, mouse_click[0]):
                self.paused = True
                self.pause()

            # The render draw method
            self.world.draw(self.window, -RENDER_DISTANCE, SCREEN_WIDTH + RENDER_DISTANCE + 96, self.scroll_x)

            # Tiles and Objects
            self.tile_group.update(self.scroll_x)
            self.objects_group.update(self.scroll_x)

            # Bullets
            self.bullet_group.draw(self.window)
            self.bullet_group.update(self.tile_group, self.scroll_x)
            self.enemy_bullets_group.draw(self.window)
            self.enemy_bullets_group.update(self.tile_group, self.scroll_x)

            # Enemy
            # self.ai_group.update()
            for enemy in self.ai_group.sprites():
                enemy.auto(self.player.rect, self.player.hp, self.tile_group)
                enemy.shoot(self.enemy_bullets_group)
                enemy.collisions(self.tile_group, self.scroll_x)
                enemy.health(self.bullet_group, True)
            
            # Player
            self.player.update()
            self.player_group.draw(self.window)
            self.player.get_key_press()
            self.player.shoot(self.bullet_group)
            self.player.collisions(self.tile_group)
            self.player.health(self.enemy_bullets_group)

            # Scrolling
            self.scroll_x = 0
            if (self.camera_x >= self.player.speed and self.player.move_left) or ((self.camera_x - WORLD_LENGTH * TILE_SIZE + SCREEN_WIDTH) <= -self.player.speed and self.player.move_right):
                self.scroll_x += self.player.scroll()
            self.camera_x -= self.scroll_x

            # Checkpoint
            self.last_checkpoint.rect.x += self.scroll_x
            self.window.blit(self.last_checkpoint.image, self.last_checkpoint.rect)
            if self.player.rect.colliderect(self.last_checkpoint) and not self.level_complete:
                self.level_complete = True

            # All levels complete
            if self.level_complete and self.level == len(os.listdir("levels/")):
                self.reset_timer += 1
                if self.reset_timer > 150:
                    pygame.draw.rect(self.window, "#5d7bf5", (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), self.reset_timer - 150)
                if self.reset_timer >= 500:
                    self.game_won(mouse_pos, click)
                    self.reset_timer = 500
                self.complete_screen("Game complete!!!", colour="orange", height=196)
            # Current level complete
            elif self.level_complete:
                self.reset_timer += 1
                self.complete_screen("Level Complete!!")
                if self.reset_timer > 200:
                    self.level += 1
                    self.reset()
            # Player dies
            elif not self.level_complete and self.player.hp <= 0 and self.player.lives == 0:
                self.reset_timer += 1
                if self.reset_timer > 200:
                    self.reset()

            # Player stats
            stats(self.window, self.player.lives, self.player.hp)

            # Update/refresh screen
            pygame.display.update()

    def pause(self):
        while self.paused:
            # Event check loop
            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True
            # Mouse
            mouse_pos = pygame.mouse.get_pos()
     
            # FPS
            clock.tick(FPS)

            if button(self.window, button_images["resume"], (SCREEN_WIDTH//2, 160), mouse_pos, click):
                self.paused = False
                
            elif button(self.window, button_images["exit"], (SCREEN_WIDTH//2, 300), mouse_pos, click):
                self.paused = False
                self.playing = False

            # Update/refresh screen
            pygame.display.update()
    
    def reset(self):
        # Empty groups
        self.tile_group.empty()
        self.ai_group.empty()
        self.bullet_group.empty()
        self.enemy_bullets_group.empty()
        self.last_checkpoint = None

        # Create new world
        self.world = World(read_level_file(self.level))
        self.tile_group = self.world.get_tile_group()
        self.player_group = self.world.get_player_group()
        self.ai_group = self.world.get_enemy_group()
        self.bullet_group = self.world.get_bullet_group()
        self.enemy_bullets_group = self.world.get_enemy_bullet_group()
        self.last_checkpoint = self.world.get_check_point()
        self.objects_group = self.world.get_objects_group()

        self.level_complete = False
        self.player_died = False
        self.camera_x = 0
        self.reset_timer = 0
        self.player = self.player_group.sprite
        self.init_pos = self.player.rect.x

    def complete_screen(self, message, colour="black", height=SCREEN_HEIGHT//2, font=pygame.font.Font("freesansbold.ttf", 50)):
        text = font.render(message, True, colour)
        rect = text.get_rect()
        rect.center = (SCREEN_WIDTH//2, height)
        self.window.blit(text, rect)

    def game_won(self, mouse_pos, click):
        if button(self.window, button_images["restart"], (SCREEN_WIDTH//4, 300), mouse_pos, click):
            self.level = 1
            self.reset()
        if button(self.window, button_images["exit"], (SCREEN_WIDTH * (3/4), 300), mouse_pos, click):
            sys.exit(0)

if __name__ == "__main__":
    game = Game()
    game.main_menu()


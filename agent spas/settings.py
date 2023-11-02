# This is the settings file for Agent Spas
# This is not a standalone file

import csv
import pygame

screen_width = 800
screen_height = 600
tile_size = 40
terminal_velocity = 24
gravity = 1
fps = 60
scroll_threshold = 300
ground = 520
bullet_damage = 30
explosion_damage = 11


# Functions
# Function for loading the levels from csv
def load_level(level_num: int) -> list:
    data_list = []
    with open(f'levels/level{level_num}.csv', newline='') as level_file:
        row = csv.reader(level_file, delimiter=';')
        for i in row:
            data_list.append(i)
        return data_list


def stats(screen: pygame.display, player: pygame.sprite, level: int) -> None:
    pygame.draw.rect(screen, 'red', (20, 20, 160, 17))
    pygame.draw.rect(screen, 'green', (20, 20, int(player.hp * 16/15), 17))
    pygame.draw.rect(screen, 'black', (18, 18, 162, 19), 2)

    font = pygame.font.Font('freesansbold.ttf', 20)

    screen.blit(font.render(f'Ammo: {player.bullet_amount}', True, 'black'), (20, 50))
    screen.blit(font.render(f'Grenades: {player.grenade_amount}', True, 'black'), (20, 80))
    screen.blit(font.render(f'Level: {level}', True, 'black'), (400, 20))


def button(screen, image, x: int, y: int) -> bool:
    # Cursor position and rect
    mouse_press = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_rect = pygame.rect.Rect(mouse_pos[0], mouse_pos[1], 5, 5)

    # Button rect
    rect = image.get_rect()
    rect.center = (x, y)

    # draw the image on the screen with x and y as the center
    screen.blit(image, (x - image.get_width()//2, y - image.get_height()//2))

    # Button and cursor collision
    if mouse_rect.colliderect(rect) and mouse_press[0]:
        return True

    return False


# Author: KwartzKaroo
# Date created: 12/07/2023
# This is the level creator for agent spas (or pretty much for any tile based game)

# Some guidelines for using this:
# Do not modify or delete existing levels
# You can create as many levels as you want, which will add to the default levels
# You cannot edit existing levels. You will have to manually load the csv data with the load_level function
# This editor does not have the option of overwriting existing files. It will simply carry on from the last level(file)
# All level files are stored in the 'levels' folder
# If you are asking why I did not add extra functionality, it's because I was too lazy to add it
# No, really. I did not think it's necessary to have all that. Sure it would have been nice to have that functionality,
# but again, I was too lazy
# Select a tile on the side panel, and place it on the screen by left-clicking. Right-clicking will clear the square.

import os

from settings import *
import pygame
import csv


pygame.init()

# ======================================================================================================================
# Creating the screen
side_panel_width = 300
bottom_panel_width = 100
screen = pygame.display.set_mode((screen_width + side_panel_width, screen_height + bottom_panel_width))
pygame.display.set_caption("Agent Spas")
clock = pygame.time.Clock()

# ======================================================================================================================
# Some needed variables
# For scrolling (DO NOT CHANGE THESE)
num_of_rows = 15
num_of_cols = 10 * tile_size
scroll = 0
world_x = 0
selected_tile_index = 0

# Images (You can load in your own images or switch the order, but that will affect the game as each index of the file in
# the list is its corresponding number when loading the csv in the main file)
image_list = [
    pygame.transform.scale(pygame.image.load('images/tiles/t1.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t2.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t3.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t4.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t5.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t6.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t7.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t8.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t9.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t10.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t11.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t12.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/tiles/t13.png'), (tile_size, tile_size)),
    pygame.transform.scale(pygame.image.load('images/consumables/health_box.png'), (28, 28)),
    pygame.transform.scale(pygame.image.load('images/consumables/ammo_box.png'), (28, 28)),
    pygame.transform.scale(pygame.image.load('images/consumables/grenade_box.png'), (28, 28)),
    pygame.image.load('images/objects/bench.png'),
    pygame.image.load('images/objects/box.png'),
    pygame.image.load('images/objects/bush.png'),
    pygame.transform.scale(pygame.image.load('images/objects/dustbin.png'), (30, 26)),
    pygame.image.load('images/objects/rock.png'),
    pygame.image.load('images/objects/Tree4.png'),
    pygame.image.load('images/objects/open gate.png'),
    pygame.image.load('images/characters/blue/idle/1.png'),
    pygame.image.load('images/characters/red/idle/1.png')
]

# For button presses
button_pressed = False

# For the side panel
selection_rect = pygame.rect.Rect(835, 50, tile_size, tile_size)

# World data
level = len(os.listdir('levels/')) + 1
world_data = []
for i in range(num_of_rows):
    r = [-1] * num_of_cols
    world_data.append(r)


# ======================================================================================================================
# Editor functions
def draw_grid():
    global scroll
    # Vertical lines
    for i in range(0, num_of_cols):
        pygame.draw.line(screen, 'grey', (i * tile_size + scroll, 0), (i * tile_size + scroll, screen_height))

    # Horizontal lines
    for i in range(0, num_of_rows):
        pygame.draw.line(screen, 'grey', (0, i * tile_size), (screen_width, i * tile_size))


def scroll_function():
    global scroll, world_x
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and world_x > 0:
        scroll += 4
        world_x -= 1
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and world_x < num_of_cols:
        scroll -= 4
        world_x += 1


def side_panel():
    global selected_tile_index, selection_rect
    pygame.draw.rect(screen, 'orange', (screen.get_width() - side_panel_width, 0, side_panel_width, screen_height))

    panel_x = 0
    panel_y = 0

    for counter, image in enumerate(image_list):
        if button(screen, pygame.transform.scale(image, (tile_size, tile_size)),
                  screen_width + 55 + (panel_x * 2 * (tile_size - 6)), panel_y * 2 * tile_size + 70):
            selection_rect = image.get_rect()
            selection_rect.h = tile_size
            selection_rect.w = tile_size
            selection_rect.center = (screen_width + 55 + (panel_x * 2 * (tile_size - 6)), panel_y * 2 * tile_size + 70)
            selected_tile_index = counter

        pygame.draw.rect(screen, 'green', selection_rect, 2)
        panel_x += 1
        if panel_x % 4 == 0:
            panel_y += 1
            panel_x = 0


def bottom_panel():
    global world_data, button_pressed, level, r
    pygame.draw.rect(screen, 'orange', (0, screen_height, screen_width + side_panel_width, bottom_panel_width))

    if button(screen, pygame.image.load('images/buttons/reset_button.png'), 300, 650):
        level = len(os.listdir('levels/')) + 1
        world_data = []
        for _ in range(num_of_rows):
            r = [-1] * num_of_cols
            world_data.append(r)

    if button(screen, pygame.image.load('images/buttons/save_button.png'), 600, 650) and not button_pressed:
        button_pressed = True
        save()


def draw_world():
    # Draw the images at the corresponding position
    for y, row in enumerate(world_data):
        for x, col in enumerate(row):
            if int(col) >= 0:
                image = image_list[int(col)]
                screen.blit(image, (x * tile_size + scroll + (tile_size - image.get_width()),
                                    y * tile_size + (tile_size - image.get_height())))


def placement():
    global button_pressed
    # Cursor position and rect
    mouse_press = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_rect = pygame.rect.Rect(mouse_pos[0], mouse_pos[1], 1, 1)

    # Update the mouse rect
    x = (mouse_rect[0] - scroll)//tile_size
    y = mouse_rect[1]//tile_size

    # Update the world data
    if mouse_press[0] and mouse_pos[0] < screen_width and mouse_pos[1] < screen_height:
        if world_data[y][x] != selected_tile_index:
            world_data[y][x] = selected_tile_index
    if mouse_press[2] and mouse_pos[0] < screen_width and mouse_pos[1] < screen_height:
        if world_data[y][x] != -1:
            world_data[y][x] = -1

    # Button press
    if not mouse_press[0] and button_pressed:
        button_pressed = False
        exit(1)


def save():
    global level
    with open(f'levels/level{level}.csv', 'w', newline='') as saved_file:
        writer = csv.writer(saved_file, delimiter=';')
        writer.writerows(world_data)
    level = len(os.listdir('levels/')) + 1


def main():
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(1)

        # FPS
        clock.tick(fps)

        # Background
        screen.fill((22, 122, 200))

        # Grid
        draw_grid()

        # Placement
        draw_world()

        # Placement
        placement()

        # Scrolling
        scroll_function()

        # Side panel
        side_panel()

        # Bottom panel
        bottom_panel()

        # Updating the screen
        pygame.display.update()


# ======================================================================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Quitting')



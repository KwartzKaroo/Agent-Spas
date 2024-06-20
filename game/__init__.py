import pygame
import csv
pygame.font.init()

# =====================================================================================================================
# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 448
TILE_SIZE = 32
FPS = 60
GRAVITY = 1
TERMINAL_VEL = 16
BULLET_DAMAGE = 10
BOUNDRY = 230
HP = 150
RENDER_DISTANCE = 128 

# For level editor
PANEL_WIDTH = 288
BOTTOM_PANEL_HEIGHT = 96 
WORLD_LENGTH = 120
WORLD_HEIGHT = SCREEN_HEIGHT//TILE_SIZE

# =====================================================================================================================
# Utilities
clock = pygame.time.Clock()
font = pygame.font.SysFont('Calibri.fft', 24)

# =====================================================================================================================
# Functions
def read_level_file(level: int):
    with open(f"levels/level{level}.csv", "r", newline="") as file:
        contents = csv.reader(file, delimiter=",")
        t = []
        for row in contents:
            t.append(list(map(int, row)))
    return t

def stats(window, lives: int, hp: int):
    pygame.draw.rect(window, "red", (15, 10, 120, 15))
    pygame.draw.rect(window, "green", (15, 10, hp*(4/5), 15))
    pygame.draw.rect(window, "black", (14, 9, 121, 16), 2)

    for i in range(0, lives):
        image = pygame.image.load("images/Extras/live.png")
        window.blit(image, (15 + i*30, 38))

def button(window: pygame.surface.Surface, image: pygame.surface.Surface, center: tuple, mouse_pos: tuple, click: bool):
    rect = image.get_rect(center=center)
    mouse_rect = pygame.rect.Rect(mouse_pos[0], mouse_pos[1], 5, 5)

    # Draw the button
    window.blit(image, rect)

    # Button clicked
    if rect.colliderect(mouse_rect) and click:
        return True
    return False

def draw_grid(window, width=SCREEN_WIDTH//TILE_SIZE, height=SCREEN_HEIGHT//TILE_SIZE):
    # Vertical lines
    for i in range(0, width):
        pygame.draw.line(window, "orange", (i * TILE_SIZE, 0), (i * TILE_SIZE, height))
    # Horizontal lines
    for i in range(0, height):
        pygame.draw.line(window, "orange", (0, i * TILE_SIZE), (width, i * TILE_SIZE))
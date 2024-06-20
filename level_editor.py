import pygame 
import csv
import os
import sys
from game import * 
from game.tile import EditorTile

images = {
    1: pygame.image.load(f"images/Tiles/(1).png"),
    2: pygame.image.load(f"images/Tiles/(2).png"),
    3: pygame.image.load(f"images/Tiles/(3).png"),
    4: pygame.image.load(f"images/Tiles/(4).png"),
    5: pygame.image.load(f"images/Tiles/(5).png"),
    6: pygame.image.load(f"images/Tiles/(6).png"),
    7: pygame.image.load(f"images/Tiles/(7).png"),
    8: pygame.image.load(f"images/Tiles/(8).png"),
    9: pygame.image.load(f"images/Tiles/(9).png"),
    10: pygame.image.load(f"images/Tiles/(10).png"),
    11: pygame.image.load(f"images/Tiles/(11).png"),
    12: pygame.image.load(f"images/Tiles/(12).png"),
    13: pygame.image.load(f"images/Tiles/(13).png"),
    14: pygame.image.load(f"images/Tiles/(14).png"),
    15: pygame.image.load(f"images/Tiles/(15).png"),
    16: pygame.image.load(f"images/Tiles/(16).png"),
    17: pygame.image.load(f"images/Tiles/(17).png"),
    18: pygame.image.load(f"images/Tiles/(18).png"),
    19: pygame.image.load(f"images/Tiles/(19).png"),
    20: pygame.image.load(f"images/Tiles/(20).png"),
    21: pygame.image.load(f"images/Tiles/(21).png"),
    22: pygame.image.load(f"images/Tiles/(22).png"),
    23: pygame.image.load(f"images/Tiles/(23).png"),
    24: pygame.image.load(f"images/Tiles/(24).png"),
    25: pygame.image.load(f"images/Tiles/(25).png"),
    26: pygame.image.load(f"images/Tiles/(26).png"),
    27: pygame.image.load(f"images/Tiles/(27).png"),
    28: pygame.image.load(f"images/Tiles/(28).png"),
    29: pygame.image.load(f"images/Tiles/(29).png"),
    30: pygame.image.load(f"images/Character/Blue/idle/1.png"),
    31: pygame.image.load(f"images/Character/Red/idle/1.png"),
}

side_panel_images = {}
for key in images:
    p = {key : pygame.transform.scale(images[key], (32, 32))}
    side_panel_images.update(p)

button_images = {
    "save": pygame.image.load("images/Buttons/save.png"),
    "new": pygame.image.load("images/Buttons/new.png"),
    "load": pygame.image.load("images/Buttons/load.png"),
}

# =====================================================================================================================
def draw_panel(group):
    y = 1
    x = 1
    for i in range(1, len(images) + 1):
        tile = EditorTile(SCREEN_WIDTH + (2 * x * TILE_SIZE) - TILE_SIZE, (y * 2 * TILE_SIZE) - TILE_SIZE, i)
        group.add(tile)
        x += 1
        if i % 4 == 0:
            y += 1
            x = 1

# =====================================================================================================================
class LevelEditor:
    def __init__(self):
        # World map
        self.world_map = []
        for _ in range(WORLD_HEIGHT):
            self.world_map.append([0 for _ in range(WORLD_LENGTH)])
        self.scroll_x = 0
        # Loading and saving levels
        self.next_level = 1
        self.loaded = False

        # The window 
        self.window = pygame.display.set_mode((SCREEN_WIDTH + PANEL_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL_HEIGHT))
        pygame.display.set_caption("Level Editor")
        pygame.display.set_icon(images[11])

        # Side panel
        self.side_panel_surface = pygame.surface.Surface((PANEL_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL_HEIGHT))
        self.side_panel_surface.fill("olivedrab")
        self.selection_rect = pygame.draw.rect(self.window, "red", (SCREEN_WIDTH + 32, 32, TILE_SIZE, TILE_SIZE), 1)
        self.selected_tile = 1
        self.side_panel_group = pygame.sprite.Group()
        draw_panel(self.side_panel_group)

        # Bottom panel
        self.bottom_panel_surface = pygame.surface.Surface((SCREEN_WIDTH, BOTTOM_PANEL_HEIGHT))
        self.bottom_panel_surface.fill("grey")

    def main(self):
        # Loop
        while True:
            single_click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    single_click = True
                # if event.type == pygame.KEYDOWN:
                #     if pygame.K_ESCAPE:
                #         exit(0)
            # FPS
            clock.tick(100)

            # Scrolling
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and -self.scroll_x >= 4:
                self.scroll_x += 4
            if keys[pygame.K_RIGHT] and -self.scroll_x <= len(self.world_map[0]) * TILE_SIZE - SCREEN_WIDTH - 4:
                self.scroll_x -= 4

            # Mouse
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            mouse_rect = pygame.rect.Rect(mouse_pos[0], mouse_pos[1], 5, 5)
            
            # Window
            self.edit_map(mouse_pos, mouse_click)
            self.window.fill('#5d7bf5')
            self.draw_grid()
            self.draw_map()

            # Side panel
            self.side_panel(mouse_rect, mouse_click[0])

            # Bottom panel
            self.window.blit(self.bottom_panel_surface, (0, SCREEN_HEIGHT))
            self.bottom_panel(mouse_pos, single_click)

            # Update/refresh screen
            pygame.display.update()

    def draw_grid(self, colour="grey"):
        # Vertical lines
        for i in range(0, len(self.world_map[0])):
            pygame.draw.line(self.window, colour, (i * TILE_SIZE + self.scroll_x, 0), (i * TILE_SIZE + self.scroll_x, SCREEN_HEIGHT))
        # Horizontal lines
        for i in range(0, SCREEN_HEIGHT//TILE_SIZE):
            pygame.draw.line(self.window, colour, (0,  i * TILE_SIZE), (SCREEN_WIDTH, i * TILE_SIZE))

    def side_panel(self, mouse_rect, mouse_click):
        self.window.blit(self.side_panel_surface, (SCREEN_WIDTH, 0))
        # Draw the buttons on the panel
        y = x = 1
        for i in range(1, len(side_panel_images) + 1):
            self.side_panel_surface.blit(side_panel_images[i], ((2 * x * TILE_SIZE) - TILE_SIZE, (y * 2 * TILE_SIZE) - TILE_SIZE))
            x += 1
            if i % 4 == 0:
                y += 1
                x = 1
        # Update selected tiled
        self.side_panel_group.update(0)
        self.selection_rect = pygame.draw.rect(self.window, "red", self.selection_rect, 2)
        for tile in self.side_panel_group.sprites():
            if mouse_rect.colliderect(tile.rect) and mouse_click:
                self.selection_rect = tile.rect
                self.selected_tile = tile.number

    def draw_map(self):
        # Visualise the entire map
        for y, row in enumerate(self.world_map):
            for x, col in enumerate(row):
                if col >= 1 and -RENDER_DISTANCE <= x * TILE_SIZE + self.scroll_x <= SCREEN_WIDTH + RENDER_DISTANCE:
                    self.window.blit(images[int(col)], (x * TILE_SIZE + (32 - images[int(col)].get_width())//2 + self.scroll_x, y * TILE_SIZE + (32 - images[int(col)].get_height())))
    
    def edit_map(self, mouse_pos, mouse_click):
        # Create new mouse coordinates updated with self.scroll_x and calculate the corresponding grid position
        if mouse_pos[0] < SCREEN_WIDTH and mouse_pos[1] < SCREEN_HEIGHT:
            mouse_pos_scroll = ((mouse_pos[0] - self.scroll_x)//TILE_SIZE, mouse_pos[1]//TILE_SIZE)
        else:
            mouse_pos_scroll = (0, 0)

        # Update a square with left-click
        if mouse_click[0] and mouse_pos[0] < SCREEN_WIDTH and mouse_pos[1] < SCREEN_HEIGHT:
            self.world_map[mouse_pos_scroll[1]][mouse_pos_scroll[0]] = self.selected_tile
        # Reset a square to default with right-click
        elif mouse_click[2] and mouse_pos[0] < SCREEN_WIDTH and mouse_pos[1] < SCREEN_HEIGHT:
            self.world_map[mouse_pos_scroll[1]][mouse_pos_scroll[0]] = 0

    def bottom_panel(self, mouse_pos, mouse_click):
        # Clear level
        if button(self.window, button_images["new"], (126, SCREEN_HEIGHT + BOTTOM_PANEL_HEIGHT//2), mouse_pos, mouse_click):
            self.loaded = False
            self.scroll_x = 0
            self.world_map = []
            for _ in range(WORLD_HEIGHT):
                self.world_map.append([0 for _ in range(WORLD_LENGTH)])
        
        # Save game
        if button(self.window, button_images["save"], (SCREEN_WIDTH//2, SCREEN_HEIGHT + BOTTOM_PANEL_HEIGHT//2), mouse_pos, mouse_click):
            if self.loaded:
                with open(f"levels/level{self.next_level - 1}.csv", "w", newline="") as file:
                    csvwriter = csv.writer(file, delimiter=",")
                    csvwriter.writerows(self.world_map)
                print(f"Saved as level {self.next_level - 1}")
            else:
                with open(f"levels/level{len(os.listdir('levels/')) + 1}.csv", "w", newline="") as file:
                    csvwriter = csv.writer(file, delimiter=",")
                    csvwriter.writerows(self.world_map)
                print(f"Saved as level {len(os.listdir('levels/'))}")

        # Load level
        if button(self.window, button_images["load"], (SCREEN_WIDTH - 126, SCREEN_HEIGHT + BOTTOM_PANEL_HEIGHT//2), mouse_pos, mouse_click):
            self.loaded = True
            self.scroll_x = 0
            if self.next_level > len(os.listdir("levels/")):
                self.next_level = 1
            try:
                self.world_map = read_level_file(self.next_level)
                self.next_level += 1
            except FileNotFoundError:
                print("No levels to load")

if __name__ == "__main__":
    editor = LevelEditor()
    editor.main()
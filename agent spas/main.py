# Author: KwartzKaroo
# Agent Spas

# images found on craftpix.com and
# audios found on pixabay

import pygame
import sys
import os
import csv
from random import randint, choice

pygame.init()

# The window
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Agent Spas')
clock = pygame.time.Clock()


# Load level function
def load_level(level_num):
    data_list = []
    with open(f'level{level_num}.csv', newline='') as level_file:
        row = csv.reader(level_file, delimiter=';')
        for i in row:
            data_list.append(i)
        return data_list


# Settings
TILE_SIZE = 32
GRAVITY = 0.9
TERMINAL_VEL = 17
GROUND = 560
FPS = 60
SCROLL_THRESH = 300
level = 1
level_data = load_level(level)
bullet_damage = 17
explosion_damage = 89

# Audio
bullet_sound = pygame.mixer.Sound('audio/bullet.mp3')
explosion_sound = pygame.mixer.Sound('audio/grenade.wav')
jump_sound = pygame.mixer.Sound('audio/jump.wav')
explosion_sound.set_volume(0.67)


# Classes
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        player = world.player_group.sprite
        self.rect.x += player.scroll


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, colour, kind, health):
        super().__init__()
        # Image animation
        self.fpi = 0.12
        self.index = 0
        self.flip = False
        self.state = 'idle'
        self.colour = colour

        # Loading images
        self.loaded_images = []
        for i in range(1, len(os.listdir(f'images/characters/blue/{self.state}'))):
            img = pygame.image.load(f'images/characters/{self.colour}/{self.state}/{i}.png')
            img = pygame.transform.flip(img, self.flip, False)
            self.loaded_images.append(img)

        self.image = self.loaded_images[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Movement and position
        self.moving_left = False
        self.moving_right = False
        self.idling = True
        self.jump = False
        self.in_air = False
        self.direction = 1
        self.run_speed = speed
        self.y_velocity = 0
        self.dx = 0
        self.dy = 0
        self.scroll = 0
        self.kind = kind

        # Shooting and throwing grenades
        self.shooting = False
        self.shoot_cooldown = 0
        self.bullet_list = []
        self.bullet_group = pygame.sprite.Group()
        self.throw_grenade = False
        self.throw_cooldown = 0
        self.grenade_list = []
        self.grenade_amount = 8
        self.grenade_group = pygame.sprite.Group()

        # AI (enemies)
        self.walk_distance = 0
        self.facing_player = False
        self.stop_timer = 0
        self.stop = False

        # health
        self.alive = True
        self.health = health
        self.death_timer = 0
        self.zero_health = False

    def update(self):
        # Loading the images
        self.loaded_images = []
        for i in range(1, len(os.listdir(f'images/characters/{self.colour}/{self.state}'))):
            img = pygame.image.load(f'images/characters/{self.colour}/{self.state}/{i}.png')
            img = pygame.transform.flip(img, self.flip, False)
            self.loaded_images.append(img)

        # Animation FPS
        self.index += self.fpi
        if not self.zero_health:
            if self.index > len(self.loaded_images):
                self.index = 0
            if self.jump:
                self.index = 0
        elif self.zero_health:
            if self.index > 3:
                self.index = 3
        self.image = self.loaded_images[int(self.index)]

    def key_press(self):
        key = pygame.key.get_pressed()

        # Running
        if key[pygame.K_a]:
            self.moving_left = True
            self.moving_right = False
            self.idling = False
        elif key[pygame.K_d]:
            self.moving_right = True
            self.moving_left = False
            self.idling = False
        else:
            self.moving_left = False
            self.moving_right = False
            self.idling = True

        # Jumping
        if key[pygame.K_SPACE] and not self.jump:
            self.jump = True

        # Shooting
        if key[pygame.K_j]:
            self.shooting = True
        else:
            self.shooting = False

        # Throwing grenades
        if key[pygame.K_k]:
            self.throw_grenade = True
        else:
            self.throw_grenade = False

    def automate(self):
        player = world.player_group.sprite
        # Facing player
        if self.rect.right < player.rect.left and self.direction == 1 and self.rect.y == player.rect.y:
            self.facing_player = True
        elif self.rect.left > player.rect.right and self.direction == -1 and self.rect.y == player.rect.y:
            self.facing_player = True
        else:
            self.facing_player = False

        # Walking
        if self.moving_left or self.moving_right and not self.zero_health:
            self.walk_distance += self.run_speed

        if self.walk_distance > randint(60, 160) or self.stop:
            self.stop_timer = 1
            self.walk_distance = 0

        # Stationary duration
        if self.stop_timer != 0:
            self.moving_right = False
            self.moving_left = False
            self.idling = True
            self.stop_timer += 1

        if self.stop_timer > int(choice([60, 80, 100, 110])):
            self.direction *= -1
            self.walk_distance = 0
            self.stop_timer = 0

        # Turning
        if self.direction == 1 and self.stop_timer == 0:
            self.moving_right = True
            self.moving_left = False
        elif self.direction == -1 and self.stop_timer == 0:
            self.moving_right = False
            self.moving_left = True

        # Shooting
        if self.facing_player and abs(player.rect.centerx - self.rect.centerx) < 200 and not player.zero_health:
            self.stop = True
            self.shooting = True
        else:
            self.stop = False
            self.shooting = False

    def move(self, scroll):
        # Horizontal movement
        if not self.zero_health:
            if self.moving_left:
                self.dx = -self.run_speed
                self.flip = True
                self.state = 'run'
                self.direction = -1
            elif self.moving_right:
                self.dx = self.run_speed
                self.flip = False
                self.state = 'run'
                self.direction = 1
            else:
                self.state = 'idle'
                self.dx = 0
        else:
            self.state = 'death'

        # Jumping
        if self.jump and not self.in_air and not self.zero_health:
            jump_sound.play()
            self.y_velocity = -13
            self.in_air = True

        # Gravity
        self.y_velocity += GRAVITY
        if self.y_velocity > TERMINAL_VEL:
            self.y_velocity = TERMINAL_VEL
        self.dy = self.y_velocity

        # World collision
        for tile in world.tile_group.spritedict:
            # Vertical collision
            if tile.rect.colliderect(self.rect.x, self.rect.y + self.dy, self.rect.w, self.rect.h):
                # while falling or on the ground
                if self.y_velocity >= 0:
                    self.dy = tile.rect.top - self.rect.bottom
                    self.y_velocity = 0
                    self.jump = False
                    self.in_air = False
                # jumping
                elif self.y_velocity < 0:
                    self.dy = tile.rect.bottom - self.rect.top
                    self.y_velocity = 0
                else:
                    self.jump = True
                    self.in_air = True
            # Horizontal collision
            if tile.rect.colliderect(self.rect.x + self.dx, self.rect.y, self.rect.w, self.rect.h):
                self.dx = 0

        if self.in_air:
            self.jump = True

        # Update position
        self.rect.x += (self.dx + scroll)
        self.rect.y += self.dy

        if self.kind == 'player':
            if self.rect.left < SCROLL_THRESH and -world.x > 0:
                self.rect.x -= self.dx
                self.scroll = self.run_speed
            elif self.rect.right > screenWidth - SCROLL_THRESH and -world.x < (len(level_data[0]) * TILE_SIZE) - 128:
                self.rect.x -= self.dx
                self.scroll = -self.run_speed
            else:
                self.scroll = 0

    def shoot(self):
        if self.shooting and self.shoot_cooldown == 0 and not self.zero_health:
            bullet_sound.play()
            if self.direction == 1:
                bullet = Bullet(self.rect.right, self.rect.top + 18, self.direction)
            else:
                bullet = Bullet(self.rect.left - 6, self.rect.top + 18, self.direction)
            self.bullet_group.add(bullet)
            self.shoot_cooldown = 1

        # Fire rate
        if self.shoot_cooldown != 0:
            self.shoot_cooldown += 1
            if self.shoot_cooldown > 18:
                self.shoot_cooldown = 0

        # self.bullet_group.add(self.bullet_list)
        self.bullet_group.update(self.scroll)
        self.bullet_group.draw(screen)

        #
        for bullet in self.bullet_group.spritedict:
            if bullet.hit:
                bullet.kill()

    def throw(self):
        if self.throw_grenade and self.throw_cooldown == 0 and not self.zero_health:
            grenade = Grenade(self.rect.centerx, self.rect.centery, abs(self.dx) - 1, self.direction)
            self.grenade_group.add(grenade)
            self.throw_cooldown = 1

        # Fire rate
        if self.throw_cooldown != 0:
            self.throw_cooldown += 1
            if self.throw_cooldown > 40:
                self.throw_cooldown = 0

        self.grenade_group.update(self.scroll)
        self.grenade_group.draw(screen)

    def health_handler(self):
        if self.health < 1:
            self.zero_health = True
            self.dx = 0
            # self.state = 'death'
            self.death_timer += 1
            if self.death_timer > 120:
                self.alive = False
        if self.rect.y > screenHeight + 400:
            self.health = 0

        if self.kind == 'enemy':
            if not self.alive:
                self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        # movement and position
        self.speed = 16
        self.direction = direction
        self.damage = 18
        self.hit = False

        # Image
        self.image = pygame.transform.scale(pygame.image.load('images/weapons/bullet.png'), (5, 2))

        # rect
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, scroll):
        dx = self.speed * self.direction

        # World collision
        for tile in world.tile_group.spritedict:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                self.hit = True
                self.kill()

        if self.off_screen():
            self.kill()

        # Update the position
        self.rect.x += (dx + scroll)

    def off_screen(self):
        return self.rect.left < -9 or self.rect.right > screenWidth + 9


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, extra_force, direction):
        super().__init__()
        # movement and position
        self.throw_force = 7 + extra_force
        self.y_velocity = -12
        self.direction = direction
        self.damage = 100
        self.bounces = 0
        self.timer = 0

        # Images
        self.image = pygame.transform.scale(pygame.image.load('images/weapons/grenade.png'), (9, 12))

        # rect
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, scroll):
        if self.timer < 80:
            # Horizontal movement
            dx = self.throw_force * self.direction

            # Gravity
            self.y_velocity += 1
            if self.y_velocity > 22:
                self.y_velocity = 22
            dy = self.y_velocity

            # World tile collision
            for tile in world.tile_group.spritedict:
                # vertical collisions
                if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                    # Falling or on the ground
                    if self.y_velocity >= 0:
                        dy = tile.rect.top - self.rect.bottom
                        self.y_velocity = self.y_velocity * -0.5 + 0.6
                        self.throw_force = self.throw_force * 0.6
                        self.bounces += 1
                    # Going up
                    elif self.y_velocity < 0:
                        dy = tile.rect.bottom - self.rect.top
                        self.y_velocity = 0
                # Horizontal collision
                if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                    dx = 0
                    self.direction *= -1
                    self.throw_force = self.throw_force * 0.6

            # After 4 bounces stop the grenade from moving
            if self.bounces > 4:
                self.y_velocity = 0
                self.throw_force = 0

            # Update the position
            self.rect.x += (dx + scroll)
            self.rect.y += dy

        elif self.timer >= 80:
            explosion = Explosion(self.rect.midbottom[0], self.rect.midbottom[1])
            explosion_group.add(explosion)
            self.kill()

        # Increment the timer
        self.timer += 1


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Image animation
        self.fpi = 0.24
        self.index = 0

        # Images
        self.explosion_img = []
        for i in range(1, 8):
            img = pygame.transform.scale(pygame.image.load(f'images/weapons/explosion/{i}.png'), (48, 48))
            self.explosion_img.append(img)

        self.image = self.explosion_img[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)

    def update(self, scroll):
        # play sound
        explosion_sound.play()
        # Update position
        self.rect.x += scroll
        # Animation
        self.index += self.fpi
        if self.index > len(self.explosion_img):
            self.index = len(self.explosion_img) - 1
            self.kill()
        self.image = self.explosion_img[int(self.index)]


class World:
    def __init__(self, data):
        # Groups
        self.tile_group = pygame.sprite.Group()
        self.deco_group = pygame.sprite.Group()
        self.gate_group = pygame.sprite.GroupSingle()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()

        # Level
        self.level_complete = False
        self.game_complete = False

        # Background
        self.x = 0
        self.scroll = 0
        self.img_1 = pygame.transform.scale(pygame.image.load('images/background/Day/1.png'), (screenWidth, screenHeight))
        self.img_2 = pygame.transform.scale(pygame.image.load('images/background/Day/2.png'), (screenWidth, screenHeight))
        self.img_3 = pygame.transform.scale(pygame.image.load('images/background/Day/3.png'), (screenWidth, screenHeight))
        self.img_4 = pygame.transform.scale(pygame.image.load('images/background/Day/5.png'), (screenWidth, screenHeight))
        self.img_2_x = 0
        self.img_3_x = 0
        self.img_4_x = 0

        # Processing the data
        for y, row in enumerate(data):
            for x, col in enumerate(row):
                if col == 'P':
                    player = Character(x * TILE_SIZE, y * TILE_SIZE, 4, 'blue', 'player', 400)
                    self.player_group.add(player)
                elif col == '0':
                    enemy = Character(x * TILE_SIZE, y * TILE_SIZE, 2, 'red', 'enemy', 80)
                    self.enemy_group.add(enemy)
                if col == '1':
                    image = pygame.image.load('images/tiles/t1.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '2':
                    image = pygame.image.load('images/tiles/t2.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '3':
                    image = pygame.image.load('images/tiles/t3.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '4':
                    image = pygame.image.load('images/tiles/t4.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '5':
                    image = pygame.image.load('images/tiles/t5.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '6':
                    image = pygame.image.load('images/tiles/t6.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '7':
                    image = pygame.image.load('images/tiles/t7.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '8':
                    image = pygame.image.load('images/tiles/t8.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '9':
                    image = pygame.image.load('images/tiles/t9.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '10':
                    image = pygame.image.load('images/tiles/t10.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '11':
                    image = pygame.image.load('images/tiles/t11.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '12':
                    image = pygame.image.load('images/tiles/t12.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '13':
                    image = pygame.image.load('images/tiles/t13.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '14':
                    image = pygame.image.load('images/tiles/t14.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE)
                    self.tile_group.add(tile)
                elif col == '22':
                    image = pygame.image.load('images/objects/bench.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '23':
                    image = pygame.image.load('images/objects/box.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '24':
                    image = pygame.image.load('images/objects/open gate.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.gate_group.add(tile)
                elif col == '25':
                    image = pygame.image.load('images/objects/closed gate.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '26':
                    image = pygame.image.load('images/objects/fence.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '27':
                    image = pygame.image.load('images/objects/dustbin.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '28':
                    image = pygame.image.load('images/objects/Ramp1.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '29':
                    image = pygame.image.load('images/objects/bush.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '30':
                    image = pygame.image.load('images/objects/rock.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)
                elif col == '31':
                    image = pygame.image.load('images/objects/Tree4.png')
                    tile = Tile(image, x * TILE_SIZE, y * TILE_SIZE + (TILE_SIZE - image.get_rect().h))
                    self.deco_group.add(tile)

    def create(self):
        # Groups
        self.tile_group.update()
        self.deco_group.update()
        self.gate_group.update()
        self.enemy_group.update()
        self.tile_group.draw(screen)
        self.deco_group.draw(screen)
        self.gate_group.draw(screen)
        self.enemy_group.draw(screen)

        # Player
        self.player_group.draw(screen)
        self.player_group.update()
        player = self.player_group.sprite
        player.health_handler()
        player.key_press()
        player.move(0)
        player.shoot()
        player.throw()

        self.x += player.scroll
        self.scroll = player.scroll

        for enemy in self.enemy_group.sprites():
            enemy.health_handler()
            enemy.automate()
            enemy.move(self.scroll)
            enemy.shoot()

    def draw_background(self):
        # Blit the images
        screen.blit(self.img_1, (0, 0))
        for i in range(0, 2):
            screen.blit(self.img_2, (self.img_2_x + (800 * i), 0))
        for i in range(0, 2):
            screen.blit(self.img_3, (self.img_3_x + (800 * i), 0))
        for i in range(0, 2):
            screen.blit(self.img_4, (self.img_4_x + (800 * i), 0))

        if -self.img_2_x > screenWidth:
            self.img_2_x = 0
        if -self.img_3_x > screenWidth:
            self.img_3_x = 0
        if -self.img_4_x > screenWidth:
            self.img_4_x = 0

        if -self.img_2_x < 0:
            self.img_2_x = -screenWidth
        if -self.img_3_x < 0:
            self.img_3_x = -screenWidth
        if -self.img_4_x < 0:
            self.img_4_x = -screenWidth

        # Background scroll
        self.img_2_x += (self.scroll * 0.2)
        self.img_3_x += (self.scroll * 0.4)
        self.img_4_x += (self.scroll * 0.6)

    def level_handler(self):
        # Increase level
        global level
        if world.player_group.sprite.rect.colliderect(world.gate_group.sprite.rect):
            world.level_complete = True
            level += 1


world = World(level_data)


# Reset/next level function
def reset():
    world.x = 0
    world.tile_group.empty()
    world.deco_group.empty()
    explosion_group.empty()
    world.player_group.empty()

    return load_level(level)


# Game functions

# Enemy and player bullet collisions
def collisions():
    player = world.player_group.sprite
    for enemy in world.enemy_group.sprites():
        if not player.zero_health:
            if pygame.sprite.spritecollide(player, enemy.bullet_group, True):
                player.health -= bullet_damage
        if not enemy.zero_health:
            if pygame.sprite.spritecollide(enemy, player.bullet_group, True):
                enemy.health -= bullet_damage
        if pygame.sprite.spritecollide(enemy, explosion_group, False):
            enemy.health -= explosion_damage


# Stats function for the player
def stats():
    player = world.player_group.sprite

    pygame.draw.rect(screen, 'red', (20, 20, 160, 17))
    pygame.draw.rect(screen, 'green', (20, 20, int(player.health * 0.4), 17))
    pygame.draw.rect(screen, 'black', (18, 18, 162, 19), 2)

    font = pygame.font.Font('freesansbold.ttf', 20)

    screen.blit(font.render(f'Grenades: {player.grenade_amount}', True, 'black'), (20, 50))


# Button function for creating buttons
def button(image, x, y):
    mouse_press = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_rect = pygame.rect.Rect(mouse_pos[0], mouse_pos[1], 5, 5)

    screen.blit(image, (x, y))

    rect = image.get_rect()
    rect.x = x
    rect.y = y

    if mouse_rect.colliderect(rect) and mouse_press[0]:
        return True


# Groups
explosion_group = pygame.sprite.Group()


# game class
class Game:
    def __init__(self):
        self.in_start_menu = True
        self.running = True
        self.paused = False
        self.in_controls_menu = False

    def start(self):
        while self.in_start_menu:
            # Event checking loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    if event.key == pygame.K_q:
                        sys.exit()

            # Background
            img = pygame.transform.scale(pygame.image.load('images/background/Day/Background.png'), (screenWidth, screenHeight))
            screen.blit(img, (0, 0))

            # screen buttons
            if button(pygame.image.load('images/buttons/start_button.png'), 284, 120):
                self.running = True
                self.play()
            if button(pygame.image.load('images/buttons/controls_button.png'), 284, 240):
                self.in_controls_menu = True
                self.controls_menu()
            if button(pygame.image.load('images/buttons/quit_button.png'), 284, 360):
                sys.exit()

            pygame.display.update()

    def play(self):
        global level, world
        while self.running:
            # Event checking loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        level = 1
                        world.level_complete = True
                    if event.key == pygame.K_p:
                        self.paused = True
                        self.pause()

            # FPS
            clock.tick(FPS)
            # When player has not completed the game
            if not world.game_complete:
                # When player is alive
                # The background
                screen.fill('alice blue')
                world.draw_background()
                world.create()
                world.level_handler()
                explosion_group.draw(screen)
                explosion_group.update(world.scroll)
                collisions()
                stats()
                # Pause
                if button(pygame.image.load('images/buttons/pause_button.png'), 387, 20):
                    self.paused = True
                    self.pause()

                # Completed level
                if level > 5:
                    world.game_complete = True
                    level = 5

                if world.level_complete and not world.game_complete:
                    data = reset()
                    world = World(data)
                    world.level_complete = False

                # When player is dead
                if not world.player_group.sprite.alive:
                    # restart level
                    if button(pygame.image.load('images/buttons/restart_button.png'), 284, 100):
                        data = reset()
                        world = World(data)
                        world.level_complete = False
                        world.game_complete = False
                    # quit
                    if button(pygame.image.load('images/buttons/quit_button.png'), 284, 320):
                        sys.exit()
            # player has completed all levels
            else:
                screen.fill('olive drab')

                font = pygame.font.Font('freesansbold.ttf', 50)
                screen.blit(font.render('Game complete!', True, 'white'), (220, 20))

                # restart
                if button(pygame.image.load('images/buttons/restart_button.png'), 284, 340):
                    level = 1
                    data = reset()
                    world = World(data)
                    world.level_complete = False
                    world.game_complete = False
                # quit
                if button(pygame.image.load('images/buttons/quit_button.png'), 284, 440):
                    sys.exit()

            pygame.display.update()

    def controls_menu(self):
        while self.in_controls_menu:
            # FPS
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        self.in_controls_menu = False

            font = pygame.font.Font('freesansbold.ttf', 30)
            screen.fill('olive drab')
            screen.blit(font.render('move left - A', True, 'white'), (170, 100))
            screen.blit(font.render('move right - D', True, 'white'), (170, 150))
            screen.blit(font.render('shoot - J', True, 'white'), (170, 200))
            screen.blit(font.render('grenade - K', True, 'white'), (170, 250))
            screen.blit(font.render('jump - SPACE/W', True, 'white'), (170, 300))
            screen.blit(font.render('pause - P', True, 'white'), (170, 350))
            screen.blit(font.render('menu - ESCAPE', True, 'white'), (170, 400))

            if button(pygame.image.load('images/buttons/back_button.png'), 450, 260):
                self.in_controls_menu = False

            pygame.display.update()

    def pause(self):
        while self.paused:
            # FPS
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
                    if event.key == pygame.K_p:
                        self.paused = False

            if button(pygame.image.load('images/buttons/paused_button.png'), 284, 220):
                self.paused = False

            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.start()

pygame.quit()

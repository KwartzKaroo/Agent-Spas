# Author: KwartzKaroo
# Date created: 09/07/2023
# Agent Spas

import os
from settings import *
from random import randint, choice
import pygame

pygame.init()

# ======================================================================================================================
# Creating the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Agent Spas")
clock = pygame.time.Clock()


# ======================================================================================================================

# Classes
class Soldier(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, direction: int, colour: str, hp: int):
        super().__init__()
        # For image animation
        self.flip = False
        self.index = 1
        self.fpi = 0.12
        self.i = 0
        self.state = 'idle'
        self.colour = colour

        # Images
        self.image = pygame.image.load(f'images/characters/{self.colour}/{self.state}/{self.index}.png')
        self.image = pygame.transform.scale(self.image, (32, 32))

        # Rect
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Movement
        self.speed = speed
        self.direction = direction
        self.y_vel = 0
        self.jumping = False
        self.moving_left = False
        self.moving_right = False
        self.scroll_num = 0
        self.on_edge = False

        # Shooting
        self.shooting = False
        self.fire_rate = 0
        self.bullet_amount = 90

        # Grenades
        self.throwing = False
        self.throw_rate = 0
        self.grenade_amount = 5

        # Health
        self.hp = hp
        self.max_hp = hp
        self.is_alive = True
        self.despawn_timer = 0

    def update(self):
        # Drawing the Soldier
        self.draw()
        self.change_state()
        self.key_press()

        # Movement
        self.scroll()
        self.walk()
        self.free_fall()

        # Shooting and grenades
        self.shoot(player_bullets)
        self.throw_grenade()

        # Damage and health
        self.handle_health(enemy_bullets)
        self.consume()

    def draw(self):
        # Loading the images
        try:
            # The try except block will reset the index, should the index be higher than the number of available images.
            self.image = pygame.image.load(f'images/characters/{self.colour}/{self.state}/{self.index}.png')
            self.image = pygame.transform.scale(self.image, (32, 32))
            self.image = pygame.transform.flip(self.image, self.flip, False)
        except FileNotFoundError:
            self.index = 1

        # Animation FPS: This controls the frame rate of the sprites. Increase self.fpi to increase the frame rate.
        self.i += self.fpi
        if self.i > 1:
            self.i = 0
            self.index += 1

        if self.index > len(os.listdir(f'images/characters/{self.colour}/{self.state}')) and self.hp > 1:
            self.index = 1
        elif self.index > len(os.listdir(f'images/characters/{self.colour}/{self.state}')) and self.hp <= 1:
            self.index = len(os.listdir(f'images/characters/{self.colour}/{self.state}'))
            self.i = 0

    def key_press(self):
        keys = pygame.key.get_pressed()

        # Left
        if keys[pygame.K_a]:
            self.moving_left = True
            self.moving_right = False
        # Right
        elif keys[pygame.K_d]:
            self.moving_left = False
            self.moving_right = True

        # Not moving
        else:
            self.moving_left = False
            self.moving_right = False

        # Jumping
        if keys[pygame.K_SPACE] and not self.jumping:
            self.jump()

        # Shooting and grenades
        if keys[pygame.K_k]:
            self.shooting = True
        else:
            self.shooting = False

        if keys[pygame.K_l]:
            self.throwing = True
        else:
            self.throwing = False

    def change_state(self):
        if self.hp > 0:
            # Left
            if self.moving_left:
                self.flip = True
                self.state = 'run'
                self.direction = -1
                self.fpi = 0.15
            # Right
            elif self.moving_right:
                self.flip = False
                self.state = 'run'
                self.direction = 1
                self.fpi = 0.15
            # Not moving
            else:
                self.state = 'idle'
                self.fpi = 0.13
        else:
            self.state = 'death'
            self.fpi = 0.10

    def walk(self):
        if self.hp > 0:
            if self.moving_left:
                dx = -self.speed
            elif self.moving_right:
                dx = self.speed
            else:
                dx = 0
        else:
            dx = 0

        # Player and world collision
        for tile in tile_group.sprites():
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.w, self.rect.h):
                dx = 0

        self.rect.x += dx + self.scroll_num

    def free_fall(self):
        # Free-free_fall
        dy = self.y_vel
        self.y_vel += gravity
        if self.y_vel > terminal_velocity:
            self.y_vel = terminal_velocity

        # World collision
        for tile in tile_group:
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.w, self.rect.h):
                # while falling or on the ground
                if self.y_vel >= 0:
                    dy = tile.rect.top - self.rect.bottom
                    self.y_vel = 0
                    self.jumping = False
                # jumping
                elif self.y_vel < 0:
                    dy = tile.rect.bottom - self.rect.top
                    self.y_vel = 0

        # Update the rect
        self.rect.y += dy

    def jump(self):
        pygame.mixer.Sound('audio/jump.wav').play()
        if self.hp > 0:
            self.y_vel = -13
            self.jumping = True

    def shoot(self, group: pygame.sprite.Group):
        if self.shooting and self.fire_rate == 0 and self.bullet_amount > 0 and self.hp > 0:
            pygame.mixer.Sound('audio/bullet.mp3').play()
            bullet = Bullet(self.rect.centerx, self.rect.top + 18, self.direction)
            group.add(bullet)
            self.bullet_amount -= 1
            self.fire_rate = 1

        # Controlling the fire rate
        if self.fire_rate > 0:
            self.fire_rate += 1
        if self.fire_rate > 20:
            self.fire_rate = 0

    def throw_grenade(self):
        if self.throwing and self.throw_rate == 0 and self.grenade_amount > 0 and self.hp > 0:
            grenade = Grenade(self.rect.centerx, self.rect.centery, self.direction)
            grenade_group.add(grenade)
            self.grenade_amount -= 1
            self.throw_rate = 1

        # Controlling the fire rate
        if self.throw_rate > 0:
            self.throw_rate += 1
        if self.throw_rate > 50:
            self.throw_rate = 0

    def handle_health(self, bullets: pygame.sprite.Group):
        if pygame.sprite.spritecollide(self, bullets, True):
            self.hp -= bullet_damage  # Change the damage in the settings file

        if pygame.sprite.spritecollide(self, explosion_group, False):
            self.hp -= explosion_damage

        if self.rect.y > screen_height + 20:
            self.hp = 0

        if self.hp <= 1:
            self.despawn_timer += 1
        if self.despawn_timer > 150:
            self.is_alive = False

        if not self.is_alive:
            self.kill()

    def consume(self):
        for item in consumables_group.sprites():
            if self.rect.colliderect(item.rect):
                if item.tile_type == 'health':
                    self.hp += 100
                    if self.hp > self.max_hp:
                        self.hp = self.max_hp
                elif item.tile_type == 'ammo':
                    self.bullet_amount += 30
                elif item.tile_type == 'grenades':
                    self.grenade_amount += 2
                item.kill()

    def scroll(self):
        if self.rect.left < scroll_threshold and world.x > 0:
            self.scroll_num = self.speed
        elif self.rect.right > 800 - scroll_threshold:
            self.scroll_num = -self.speed
        else:
            self.scroll_num = 0


# Enemy class
class AI(Soldier):
    def __init__(self, x: int, y: int, speed: int, direction: int, colour: str, hp: int):
        super().__init__(x, y, speed, direction, colour, hp)
        self.walking = True
        self.walk_distance = 0
        self.stationary_time = 0
        self.stop = False
        self.sees_player = False
        self.turn_var = self.direction

    def update(self):
        self.change_state()
        self.draw()
        self.automation()
        self.walk()
        self.free_fall()
        self.facing_player()
        self.shoot(enemy_bullets)
        self.handle_health(player_bullets)
        self.prevent_fall()

    def prevent_fall(self):
        rect = EdgeDetector(self.rect.centerx + (35 * self.turn_var), self.rect.bottom + 5)
        if pygame.sprite.spritecollide(rect, tile_group, False):
            self.on_edge = False
        else:
            self.turn_var *= -1
            self.on_edge = True

    def automation(self):
        # Changing the walking state
        if self.direction == 1 and self.stationary_time == 0 and self.walking:
            self.moving_right = True
            self.moving_left = False
            self.turn_var = 1
        elif self.direction == -1 and self.stationary_time == 0 and self.walking:
            self.moving_right = False
            self.moving_left = True
            self.turn_var = -1
        else:
            self.moving_right = False
            self.moving_left = False

        # Updating the walking distance
        self.rect.x += player.scroll_num
        if self.walking:
            self.walk_distance += self.speed

        # Stopping after walking some distance
        if self.walk_distance > randint(40, 160) or self.stop or self.on_edge:
            self.stationary_time = 1
            self.walk_distance = 0

        # Stationary duration
        if self.stationary_time > 0:
            self.stationary_time += 1
            self.walking = False

        if self.stationary_time > randint(50, 200):
            self.direction *= -1
            self.walk_distance = 0
            self.stationary_time = 0
            self.walking = True

    def facing_player(self):
        if self.direction == 1 and self.rect.right < player.rect.left and abs(self.rect.x - player.rect.x) < 100 \
                and player.rect.top < self.rect.y + 18 < player.rect.bottom and player.hp > 0:
            self.stop = True
            self.shooting = True
        elif self.direction == -1 and self.rect.left > player.rect.right and abs(self.rect.x - player.rect.x) < 100 \
                and player.rect.top < self.rect.y + 18 < player.rect.bottom and player.hp > 0:
            self.stop = True
            self.shooting = True
        else:
            self.stop = False
            self.shooting = False


class EdgeDetector:
    def __init__(self, x, y):
        self.rect = pygame.rect.Rect(x, y, 5, 5)


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, direction: int):
        super().__init__()

        # Image
        self.image = pygame.image.load("images/weapons/bullet.png")
        self.image = pygame.transform.scale(self.image, (7, 4))
        self.rect = self.image.get_rect()

        # Movement
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.move()
        self.collision()
        self.off_screen()

    def move(self):
        self.rect.centerx += 13 * self.direction

    def collision(self):
        if pygame.sprite.spritecollide(self, tile_group, False):
            self.kill()

    def off_screen(self):
        if self.rect.right < -10 or self.rect.right > screen_width + 10:
            self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        # Image
        self.image = pygame.image.load("images/weapons/grenade.png")
        self.image = pygame.transform.scale(self.image, (11, 11))
        self.rect = self.image.get_rect()

        # Movement
        self.rect.center = (x, y)
        self.y_vel = -10
        self.x_velocity = 6
        self.direction = direction
        self.bounce = 0

        # Explosion
        self.time = 105

    def update(self):
        self.throw()
        self.countdown()

    def explode(self):
        explosion = Explosion(self.rect.midbottom[0], self.rect.midbottom[1])
        explosion_group.add(explosion)

    def throw(self):
        # Horizontal movement
        dx = self.x_velocity * self.direction

        # Free-fall
        dy = self.y_vel
        self.y_vel += gravity
        if self.y_vel > terminal_velocity:
            self.y_vel = terminal_velocity

        for tile in tile_group.sprites():
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.w, self.rect.h):
                if self.y_vel >= 0:
                    dy = tile.rect.top - self.rect.bottom
                    self.y_vel *= -0.6
                    self.x_velocity *= 0.6
                    self.bounce += 1
                else:
                    dy = tile.rect.bottom - self.rect.top
                    self.y_vel = 0

            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.w, self.rect.h):
                dx = 0
                self.x_velocity *= 0.8
                self.direction *= -1

        # Stop moving after 3 bounces
        if self.bounce > 3:
            self.y_vel = 0
            self.x_velocity = 0

        # Move the grenade
        self.rect.x += dx + player.scroll_num
        self.rect.y += dy

    def countdown(self):
        self.time -= 1
        if self.time <= 0:
            self.explode()
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        # Image animation
        self.fpi = 0.24
        self.index = 1
        self.i = 0

        # Images
        self.image = pygame.image.load(f'images/weapons/explosion/{self.index}.png')
        self.image = pygame.transform.scale(self.image, (48, 48))

        # Rect
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)

    def update(self):
        self.rect.x += player.scroll_num
        pygame.mixer.Sound('audio/grenade.wav').play()
        self.draw()

    def draw(self):
        # Draw the images
        try:
            self.image = pygame.image.load(f'images/weapons/explosion/{self.index}.png')
            self.image = pygame.transform.scale(self.image, (48, 48))
        except FileNotFoundError:
            self.index = len(os.listdir(f'images/weapons/explosion/'))

        # Animation
        self.i += self.fpi
        if self.i > 1:
            self.i = 0
            self.index += 1
        if self.index > len(os.listdir(f'images/weapons/explosion/')):
            self.index = len(os.listdir(f'images/weapons/explosion/'))
            self.kill()


class Tile(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface.Surface, x: int, y: int, tile_type: str):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tile_type = tile_type

    def update(self):
        self.rect.x += player.scroll_num


# ======================================================================================================================
# Groups
player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
deco_group = pygame.sprite.Group()
consumables_group = pygame.sprite.Group()
gate = pygame.sprite.GroupSingle()


# ======================================================================================================================
# The world
class World:
    def __init__(self, data):
        self.x = 0
        self.length = len(data[0]) * tile_size
        self.offset = 0

        for y, row in enumerate(data):
            for x, col in enumerate(row):
                if col == '23':
                    player = Soldier(x * tile_size, y * tile_size, 3, 1, 'blue', 150)
                    player_group.add(player)
                    self.offset = x * tile_size
                elif col == '24':
                    enemy = AI(x * tile_size, y * tile_size, 2, int(choice([1, -1])), 'red', 80)
                    enemy_group.add(enemy)
                elif col == '0':
                    image = pygame.image.load('images/tiles/t1.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '1':
                    image = pygame.image.load('images/tiles/t2.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '2':
                    image = pygame.image.load('images/tiles/t3.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '3':
                    image = pygame.image.load('images/tiles/t4.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '4':
                    image = pygame.image.load('images/tiles/t5.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '5':
                    image = pygame.image.load('images/tiles/t6.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '6':
                    image = pygame.image.load('images/tiles/t7.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '7':
                    image = pygame.image.load('images/tiles/t8.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '8':
                    image = pygame.image.load('images/tiles/t9.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '9':
                    image = pygame.image.load('images/tiles/t10.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '10':
                    image = pygame.image.load('images/tiles/t11.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '11':
                    image = pygame.image.load('images/tiles/t12.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '12':
                    image = pygame.image.load('images/tiles/t13.png')
                    image = pygame.transform.scale(image, (tile_size, tile_size))
                    tile = Tile(image, x * tile_size, y * tile_size, "thing")
                    tile_group.add(tile)
                elif col == '13':
                    image = pygame.image.load('images/consumables/health_box.png')
                    image = pygame.transform.scale(image, (28, 28))
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "health")
                    consumables_group.add(tile)
                elif col == '14':
                    image = pygame.image.load('images/consumables/ammo_box.png')
                    image = pygame.transform.scale(image, (28, 28))
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "ammo")
                    consumables_group.add(tile)
                elif col == '15':
                    image = pygame.image.load('images/consumables/grenade_box.png')
                    image = pygame.transform.scale(image, (28, 28))
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "grenades")
                    consumables_group.add(tile)
                elif col == '16':
                    image = pygame.image.load('images/objects/bench.png')
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "deco")
                    deco_group.add(tile)
                elif col == '17':
                    image = pygame.image.load('images/objects/box.png')
                    tile = Tile(image, x * tile_size, y * tile_size + (tile_size - image.get_height()), "deco")
                    tile_group.add(tile)
                elif col == '18':
                    image = pygame.image.load('images/objects/bush.png')
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "deco")
                    deco_group.add(tile)
                elif col == '19':
                    image = pygame.image.load('images/objects/dustbin.png')
                    image = pygame.transform.scale(image, (30, 26))
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "deco")
                    deco_group.add(tile)
                elif col == '20':
                    image = pygame.image.load('images/objects/rock.png')
                    tile = Tile(image, x * tile_size, y * tile_size + (tile_size - image.get_height()), "deco")
                    deco_group.add(tile)
                elif col == '21':
                    image = pygame.image.load('images/objects/Tree4.png')
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "deco")
                    deco_group.add(tile)
                elif col == '22':
                    image = pygame.image.load('images/objects/open gate.png')
                    image = pygame.transform.scale(image, (tile_size, 55))
                    tile = Tile(image, x * tile_size + (tile_size - image.get_width()), y * tile_size + (tile_size - image.get_height()), "gate")
                    gate.add(tile)

    def create(self):
        self.x -= player.scroll_num//3

        tile_group.draw(screen)
        tile_group.update()
        # Decorations
        deco_group.draw(screen)
        deco_group.update()
        consumables_group.draw(screen)
        consumables_group.update()
        gate.draw(screen)
        gate.update()

        # Bullets
        player_bullets.draw(screen)
        player_bullets.update()
        enemy_bullets.draw(screen)
        enemy_bullets.update()

        # Grenades and explosions
        grenade_group.draw(screen)
        grenade_group.update()
        explosion_group.draw(screen)
        explosion_group.update()

        # enemy
        enemy_group.draw(screen)
        enemy_group.update()

        # Player
        player_group.draw(screen)
        player_group.update()


# Game variables and instances
level = 1
countdown = 140
data = load_level(level)
level_complete = False
game_complete = False
start = False
running = True
world = World(data)
player = player_group.sprite


# Some functions for the game
# Function that resets a/the level (not a the whole game)
def reset():
    global level_complete, game_complete, data, world, player
    world.x = 0
    player_group.empty()
    enemy_group.empty()
    player_bullets.empty()
    deco_group.empty()
    grenade_group.empty()
    enemy_bullets.empty()
    consumables_group.empty()
    tile_group.empty()
    explosion_group.empty()
    data = load_level(level)
    world = World(data)
    player = player_group.sprite
    level_complete = False
    game_complete = False


# Display screen when player completes a level
def level_complete_screen():
    global level, countdown
    font = pygame.font.Font('freesansbold.ttf', 40)
    image = font.render(f'Level {level} complete', True, 'white smoke')
    screen.blit(image, (screen_width//2 - image.get_width()//2, screen_height//2 - image.get_height()))


# Function that handles the game play
def play():
    global start, level, level_complete, game_complete, data, world, player, countdown

    # Main loop
    while start:
        # Event checking loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(1)

        # FPS
        clock.tick(fps)

        # Background
        screen.fill((222, 222, 200))
        screen.blit(
            pygame.transform.scale(pygame.image.load('images/background/Background.png'),
                                   (screen_width, screen_height)),
            (0, 0)
        )

        # The world and player stats
        world.create()
        stats(screen, player, level)

        # When player dies:
        if not player.is_alive:
            # Restart the level
            if button(screen, pygame.image.load('images/buttons/restart_button.png'), 400, 100):
                reset()
            # Quit
            if button(screen, pygame.image.load('images/buttons/quit_button.png'), 400, 320):
                exit()

        # Player collides the gate to complete the level
        if pygame.sprite.spritecollideany(player, gate):
            level_complete = True

        # When player completes a level, go on to the next
        if level_complete and not game_complete:
            level_complete_screen()
            countdown -= 1
        if countdown < 0:
            level += 1
            reset()
            countdown = 140

        if level_complete and level == len(os.listdir('levels')):
            screen.fill('olive drab')
            game_complete = True

        # When the player completes the game:
        if game_complete:
            # Restart the game
            if button(screen, pygame.image.load('images/buttons/restart_button.png'), 400, 100):
                level = 1
                reset()
            # Quit
            if button(screen, pygame.image.load('images/buttons/quit_button.png'), 400, 320):
                exit()

        # Updating the screen
        pygame.display.update()


# The start menu
def start_menu():
    global start, running, level

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(1)

        # FPS
        clock.tick(fps)

        # Background
        screen.fill((222, 222, 200))
        if button(screen, pygame.image.load('images/buttons/start_button.png'), 400, 150):
            start = True
            # Play the game
            if start:
                play()

        elif button(screen, pygame.image.load('images/buttons/quit_button.png'), 400, 300):
            exit(1)

        # Updating the screen
        pygame.display.update()


# ======================================================================================================================
# Main loop
if __name__ == '__main__':
    start_menu()
    pygame.quit()

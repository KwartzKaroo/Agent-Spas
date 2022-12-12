# Author: Kwartz Karoo
# Date created: 8 December 2022
# Space Shooter

# All images used in this game were made by me, except for the explosion images
# Explosion image credit - codingwithruss
# Audio files found from soundbible.com, by Mike Koenig

import pygame
import sys
from random import choice, randint

pygame.init()

# The window
screenWidth = 600
screenHeight = 600
window = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Space Shooter')

# Game attributes
clock = pygame.time.Clock()
FPS = 60


# Ship class
class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, kind, speed):
        super().__init__()
        self.kind = kind
        self.speed = speed

        # Controls
        self.moving_left = False
        self.moving_right = False
        self.shoot = False

        # Images
        if kind == 'player':
            self.image = pygame.transform.scale(pygame.image.load('images/rocket.png'), (64, 64))
        else:
            self.image = pygame.image.load('images/ufo1.png')

        # Bullet and laser images
        self.bullet_image = pygame.image.load('images/bullet.png')
        self.laser_image = choice([
            pygame.image.load('images/red laser.png'),
            pygame.image.load('images/green laser.png'),
            pygame.image.load('images/yellow laser.png'),
        ])

        # Explosion images
        self.explode_image = [
            pygame.image.load('images/explosion/0.png'),
            pygame.image.load('images/explosion/1.png'),
            pygame.image.load('images/explosion/2.png'),
            pygame.image.load('images/explosion/3.png'),
            pygame.image.load('images/explosion/4.png')
        ]

        self.fpi = 0
        self.index = 0  # For explosion animation`

        # Rects
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Shooting
        self.bullet_list1 = []
        self.bullet_list2 = []
        self.cooldown = 0

        # Health
        self.alive = True
        self.health = 100
        self.lives = 5
        self.blown_up = False
        self.respawn_timer = 0
        self.invulnerable = False
        self.invulnerable_time = 0

    def draw(self):
        # Health bars
        pygame.draw.rect(window, 'red', (self.rect.left - 18, self.rect.bottom + 12, 100, 12))
        pygame.draw.rect(window, 'green', (self.rect.left - 18, self.rect.bottom + 12, self.health, 12))

        # Drawing the actual ship
        if self.health >= 1 and not self.blown_up:
            window.blit(self.image, (self.rect.x, self.rect.y))
            self.speed = 5
        # Explosion
        elif self.health < 1 and self.respawn_timer < 41:
            self.fpi += 1
            if self.fpi > 6:
                self.index += 1
                self.fpi = 0
                if self.index > 4:
                    self.index = 4
            window.blit(self.explode_image[self.index], (self.rect.x - 10, self.rect.y - 20))

        # Barrier after spawning
        if self.invulnerable:
            pygame.draw.circle(window, 'alice blue', self.rect.center, 47, 2)

    def keypress(self):
        key = pygame.key.get_pressed()

        # Movements
        if key[pygame.K_a] and self.rect.left > 0:
            self.moving_left = True
            self.moving_right = False
        elif key[pygame.K_d] and self.rect.right < screenWidth:
            self.moving_left = False
            self.moving_right = True
        else:
            self.moving_left = False
            self.moving_right = False

        # Shooting
        if key[pygame.K_SPACE]:
            self.shoot = True
        else:
            self.shoot = False

    def update(self):
        # Movements
        if self.moving_left and self.respawn_timer == 0:
            self.rect.x -= self.speed
        if self.moving_right and self.respawn_timer == 0:
            self.rect.x += self.speed

        # Shooting
        if self.shoot and self.cooldown == 0 and self.respawn_timer == 0:
            bullet1 = Bullet(self.bullet_image, self.rect.left + 7, self.rect.top + 28, 16, -1)
            bullet2 = Bullet(self.bullet_image, self.rect.right - 7, self.rect.top + 28, 16, -1)
            self.bullet_list1.append(bullet1)
            self.bullet_list2.append(bullet2)
            bullet_sound = pygame.mixer.Sound('audio/bullet.mp3')
            bullet_sound.play()
            player_bullets_group.add(self.bullet_list1)
            player_bullets_group.add(self.bullet_list2)
            self.cooldown = 1

        # Fire rate
        if self.cooldown > 0:
            self.cooldown += 1
            if self.cooldown > 16:
                self.cooldown = 0

        # Checking if bullets are off the screen
        for bullet in self.bullet_list1:
            if bullet.off_screen():
                player_bullets_group.remove(bullet)
                self.bullet_list1.remove(bullet)
        for bullet in self.bullet_list2:
            if bullet.off_screen():
                player_bullets_group.remove(bullet)
                self.bullet_list2.remove(bullet)

        if self.health < 1 and not self.blown_up:
            explosion_sound = pygame.mixer.Sound('audio/explosion.mp3')
            explosion_sound.set_volume(0.69)
            explosion_sound.play()
            self.lives -= 1
            self.blown_up = True
            self.respawn_timer = 1
            self.speed = 0

        # When player is out of lives
        if self.lives <= 0 and self.health < 1:
            self.alive = False

        # Respawn timer
        if self.respawn_timer > 0:
            self.respawn_timer += 1
            if self.respawn_timer > 130:
                self.invulnerable_time = 1
                self.invulnerable = True
                self.respawn_timer = 0
                self.blown_up = False
                self.health = 100
                self.rect.center = (300, 520)

        # Barrier after spawning
        if self.invulnerable_time > 0:
            self.invulnerable_time += 1
            if self.invulnerable_time > 200:
                self.invulnerable_time = 0
                self.invulnerable = False

    def draw_stats(self):
        font = pygame.font.Font('freesansbold.ttf', 30)
        lives_text = font.render(f'Lives: {int(self.lives)}', True, 'white')
        level_text = font.render(f'Level: {space.level}', True, 'white')

        window.blit(lives_text, (20, 26))
        window.blit(level_text, (screenWidth - 130, 26))

    def reset(self):
        self.alive = True
        self.rect.center = (300, 520)
        self.lives = 5
        self.health = 100
        self.invulnerable = False
        self.invulnerable_time = 0
        self.respawn_timer = 0
        self.blown_up = False


# UFO class
class Ufo(Ship):
    def __init__(self, x, y, kind, speed):
        super().__init__(x, y, kind, speed)
        self.speed = randint(speed, speed)

    def draw(self):
        if self.health > 1:
            # Health bars
            pygame.draw.rect(window, 'red', (self.rect.left + 7, self.rect.top - 17, 50, 10))
            pygame.draw.rect(window, 'yellow', (self.rect.left + 7, self.rect.top - 17, self.health // 2, 10))
            window.blit(self.image, (self.rect.x, self.rect.y))
        elif self.health < 1:
            explosion_sound = pygame.mixer.Sound('audio/explosion.mp3')
            explosion_sound.set_volume(0.68)
            explosion_sound.play()
            self.speed = 0
            self.fpi += 1
            if self.fpi > 6:
                self.index += 1
                self.fpi = 0
            if self.index > 4:
                self.index = 4
                self.alive = False
            window.blit(self.explode_image[self.index], (self.rect.x - 10, self.rect.y - 20))

    def update(self):
        self.rect.y += self.speed

        # Shooting
        if self.cooldown == 0 and self.rect.bottom > 20 and self.health > 1:
            bullet = Bullet(self.laser_image, self.rect.centerx, self.rect.bottom, 12, 1)
            self.bullet_list1.append(bullet)
            laser_sound = pygame.mixer.Sound('audio/laser.mp3')
            laser_sound.set_volume(0.5)
            laser_sound.play()
            ufo_bullets_group.add(self.bullet_list1)
            self.cooldown = 1

        # Fire rate
        if self.cooldown > 0:
            self.cooldown += 1
        if self.cooldown > 184:
            self.cooldown = 0

        # Checking if bullets are off the screen
        for bullet in self.bullet_list1:
            if bullet.off_screen():
                player_bullets_group.remove(bullet)
                self.bullet_list1.remove(bullet)

    def off_screen(self):
        return self.rect.top > screenHeight


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed, direction):
        super().__init__()
        # The image
        self.image = image
        self.speed = speed
        self.direction = direction

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y += self.speed * self.direction

    def off_screen(self):
        return self.rect.bottom > screenHeight or self.rect.top < -10


# The whole world (space)
class Space:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.bg_img = pygame.transform.scale(pygame.image.load('images/background.png'), (600, 600))

        # UFOs
        self.ufo_list = []
        self.ufo_cooldown = 0

        # Levels
        self.level = 1
        self.ufo_count = self.level * 3

    def draw_background(self):
        window.blit(self.bg_img, (0, self.y))
        window.blit(self.bg_img, (0, self.y - screenHeight))

        self.y += 1.1
        if self.y > screenHeight:
            self.y = 0

    def spawn_ufo(self):
        # Creating the UFO
        if self.ufo_cooldown == 0 and self.ufo_count > 0:
            ufo = Ufo(randint(100, 500), randint(-300, -150), 'ufo', 1)
            self.ufo_list.append(ufo)
            ufo_group.add(self.ufo_list)
            self.ufo_count -= 1
            self.ufo_cooldown = 1

        # UFO spawn rate
        if self.ufo_cooldown > 0:
            self.ufo_cooldown += 1
        if self.ufo_cooldown > 200 - (self.level * 10):
            self.ufo_cooldown = 0

        # Increasing the level
        if self.ufo_count <= 0:
            self.level += 1
            self.ufo_count = self.level * 3

        for ufo in self.ufo_list:
            ufo.draw()
            # Removing the UFOs that are off-screen
            if ufo.off_screen():
                player.lives -= 0.3
                ufo_group.remove(ufo)
                self.ufo_list.remove(ufo)

    def collisions(self):
        for ufo in self.ufo_list:
            # UFO and player collision
            if player.rect.colliderect(ufo.rect) and not player.blown_up:
                if not player.invulnerable:
                    player.health -= 50
                self.ufo_list.remove(ufo)
                ufo_group.remove(ufo)
            # UFO laser and player collision
            for bullet in ufo.bullet_list1:
                if player.rect.colliderect(bullet.rect) and not player.blown_up:
                    if not player.invulnerable:
                        player.health -= 30
                    ufo.bullet_list1.remove(bullet)
                    ufo_bullets_group.remove(bullet)

            # Player bullets and UFO collision
            for bullet in player.bullet_list1:
                if ufo.rect.colliderect(bullet.rect):
                    ufo.health -= 40
                    player.bullet_list1.remove(bullet)
                    player_bullets_group.remove(bullet)
            for bullet in player.bullet_list2:
                if ufo.rect.colliderect(bullet.rect):
                    ufo.health -= 40
                    player.bullet_list2.remove(bullet)
                    player_bullets_group.remove(bullet)

            if not ufo.alive:
                self.ufo_list.remove(ufo)
                ufo_group.remove(ufo)


# Class instances
player = Ship(300, 520, 'player', 5)
space = Space()


# Groups
player_group = pygame.sprite.Group()
player_group.add(player)
ufo_group = pygame.sprite.Group()
ufo_bullets_group = pygame.sprite.Group()
player_bullets_group = pygame.sprite.Group()


# Class that handles UI
class Game:
    def __init__(self):
        self.running = False
        self.in_menu = True
        self.in_controls_menu = False
        self.paused = False

    def main_menu(self):
        while self.in_menu:
            # FPS
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.running = True
                        self.playing()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.in_controls_menu = True
                        self.controls_menu()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or pygame.K_ESCAPE:
                        sys.exit()

            # The background
            window.fill('olive drab')
            window.blit(pygame.image.load('images/background.png'), (0, 0))

            # The buttons
            window.blit(pygame.image.load('images/buttons/start_button.png'), (184, 120))
            window.blit(pygame.image.load('images/buttons/controls_button.png'), (184, 240))
            window.blit(pygame.image.load('images/buttons/quit_button.png'), (184, 360))

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

            window.fill('olive drab')
            font = pygame.font.Font('freesansbold.ttf', 30)
            window.blit(font.render('move left - A', True, 'white'), (170, 150))
            window.blit(font.render('move right - D', True, 'white'), (170, 200))
            window.blit(font.render('shoot - SPACE', True, 'white'), (170, 250))
            window.blit(font.render('pause - ESCAPE', True, 'white'), (170, 300))

            # Back button
            window.blit(pygame.image.load('images/buttons/back_button.png'), (170, 360))

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

            pygame.mouse.set_visible(False)

            pause_text = pygame.image.load('images/buttons/paused_button.png')
            window.blit(pause_text, (184, 220))
            pygame.display.update()

    def lost_screen(self):
        while not player.alive:
            # FPS
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                    if event.key == pygame.K_r:
                        player.reset()
                        player.rect.center = (320, 500)
                        space.level = 1
                        space.spawn_ufo()

            pygame.mouse.set_visible(False)

            # Buttons
            window.blit(pygame.image.load('images/buttons/restart_button.png'), (184, 170))
            window.blit(pygame.image.load('images/buttons/quit_button.png'), (184, 320))

            pygame.display.update()

    def playing(self):
        # Main game loop
        while self.running:
            # FPS
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        player.reset()
                        self.running = False
                    if event.key == pygame.K_p:
                        self.paused = True
                        self.pause()

            pygame.mouse.set_visible(False)

            # The background
            window.fill('alice blue')
            space.draw_background()

            # While player is alive
            if player.alive:
                # The player
                player.draw()
                player.keypress()
                ufo_bullets_group.update()
                player_group.update()

                player_bullets_group.draw(window)
                player_bullets_group.update()

                # Ufo
                space.spawn_ufo()
                ufo_group.update()
                ufo_bullets_group.draw(window)

                # Collisions
                space.collisions()
            # When player dies
            if not player.alive:
                del space.ufo_list[:]
                self.lost_screen()
                ufo_group.empty()
                player_bullets_group.empty()
                ufo_bullets_group.empty()

            # Stats
            player.draw_stats()

            # Update the screen
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.main_menu()

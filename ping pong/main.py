# Ping pong game
# Created by KwartzKaroo
# On 19/01/2023

import pygame
import sys
from random import choice, randint

pygame.init()

# The screen
screenWidth = 850
screenHeight = 650
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Ping pong')

# Game settings
clock = pygame.time.Clock()
FPS = 60
game_over = False
winning_score = 7

# Fonts
font = pygame.font.SysFont('arialnova.ttf', 47, False, False)
font_2 = pygame.font.SysFont('arial.ttf', 100, False, False)


# Game functions
def background():
    field_rect = (25, 50, screenWidth - 50, screenHeight - 75)
    screen.fill('orange')
    pygame.draw.rect(screen, 'green', field_rect, 5)
    pygame.draw.circle(screen, 'green', (screenWidth//2, screenHeight//2), 30, 5)
    pygame.draw.line(screen, 'green', (screenWidth//2, 50), (screenWidth//2, screenHeight - 26), 5)


def display_score(player_1, player_2):
    left_score = font.render(f'P1: {player_1}', True, 'white')
    right_score = font.render(f'P2: {player_2}', True, 'white')

    screen.blit(left_score, (16, 10))
    screen.blit(right_score, (screenWidth - right_score.get_width() - 16, 10))

    pygame.draw.line(screen, 'black', (10, 42), (screenWidth - 10, 42), 3)


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


# Game classes
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, side):
        super().__init__()
        # Image
        self.image = pygame.surface.Surface((13, 76))
        self.image.fill('white')
        self.rect = self.image.get_rect(center=(x, y))

        # Movement
        self.speed = 8.1
        self.roaming_speed = 3
        self.move_timer = 0
        self.friction = 1
        self.side = side

        # scores
        self.score = 0

    def draw(self):
        screen.blit(self.image, self.rect)

    def move(self, moving_up, moving_down):
        self.friction = 1
        if moving_up:
            self.rect.y -= self.speed
            self.friction = -1
        if moving_down:
            self.rect.y += self.speed
            self.friction = 1

    def collision(self):
        # Paddle and wall collision
        if self.rect.top < 61:
            self.rect.top = 61
            self.speed = 0
        elif self.rect.bottom > screenHeight - 35:
            self.rect.bottom = screenHeight - 35
            self.speed = 0
        else:
            self.speed = 8.1

        # Ball and paddle collision
        if self.rect.colliderect(ball.rect):
            ball.x_direction *= -1
            ball.y_direction *= self.friction
            ball.y_speed += 1.14
            ball.x_speed += 1.14

        # Score handler
        if (self.side == 'left' and ball.rect.left > screenWidth) or (self.side == 'right' and ball.rect.right < 0):
            self.score += 1
            ball.reset()

    def auto_move(self, difficulty):
        # Normal speed
        if difficulty == 'easy':
            self.speed = 5.9
        elif difficulty == 'medium':
            self.speed = 7
        elif difficulty == 'hard':
            self.speed = 8.1
        else:
            self.speed = 7

        # Roaming speed
        i = randint(40, 80)
        self.move_timer += 1
        if self.move_timer > i:
            self.roaming_speed *= int(choice([-1, 1]))
            self.move_timer = 0

        # Moving the Paddle
        if self.rect.centery > ball.rect.bottom and abs(ball.rect.x - self.rect.x) < 300:
            self.rect.y -= self.speed
        elif self.rect.centery < ball.rect.top and abs(ball.rect.x - self.rect.x) < 300:
            self.rect.y += self.speed
        else:
            self.rect.y += self.roaming_speed


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Image
        self.image = pygame.surface.Surface((21, 21))
        self.image.fill('olive drab')
        self.rect = self.image.get_rect(center=(screenWidth//2, screenHeight//2))

        # Movement
        self.x_speed = 2
        self.y_speed = 2
        self.max_speed = 9.3
        self.x_direction = int(choice([1, -1]))
        self.y_direction = int(choice([1, -1]))
        self.reset_timer = 1

    def draw(self):
        pygame.draw.circle(screen, 'black', self.rect.center, self.rect.w/2)

    def move(self):
        # top collision
        if self.rect.top < 55:
            self.rect.top = 55
            self.y_direction *= -1
        # bottom collision
        if self.rect.bottom > screenHeight - 30:
            self.rect.bottom = screenHeight - 30
            self.y_direction *= -1

        # Start delay
        if self.reset_timer != 0:
            self.reset_timer += 1
            if self.reset_timer > 97:
                self.reset_timer = 0

        # Update movement
        if self.reset_timer == 0:
            self.rect.x += self.x_speed * self.x_direction
            self.rect.y += self.y_speed * self.y_direction

        # Maximum speed
        if self.y_speed > self.max_speed:
            self.y_speed = self.max_speed
        if self.x_speed > self.max_speed:
            self.x_speed = self.max_speed

    def reset(self):
        self.rect.center = (screenWidth//2, screenHeight//2)
        self.y_direction = int(choice([1, -1]))
        self.x_speed = 2
        self.y_speed = 2
        self.reset_timer = 1


# Instances
player1 = Paddle(50, 300, 'left')
player2 = Paddle(screenWidth - 50, 300, 'right')
ball = Ball()


# Game UI
class Game:
    def __init__(self):
        self.running = False
        self.difficulty_select = False

    def start(self):
        while True:
            # Event checking loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            key = pygame.key.get_pressed()

            screen.fill('orange')

            # Main menu buttons
            if button(pygame.image.load('buttons/1player.png'), screenWidth // 2 - 116, 100):
                self.difficulty_select = True
                self.select_difficulty()
            elif button(pygame.image.load('buttons/2player.png'), screenWidth // 2 - 116, 250):
                self.running = True
                self.play(False, 'easy')
            elif button(pygame.image.load('buttons/quit.png'), screenWidth // 2 - 116, 400) or key[pygame.K_ESCAPE]:
                sys.exit()

            # Display
            clock.tick(FPS)
            pygame.display.update()

    def select_difficulty(self):
        while self.difficulty_select:
            # Event checking loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            screen.fill('orange')

            if button(pygame.image.load('buttons/easy.png'), 41, 100):
                self.running = True
                self.play(True, 'easy')
            elif button(pygame.image.load('buttons/medium.png'), 314, 250):
                self.running = True
                self.play(True, 'medium')
            elif button(pygame.image.load('buttons/hard.png'), 578, 400):
                self.running = True
                self.play(True, 'hard')

            # Display
            clock.tick(FPS)
            pygame.display.update()

    def play(self, auto, difficulty):
        while self.running:
            # Event checking loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # Key presses
            key = pygame.key.get_pressed()

            # Background
            background()

            # Score board
            global game_over
            display_score(player1.score, player2.score)
            if player1.score == winning_score or player2.score == winning_score:
                game_over = True

            # Not game over
            if not game_over:
                # Player 1
                player1.draw()
                player1.move(key[pygame.K_w], key[pygame.K_s])
                player1.collision()

                # Player 2
                if auto:
                    # CPU
                    player2.draw()
                    player2.auto_move(difficulty)
                    player2.collision()
                else:
                    # Second player
                    player2.draw()
                    player2.move(key[pygame.K_UP], key[pygame.K_DOWN])
                    player2.collision()

                # The ball
                ball.draw()
                ball.move()

            # Game over
            else:
                # Player won text
                if player1.score == winning_score:
                    screen.blit(font_2.render('Player 1 won', True, 'black'), (screenWidth//2 - 215, 100))
                elif player2.score == winning_score:
                    screen.blit(font_2.render('Player 2 won', True, 'black'), (screenWidth//2 - 215, 100))

                # Restart button
                if button(pygame.image.load('buttons/restart.png'), screenWidth//2 - 116, 250):
                    game_over = False
                    player1.score = 0
                    player2.score = 0
                # Quit button
                elif button(pygame.image.load('buttons/quit.png'), screenWidth // 2 - 116, 400):
                    self.running = False
                    self.difficulty_select = False

            # Display update
            clock.tick(FPS)
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.start()

    pygame.quit()

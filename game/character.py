import pygame
import random
from game.bullet import Bullet
from game import GRAVITY, TERMINAL_VEL, BULLET_DAMAGE, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, BOUNDRY


class Soldier(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, speed: int, colour: str = "Blue", hp: int = 50):
        super().__init__()
        # Images
        self.image = pygame.image.load(f"images/Character/{colour}/idle/1.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.overlap = self.image.get_masks()
        self.colour = colour

        # Animation
        self.i = 1
        self.fps = 0.11
        self.state = 'idle'
        self.flip = False

        # Movement
        self.move_left = False
        self.move_right = False
        self.dx = 0
        self.dy = 0
        self.jumping = False
        self.speed = speed
        self.direction = 1
        self.y_vel = 0
        self.in_air = False

        # Shooting
        self.shoot_cooldown = 0
        self.shooting = False
        self.ammo = 100
        self.bullet_sound = pygame.mixer.Sound("audio/bullet.mp3")

        # Health
        self.hp = hp
        self.dead_timer = 0
        self.lives = 3

        # Automation (For AI enemies)
        self.range_rect = pygame.rect.Rect(self.rect.centerx - (110 * self.direction), self.rect.y, 110, 20)
        self.edge_rect = pygame.rect.Rect(self.rect.centerx + (10 * self.direction) , self.rect.bottom + 8, 4, 4)
        self.jump_rect = pygame.rect.Rect(self.rect.centerx + (10 * self.direction) , self.rect.centery - 8, 4, 4)
        self.wait_timer = 0
        self.displacement = 100
        
    def update(self):
        # These methods work exactly the same for any Soldier instance created. So that's why they are called in here
        # Movement
        self.move()

        # Free falling 
        self.fall()

        # Draw the Soldier
        self.draw()

    def draw(self):
        try:
            image = pygame.image.load(f"images/Character/{self.colour}/{self.state}/{int(self.i)}.png")
            self.image = pygame.transform.flip(image, self.flip, False)
            self.i += self.fps
        except:
            self.i = 1

    def move(self):
        # Jumping
        if self.jumping and not self.in_air:
            self.y_vel = -13
            self.in_air = True
            self.state = "jump"

        # Running left
        self.dx = 0
        if self.move_left:
            self.dx = -self.speed # The rect is moved in the collision method
            self.flip = True
            self.direction = -1
            if not self.in_air:
                self.state = "run"
        # Running right
        if self.move_right:
            self.dx = self.speed  # The rect is moved in the collision method
            self.flip = False
            self.direction = 1
            if not self.in_air:
                self.state = "run"

        # Idling
        if not (self.move_left or self.move_right) and self.hp > 0:
            if not self.in_air:
                self.state = "idle"

    def shoot(self, bullet_group: pygame.sprite.Group):
        if self.shooting and self.shoot_cooldown == 0:
            bullet = Bullet(self.rect.centerx, self.rect.y + 15, self.direction)
            bullet_group.add(bullet)
            self.bullet_sound.play()
            self.shoot_cooldown = 1

        # Firerate
        if self.shoot_cooldown != 0:
            self.shoot_cooldown += 1
        if self.shoot_cooldown > 20:
            self.shoot_cooldown = 0

    def get_key_press(self):
        keys = pygame.key.get_pressed()

        # Default states
        self.move_left = self.move_right = self.jumping = self.shooting = False

        # Move left
        if keys[pygame.K_a] and self.hp > 0:
            self.move_right = False
            self.move_left = True
        # Move right
        if keys[pygame.K_d] and self.hp > 0:
            self.move_left = False
            self.move_right = True
        # Jump
        if (keys[pygame.K_j] or keys[pygame.K_SPACE])and self.hp > 0:
            self.jumping = True
        # Shoot
        if (keys[pygame.K_k] or keys[pygame.K_s])and self.hp > 0:
            self.shooting = True

    def auto(self, player_rect, player_hp, tile_group: pygame.sprite.Group):
        # Move in the direction
        self.move_left = self.move_right = False
        if self.direction == 1 and self.wait_timer == 0 and self.hp > 0:
            self.move_right = True
            self.move_left = False
        elif self.direction == -1 and self.wait_timer == 0 and self.hp > 0:
            self.move_left = True
            self.move_right = False

        # Update displacement
        if self.move_right or self.move_left:
            self.displacement -= 2
        
        # Roam for a little while before turning around or continue walking
        if self.displacement <= 0:
            self.wait_timer += 1
        elif self.wait_timer != 0:
            self.wait_timer += 1
        if self.wait_timer > random.randint(50, 300):
            self.direction *= int(random.choice([1, -1]))
            self.displacement = 100
            self.wait_timer = 0

        # Update rect positions
        if self.direction == 1:
            self.range_rect = pygame.rect.Rect(self.rect.right, self.rect.y + 14, 120, 2)
            self.jump_rect = pygame.rect.Rect(self.rect.right + 5, self.rect.top + 4, 12, 10)
            self.edge_rect = pygame.rect.Rect(self.rect.right + 14, self.rect.bottom + 28, 8, 8)
            self.flip = False
        elif self.direction == -1:
            self.range_rect = pygame.rect.Rect(self.rect.left - 120, self.rect.y + 14, 120, 2)
            self.jump_rect = pygame.rect.Rect(self.rect.left - 15, self.rect.top + 4, 12, 10)
            self.edge_rect = pygame.rect.Rect(self.rect.left - 22, self.rect.bottom + 28, 8, 8)
            self.flip = True 

        # Don't fall off an edge
        if not self.edge_rect.collidedictall(tile_group.spritedict) and not self.jumping:
            self.wait_timer += 1

        # Jump when there is a block in front of the Soldier
        self.jumping = False
        if self.jump_rect.collidedictall(tile_group.spritedict):
            self.jumping = True
        
        # Shooting
        self.shooting = False
        # if self.range_rect.colliderect(player_rect) and not self.range_rect.collidedictall(tile_group.spritedict) and self.hp > 0 and player_hp > 0:
        if self.range_rect.colliderect(player_rect) and self.hp > 0 and player_hp > 0:
            self.wait_timer = 30
            self.shooting = True

    def health(self, bullet_group, kill=False):
        # Check if bullets hit the Soldier
        for bullet in bullet_group.sprites():
            if pygame.sprite.collide_mask(self, bullet):
                self.hp -= BULLET_DAMAGE
                bullet.kill()
        
        # Delay before killing
        if self.hp <= 0:
            self.fps = 0.08
            self.state = "death"
            self.move_left = self.move_right = self.jumping = self.shooting = False
            self.wait_timer = 1
            self.dead_timer += 1
            if self.i >= 7:
                self.i = 8
                self.fps = 0
        
        # Kill or respawn
        if self.dead_timer > 170:
            if kill:
                self.kill()
            elif self.lives > 0:
                self.respawn()

    def scroll(self):
        scroll = 0
        if (self.move_left and self.rect.left <= BOUNDRY):
            scroll = self.speed
        elif self.move_right and self.rect.right >= SCREEN_WIDTH - BOUNDRY:
            scroll = -self.speed
        self.rect.x += scroll

        return scroll
                 
    def respawn(self):
        self.lives -= 1
        self.hp = 120
        self.dead_timer = 0
        self.ammo = 100
        self.rect.center = (random.randint(200, 400), -100)  # This doesn't check if the player spawns on land or not
        self.fps = 0.11

    def fall(self):
        # Apply gravity and terminal velocity
        self.y_vel += GRAVITY
        if self.y_vel >= TERMINAL_VEL:
            self.y_vel = TERMINAL_VEL

        self.dy = self.y_vel  # The rect is moved in the collision method
        if self.y_vel != 0:
            self.in_air = True

        if self.rect.top >= 500:
            self.hp = 0

    def collisions(self, tile_group: pygame.sprite.Group, scroll=0):
        for tile in tile_group.sprites():
            # Vertical collision
            if tile.rect.colliderect(self.rect.x, self.rect.y + self.dy, self.rect.width, self.rect.height):
                if self.y_vel >= 0:
                    self.dy = tile.rect.top - self.rect.bottom
                    self.y_vel = 0
                    self.in_air = False
                elif self.y_vel < 0:
                    self.dy = self.rect.top - tile.rect.bottom
                    self.y_vel = 0

            # Horizontal collision
            if tile.rect.colliderect(self.rect.x + self.dx, self.rect.y + 5, self.rect.width, self.rect.height - 10):
                self.dx = 0

        # Move the rect here
        self.rect.x += self.dx + scroll
        self.rect.y += self.dy

    def __str__(self) -> str:
        return f"(Speed: {self.speed})"
    
if __name__ == "__main__":
    print("This is the character class. It is not a standalone file.")
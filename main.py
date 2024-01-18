import pygame

import random

import math

# Initialize Pygame
pygame.init()

# Game screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Metroidvania Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
TRANSPARENT_WHITE = (255, 255, 255, 128)  # Semi-transparent white for afterimages

# Initialize game state
font = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 36)


# ! Player class ! # 

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_height = 60
        self.crouched_height = self.original_height // 2
        self.width = 30
        self.image = pygame.Surface([self.width, self.original_height])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - self.original_height

        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -15
        self.move_speed = 10
        self.crouch_speed = 1.5  # Speed multiplier when crouching in mid-air

        self.is_crouching = False
        self.jumps_remaining = 20  # Allow for double jump

        self.is_dashing = False
        self.dash_speed = 20
        self.dash_duration = 10
        self.dash_cooldown = 10
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

        self.facing_right = True # We start facing Right
        self.is_airborne = False
        
    # ! -- Technical Shiz -- ! # 
    def get_debug_info(self):
        info = [
            f"Position: ({self.rect.x}, {self.rect.y})",
            f"Velocity: ({self.velocity_x}, {self.velocity_y})",
            f"Is Dashing: {self.is_dashing}",
            f"Jumps Remaining: {self.jumps_remaining}",
            f"Grounded: {self.is_grounded()}",
            f"Crouching: {self.is_crouching}",
            f"Facing Right: {self.facing_right}"
            # Add any other relevant states here
        ]
        return info
    
    def is_grounded(self):
        # Check if the player is on or very close to the ground
        return self.rect.bottom >= SCREEN_HEIGHT 
    
    def handle_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
    
        # Correct the player position if it's below the ground
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
    
    def handle_wall_collision(self):
        # Left wall collision
        if self.rect.left < 0:
            self.rect.left = 0
            self.handle_wall_stick()

        # Right wall collision
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.handle_wall_stick()

    def handle_wall_stick(self):
        # Implement wall stick logic
        # For now, just set vertical velocity to a slower slide down
        self.velocity_y = min(self.velocity_y, 1)  # Slower slide down speed
    def on_landing(self):
        self.jumps_remaining = 20
        
    # ! Ye Old Update Function ! # 
    def update(self):
        keys = pygame.key.get_pressed()
        self.velocity_x = 0

        # Handle movement and actions
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.move_speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.velocity_x = self.move_speed
            self.facing_right = True

        if keys[pygame.K_LSHIFT] and self.dash_cooldown_timer == 0:
            self.start_dash()
            
        if keys[pygame.K_DOWN]:
            self.crouch()
        elif self.is_crouching:
            self.stand_up()  # Stand up on crouch release
            
        was_airborne = self.is_airborne
        self.is_airborne = not self.is_grounded()

        # Call on_landing when transitioning from airborne to grounded
        if was_airborne and not self.is_airborne:
            self.on_landing()
        self.handle_gravity()
        self.handle_wall_collision()
        self.handle_dash()
        
        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    # ! 'Abilities' ! # 
    def jump(self):
        if self.jumps_remaining > 0:
            self.velocity_y = self.jump_strength 
            self.jumps_remaining -= 1

    def crouch(self):
        if not self.is_crouching:
            self.is_crouching = True
            bottom = self.rect.bottom
            self.rect.height = self.crouched_height
            self.rect.bottom = bottom

    def stand_up(self):
        print('standup comedy')
        self.is_crouching = False
        bottom = self.rect.bottom  # Store the bottom position
        self.rect.height = self.original_height
        self.rect.bottom = bottom  # Reset the bottom position
            
    def start_dash(self):
        if self.dash_cooldown_timer == 0:  # Check if cooldown is over
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            self.velocity_x = self.dash_speed if self.facing_right else -self.dash_speed

    def handle_dash(self):
        if self.is_dashing:
            if self.dash_timer > 0:
                self.dash_timer -= 1
                self.velocity_x = self.dash_speed if self.facing_right else -self.dash_speed
                self.create_afterimage()
            else:
                self.is_dashing = False
                # Reset the horizontal velocity to 0 or normal movement speed when dash ends
                self.velocity_x = self.move_speed if self.facing_right else -self.move_speed

        # Dash cooldown timer
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

    # Raddest VFX effect since never
    def create_afterimage(self):
        afterimage = Afterimage(self.rect.x, self.rect.y, self.width, self.rect.height)
        all_sprites.add(afterimage)

# Afterimage class
class Afterimage(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.fill(TRANSPARENT_WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.lifetime = 10  # Frames before disappearing

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 120)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect()

        # Spawn off-screen at the top with a slight horizontal velocity
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = -self.size

        self.horizontal_speed = random.choice([-1, 1]) * random.uniform(0.5, 1.5)  # Slight horizontal velocity
        self.vertical_speed = random.uniform(3, 8) + 8 / self.size  # Vertical speed

    def update(self):
        self.rect.x += self.horizontal_speed
        self.rect.y += self.vertical_speed

        if self.rect.bottom > SCREEN_HEIGHT:
            self.create_debris()
            self.kill()

    def create_debris(self):
        for _ in range(random.randint(self.size // 2, self.size)):  # Create 3-6 debris particles
            debris = Debris(self.rect.center)
            all_sprites.add(debris)

class Debris(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface([5, 5], pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (2, 2), 2)
        self.rect = self.image.get_rect(center=position)

        self.horizontal_speed = random.uniform(-3, 3)
        self.vertical_speed = -random.uniform(2, 4)  # Initially move upwards
        self.gravity = 0.1
        self.lifetime = random.randint(20, 60)

    def update(self):
        self.rect.x += self.horizontal_speed
        self.vertical_speed += self.gravity
        self.rect.y += self.vertical_speed

        # Fade out
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            alpha = int(255 * (self.lifetime / 60))
            self.image.set_alpha(alpha)

        # Remove if off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.top > SCREEN_HEIGHT:
            self.kill()

    # Rest of the class...

class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([60, 40])
        self.image.fill(WHITE)  # Placeholder for spaceship image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 60)  # Random horizontal start position
        self.rect.y = 10  # Start just above the top of the screen

        self.move_speed = 3  # Speed of the spaceship's movement
        self.direction = 1  # 1 for moving right, -1 for moving left

    def update(self):
        # Move the spaceship horizontally
        self.rect.x += self.move_speed * self.direction

        # Change direction upon hitting the screen boundaries
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

    def drop_bomb(self):
        bomb = Bomb(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bomb)
        # Assuming bombs is a Group for all bomb sprites
        bombs.add(bomb)

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(RED)  # Red color for the bomb
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_HEIGHT:
            self.create_debris()
            self.kill()  # Remove the bomb if it goes off the screen
        
    def create_debris(self):
        for _ in range(random.randint(5, 10)):  # Create 3-6 debris particles
            debris = Debris(self.rect.center)
            all_sprites.add(debris)

def draw_debug_info(player, screen):
    # Debug util func
    debug_info = player.get_debug_info()
    y = 10
    for line in debug_info:
        text_surface = font_small.render(line, True, WHITE)
        screen.blit(text_surface, (10, y))
        y += 30


# ! -- nitialize game state

# Asteroid Spawn Logic 
spawn_interval = 1500  # in milliseconds (1.5 seconds)
last_spawn_time = pygame.time.get_ticks()

# Mmm spaceship logic
spaceship_added = False
spaceship_visible_time = 10000  # 10 seconds visible
spaceship_disappear_time = pygame.time.get_ticks() + spaceship_visible_time
spaceship_time = 10000  # Add spaceship after 10 seconds
bomb_drop_interval = 800  # Drop a bomb every 2 seconds
last_bomb_time = pygame.time.get_ticks()

running = True
show_debug = False
game_over = False
score = 0

# init player
player = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
asteroids = pygame.sprite.Group()
bombs = pygame.sprite.Group()   

clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

## !! ----------------- GAME LOOP -------------------------- !! ## 

while running:

    # !-- GAME OVER LOGIC ! -- # 
    if game_over:
        screen.fill(BLACK)
        game_over_text = font.render("Game Over", True, WHITE)
        restart_text = font_small.render("Press Space to Restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            # To display the score
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 50))
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over = False
                    score = 0
                                        # Mmm spaceship logic
                    spaceship_added = False
                    spaceship_visible_time = 10000  # 10 seconds visible
                    spaceship_disappear_time = pygame.time.get_ticks() + spaceship_visible_time
                    spaceship_time = 10000  # Add spaceship after 10 seconds
                    bomb_drop_interval = 800  # Drop a bomb every 2 seconds
                    last_bomb_time = pygame.time.get_ticks()
                    
                                        
                    start_ticks = pygame.time.get_ticks()  # Reset the timer
                    player.rect.x, player.rect.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - player.original_height  # Reset player position

                    
                    all_sprites.empty()
                    asteroids.empty()  # Clear all asteroids
                    bombs.empty()  # Clear all bombs
                    # Add any other necessary resets here
                    all_sprites.add(player)
        pygame.display.flip()
        continue

    # ELSE 
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        # If X 
        if event.type == pygame.QUIT:
            running = False
    
        # You better... 
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            # Show Debug Toggle
            if event.key == pygame.K_q:
                show_debug = not show_debug
    
    
    # jaja dumb
    all_sprites.update()
    
    # Asteroid Spawning Logic
    if current_time - last_spawn_time > spawn_interval:
        new_asteroid = Asteroid()
        asteroids.add(new_asteroid)
        all_sprites.add(new_asteroid)
        last_spawn_time = current_time
        spawn_interval = max(500, spawn_interval - 1)  # Decrease the interval, but not below 0.5 seconds
    
    # Asteroid Self Detection, Just looks kinda cool, is sometimes handy
    for asteroid in asteroids:
        hits = pygame.sprite.spritecollide(asteroid, asteroids, False)
        if len(hits) > 1:
            asteroid.create_debris()
            asteroid.kill()
    
    # Asteroid collisions with walls
    for asteroid in asteroids:
        if asteroid.rect.left <= 0 or asteroid.rect.right >= SCREEN_WIDTH:
            asteroid.create_debris()
            asteroid.kill()
            
    if not spaceship_added and current_time >= spaceship_time:
        spaceship = Spaceship()
        all_sprites.add(spaceship)
        spaceship_added = True
        spaceship_disappear_time = current_time + spaceship_visible_time
        spawn_interval *= 2  # Reset to normal asteroid spawn rate

    if current_time >= spaceship_disappear_time:
        spaceship.kill()  # Remove the spaceship
        spawn_interval /= 2  # Double the rate of asteroid spawning
        spaceship_added = False
        # Set timer for spaceship to reappear
        spaceship_time = current_time + 10000  # 5 minutes later

    # Drop bombs from the spaceship
    if spaceship_added and current_time - last_bomb_time > bomb_drop_interval:
        spaceship.drop_bomb()
        last_bomb_time = current_time
    
    # If Anything Hits the player they die :( 
    if pygame.sprite.spritecollideany(player, asteroids) or pygame.sprite.spritecollideany(player, bombs):
        game_over = True
    
    
    # Calculate Seconds Alive
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    score = seconds
    
    # Drawing 
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    
    if show_debug:
        draw_debug_info(player, screen)
    
    
    # To display the score
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 50))
    
    pygame.display.flip()
    
    clock.tick(60)
    
pygame.quit()

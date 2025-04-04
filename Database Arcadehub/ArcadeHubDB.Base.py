import pygame
import os
import sys

if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"

print("Logged in as:", CURRENT_USER)

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
ah_width, ah_height = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Move the Sprite")

# Load assets
sprite = pygame.image.load("dove.png")
sprite = pygame.transform.scale(sprite, (50, 50))
background = pygame.image.load("testbackground1.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

sprite_x, sprite_y = WIDTH // 2, HEIGHT // 2

# Movement speed
speed = 10

# Define wall boundaries (brick areas)
walls = [
    pygame.Rect(0, 0, 352, 198),
    pygame.Rect(450, 0, 354, 197),
    pygame.Rect(0, 400, 350, 200),
    pygame.Rect(460, 400, 345, 200)
]

# Function to launch other games
def launch_roshambo():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.ROSHAMBO.py", CURRENT_USER])

def launch_tetris():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.Tetris.py", CURRENT_USER])

def launch_snake():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.Snake.py", CURRENT_USER])

def launch_pacman():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.pacman.py", CURRENT_USER])

# Main loop
running = True
while running:
    pygame.time.delay(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    # Get key states
    keys = pygame.key.get_pressed()
    new_x, new_y = sprite_x, sprite_y
    if keys[pygame.K_LEFT]:
        new_x -= speed
    if keys[pygame.K_RIGHT]:
        new_x += speed
    if keys[pygame.K_UP]:
        new_y -= speed
    if keys[pygame.K_DOWN]:
        new_y += speed

    # Prevent moving out of bounds
    new_x = max(0, min(ah_width - sprite.get_width(), new_x))
    new_y = max(0, min(ah_height - sprite.get_height(), new_y))

    # Check collision with walls
    sprite_rect = pygame.Rect(new_x, new_y, sprite.get_width(), sprite.get_height())
    if not any(sprite_rect.colliderect(wall) for wall in walls):
        sprite_x, sprite_y = new_x, new_y
    if sprite_y >= HEIGHT - sprite.get_height() and 350 < sprite_x < 460:
        launch_roshambo()
    if sprite_x <= 10 and 200 < sprite_y < 400: #tetris
        launch_tetris()
    if sprite_y <= 10 and 250 < sprite_x < 550:#snake
        launch_snake()
    if sprite_x >= ah_width - sprite.get_width() - 10 and 200 < sprite_y < 400:#pacman
        launch_pacman()


    # Draw everything
    win.blit(background, (0, 0))
    win.blit(sprite, (sprite_x, sprite_y))
    pygame.display.update()
pygame.quit()

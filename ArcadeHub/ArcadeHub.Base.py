import pygame
import os
import subprocess

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Move the Sprite")

# Load assets
sprite = pygame.image.load("dove.png")  # Replace with your sprite image
sprite = pygame.transform.scale(sprite, (50, 50))  # Resize if needed
background = pygame.image.load("testbackground1.png")  # Replace with your background image
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

sprite_x, sprite_y = WIDTH // 2, HEIGHT // 2

# Movement speed
speed = 10

# Define wall boundaries (brick areas)
walls = [
    pygame.Rect(0, 0, 352, 198),  # Top-left wall
    pygame.Rect(450, 0, 354, 197),  # Top-right wall
    pygame.Rect(0, 400, 350, 200),  # Bottom-left wall
    pygame.Rect(460, 400, 345, 200)  # Bottom-right wall
]

# Function to launch another script
def launch_roshambo():
    pygame.quit()
    subprocess.run(["python", "ArcadeHub.ROSHAMBO.py"])
    exit()


# Main loop
running = True
while running:
    pygame.time.delay(30)  # Delay to control frame rate

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Check if the ESC key is pressed
                running = False  # Close the program

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
    new_x = max(0, min(WIDTH - sprite.get_width(), new_x))
    new_y = max(0, min(HEIGHT - sprite.get_height(), new_y))

    # Check collision with walls
    sprite_rect = pygame.Rect(new_x, new_y, sprite.get_width(), sprite.get_height())
    if not any(sprite_rect.colliderect(wall) for wall in walls):
        sprite_x, sprite_y = new_x, new_y

    # Check if sprite is at the bottom between bottom-left and bottom-right walls
    if sprite_y >= HEIGHT - sprite.get_height() and 350 < sprite_x < 460:
        launch_roshambo()

    # Draw everything
    win.blit(background, (0, 0))  # Draw background
    win.blit(sprite, (sprite_x, sprite_y))
    pygame.display.update()

pygame.quit()

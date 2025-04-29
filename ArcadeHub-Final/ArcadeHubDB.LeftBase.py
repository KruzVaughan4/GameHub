import pygame
import os
import sys
import subprocess

# Get user login name
if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"

pygame.init()

# Display
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Hub - Left Base")

# Load assets
try:
    sprite = pygame.image.load("man.png")
    sprite = pygame.transform.scale(sprite, (50, 50))
    background = pygame.image.load("ArcadeHubB3.png")  # Updated background
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Error loading assets: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# Starting position (right side on red carpet)
sprite_x = 700
sprite_y = 285
speed = 10

# Walls (update as needed for new background layout)
walls = [
    pygame.Rect(0, 0, 680, 265),
    pygame.Rect(0, 337, 800, 264),
    pygame.Rect(734, 0, 66, 267)
]

# Dictionary of teleport portals
portals = {
    "dino": {
        "rect": pygame.Rect(680, 0, 51, 63),  # Purple door
        "game_file": "dinorun.py"
    } ,
    "Mainbase": {
        "rect": pygame.Rect(788, 265, 11, 68),  # Purple door
        "game_file": "ArcadeHubDB.Base.py"
    }

}

# Launch any game
def launch_game(game_file):
    command = [sys.executable, game_file, CURRENT_USER]
    print(f"\nLaunching {game_file}...")
    pygame.quit()
    os.execv(sys.executable, command)

# Game loop
running = True
while running:
    pygame.time.delay(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ESC key to open ArcadeHub_Database.py
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                launch_game("ArcadeHub_Database.py")

    # Movement
    keys = pygame.key.get_pressed()
    new_x, new_y = sprite_x, sprite_y

    if keys[pygame.K_a]: new_x -= speed
    if keys[pygame.K_d]: new_x += speed
    if keys[pygame.K_w]: new_y -= speed
    if keys[pygame.K_s]: new_y += speed

    new_x = max(0, min(WIDTH - sprite.get_width(), new_x))
    new_y = max(0, min(HEIGHT - sprite.get_height(), new_y))

    sprite_rect = pygame.Rect(new_x, new_y, sprite.get_width(), sprite.get_height())

    if not any(sprite_rect.colliderect(w) for w in walls):
        sprite_x, sprite_y = new_x, new_y

    # Check each portal
    for portal in portals.values():
        if sprite_rect.colliderect(portal["rect"]):
            launch_game(portal["game_file"])

    # Draw
    win.blit(background, (0, 0))
    win.blit(sprite, (sprite_x, sprite_y))
    pygame.display.update()

pygame.quit()

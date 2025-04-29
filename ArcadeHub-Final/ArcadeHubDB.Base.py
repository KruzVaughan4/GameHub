import pygame
import os
import sys
import subprocess
import time
import platform
import random  # AI - Added for fun facts

# Get user login name
if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"

print("Logged in as:", CURRENT_USER)

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Hub Main Base")

# Load assets
try:
    sprite = pygame.image.load("man.png")
    sprite = pygame.transform.scale(sprite, (50, 50))
    background = pygame.image.load("ArcadeHubB2.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    tab_image = pygame.image.load("Images/tab_key.jpg")  # AI - Load tab image
    tab_image = pygame.transform.scale(tab_image, (50, 50))
except Exception as e:
    print(f"Error loading assets: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# Set starting position (bottom center of carpet)
sprite_x = WIDTH // 2 - sprite.get_width() // 2
sprite_y = HEIGHT - 80

# Movement speed
speed = 10

# Define wall boundaries
walls = [
    pygame.Rect(0, 0, 65, 265),
    pygame.Rect(115, 0, 71, 265),
    pygame.Rect(245, 0, 101, 265),
    pygame.Rect(453, 0, 101, 265),
    pygame.Rect(607, 0, 70, 265),
    pygame.Rect(738, 0, 68, 265),
    pygame.Rect(0, 334, 362, 266),
    pygame.Rect(432, 334, 367, 265)
]

# Define game launch zones as a dictionary
game_zones = {
    "roshambo": {
        "rect": pygame.Rect(195, 55, 51, 63),
        "game_file": "ArcadeHubDB.ROSHAMBO.py",
        "test_command": [sys.executable, "ArcadeHubDB.ROSHAMBO.py", CURRENT_USER]
    },
    "tetris": {
        "rect": pygame.Rect(556, 55, 51, 63),
        "game_file": "ArcadeHubDB.Tetris.py",
        "test_command": [sys.executable, "ArcadeHubDB.Tetris.py", CURRENT_USER]
    },
    "left_block": {
        "rect": pygame.Rect(0, 267, 8, 65),
        "game_file": "ArcadeHubDB.LeftBase.py",
        "test_command": [sys.executable, "ArcadeHubDB.LeftBase.py", CURRENT_USER]
    },
    "snake": {
        "rect": pygame.Rect(680, 55, 51, 63),
        "game_file": "ArcadeHubDB.Snake.py",
        "test_command": [sys.executable, "ArcadeHubDB.Snake.py", CURRENT_USER]
    },
    "pacman": {
        "rect": pygame.Rect(70, 55, 51, 63),
        "game_file": "ArcadeHubDB.pacman.py",
        "test_command": [sys.executable, "ArcadeHubDB.pacman.py", CURRENT_USER]
    }
}

# AI - Load fun facts
def load_fun_facts(filename="Images/fun_facts.txt"):
    with open(filename, "r") as f:
        facts = f.readlines()
    return [fact.strip() for fact in facts if fact.strip()]

# Initialize fun facts
show_fun_fact = False
fun_facts = load_fun_facts()
current_fun_fact = ""
tab_pressed = False

# Verify all game files exist before starting
def verify_game_files():
    """Check if all game files exist before running"""
    missing_files = []
    for zone_name, zone_data in game_zones.items():
        if not os.path.exists(zone_data["game_file"]):
            missing_files.append(zone_data["game_file"])

    if missing_files:
        print("ERROR: Missing game files:")
        for f in missing_files:
            print(f" - {f}")
        print("\nPlease ensure all game files are in the same directory as the hub.")
        return False
    return True

# Launch a game
def launch_game(game_file, test_command):
    """Ultimate game launching function with all possible fixes"""
    print(f"\n=== Launching {game_file} ===")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Absolute path: {os.path.abspath(game_file)}")

    try:
        # First try the standard method
        pygame.quit()
        os.execv(sys.executable, test_command)

    except Exception as e:
        print(f"CRITICAL: All launch methods failed: {e}")
        print("Attempting to restart hub...")
        hub_path = os.path.abspath(__file__)
        subprocess.Popen([sys.executable, hub_path, CURRENT_USER])
        sys.exit()

# AI - Toggle fun fact
def toggle_fun_fact():
    global show_fun_fact, current_fun_fact
    if show_fun_fact:
        show_fun_fact = False
    else:
        current_fun_fact = random.choice(fun_facts)
        show_fun_fact = True

# Check if sprite entered any game zone
def check_game_zones(sprite_rect):
    """Check if sprite is in any game launch zone"""
    for zone_name, zone_data in game_zones.items():
        if sprite_rect.colliderect(zone_data["rect"]):
            print(f"\nEntering {zone_name} game...")
            launch_game(zone_data["game_file"], zone_data["test_command"])

# Load font for rendering fun facts
font = pygame.font.SysFont('Arial', 20)

if not verify_game_files():
    input("Press Enter to exit...")
    sys.exit(1)

# Main loop
running = True
while running:
    pygame.time.delay(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # AI - Handle tab press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB and not tab_pressed:
                toggle_fun_fact()
                tab_pressed = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_TAB:
                tab_pressed = False

    keys = pygame.key.get_pressed()
    new_x, new_y = sprite_x, sprite_y

    if keys[pygame.K_a]:
        new_x -= speed
    if keys[pygame.K_d]:
        new_x += speed
    if keys[pygame.K_w]:
        new_y -= speed
    if keys[pygame.K_s]:
        new_y += speed

    # Keep sprite on screen
    new_x = max(0, min(WIDTH - sprite.get_width(), new_x))
    new_y = max(0, min(HEIGHT - sprite.get_height(), new_y))

    # Check for wall collisions
    sprite_rect = pygame.Rect(new_x, new_y, sprite.get_width(), sprite.get_height())
    if not any(sprite_rect.colliderect(w) for w in walls):
        sprite_x, sprite_y = new_x, new_y

    # Check if sprite entered any game zone
    check_game_zones(pygame.Rect(sprite_x, sprite_y, sprite.get_width(), sprite.get_height()))

    if keys[pygame.K_ESCAPE]:
        running = False

    # Draw everything
    win.blit(background, (0, 0))
    win.blit(sprite, (sprite_x, sprite_y))

    # AI - Fun fact display
    if show_fun_fact:
        fun_fact_text = current_fun_fact
        max_text_width = 400
        lines = []
        current_line = ""
        words = fun_fact_text.split()

        for word in words:
            if font.size(current_line + " " + word)[0] <= max_text_width:
                current_line += " " + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        line_height = 30
        total_text_height = len(lines) * line_height

        start_y = HEIGHT - (len(lines) * line_height) - 20
        start_x = 20

        for i, line in enumerate(lines):
            # Outline
            outline_surface = font.render(line, True, (255, 255, 255))
            win.blit(outline_surface, (start_x - 2, start_y + (i * line_height) - 2))
            win.blit(outline_surface, (start_x + 2, start_y + (i * line_height) - 2))
            win.blit(outline_surface, (start_x - 2, start_y + (i * line_height) + 2))
            win.blit(outline_surface, (start_x + 2, start_y + (i * line_height) + 2))

            # Text
            line_surface = font.render(line, True, (0, 0, 0))
            win.blit(line_surface, (start_x, start_y + (i * line_height)))
    else:
        win.blit(tab_image, (20, HEIGHT - tab_image.get_height() - 20))


    pygame.display.update()

pygame.quit()

import pygame
import os
import sys
import subprocess
import time
import platform

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
pygame.display.set_caption("Arcade Hub B2")

# Load assets
try:
    sprite = pygame.image.load("man.png")
    sprite = pygame.transform.scale(sprite, (50, 50))
    background = pygame.image.load("ArcadeHubB2.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
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
        "rect": pygame.Rect(217, 55, 50, 50),
        "game_file": "ArcadeHubDB.ROSHAMBO.py",
        "test_command": [sys.executable, "ArcadeHubDB.ROSHAMBO.py", CURRENT_USER]
    },
    "tetris": {
        "rect": pygame.Rect(0, 200, 10, 200),
        "game_file": "ArcadeHubDB.Tetris.py",
        "test_command": [sys.executable, "ArcadeHubDB.Tetris.py", CURRENT_USER]
    },
    "snake": {
        "rect": pygame.Rect(250, 0, 300, 10),
        "game_file": "ArcadeHubDB.Snake.py",
        "test_command": [sys.executable, "ArcadeHubDB.Snake.py", CURRENT_USER]
    },
    "pacman": {
        "rect": pygame.Rect(WIDTH - 10, 200, 10, 200),
        "game_file": "ArcadeHubDB.pacman.py",
        "test_command": [sys.executable, "ArcadeHubDB.pacman.py", CURRENT_USER]
    }
}


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


def launch_game(game_file, test_command):
    """Ultimate game launching function with all possible fixes"""
    print(f"\n=== Launching {game_file} ===")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Absolute path: {os.path.abspath(game_file)}")

    try:
        # First try the standard method
        pygame.quit()
        time.sleep(0.2)  # Ensure pygame fully quits

        # Method 1: Standard Popen with new process group
        try:
            if platform.system() == "Windows":
                subprocess.Popen(test_command,
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                                 shell=True)
            else:
                subprocess.Popen(test_command,
                                 start_new_session=True)
            print("Launched using standard method")
            sys.exit()
        except Exception as e:
            print(f"Standard launch failed: {e}")

        # Method 2: Alternative Windows method
        if platform.system() == "Windows":
            try:
                subprocess.Popen(['start', 'cmd', '/k'] + test_command, shell=True)
                print("Launched using Windows cmd method")
                sys.exit()
            except Exception as e:
                print(f"Windows cmd method failed: {e}")

        # Method 3: Direct system call
        try:
            if platform.system() == "Windows":
                os.system(f'start "" "{sys.executable}" "{game_file}" "{CURRENT_USER}"')
            else:
                os.system(f'"{sys.executable}" "{game_file}" "{CURRENT_USER}" &')
            print("Launched using system call")
            sys.exit()
        except Exception as e:
            print(f"System call failed: {e}")

        # If all else fails, try running directly
        try:
            os.execv(sys.executable, ['python'] + test_command[1:])
            print("Launched using execv")
        except Exception as e:
            print(f"Execv failed: {e}")
            raise

    except Exception as e:
        print(f"CRITICAL: All launch methods failed: {e}")
        print("Attempting to restart hub...")
        hub_path = os.path.abspath(__file__)
        subprocess.Popen([sys.executable, hub_path, CURRENT_USER])
        sys.exit()


def check_game_zones(sprite_rect):
    """Check if sprite is in any game launch zone"""
    for zone_name, zone_data in game_zones.items():
        if sprite_rect.colliderect(zone_data["rect"]):
            print(f"\nEntering {zone_name} game...")
            launch_game(zone_data["game_file"], zone_data["test_command"])


# Verify all game files exist before starting
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
    pygame.display.update()

pygame.quit()

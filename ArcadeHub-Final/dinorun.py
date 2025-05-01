import pygame
import random
import os
import sys  # <-- Import sys to exit properly if needed

if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"



# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 300
WHITE = (255, 255, 255)
GRAVITY = 1
JUMP_STRENGTH = -15
FPS = 30
CENTER_Y = HEIGHT // 2  # Center the game elements
SPEED_INCREMENT = 0.5  # Speed increase per 15 points

# Asset paths
ASSET_DIR = "assets"
DINO_START_IMG = pygame.image.load(os.path.join(ASSET_DIR, "dinoStart.png"))
DINO_RUN_IMGS = [
    pygame.image.load(os.path.join(ASSET_DIR, "dinoRun1.png")),
    pygame.image.load(os.path.join(ASSET_DIR, "dinoRun2.png"))
]
DINO_END_IMG = pygame.image.load(os.path.join(ASSET_DIR, "dinoEnd.png"))
CACTUS_IMG = pygame.image.load(os.path.join(ASSET_DIR, "cactus.png"))
BACKGROUND_IMG = pygame.image.load(os.path.join(ASSET_DIR, "backdrop.png"))

# Scale images
DINO_RUN_IMGS = [pygame.transform.scale(img, (50, 50)) for img in DINO_RUN_IMGS]
DINO_START_IMG = pygame.transform.scale(DINO_START_IMG, (50, 50))
DINO_END_IMG = pygame.transform.scale(DINO_END_IMG, (50, 50))
CACTUS_IMG = pygame.transform.scale(CACTUS_IMG, (30, 50))
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))

# Game Variables
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Function to read the highest score from scores.txt
def read_high_score():
    if os.path.exists("scores.txt"):
        with open("scores.txt", "r") as file:
            try:
                return int(file.read().strip())  # Read and convert to int
            except ValueError:
                return 0  # Default if file is empty or invalid
    return 0  # Default if file doesn't exist

# Function to write a new highest score
def write_high_score(score):
    with open("scores.txt", "w") as file:
        file.write(str(score))

class Dinosaur:
    def __init__(self):
        self.x, self.y = 50, CENTER_Y - 25  # Centered vertically
        self.velocity = 0
        self.is_jumping = False
        self.running = False
        self.alive = True
        self.animation_index = 0
        self.image = DINO_START_IMG
        self.last_animation_time = pygame.time.get_ticks()  # Animation timing

    def jump(self):
        if not self.is_jumping and self.alive:
            self.is_jumping = True
            self.velocity = JUMP_STRENGTH

    def update(self):
        self.y += self.velocity
        self.velocity += GRAVITY
        if self.y >= CENTER_Y - 25:
            self.y = CENTER_Y - 25
            self.is_jumping = False
        if self.running and self.alive:
            # Change animation every 0.5s
            current_time = pygame.time.get_ticks()
            if current_time - self.last_animation_time > 500:
                self.animation_index = (self.animation_index + 1) % 2
                self.image = DINO_RUN_IMGS[self.animation_index]
                self.last_animation_time = current_time
        elif not self.alive:
            self.image = DINO_END_IMG

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Cactus:
    def __init__(self, speed):
        self.image = CACTUS_IMG
        self.x = WIDTH
        self.y = CENTER_Y - 25  # Centered vertically
        self.speed = speed

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def off_screen(self):
        return self.x < -30

    def collide(self, dino):
        return pygame.Rect(self.x, self.y, 30, 50).colliderect(
            pygame.Rect(dino.x, dino.y, 50, 50))


def launch_left_base():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHubDB.LeftBase.py", CURRENT_USER])

def main():
    high_score = read_high_score()  # Load the highest score

    while True:
        # Start screen
        screen.fill(WHITE)
        text = font.render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 3, HEIGHT // 2))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        launch_left_base()

        dino = Dinosaur()
        dino.running = True
        obstacles = []
        running = True
        score = 0
        spawn_timer = 0
        cactus_speed = 5

        while running:
            screen.fill(WHITE)
            screen.blit(BACKGROUND_IMG, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        dino.jump()
                    elif event.key == pygame.K_ESCAPE:
                        launch_left_base()

            dino.update()
            dino.draw(screen)

            spawn_timer += 1
            if spawn_timer > FPS * 1.5 and random.randint(1, 100) < 10:
                obstacles.append(Cactus(cactus_speed))
                spawn_timer = 0

            for obstacle in obstacles[:]:
                obstacle.update()
                obstacle.draw(screen)
                if obstacle.off_screen():
                    obstacles.remove(obstacle)
                    score += 1
                    if score % 15 == 0:
                        cactus_speed += SPEED_INCREMENT  # Increase speed every 15 points
                if obstacle.collide(dino):
                    dino.alive = False
                    running = False  # Game Over

            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 40))

            pygame.display.update()
            clock.tick(FPS)

        # Update high score if beaten
        if score > high_score:
            high_score = score
            write_high_score(high_score)

        # Game Over Screen
        screen.fill(WHITE)
        text1 = font.render("Game Over!", True, (0, 0, 0))
        text2 = font.render("Press SPACE to Restart or ESC to Quit", True, (0, 0, 0))
        high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
        screen.blit(text1, (WIDTH // 3, HEIGHT // 3))
        screen.blit(text2, (WIDTH // 6, HEIGHT // 2))
        screen.blit(high_score_text, (WIDTH // 3, HEIGHT // 2 + 40))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        launch_left_base()


if __name__ == "__main__":
    main()

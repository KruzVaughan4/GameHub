import random
import pygame
import sys
import sqlite3


if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "player1"

def create_table():
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user TEXT PRIMARY KEY,
            roshambo INTEGER DEFAULT 0,
            tetris INTEGER DEFAULT 0,
            snake INTEGER DEFAULT 0,
            pacman INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def ensure_user_exists(username):
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user=?", (username,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users (user, roshambo) VALUES (?, ?)", (username, 0))
        conn.commit()
    conn.close()

def get_db_roshambo():
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute("SELECT roshambo FROM users WHERE user=?", (CURRENT_USER,))
    result = cur.fetchone()
    conn.close()
    if result:
        return int(result[0])
    return 0

def update_db_roshambo():
    hiWins = get_db_roshambo()
    if game.winCount > hiWins:
        conn = sqlite3.connect('arcade_users.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET roshambo=? WHERE user=?", (game.winCount, CURRENT_USER))
        conn.commit()
        conn.close()

def launch_arcadehub():
    # This function is no longer used since pressing ESC will simply exit.
    pygame.quit()
    sys.exit()

# Screen Settings
TITLE = "Rock Paper Scissors"
WIDTH = 800
HEIGHT = 600

# Variables
player_choice = ""
ai_choice = ""

class GameData:
    def __init__(self):
        self.winCount = 0
        self.lostCount = 0
        self.tieCount = 0
        self.round = 0

def aiChooses():
    choices = ["Rock", "Scissors", "Paper"]
    return random.choice(choices)

def judgeGame(player, ai):
    global game, opponent
    if player == ai:
        game.tieCount += 1
    elif (player == "Rock" and ai == "Scissors") or \
         (player == "Scissors" and ai == "Paper") or \
         (player == "Paper" and ai == "Rock"):
        game.winCount += 1
    else:
        game.lostCount += 1
    game.round += 1
    if ai == "Rock":
        opponent = pygame.image.load("s0.png")
    elif ai == "Scissors":
        opponent = pygame.image.load("s1.png")
    elif ai == "Paper":
        opponent = pygame.image.load("s2.png")
    opponent = pygame.transform.scale(opponent, (150, 150))

game = GameData()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

opponent = pygame.image.load("q0.png")
rock = pygame.image.load("d0.png")
scissors = pygame.image.load("d1.png")
paper = pygame.image.load("d2.png")
selectionBox = pygame.image.load("box.png")

opponent = pygame.transform.scale(opponent, (150, 150))
rock = pygame.transform.scale(rock, (100, 100))
scissors = pygame.transform.scale(scissors, (100, 100))
paper = pygame.transform.scale(paper, (100, 100))
selectionBox = pygame.transform.scale(selectionBox, (110, 110))

create_table()
ensure_user_exists(CURRENT_USER)
hiWins = get_db_roshambo()

running = True
selectionBox_y = HEIGHT * 0.4
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                update_db_roshambo()
                running = False
            elif event.key == pygame.K_DOWN:
                if selectionBox_y == HEIGHT * 0.4:
                    selectionBox_y = HEIGHT * 0.6
                elif selectionBox_y == HEIGHT * 0.6:
                    selectionBox_y = HEIGHT * 0.8
            elif event.key == pygame.K_UP:
                if selectionBox_y == HEIGHT * 0.6:
                    selectionBox_y = HEIGHT * 0.4
                elif selectionBox_y == HEIGHT * 0.8:
                    selectionBox_y = HEIGHT * 0.6
            elif event.key == pygame.K_RETURN:
                ai_choice = aiChooses()
                if selectionBox_y == HEIGHT * 0.4:
                    player_choice = "Rock"
                elif selectionBox_y == HEIGHT * 0.6:
                    player_choice = "Scissors"
                else:
                    player_choice = "Paper"
                judgeGame(player_choice, ai_choice)
                hiWins = get_db_roshambo()  
    screen.blit(opponent, (WIDTH * 0.6, HEIGHT * 0.5))
    screen.blit(rock, (WIDTH * 0.25 - 3, HEIGHT * 0.4 + 5))
    screen.blit(scissors, (WIDTH * 0.25 - 3, HEIGHT * 0.6 + 5))
    screen.blit(paper, (WIDTH * 0.25 - 3 , HEIGHT * 0.8 + 5))
    screen.blit(selectionBox, (WIDTH * 0.25 - 10, selectionBox_y))
    font = pygame.font.Font(None, 36)
    screen.blit(font.render("Press Esc to exit", True, WHITE), (20, 20))
    screen.blit(font.render("CHOOSE A MOVE", True, WHITE), (WIDTH * 0.5 - 150, HEIGHT * 0.1))
    screen.blit(font.render(f"Round: {game.round}", True, WHITE), (WIDTH * 0.15, HEIGHT * 0.2))
    screen.blit(font.render(f"Won: {game.winCount}", True, WHITE), (WIDTH * 0.65, HEIGHT * 0.2))
    screen.blit(font.render(f"Lost: {game.lostCount}", True, WHITE), (WIDTH * 0.65, HEIGHT * 0.25))
    screen.blit(font.render(f"Draw: {game.tieCount}", True, WHITE), (WIDTH * 0.65, HEIGHT * 0.3))
    screen.blit(font.render("VS", True, WHITE), (WIDTH * 0.5 - 50, HEIGHT * 0.6))
    screen.blit(font.render(f"High Score (Wins): {hiWins}", True, WHITE), (WIDTH - 310, HEIGHT - 40))
    pygame.display.flip()
    clock.tick(30)

update_db_roshambo()
pygame.quit()
sys.exit()

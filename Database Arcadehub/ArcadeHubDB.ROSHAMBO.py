import random
import pygame
import sys
import os
import ArcadeHub_Database

if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"

ArcadeHub_Database.create_table()
ArcadeHub_Database.ensure_user_exists(CURRENT_USER)

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

class GameData:
    def __init__(self):
        self.winCount = 0
        self.lostCount = 0
        self.tieCount = 0
        self.round = 0

game = GameData()

WHITE = (255,255,255)
BLACK = (0,0,0)

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors")

opponent = pygame.image.load("q0.png")
rock = pygame.image.load("d0.png")
scissors = pygame.image.load("d1.png")
paper = pygame.image.load("d2.png")
selectionBox = pygame.image.load("box.png")

opponent = pygame.transform.scale(opponent, (150,150))
rock = pygame.transform.scale(rock, (100,100))
scissors = pygame.transform.scale(scissors, (100,100))
paper = pygame.transform.scale(paper, (100,100))
selectionBox = pygame.transform.scale(selectionBox, (110,110))

hiWins = ArcadeHub_Database.get_high_score(CURRENT_USER, "roshambo")

running = True
selectionBox_y = HEIGHT*0.4
clock = pygame.time.Clock()

def launch_arcadehub():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.Base.py", CURRENT_USER])

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ArcadeHub_Database.update_high_score(CURRENT_USER, "roshambo", game.winCount)
                launch_arcadehub()
            elif event.key == pygame.K_DOWN:
                if selectionBox_y == HEIGHT*0.4:
                    selectionBox_y = HEIGHT*0.6
                elif selectionBox_y == HEIGHT*0.6:
                    selectionBox_y = HEIGHT*0.8
            elif event.key == pygame.K_UP:
                if selectionBox_y == HEIGHT*0.6:
                    selectionBox_y = HEIGHT*0.4
                elif selectionBox_y == HEIGHT*0.8:
                    selectionBox_y = HEIGHT*0.6
            elif event.key == pygame.K_RETURN:
                ai_choice = aiChooses()
                if selectionBox_y == HEIGHT*0.4:
                    player_choice = "Rock"
                elif selectionBox_y == HEIGHT*0.6:
                    player_choice = "Scissors"
                else:
                    player_choice = "Paper"
                judgeGame(player_choice, ai_choice)
                hiWins = ArcadeHub_Database.get_high_score(CURRENT_USER, "roshambo")
    screen.blit(opponent,(WIDTH*0.6,HEIGHT*0.5))
    screen.blit(rock,(WIDTH*0.25-3,HEIGHT*0.4+5))
    screen.blit(scissors,(WIDTH*0.25-3,HEIGHT*0.6+5))
    screen.blit(paper,(WIDTH*0.25-3,HEIGHT*0.8+5))
    screen.blit(selectionBox,(WIDTH*0.25-10,selectionBox_y))
    font = pygame.font.Font(None,36)
    screen.blit(font.render("Press Esc to exit",True,WHITE),(20,20))
    screen.blit(font.render("CHOOSE A MOVE",True,WHITE),(WIDTH*0.5-150,HEIGHT*0.1))
    screen.blit(font.render(f"Round: {game.round}",True,WHITE),(WIDTH*0.15,HEIGHT*0.2))
    screen.blit(font.render(f"Won: {game.winCount}",True,WHITE),(WIDTH*0.65,HEIGHT*0.2))
    screen.blit(font.render(f"Lost: {game.lostCount}",True,WHITE),(WIDTH*0.65,HEIGHT*0.25))
    screen.blit(font.render(f"Draw: {game.tieCount}",True,WHITE),(WIDTH*0.65,HEIGHT*0.3))
    screen.blit(font.render("VS",True,WHITE),(WIDTH*0.5-50,HEIGHT*0.6))
    screen.blit(font.render(f"High Score (Wins): {hiWins}",True,WHITE),(WIDTH-310,HEIGHT-40))
    pygame.display.flip()
    clock.tick(30)

ArcadeHub_Database.update_high_score(CURRENT_USER, "roshambo", game.winCount)
pygame.quit()
sys.exit()

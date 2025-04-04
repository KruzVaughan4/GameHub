import pygame
import random
import sys
import os
import ArcadeHub_Database

pygame.init()

if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"

ArcadeHub_Database.create_table()
ArcadeHub_Database.ensure_user_exists(CURRENT_USER)

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

dis_width = 600
dis_height = 400

dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake')

overlay = pygame.image.load("assets/scanlines.png")
overlay = pygame.transform.scale(overlay, (dis_width, dis_height))

clock = pygame.time.Clock()

snake_block = 10
snake_speed = 15

font_style = pygame.font.Font("assets/Daydream.ttf", 15)
score_font = pygame.font.Font("assets/Daydream.ttf", 20)

def Your_score(score):
    value = score_font.render("YOUR SCORE: " + str(score), True, yellow)
    dis.blit(value, [5, 5])

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 10, dis_height / 2])

def launch_arcadehub():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.Base.py", CURRENT_USER])


def gameLoop():
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            dis.fill(black)
            message("Press Space-Play Again or Esc-Quit", red)
            Your_score(Length_of_snake - 1)
            pygame.draw.rect(dis, white, [0, 0, dis_width, dis_height], 5)
            dis.blit(overlay, (0, 0))
            pygame.display.update()
            ArcadeHub_Database.update_high_score(CURRENT_USER, "snake", (Length_of_snake - 1))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        launch_arcadehub()
                    if event.key == pygame.K_SPACE:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_d:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_w:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_s:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= (dis_width - 10) or x1 < 10 or y1 >= (dis_height - 10) or y1 < 10:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        dis.fill(black)
        pygame.draw.rect(dis, white, [0, 0, dis_width, dis_height], 5)
        pygame.draw.rect(dis, red, [foodx, foody, snake_block, snake_block])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        dis.blit(overlay, (0, 0))
        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(10, (dis_width - 10) - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(10, (dis_height - 10) - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()

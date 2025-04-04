# original tetris game based on TechWithTim's Tetris tutorials
# https://www.techwithtim.net/tutorials/game-development-with-python/tetris-pygame/tutorial-1
# Modified with different game modes by Kruz Vaughan


import pygame
import random
import sys
import ArcadeHub_Database
import os

pygame.font.init()

if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = "Guest"

ArcadeHub_Database.create_table()
ArcadeHub_Database.ensure_user_exists(CURRENT_USER)

# GLOBALS VARS
s_width = 800
s_height = 600  # make this 700 if it breaks
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

def launch_arcadehub():
    pygame.quit()
    os.execv(sys.executable, [sys.executable, "ArcadeHub.Base.py", CURRENT_USER])


# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0,255,0)]*7
# index 0 - 6 represent shape


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_pos={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions

def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5,0,random.choice(shapes))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("arial", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))

def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        pygame.draw.line(surface, (0,128,0), (sx, sy + i*block_size), (sx+play_width, sy+i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (0,128,0), (sx + j*block_size, sy), (sx + j*block_size, sy+play_height))

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y+inc)
                locked[newKey] = locked.pop(key)
    return inc

def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('arial',30)
    label = font.render('Next Shape',1,(0,255,0))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx+j*block_size, sy+i*block_size, block_size, block_size), 0)
    surface.blit(label, (sx+10, sy-30))

def draw_window(surface, grid, score=0):
    surface.fill((0,0,0))
    pygame.font.init()
    font = pygame.font.SysFont('arial',60)
    label = font.render('Tetris', 1, (0,255,0))
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), 30))
    # current score
    font = pygame.font.SysFont('arial',30)
    label = font.render('Score: ' + str(score), 1, (0,255,0))
    sx = top_left_x + play_width + 20
    sy = top_left_y + play_height/2 - 100
    surface.blit(label, (sx+20, sy+160))

    # exit
    font = pygame.font.SysFont('arial', 30)
    label = font.render('ESC to Exit: ', 1, (0, 255, 0))
    sx = top_left_x + play_width - 550
    sy = top_left_y + play_height - 750
    surface.blit(label, (sx + 20, sy + 160))

    hiScore = ArcadeHub_Database.get_high_score(CURRENT_USER, "tetris")
    label = font.render('High Score: ' + str(hiScore), 1, (0,255,0))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx-40, sy-300))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x+j*block_size, top_left_y+i*block_size, block_size, block_size), 0)
    pygame.draw.rect(surface, (0,255,0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)
    # pygame.display.update()

def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27 # default fall speed
    level_time = 0
    score = 0
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                launch_arcadehub()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
    ArcadeHub_Database.update_high_score(CURRENT_USER, "tetris", score)
    main_menu(win)

def gamemode2(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.05
    level_time = 0
    score = 0
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                launch_arcadehub()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
    ArcadeHub_Database.update_high_score(CURRENT_USER, "tetris", score)
    main_menu(win)

def gamemode3(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27 # fall speed
    level_time = 0
    score = 0

    swap_time = pygame.time.get_ticks()
    swap_interval = 1000 # 3000 milliseconds (3 seconds)


    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        if pygame.time.get_ticks() - swap_time > swap_interval:
            old_x, old_y, old_rotation = current_piece.x, current_piece.y, current_piece.rotation
            swap_time = pygame.time.get_ticks()
            current_piece = next_piece
            next_piece = get_shape()
            current_piece.x, current_piece.y, current_piece.rotation = old_x, old_y, old_rotation
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                launch_arcadehub()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (0,255,0))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
    ArcadeHub_Database.update_high_score(CURRENT_USER, "tetris", score)
    main_menu(win)

def gamemode4(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.05  # fall speed
    level_time = 0
    score = 0

    swap_time = pygame.time.get_ticks()
    swap_interval = 200 # 3000 milliseconds (3 seconds)

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        if pygame.time.get_ticks() - swap_time > swap_interval:
            old_x, old_y, old_rotation = current_piece.x, current_piece.y, current_piece.rotation
            swap_time = pygame.time.get_ticks()
            current_piece = next_piece
            next_piece = get_shape()
            current_piece.x, current_piece.y, current_piece.rotation = old_x, old_y, old_rotation
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                launch_arcadehub()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (0,255,0))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
    ArcadeHub_Database.update_high_score(CURRENT_USER, "tetris", score)
    main_menu(win)

def main_menu(win):
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press 1 for regular, 2 for turbo, 3 for random block, and 4 for expert mode', 20, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main(win)
                if event.key == pygame.K_2:
                    gamemode2(win)
                if event.key == pygame.K_3:
                    gamemode3(win)
                if event.key == pygame.K_4:
                    gamemode4(win)
                if event.key == pygame.K_ESCAPE:
                    launch_arcadehub()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

main_menu(win)

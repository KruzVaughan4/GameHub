import pgzrun
import random
import math
import pygame
import subprocess
import sys
TEST_MODE = True
speed = 2
ghost_speed = 1
TITLE = 'Pac-Man'
world_size = 20
block_size = 32
WIDTH = world_size * block_size
HEIGHT = world_size * block_size

pacman = Actor('pacman_o.png')
pacman.x = pacman.y = 1.5 * block_size
pacman.dx, pacman.dy = 0, 0
pacman.food_left = None
pacman.level = 1
pacman.score = 0
pacman.lives = 3
pacman.power = 0
pacman.banner = None
pacman.banner_counter = 0

char_to_image = {
    '.': 'dot.png',
    '=': 'wall.png',
    '*': 'power.png',
    'g': 'ghost1.png',
    'G': 'ghost3.png',
    'h': 'ghost4.png',
    'H': 'ghost5.png',
}

world = []
ghosts = []
game_over_flag = False
def launch_arcadehub():
    pygame.quit()
    subprocess.run(["python", "arcadehub.base.py"])
    sys.exit()
def load_level(number):
    pacman.food_left = 0
    with open("level_%s.txt" % number) as f:
        for line in f:
            row = []
            for block in line:
                row.append(block)
                if block == '.':
                    pacman.food_left += 1
            world.append(row)

def set_banner(message, count):
    pacman.banner = message
    pacman.banner_counter = count

def alternate(value, option1, option2):
    if value == option1:
        return option2
    else:
        return option1

def periodic():
    if pacman.banner_counter > 0:
        pacman.banner_counter -= 1
    if pacman.power > 0:
        pacman.power -= 1
        if pacman.power > 10:
            for g in ghosts:
                g.image = 'ghost2.png'
        else:
            for g in ghosts:
                if g.active:
                    g.image = alternate(g.image, 'ghost_white.png', 'ghost2.png')
        if pacman.power == 0:
            for g in ghosts:
                g.image = g.orig_image

clock.schedule_interval(periodic, 0.2)

def draw():
    screen.clear()
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            image = char_to_image.get(block, None)
            if image:
                screen.blit(image, (x * block_size, y * block_size))
    pacman.draw()
    if not game_over_flag:
        if pacman.banner and pacman.banner_counter > 0:
            screen.draw.text(pacman.banner, center=(WIDTH / 2, HEIGHT / 2), fontsize=120)
    for g in ghosts:
        if g.active:
            g.draw()
    screen.draw.text("Score: %s" % pacman.score, topleft=(8, 4), fontsize=40)
    screen.draw.text("Lives: %s" % pacman.lives, topright=(WIDTH - 8, 4), fontsize=40)
    if game_over_flag:
        screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2), fontsize=120, color="red")

def set_random_dir(sprite, speed):
    sprite.dx = random.choice([-speed, speed])
    sprite.dy = random.choice([-speed, speed])

def new_ghost_direction(g):
    if pacman.power:
        g.dx = math.copysign(ghost_speed * 1.5, g.x - pacman.x)
        g.dy = math.copysign(ghost_speed * 1.5, g.y - pacman.y)
    else:
        g.dx = random.choice([-ghost_speed, ghost_speed])
        g.dy = random.choice([-ghost_speed, ghost_speed])

def make_ghost_actors():
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block in ('g', 'G', 'h', 'H'):
                g = Actor(char_to_image[block], (x * block_size, y * block_size), anchor=('left', 'top'))
                g.orig_image = g.image
                g.start_pos = (x, y)
                g.active = True
                set_random_dir(g, ghost_speed)
                ghosts.append(g)
                new_ghost_direction(g)
                world[y][x] = None

def next_level():
    global world, ghosts
    world = []
    ghosts = []
    pacman.level += 1
    load_level(pacman.level)
    make_ghost_actors()
    reset_sprites()

def eat_food():
    ix, iy = int(pacman.x / block_size), int(pacman.y / block_size)
    if world[iy][ix] == '.':
        world[iy][ix] = None
        pacman.food_left -= 1
        pacman.score += 1
    elif world[iy][ix] == '*':
        world[iy][ix] = None
        pacman.power = 25
        set_banner("Power Up!", 5)
        for g in ghosts:
            new_ghost_direction(g)
        pacman.score += 5

def on_key_down(key):
    if key == keys.LEFT:
        pacman.dx = -speed
    if key == keys.RIGHT:
        pacman.dx = speed
    if key == keys.UP:
        pacman.dy = -speed
    if key == keys.DOWN:
        pacman.dy = speed
    if key == keys.ESCAPE:
        launch_arcadehub()

def on_key_up(key):
    if key in (keys.LEFT, keys.RIGHT):
        pacman.dx = 0
    if key in (keys.UP, keys.DOWN):
        pacman.dy = 0
    if TEST_MODE:
        if key == keys.N:
            next_level()

def blocks_ahead_of(sprite, dx, dy):
    x = int(round(sprite.left)) + dx
    y = int(round(sprite.top)) + dy
    ix, iy = int(x // block_size), int(y // block_size)
    rx, ry = x % block_size, y % block_size
    if ix == world_size - 1:
        rx = 0
    if iy == world_size - 1:
        ry = 0
    blocks = [world[iy][ix]]
    if rx:
        blocks.append(world[iy][ix + 1])
    if ry:
        blocks.append(world[iy + 1][ix])
    if rx and ry:
        blocks.append(world[iy + 1][ix + 1])
    return blocks

def wrap_around(mini, val, maxi):
    if val < mini:
        return maxi
    elif val > maxi:
        return mini
    else:
        return val

def move_ahead(sprite):
    oldx, oldy = sprite.x, sprite.y
    if '=' not in blocks_ahead_of(sprite, sprite.dx, 0):
        sprite.x += sprite.dx
    if '=' not in blocks_ahead_of(sprite, 0, sprite.dy):
        sprite.y += sprite.dy
    sprite.x = wrap_around(0, sprite.x, WIDTH - block_size)
    sprite.y = wrap_around(0, sprite.y, HEIGHT - block_size)
    moved = (oldx != sprite.x or oldy != sprite.y)
    if moved and sprite == pacman:
        a = 0
        if oldx < sprite.x:
            a = 0
        elif oldy > sprite.y:
            a = 90
        elif oldx > sprite.x:
            a = 180
        elif oldy < sprite.y:
            a = 270
        sprite.angle = a
    return moved

def reset_sprites():
    pacman.x = pacman.y = 1.5 * block_size
    for g in ghosts:
        g.x = g.start_pos[0] * block_size
        g.y = g.start_pos[1] * block_size
        g.active = True

def ghost_eaten(g):
    g.active = False
    set_banner("Ghost Eaten!", 5)
    pacman.score += 50
    clock.schedule_unique(lambda: respawn_ghost(g), 3.0)

def respawn_ghost(g):
    g.x = g.start_pos[0] * block_size
    g.y = g.start_pos[1] * block_size
    g.active = True

def game_over():
    global game_over_flag
    game_over_flag = True
    set_banner("", 0)

def update():
    if game_over_flag:
        return
    move_ahead(pacman)
    eat_food()
    if pacman.food_left == 0:
        next_level()
    for g in ghosts:
        if not g.active:
            continue
        if not move_ahead(g):
            set_random_dir(g, ghost_speed)
        if g.colliderect(pacman):
            if pacman.power > 0:
                ghost_eaten(g)
            else:
                reset_sprites()
                set_banner("Live lost", 5)
                pacman.lives -= 1
                if pacman.lives <= 0:
                    game_over()
                reset_sprites()

load_level(1)
make_ghost_actors()
pgzrun.go()

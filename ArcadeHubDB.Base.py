import sqlite3
import pygame
import sys
import subprocess
import random

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

def create_user_db(username):
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (user) VALUES (?)', (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def delete_user_db(username):
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE user=?', (username,))
    conn.commit()
    conn.close()

def update_high_score(user, game, score):
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET {game}=? WHERE user=?', (score, user))
    conn.commit()
    conn.close()

def get_high_score(user, game):
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute(f'SELECT {game} FROM users WHERE user=?', (user,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def get_all_users():
    conn = sqlite3.connect('arcade_users.db')
    cur = conn.cursor()
    cur.execute('SELECT user, roshambo, tetris, snake, pacman FROM users')
    users = cur.fetchall()
    conn.close()
    return users

# AI
def load_fun_facts(filename="Images/fun_facts.txt"):
    with open(filename, "r") as f:
        facts = f.readlines()
    return [fact.strip() for fact in facts if fact.strip()]
# AI

class Button:
    def __init__(self, rect, text, action, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = font
        self.bg_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
    def draw(self, surface, selected=False):
        color = (150, 150, 250) if selected else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main():
    pygame.init()
    win = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Arcade Hub")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    create_table()
    current_state = "main_menu"
    selected_button_index = 0
    last_state = current_state
    selected_user = None
    input_text = ""
    message = ""
    arcade_initialized = False
    ah_width, ah_height = 800, 600
    ah_sprite = None
    ah_background = None
    sprite_x, sprite_y = 0, 0
    speed = 10
    walls = []

# AI
    show_fun_fact = False
    tab_image = pygame.image.load("Images/tab_key.jpg")
    tab_image = pygame.transform.scale(tab_image, (50, 50))
    fun_facts = load_fun_facts()
    current_fun_fact = ""
    tab_pressed = False
# AI

    # launch_game now passes the selected user as an argument.
    def launch_game(game_script):
        subprocess.run(["python", game_script, selected_user])
        return "user_menu"
    
# AI    
    def toggle_fun_fact():
        nonlocal show_fun_fact, current_fun_fact
        if show_fun_fact:
            show_fun_fact = False
        else:
            current_fun_fact = random.choice(fun_facts)
            show_fun_fact = True
# AI

    running = True
    while running:
        if current_state != last_state:
            selected_button_index = 0
            last_state = current_state
        current_buttons = []
        extra_draw = []
        if current_state == "main_menu":
            extra_draw.append((font.render("Main Menu", True, (0,0,0)), (300,30)))
            def goto_create_user():
                nonlocal current_state, input_text, message
                input_text = ""
                message = ""
                current_state = "create_user"
            def goto_delete_user():
                nonlocal current_state, message
                message = ""
                current_state = "delete_user"
            def goto_select_user():
                nonlocal current_state, message
                message = ""
                current_state = "select_user"
            current_buttons = [
                Button((300,100,200,50), "Create User", goto_create_user, font),
                Button((300,170,200,50), "Delete User", goto_delete_user, font),
                Button((300,240,200,50), "Select User", goto_select_user, font),
                Button((300,310,200,50), "Exit", lambda: sys.exit(), font)
            ]
            extra_draw.append((small_font.render("Users:", True, (0,0,0)), (50,100)))
            users = get_all_users()
            y_offset = 130
            for user, r, t, s, p in users:
                extra_draw.append((small_font.render(f"{user} | R:{r} T:{t} S:{s} P:{p}", True, (0,0,0)), (50, y_offset)))
                y_offset += 25
        elif current_state == "create_user":
            extra_draw.append((font.render("Create User", True, (0,0,0)), (300,30)))
            extra_draw.append((small_font.render("Enter username:", True, (0,0,0)), (200,100)))
            def confirm_create():
                nonlocal input_text, current_state, message
                if input_text.strip():
                    create_user_db(input_text.strip())
                    message = f"User '{input_text.strip()}' created."
                input_text = ""
                current_state = "main_menu"
            def back_to_main():
                nonlocal current_state, input_text
                input_text = ""
                current_state = "main_menu"
            current_buttons = [
                Button((250,220,120,50), "Confirm", confirm_create, font),
                Button((430,220,120,50), "Back", back_to_main, font)
            ]
            if message:
                extra_draw.append((small_font.render(message, True, (0,100,0)), (200,300)))
        elif current_state == "delete_user":
            extra_draw.append((font.render("Delete User", True, (0,0,0)), (300,30)))
            users = get_all_users()
            btn_y = 100
            btn_list = []
            for (user, r, t, s, p) in users:
                def make_delete_action(u):
                    return lambda: delete_user_db(u)
                btn_list.append(Button((250, btn_y, 300, 40), f"{user} | R:{r} T:{t} S:{s} P:{p}", make_delete_action(user), small_font))
                btn_y += 50
            def back_to_main():
                nonlocal current_state
                current_state = "main_menu"
            btn_list.append(Button((300,450,200,50), "Back", back_to_main, font))
            current_buttons = btn_list
            extra_draw.append((small_font.render("Use arrows then Enter to delete user.", True, (0,0,0)), (250,70)))
        elif current_state == "select_user":
            extra_draw.append((font.render("Select User", True, (0,0,0)), (300,30)))
            users = get_all_users()
            btn_list = []
            btn_y = 100
            def select_user(u):
                nonlocal selected_user, current_state
                selected_user = u
                current_state = "user_menu"
            for (user, r, t, s, p) in users:
                def make_select_action(u):
                    return lambda: select_user(u)
                btn_list.append(Button((250, btn_y, 300, 40), f"{user} | R:{r} T:{t} S:{s} P:{p}", make_select_action(user), small_font))
                btn_y += 50
            def back_to_main():
                nonlocal current_state
                current_state = "main_menu"
            btn_list.append(Button((300,450,200,50), "Back", back_to_main, font))
            current_buttons = btn_list
            extra_draw.append((small_font.render("Use arrows then Enter to select user.", True, (0,0,0)), (250,70)))
        elif current_state == "user_menu":
            extra_draw.append((font.render(f"User: {selected_user}", True, (0,0,0)), (300,30)))
            def goto_arcade():
                nonlocal current_state
                current_state = "arcade_hub"
            def view_scores():
                nonlocal current_state
                current_state = "view_high_score"
            def back_to_main():
                nonlocal current_state, selected_user
                selected_user = None
                current_state = "main_menu"
            current_buttons = [
                Button((300,120,200,50), "Play Arcade Hub", goto_arcade, font),
                Button((300,190,200,50), "View Scores", view_scores, font),
                Button((300,260,200,50), "Main Menu", back_to_main, font)
            ]
        elif current_state == "view_high_score":
            scores = get_all_users()
            for user, r, t, s, p in scores:
                if user == selected_user:
                    score_text = f"R:{r} T:{t} S:{s} P:{p}"
                    break
            extra_draw.append((font.render(f"{selected_user} Scores", True, (0,0,0)), (280,30)))
            extra_draw.append((font.render(score_text, True, (0,0,0)), (300,150)))
            def back_to_user_menu():
                nonlocal current_state
                current_state = "user_menu"
            current_buttons = [Button((350,300,100,50), "Back", back_to_user_menu, font)]
        elif current_state == "arcade_hub":
            if not arcade_initialized:
                ah_sprite = pygame.image.load("Images/dove.png")
                ah_sprite = pygame.transform.scale(ah_sprite, (50,50))
                ah_background = pygame.image.load("Images/testbackground1.png")
                ah_background = pygame.transform.scale(ah_background, (ah_width, ah_height))
                sprite_x, sprite_y = ah_width//2, ah_height//2
                walls = [pygame.Rect(0,0,352,198), pygame.Rect(450,0,354,197), pygame.Rect(0,400,350,200), pygame.Rect(460,400,345,200)]
                arcade_initialized = True

            # AI    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB and not tab_pressed:
                    toggle_fun_fact()
                    tab_pressed = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:
                    tab_pressed = False
            # AI

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
            new_x = max(0, min(ah_width - ah_sprite.get_width(), new_x))
            new_y = max(0, min(ah_height - ah_sprite.get_height(), new_y))
            sprite_rect = pygame.Rect(new_x, new_y, ah_sprite.get_width(), ah_sprite.get_height())
            if not any(sprite_rect.colliderect(w) for w in walls):
                sprite_x, sprite_y = new_x, new_y
            if sprite_y >= ah_height - ah_sprite.get_height() and 350 < sprite_x < 460:
                current_state = launch_game("ArcadeHubDB.ROSHAMBO.py")
                arcade_initialized = False
            if sprite_x <= 10 and 200 < sprite_y < 400:
                current_state = launch_game("ArcadeHubDB.Tetris.py")
                arcade_initialized = False
            if sprite_y <= 10 and 250 < sprite_x < 550:
                current_state = launch_game("ArcadeHubDB.Snake.py")
                arcade_initialized = False
            if sprite_x >= ah_width - ah_sprite.get_width() - 10 and 200 < sprite_y < 400:
                current_state = launch_game("ArcadeHubDB.pacman.py")
                arcade_initialized = False
            if keys[pygame.K_ESCAPE]:
                current_state = "user_menu"
                arcade_initialized = False
            win.blit(ah_background, (0,0))
            win.blit(ah_sprite, (sprite_x, sprite_y))

# AI
            if show_fun_fact:
                fun_fact_text = current_fun_fact
                max_text_width = 400  # You can adjust this based on the space you want for the text
                lines = []
                current_line = ""
                words = fun_fact_text.split()

    # Split the text into lines based on the width
                for word in words:
                    if font.size(current_line + " " + word)[0] <= max_text_width:
                        current_line += " " + word
                    else:
                        if current_line:  # Save the current line before starting a new one
                            lines.append(current_line)
                        current_line = word  # Start a new line with the current word
                if current_line:  # Add the last line if any
                    lines.append(current_line)

                line_height = 30  # Adjust line height if needed
                total_text_height = len(lines) * line_height

    # Position for the text (top-right corner)
                start_y = 20  # 20px padding from the top
                start_x = ah_width - max_text_width - 20  # 20px padding from the right edge

    # Draw each line of text
                for i, line in enumerate(lines):
                     # First render white text (outline effect)
                    outline_surface = font.render(line, True, (255, 255, 255))  # White outline
                    # Blit the outline at different offsets to create the outline effect
                    win.blit(outline_surface, (start_x - 2, start_y + (i * line_height) - 2))  # Top-left offset
                    win.blit(outline_surface, (start_x + 2, start_y + (i * line_height) - 2))  # Top-right offset
                    win.blit(outline_surface, (start_x - 2, start_y + (i * line_height) + 2))  # Bottom-left offset
                    win.blit(outline_surface, (start_x + 2, start_y + (i * line_height) + 2))  # Bottom-right offset

        # Then render black text on top of the outline
                    line_surface = font.render(line, True, (0, 0, 0))  # Black text
                    win.blit(line_surface, (start_x, start_y + (i * line_height)))

            else:
                win.blit(tab_image, (ah_width - tab_image.get_width() - 20, 20))
# AI

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if current_state not in ["arcade_hub"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and current_buttons:
                        selected_button_index = (selected_button_index - 1) % len(current_buttons)
                    elif event.key == pygame.K_DOWN and current_buttons:
                        selected_button_index = (selected_button_index + 1) % len(current_buttons)
                    elif event.key == pygame.K_RETURN and current_buttons:
                        current_buttons[selected_button_index].action()
                    elif current_state == "create_user":
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.key not in [pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN]:
                            input_text += event.unicode
        if current_state not in ["arcade_hub"]:
            win.fill((255,255,255))
            for surf, pos in extra_draw:
                win.blit(surf, pos)
            if current_state == "create_user":
                input_box = pygame.Rect(200,140,400,40)
                pygame.draw.rect(win, (230,230,230), input_box)
                pygame.draw.rect(win, (0,0,0), input_box, 2)
                text_surface = font.render(input_text, True, (0,0,0))
                win.blit(text_surface, (input_box.x+5, input_box.y+5))
            for i, btn in enumerate(current_buttons):
                btn.draw(win, selected=(i==selected_button_index))
            
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
    sys.exit()

main()

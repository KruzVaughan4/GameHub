import pygame
import sys
import sqlite3
import os

DB_NAME = 'arcade_users.db'

def create_table():
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (user) VALUES (?)', (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def delete_user_db(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE user=?', (username,))
    conn.commit()
    conn.close()

def update_high_score(user, game, score):
    current = get_high_score(user, game)
    if score > current:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(f'UPDATE users SET {game}=? WHERE user=?', (score, user))
        conn.commit()
        conn.close()

def get_high_score(user, game):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f'SELECT {game} FROM users WHERE user=?', (user,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT user, roshambo, tetris, snake, pacman FROM users')
    users = cur.fetchall()
    conn.close()
    return users

def ensure_user_exists(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user=?", (username,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user, roshambo, tetris, snake, pacman) VALUES (?, 0, 0, 0, 0)",
            (username,)
        )
        conn.commit()
    conn.close()


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
    pygame.display.set_caption("Arcade Hub Menu")
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

    running = True
    while running:
        if current_state != last_state:
            selected_button_index = 0
            last_state = current_state

        current_buttons = []
        extra_draw = []

        if current_state == "main_menu":
            extra_draw.append((font.render("Main Menu", True, (0, 0, 0)), (300, 30)))

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
                Button((300, 100, 200, 50), "Create User", goto_create_user, font),
                Button((300, 170, 200, 50), "Delete User", goto_delete_user, font),
                Button((300, 240, 200, 50), "Select User", goto_select_user, font),
                Button((300, 310, 200, 50), "Exit", lambda: sys.exit(), font)
            ]

            extra_draw.append((small_font.render("Users:", True, (0, 0, 0)), (50, 100)))
            users = get_all_users()
            y_offset = 130
            for user, r, t, s, p in users:
                extra_draw.append(
                    (small_font.render(f"{user} | R:{r} T:{t} S:{s} P:{p}", True, (0, 0, 0)), (50, y_offset)))
                y_offset += 25

        elif current_state == "create_user":
            extra_draw.append((font.render("Create User", True, (0, 0, 0)), (300, 30)))
            extra_draw.append((small_font.render("Enter username:", True, (0, 0, 0)), (200, 100)))

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
                Button((250, 220, 120, 50), "Confirm", confirm_create, font),
                Button((430, 220, 120, 50), "Back", back_to_main, font)
            ]
            if message:
                extra_draw.append((small_font.render(message, True, (0, 100, 0)), (200, 300)))

        elif current_state == "delete_user":
            extra_draw.append((font.render("Delete User", True, (0, 0, 0)), (300, 30)))
            users = get_all_users()
            btn_y = 100
            btn_list = []
            for (user, r, t, s, p) in users:
                def make_delete_action(u):
                    return lambda: delete_user_db(u)
                btn_list.append(
                    Button((250, btn_y, 300, 40), f"{user} | R:{r} T:{t} S:{s} P:{p}",
                           make_delete_action(user), small_font))
                btn_y += 50

            def back_to_main():
                nonlocal current_state
                current_state = "main_menu"

            btn_list.append(Button((300, 450, 200, 50), "Back", back_to_main, font))
            current_buttons = btn_list
            extra_draw.append((small_font.render("Use arrows then Enter to delete user.", True, (0, 0, 0)), (250, 70)))

        elif current_state == "select_user":
            extra_draw.append((font.render("Select User", True, (0, 0, 0)), (300, 30)))
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
                btn_list.append(
                    Button((250, btn_y, 300, 40), f"{user} | R:{r} T:{t} S:{s} P:{p}",
                           make_select_action(user), small_font))
                btn_y += 50

            def back_to_main():
                nonlocal current_state
                current_state = "main_menu"

            btn_list.append(Button((300, 450, 200, 50), "Back", back_to_main, font))
            current_buttons = btn_list
            extra_draw.append((small_font.render("Use arrows then Enter to select user.", True, (0, 0, 0)), (250, 70)))

        elif current_state == "user_menu":
            extra_draw.append((font.render(f"User: {selected_user}", True, (0, 0, 0)), (300, 30)))

            def play_game():
                os.execv(sys.executable, [sys.executable, "ArcadeHubDB.Base.py", selected_user])

            def view_scores():
                nonlocal current_state
                current_state = "view_high_score"

            def back_to_main():
                nonlocal current_state, selected_user
                selected_user = None
                current_state = "main_menu"

            current_buttons = [
                Button((300, 120, 200, 50), "Play Game", play_game, font),
                Button((300, 190, 200, 50), "View Scores", view_scores, font),
                Button((300, 260, 200, 50), "Main Menu", back_to_main, font)
            ]

        elif current_state == "view_high_score":
            scores = get_all_users()
            score_text = "No scores found."
            for user, r, t, s, p in scores:
                if user == selected_user:
                    score_text = f"R:{r} T:{t} S:{s} P:{p}"
                    break
            extra_draw.append((font.render(f"{selected_user} Scores", True, (0, 0, 0)), (280, 30)))
            extra_draw.append((font.render(score_text, True, (0, 0, 0)), (300, 150)))

            def back_to_user_menu():
                nonlocal current_state
                current_state = "user_menu"

            current_buttons = [Button((350, 300, 100, 50), "Back", back_to_user_menu, font)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_state == "create_user":
                    if event.key == pygame.K_LEFT and current_buttons:
                        selected_button_index = (selected_button_index - 1) % len(current_buttons)
                    elif event.key == pygame.K_RIGHT and current_buttons:
                        selected_button_index = (selected_button_index + 1) % len(current_buttons)
                    elif event.key == pygame.K_RETURN and current_buttons:
                        current_buttons[selected_button_index].action()
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                else:
                    if event.key == pygame.K_UP and current_buttons:
                        selected_button_index = (selected_button_index - 1) % len(current_buttons)
                    elif event.key == pygame.K_DOWN and current_buttons:
                        selected_button_index = (selected_button_index + 1) % len(current_buttons)
                    elif event.key == pygame.K_RETURN and current_buttons:
                        current_buttons[selected_button_index].action()

        win.fill((255, 255, 255))
        for surf, pos in extra_draw:
            win.blit(surf, pos)
        if current_state == "create_user":
            input_box = pygame.Rect(200, 140, 400, 40)
            pygame.draw.rect(win, (230, 230, 230), input_box)
            pygame.draw.rect(win, (0, 0, 0), input_box, 2)
            text_surface = font.render(input_text, True, (0, 0, 0))
            win.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        for i, btn in enumerate(current_buttons):
            btn.draw(win, selected=(i == selected_button_index))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

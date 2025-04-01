import pygame
import sys
import subprocess
import ArcadeHub_Database as Database


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

    Database.create_table()

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


    def launch_game(game_script):
        subprocess.run(["python", game_script, selected_user])
        return "arcade_hub"

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
            users = Database.get_all_users()
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
                    Database.create_user_db(input_text.strip())
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
            users = Database.get_all_users()
            btn_y = 100
            btn_list = []
            for (user, r, t, s, p) in users:
                def make_delete_action(u):
                    return lambda: Database.delete_user_db(u)

                btn_list.append(
                    Button((250, btn_y, 300, 40), f"{user} | R:{r} T:{t} S:{s} P:{p}", make_delete_action(user),
                           small_font))
                btn_y += 50

            def back_to_main():
                nonlocal current_state
                current_state = "main_menu"

            btn_list.append(Button((300, 450, 200, 50), "Back", back_to_main, font))
            current_buttons = btn_list
            extra_draw.append((small_font.render("Use arrows then Enter to delete user.", True, (0, 0, 0)), (250, 70)))
        elif current_state == "select_user":
            extra_draw.append((font.render("Select User", True, (0, 0, 0)), (300, 30)))
            users = Database.get_all_users()
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
                    Button((250, btn_y, 300, 40), f"{user} | R:{r} T:{t} S:{s} P:{p}", make_select_action(user),
                           small_font))
                btn_y += 50

            def back_to_main():
                nonlocal current_state
                current_state = "main_menu"

            btn_list.append(Button((300, 450, 200, 50), "Back", back_to_main, font))
            current_buttons = btn_list
            extra_draw.append((small_font.render("Use arrows then Enter to select user.", True, (0, 0, 0)), (250, 70)))
        elif current_state == "user_menu":
            extra_draw.append((font.render(f"User: {selected_user}", True, (0, 0, 0)), (300, 30)))

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
                Button((300, 120, 200, 50), "Play Arcade Hub", goto_arcade, font),
                Button((300, 190, 200, 50), "View Scores", view_scores, font),
                Button((300, 260, 200, 50), "Main Menu", back_to_main, font)
            ]
        elif current_state == "view_high_score":
            scores = Database.get_all_users()
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
        elif current_state == "arcade_hub":
            if not arcade_initialized:
                ah_sprite = pygame.image.load("dove.png")
                ah_sprite = pygame.transform.scale(ah_sprite, (50, 50))
                ah_background = pygame.image.load("testbackground1.png")
                ah_background = pygame.transform.scale(ah_background, (ah_width, ah_height))
                sprite_x, sprite_y = ah_width // 2, ah_height // 2
                walls = [pygame.Rect(0, 0, 352, 198), pygame.Rect(450, 0, 354, 197),
                         pygame.Rect(0, 400, 350, 200), pygame.Rect(460, 400, 345, 200)]
                arcade_initialized = True
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
                current_state = launch_game("ArcadeHub.ROSHAMBO.py")
                arcade_initialized = False
            if sprite_x <= 10 and 200 < sprite_y < 400:
                current_state = launch_game("ArcadeHub.Tetris.py")
                arcade_initialized = False
            if sprite_y <= 10 and 250 < sprite_x < 550:
                current_state = launch_game("ArcadeHub.Snake.py")
                arcade_initialized = False
            if sprite_x >= ah_width - ah_sprite.get_width() - 10 and 200 < sprite_y < 400:
                current_state = launch_game("ArcadeHub.pacman.py")
                arcade_initialized = False
            if keys[pygame.K_ESCAPE]:
                current_state = "main_menu"
                arcade_initialized = False
            win.blit(ah_background, (0, 0))
            win.blit(ah_sprite, (sprite_x, sprite_y))

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


main()

# fun_facts.txt and tab_key.jpg need to go in the images folder for this to work.
# I would put them there but idk which repository os the most updated one at this point.

# Attached is the version of the arcade hub I implemented this function
# into. Each item is blocked off by '# AI' so you can just ctrl f and 
# search for it. Below are instructions or you can just look at the 
# arcade hub version and see where I put things.


# If it isn't already there, add import random. Then add the
# load fun facts function with the other functions.

import random

def load_fun_facts(filename="Images/fun_facts.txt"):
  with open(filename, "r") as f:
    facts = f.readlines()
  return [fact.strip() for fact in facts if fact.strip()]

# This shoud go in MAIN right before the launch game function " def launch_game(game_script) "

show_fun_fact = False
tab_image = pygame.image.load("Images/tab_key.jpg")
tab_image = pygame.transform.scale(tab_image, (50, 50))
fun_facts = load_fun_facts()
current_fun_fact = ""
tab_pressed = False

# This part goes right under " def launch_game(game_script) "

def toggle_fun_fact():
  nonlocal show_fun_fact, current_fun_fact
  if show_fun_fact:
    show_fun_fact = False
  else:
    current_fun_fact = random.choice(fun_facts)
    show_fun_fact = True

# Specifically this one needs to go above " keys = pygame.key.get_pressed() "
# IDK why but it didn't work when i put it under the other key press instructions.

if event.type == pygame.KEYDOWN:
  if event.key == pygame.K_TAB and not tab_pressed:
      toggle_fun_fact()
      tab_pressed = True
if event.type == pygame.KEYUP:
  if event.key == pygame.K_TAB:
      tab_pressed = False

# I apologize in advance for the following lines of code
# I couldn't get the positioning right and I was sick of fighting 
# with it so ChatGPT wrote everything below. From here down goes under
# the button instructions. Like right under " win.blit(ah_sprite, (sprite_x, sprite_y)) "
#


if show_fun_fact:
  fun_fact_text = current_fun_fact
  max_text_width = 400 
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
    win.blit(outline_surface, (start_x - 2, start_y + (i * line_height) - 2))  # Top-left offset
    win.blit(outline_surface, (start_x + 2, start_y + (i * line_height) - 2))  # Top-right offset
    win.blit(outline_surface, (start_x - 2, start_y + (i * line_height) + 2))  # Bottom-left offset
    win.blit(outline_surface, (start_x + 2, start_y + (i * line_height) + 2))  # Bottom-right offset

    # Then render black text on top of the outline
    line_surface = font.render(line, True, (0, 0, 0))  # Black text
    win.blit(line_surface, (start_x, start_y + (i * line_height)))

    else:
      win.blit(tab_image, (ah_width - tab_image.get_width() - 20, 20))
    


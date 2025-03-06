import pygame
import random

# Initialize pygame library
pygame.init()

# Define color constants
white = (255, 255, 255)  # White
yellow = (255, 255, 102)  # Yellow
black = (0, 0, 0)  # Black
red = (255, 0, 0)  # Red
green = (0, 255, 0)  # Green

# Set the dimensions of the game window
dis_width = 600
dis_height = 400

# Create the game display window with specified width and height
dis = pygame.display.set_mode((dis_width, dis_height))

# Set the title of the game window
pygame.display.set_caption('Snake')

# Load and scale the overlay image (scanlines) to match the window size
overlay = pygame.image.load("assets/scanlines.png")
overlay = pygame.transform.scale(overlay, (dis_width, dis_height))

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Define the snake block size and speed
snake_block = 10
snake_speed = 15

# Load custom fonts for displaying score and game messages
font_style = pygame.font.Font("assets/Daydream.ttf", 15)
score_font = pygame.font.Font("assets/Daydream.ttf", 20)

# Function to display the player's current score
def Your_score(score):
    value = score_font.render("YOUR SCORE: " + str(score), True, yellow)  # Render the score text
    dis.blit(value, [5, 5])  # Draw the score text on the screen at position (5, 5)

# Function to draw the snake on the screen
def our_snake(snake_block, snake_list):
    for x in snake_list:  # Loop through each segment of the snake
        pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])  # Draw each segment

# Function to display a game over message
def message(msg, color):
    mesg = font_style.render(msg, True, color)  # Render the message text
    dis.blit(mesg, [dis_width / 10, dis_height / 2])  # Draw the message on the screen at the center

# Main game loop function
def gameLoop():
    game_over = False  # Variable to track if the game is over
    game_close = False  # Variable to track if the player is close to game over

    # Initialize the snake's starting position and movement
    x1 = dis_width / 2
    y1 = dis_height / 2
    x1_change = 0  # No initial movement on x-axis
    y1_change = 0  # No initial movement on y-axis

    snake_List = []  # List to hold the coordinates of the snake's body
    Length_of_snake = 1  # The initial length of the snake

    # Randomly generate the position of the food
    foodx = round(random.randrange(10, dis_width - snake_block - 10) / 10.0) * 10.0
    foody = round(random.randrange(10, dis_height - snake_block - 10) / 10.0) * 10.0

    # Main game loop, runs until game_over is True
    while not game_over:

        while game_close == True:  # If the player loses
            dis.fill(black)  # Fill the screen with black color
            message("Press Space-Play Again or Esc-Quit", red)  # Display the game over message
            Your_score(Length_of_snake - 1)  # Show the score
            pygame.draw.rect(dis, white, [0, 0, dis_width, dis_height], 5)  # Draw a white border
            dis.blit(overlay, (0, 0))  # Draw the overlay image
            pygame.display.update()  # Update the display

            # Save the current score to a file
            with open("score.txt", "w") as file:
                file.write(str(Length_of_snake - 1))  # Write the score to score.txt

            # Handle keyboard events for restarting or quitting the game
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # If Escape is pressed, quit the game
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_SPACE:  # If Space is pressed, restart the game
                        gameLoop()  # Call the gameLoop function recursively to restart

        # Event handling for controlling the snake's movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the player closes the window, quit the game
                game_over = True
            if event.type == pygame.KEYDOWN:  # If a key is pressed, move the snake
                if event.key == pygame.K_a:  # Left arrow key moves snake left
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_d:  # Right arrow key moves snake right
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_w:  # Up arrow key moves snake up
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_s:  # Down arrow key moves snake down
                    y1_change = snake_block
                    x1_change = 0

        # Check if the snake hits the border, causing a game over
        if x1 >= (dis_width - 10) or x1 < 10 or y1 >= (dis_height - 10) or y1 < 10:
            game_close = True  # Set the game_close flag to True, indicating game over

        # Update the snake's position based on the movement
        x1 += x1_change
        y1 += y1_change

        # Fill the screen with black and draw the border
        dis.fill(black)
        pygame.draw.rect(dis, white, [0, 0, dis_width, dis_height], 5)
        pygame.draw.rect(dis, red, [foodx, foody, snake_block, snake_block])  # Draw the food block

        # Add the new head of the snake to the snake list
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)

        # Remove the tail of the snake if it exceeds the current length
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Check if the snake collides with itself
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True  # If the snake collides with itself, game over

        # Draw the snake on the screen
        our_snake(snake_block, snake_List)

        # Draw the overlay image
        dis.blit(overlay, (0, 0))

        pygame.display.update()  # Update the display

        # Check if the snake eats the food
        if x1 == foodx and y1 == foody:
            # Randomly generate a new position for the food
            foodx = round(random.randrange(10, (dis_width - 10) - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(10, (dis_height - 10) - snake_block) / 10.0) * 10.0
            Length_of_snake += 1  # Increase the length of the snake when food is eaten

        clock.tick(snake_speed)  # Control the frame rate of the game

    pygame.quit()  # Quit pygame when the game is over
    quit()  # Exit the program


# Start the game loop
gameLoop()

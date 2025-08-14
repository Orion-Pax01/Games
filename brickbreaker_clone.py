import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Brick Breaker")

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (200, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 200, 50)

# Game settings
FPS = 60
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 30
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 8
LIVES = 3

# Fonts
FONT = pygame.font.SysFont("Arial", 24)
LARGE_FONT = pygame.font.SysFont("Arial", 48)

# Clock
clock = pygame.time.Clock()

# Create paddle
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)

# Create ball
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed = [4, -4]

# Create bricks
def create_brick_row():
    return [pygame.Rect(col * BRICK_WIDTH, 0, BRICK_WIDTH, BRICK_HEIGHT) for col in range(BRICK_COLS)]

bricks = []
for row in range(BRICK_ROWS):
    bricks.extend([pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT)
                   for col in range(BRICK_COLS)])

# Score and lives
score = 0
lives = LIVES
game_over = False

def draw():
    SCREEN.fill(GRAY)
    
    # Draw paddle
    pygame.draw.rect(SCREEN, BLUE, paddle)
    
    # Draw ball
    pygame.draw.ellipse(SCREEN, WHITE, ball)
    
    # Draw bricks
    for brick in bricks:
        pygame.draw.rect(SCREEN, GREEN, brick)
        pygame.draw.rect(SCREEN, GRAY, brick, 2)

    # Draw score and lives
    score_text = FONT.render(f"Score: {score}", True, WHITE)
    lives_text = FONT.render(f"Lives: {lives}", True, WHITE)
    SCREEN.blit(score_text, (10, 10))
    SCREEN.blit(lives_text, (WIDTH - 110, 10))

    if game_over:
        over_text = LARGE_FONT.render("GAME OVER", True, RED)
        SCREEN.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))
        hint_text = FONT.render("Press R to Restart", True, WHITE)
        SCREEN.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()

def reset_ball():
    ball.x, ball.y = WIDTH // 2, HEIGHT // 2
    ball_speed[0] = 4 * random.choice([-1, 1])
    ball_speed[1] = -4

running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    if not game_over:
        # Paddle movement
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= 6
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.x += 6

        # Move ball
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # Ball collision with walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speed[0] *= -1
        if ball.top <= 0:
            ball_speed[1] *= -1

        # Ball collision with paddle
        if ball.colliderect(paddle) and ball_speed[1] > 0:
            ball_speed[1] *= -1

        # Ball collision with bricks
        hit_index = ball.collidelist(bricks)
        if hit_index != -1:
            bricks.pop(hit_index)
            score += 10
            ball_speed[1] *= -1

        # Endless row management
        grid = [[0 for _ in range(BRICK_COLS)] for _ in range(BRICK_ROWS)]
        for brick in bricks:
            row = brick.y // BRICK_HEIGHT
            col = brick.x // BRICK_WIDTH
            if 0 <= row < BRICK_ROWS and 0 <= col < BRICK_COLS:
                grid[row][col] = 1

        for row in range(BRICK_ROWS):
            if sum(grid[row]) == BRICK_COLS:
                bricks = [b for b in bricks if b.y != row * BRICK_HEIGHT]
                for b in bricks:
                    if b.y < row * BRICK_HEIGHT:
                        b.y += BRICK_HEIGHT
                new_row = create_brick_row()
                for b in new_row:
                    b.y = 0
                bricks = new_row + bricks
                score += 50
                break

        # Ball falls below screen
        if ball.top > HEIGHT:
            lives -= 1
            if lives == 0:
                game_over = True
            else:
                reset_ball()

    else:
        if keys[pygame.K_r]:
            # Reset game
            score = 0
            lives = LIVES
            game_over = False
            paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
            bricks = []
            for row in range(BRICK_ROWS):
                bricks.extend([pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT)
                               for col in range(BRICK_COLS)])
            reset_ball()

    draw()

pygame.quit()

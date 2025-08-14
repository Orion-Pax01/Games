import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Square")

# Colors
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)

# Bird properties
bird_size = 30
bird_x = 80
bird_y = HEIGHT // 2
bird_velocity = 0
gravity = 0.5
jump_strength = -9

# Pipe properties
pipe_width = 60
pipe_gap = 160
pipe_velocity = 3
pipe_frequency = 1500  # ms
last_pipe = pygame.time.get_ticks()
pipes = []

# Score
score = 0
font = pygame.font.SysFont("Arial", 30)

clock = pygame.time.Clock()

def draw_bird(y):
    pygame.draw.rect(screen, YELLOW, (bird_x, y, bird_size, bird_size))

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, pipe['top'])
        pygame.draw.rect(screen, GREEN, pipe['bottom'])

def check_collision(bird_rect, pipes):
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        return True
    for pipe in pipes:
        if bird_rect.colliderect(pipe['top']) or bird_rect.colliderect(pipe['bottom']):
            return True
    return False

def display_score(score):
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

# Game loop
running = True
while running:
    screen.fill(LIGHT_BLUE)
    dt = clock.tick(60)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bird_velocity = jump_strength

    # Bird physics
    bird_velocity += gravity
    bird_y += bird_velocity
    bird_rect = pygame.Rect(bird_x, bird_y, bird_size, bird_size)

    # Pipe generation
    current_time = pygame.time.get_ticks()
    if current_time - last_pipe > pipe_frequency:
        pipe_height = random.randint(100, HEIGHT - pipe_gap - 100)
        top_pipe = pygame.Rect(WIDTH, 0, pipe_width, pipe_height)
        bottom_pipe = pygame.Rect(WIDTH, pipe_height + pipe_gap, pipe_width, HEIGHT)
        pipes.append({'top': top_pipe, 'bottom': bottom_pipe, 'passed': False})
        last_pipe = current_time

    # Move and draw pipes
    for pipe in pipes:
        pipe['top'].x -= pipe_velocity
        pipe['bottom'].x -= pipe_velocity

        if pipe['top'].x + pipe_width < bird_x and not pipe['passed']:
            score += 1
            pipe['passed'] = True

    # Remove off-screen pipes
    pipes = [pipe for pipe in pipes if pipe['top'].x + pipe_width > 0]

    # Draw
    draw_bird(bird_y)
    draw_pipes(pipes)
    display_score(score)

    # Collision
    if check_collision(bird_rect, pipes):
        print(f"Over! Final Score: {score}")
        pygame.time.wait(1500)
        running = False

    pygame.display.flip()

pygame.quit()
sys.exit()

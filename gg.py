import pygame
import random
import time
import math

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga Clone")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUG_COLOR = (0, 255, 0)
BOSS_COLOR = (255, 0, 0)
PLAYER_COLOR = (230, 230, 230)
BULLET_COLOR = (255, 255, 0)

# Font
font = pygame.font.SysFont("arial", 24)

# Player
player_width, player_height = 40, 20
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5
lives = 3

# Bullets
bullets = []
bullet_speed = 7

# Enemies
enemy_rows = 5
enemy_cols = 8
enemy_spacing_x = 80
enemy_spacing_y = 50
enemy_start_x = 100
enemy_start_y = 50
enemy_formation = []
zigzag_range = 30
zigzag_speed = 0.5
dive_speed = 5
dive_cooldown = 200
dive_timer = 0

# Score and time
score = 0
start_time = time.time()
game_duration = 60  # seconds

# Stars
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]


def draw_player(x, y):
    pygame.draw.rect(screen, PLAYER_COLOR, (x, y, player_width, player_height))


def draw_bullet(x, y):
    pygame.draw.rect(screen, BULLET_COLOR, (x, y, 4, 10))


def draw_triangle(x, y, size, color):
    points = [(x, y), (x - size, y + size), (x + size, y + size)]
    pygame.draw.polygon(screen, color, points)


def draw_score(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))


def draw_lives(lives):
    text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(text, (WIDTH - 120, 10))


def draw_timer(time_left):
    text = font.render(f"Time: {int(time_left)}s", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 50, 10))


def create_enemy_formation():
    formation = []
    for row in range(enemy_rows):
        for col in range(enemy_cols):
            x = enemy_start_x + col * enemy_spacing_x
            y = enemy_start_y + row * enemy_spacing_y
            is_boss = (row == enemy_rows - 1)
            color = BOSS_COLOR if is_boss else BUG_COLOR
            size = 15 if is_boss else 10
            health = 3 if is_boss else 1
            formation.append({
                'x0': x, 'y0': y,       # original position
                'x': x, 'y': y,         # current position
                'size': size,
                'color': color,
                'boss': is_boss,
                'health': health,
                'zigzag_offset': random.uniform(0, 3.14),
                'diving': False,
                'returning': False
            })
    return formation


def move_enemies():
    for enemy in enemy_formation:
        if enemy['diving']:
            enemy['y'] += dive_speed
            if enemy['y'] > HEIGHT:
                enemy['returning'] = True
                enemy['diving'] = False
        elif enemy['returning']:
            # Move back to formation
            dx = enemy['x0'] - enemy['x']
            dy = enemy['y0'] - enemy['y']
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < 5:
                enemy['x'], enemy['y'] = enemy['x0'], enemy['y0']
                enemy['returning'] = False
            else:
                enemy['x'] += dx / 15
                enemy['y'] += dy / 15
        else:
            # Zigzag in place
            enemy['x'] = enemy['x0'] + math.sin(pygame.time.get_ticks() * 0.002 + enemy['zigzag_offset']) * zigzag_range


def trigger_dive():
    global dive_timer
    if dive_timer > 0:
        dive_timer -= 1
        return
    candidates = [e for e in enemy_formation if not e['diving'] and not e['returning'] and not e['boss']]
    if candidates:
        diver = random.choice(candidates)
        diver['diving'] = True
    dive_timer = dive_cooldown


def draw_enemies():
    for enemy in enemy_formation:
        draw_triangle(int(enemy['x']), int(enemy['y']), enemy['size'], enemy['color'])


def check_collisions():
    global score, bullets, enemy_formation
    for bullet in bullets[:]:
        for enemy in enemy_formation[:]:
            dx = abs(bullet['x'] - enemy['x'])
            dy = abs(bullet['y'] - enemy['y'])
            if dx < enemy['size'] and dy < enemy['size']:
                bullets.remove(bullet)
                enemy['health'] -= 1
                if enemy['health'] <= 0:
                    enemy_formation.remove(enemy)
                    score += 50 if enemy['boss'] else 10
                break


def check_player_hit():
    global lives, enemy_formation
    for enemy in enemy_formation:
        if enemy['diving']:
            if abs(enemy['x'] - player_x - player_width // 2) < 20 and abs(enemy['y'] - player_y) < 20:
                enemy['diving'] = False
                enemy['returning'] = True
                lives -= 1


# Init formation
enemy_formation = create_enemy_formation()

# Main loop
running = True
while running:
    dt = clock.tick(60)
    screen.fill(BLACK)

    # Stars
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)

    # Timer
    time_left = max(0, game_duration - (time.time() - start_time))
    if time_left <= 0 or lives <= 0 or score == 720:
        screen.fill(BLACK)
        game_over_text = font.render(f"Game Over! Final Score: {score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(4000)
        break

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    player_x = max(0, min(WIDTH - player_width, player_x))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            bullets.append({'x': player_x + player_width // 2, 'y': player_y})

    # Update bullets
    for bullet in bullets[:]:
        bullet['y'] -= bullet_speed
        if bullet['y'] < 0:
            bullets.remove(bullet)

    # Enemies
    trigger_dive()
    move_enemies()

    # Collisions
    check_collisions()
    check_player_hit()

    # Draw all
    draw_player(player_x, player_y)
    for bullet in bullets:
        draw_bullet(bullet['x'], bullet['y'])
    draw_enemies()
    draw_score(score)
    draw_lives(lives)
    draw_timer(time_left)

    pygame.display.flip()

pygame.quit()

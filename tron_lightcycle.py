
"""
Tron Lightcycle - pygame
Controls:
 Player 1 (Blue): W = up, S = down, A = left, D = right
 Player 2 (Orange): Arrow keys
 Restart: R, Quit: ESC or close window

Dependencies:
 pip install pygame

Run:
 python tron_lightcycle.py
"""

import pygame
import sys
import random

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20           # size of each cell (px)
FPS = 12                 # game frames per second (speed of cycles)
BORDER_WRAP = False      # if True, cycles wrap around screen edges; else collide with walls

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
ORANGE = (255, 150, 50)
GREY = (40, 40, 40)
RED = (220, 50, 50)
GREEN = (50, 220, 80)

pygame.init()
FONT = pygame.font.SysFont("consolas", 20)
BIG_FONT = pygame.font.SysFont("consolas", 40)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tron Lightcycle")
clock = pygame.time.Clock()

# Directions as (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def grid_pos(pixel_pos):
    """Convert pixel position to grid cell coordinates"""
    x, y = pixel_pos
    return (x // GRID_SIZE, y // GRID_SIZE)

def pixel_rect(grid_cell):
    x, y = grid_cell
    return pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

class Player:
    def __init__(self, name, color, start_cell, direction):
        self.name = name
        self.color = color
        self.head = start_cell  # grid cell tuple (x, y)
        self.direction = direction  # (dx, dy)
        self.trail = [start_cell]   # list of grid cells occupied by trail (including head)
        self.alive = True
        self.score = 0

    def change_direction(self, new_dir):
        # prevent reversing onto yourself
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.direction = new_dir

    def move(self):
        if not self.alive:
            return
        nx = self.head[0] + self.direction[0]
        ny = self.head[1] + self.direction[1]
        self.head = (nx, ny)
        self.trail.append(self.head)

    def reset(self, start_cell, direction):
        self.head = start_cell
        self.direction = direction
        self.trail = [start_cell]
        self.alive = True

class Game:
    def __init__(self, width, height, grid_size):
        self.width_cells = width // grid_size
        self.height_cells = height // grid_size
        self.grid_size = grid_size
        self.players = []
        self.all_trail_set = set()  # set of occupied cells by trails (for quick collision check)
        self.running = True
        self.winner = None
        self.single_player = False

    def new_game(self, single_player=False):
        self.single_player = single_player
        # Initialize players in opposite halves
        p1_start = (self.width_cells // 4, self.height_cells // 2)
        p2_start = (3 * self.width_cells // 4, self.height_cells // 2)
        p1_dir = RIGHT
        p2_dir = LEFT
        self.players = [
            Player("Player 1", BLUE, p1_start, p1_dir),
            Player("Player 2", ORANGE, p2_start, p2_dir)
        ]
        self.all_trail_set = set([p1_start, p2_start])
        self.winner = None

    def update(self):
        # move players
        for p in self.players:
            if p.alive:
                p.move()

        # check collisions
        for p in self.players:
            if not p.alive:
                continue
            x, y = p.head
            # wall collision
            if not BORDER_WRAP:
                if x < 0 or x >= self.width_cells or y < 0 or y >= self.height_cells:
                    p.alive = False
                    continue
            else:
                # wrap around
                x %= self.width_cells
                y %= self.height_cells
                p.head = (x, y)
                p.trail[-1] = p.head

            # trail collision (including own trail except the last move? In Tron you die if you hit any occupied cell)
            # If head is already in all_trail_set, collision
            # We need to check collision against trails before adding the new head to the set
            # Build a temp set from other players' trails (but including your past trail as well)
            # We'll check for head collision with existing trails (excluding the head cell that was just vacated is not necessary because trail is continuous)
            head_cell = p.head
            # If head_cell is in set of ANY trails (excluding the case where last two cells coincide when reversing which we prevented), collision.
            if head_cell in self.all_trail_set:
                p.alive = False
                continue

        # After all collision checks, add new head positions into all_trail_set
        for p in self.players:
            # Only add if alive (dead players still leave trail)
            # Actually in Tron, a dead player leaves the trail as it was; so we add their new head if it exists
            if p.trail:
                self.all_trail_set.add(p.trail[-1])

        # check for round end: if <=1 alive, determine winner
        alive = [p for p in self.players if p.alive]
        if len(alive) <= 1:
            if len(alive) == 1:
                self.winner = alive[0].name
                alive[0].score += 1
            else:
                self.winner = "Draw"
            # mark running false until reset requested
            self.running = False

    def draw_grid(self, surface):
        for x in range(0, self.width_cells * self.grid_size, self.grid_size):
            pygame.draw.line(surface, GREY, (x, 0), (x, self.height_cells * self.grid_size))
        for y in range(0, self.height_cells * self.grid_size, self.grid_size):
            pygame.draw.line(surface, GREY, (0, y), (self.width_cells * self.grid_size, y))

    def draw(self, surface):
        # surface.fill(BLACK)  # caller handles fill
        # draw trails
        for p in self.players:
            for cell in p.trail:
                rect = pixel_rect(cell)
                pygame.draw.rect(surface, p.color, rect)

        # draw heads with a border
        for p in self.players:
            if p.alive:
                head_rect = pixel_rect(p.head)
                inner = head_rect.inflate(-4, -4)
                pygame.draw.rect(surface, WHITE, head_rect, 2)
                pygame.draw.rect(surface, p.color, inner)

    def reset_for_next_round(self):
        self.running = True
        self.all_trail_set.clear()
        self.new_game(single_player=self.single_player)

def draw_text(surface, text, pos, font=FONT, color=WHITE):
    surf = font.render(text, True, color)
    surface.blit(surf, pos)

def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)
    game.new_game(single_player=False)

    paused = False
    auto_restart_delay = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    # restart a fresh game (scores kept)
                    game.reset_for_next_round()
                # Player 1 controls (WASD)
                if event.key == pygame.K_w:
                    game.players[0].change_direction(UP)
                if event.key == pygame.K_s:
                    game.players[0].change_direction(DOWN)
                if event.key == pygame.K_a:
                    game.players[0].change_direction(LEFT)
                if event.key == pygame.K_d:
                    game.players[0].change_direction(RIGHT)
                # Player 2 controls (arrows)
                if event.key == pygame.K_UP:
                    game.players[1].change_direction(UP)
                if event.key == pygame.K_DOWN:
                    game.players[1].change_direction(DOWN)
                if event.key == pygame.K_LEFT:
                    game.players[1].change_direction(LEFT)
                if event.key == pygame.K_RIGHT:
                    game.players[1].change_direction(RIGHT)
                # toggle wrap
                if event.key == pygame.K_SPACE and not game.running:
                    # start next round
                    game.reset_for_next_round()

        # Only update game logic when running (not between rounds)
        if game.running:
            # Simple AI for player2 if single_player enabled
            if game.single_player:
                selfp = game.players[1]
                # naive AI: try to keep moving, randomly change if next cell collides
                nx = selfp.head[0] + selfp.direction[0]
                ny = selfp.head[1] + selfp.direction[1]
                next_cell = (nx, ny)
                if next_cell in game.all_trail_set or nx < 0 or nx >= game.width_cells or ny < 0 or ny >= game.height_cells:
                    # try random turn left or right
                    choices = [UP, DOWN, LEFT, RIGHT]
                    random.shuffle(choices)
                    for c in choices:
                        if c[0] == -selfp.direction[0] and c[1] == -selfp.direction[1]:
                            continue
                        tcell = (selfp.head[0] + c[0], selfp.head[1] + c[1])
                        if tcell not in game.all_trail_set and 0 <= tcell[0] < game.width_cells and 0 <= tcell[1] < game.height_cells:
                            selfp.change_direction(c)
                            break
            game.update()

        # draw
        screen.fill(BLACK)
        # game.draw_grid(screen)  # optional grid
        game.draw(screen)

        # HUD
        draw_text(screen, f"P1 (Blue): {game.players[0].score}", (10, 10))
        draw_text(screen, f"P2 (Orange): {game.players[1].score}", (SCREEN_WIDTH - 180, 10))
        if not game.running:
            # overlay round result
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            screen.blit(overlay, (0,0))
            res = "Round Over - "
            if game.winner == "Draw":
                res += "Draw"
            else:
                res += f"{game.winner} wins!"
            txt = BIG_FONT.render(res, True, WHITE)
            screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
            info = FONT.render("Press R to restart round, or ESC to quit.", True, WHITE)
            screen.blit(info, info.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10)))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

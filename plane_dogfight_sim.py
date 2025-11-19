import pygame, random, math
pygame.init()

# --- SETTINGS ---
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dogfight Simulator")
CLOCK = pygame.time.Clock()

# --- PLAYER PLANE ---
class Plane:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        self.max_speed = 6
        self.turn_speed = 4
        self.size = 20

    def update(self, keys):
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + 0.2, self.max_speed)
        if keys[pygame.K_DOWN]:
            self.speed = max(self.speed - 0.2, -2)

        if keys[pygame.K_LEFT]:
            self.angle -= self.turn_speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.turn_speed

        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed

        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        rad = math.radians(self.angle)
        tip = (self.x + math.cos(rad) * self.size,
               self.y + math.sin(rad) * self.size)
        left = (self.x + math.cos(rad + 2.3) * self.size,
                self.y + math.sin(rad + 2.3) * self.size)
        right = (self.x + math.cos(rad - 2.3) * self.size,
                 self.y + math.sin(rad - 2.3) * self.size)
        pygame.draw.polygon(WIN, (255,255,255), [tip, left, right])

# --- ENEMY FIGHTERS ---
class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.angle = random.randint(0, 360)
        self.speed = random.uniform(2, 4)
        self.size = 20

    def update(self, player):
        # chase player
        dx = player.x - self.x
        dy = player.y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        rad = math.radians(self.angle)
        tip = (self.x + math.cos(rad) * self.size,
               self.y + math.sin(rad) * self.size)
        left = (self.x + math.cos(rad + 2.3) * self.size,
                self.y + math.sin(rad + 2.3) * self.size)
        right = (self.x + math.cos(rad - 2.3) * self.size,
                 self.y + math.sin(rad - 2.3) * self.size)
        pygame.draw.polygon(WIN, (255,0,0), [tip, left, right])

# --- BULLETS ---
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.life = 60

    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        self.life -= 1

    def draw(self):
        pygame.draw.circle(WIN, (255,255,0), (int(self.x), int(self.y)), 4)

# --- GAME LOOP ---
def main():
    player = Plane()
    enemies = [Enemy() for _ in range(5)]
    bullets = []

    running = True
    while running:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullets.append(Bullet(player.x, player.y, player.angle))

        keys = pygame.key.get_pressed()
        player.update(keys)

        for e in enemies:
            e.update(player)

        for b in bullets[:]:
            b.update()
            if b.life <= 0:
                bullets.remove(b)

        # collision
        for b in bullets[:]:
            for e in enemies[:]:
                if (e.x - b.x)**2 + (e.y - b.y)**2 < 25**2:
                    enemies.remove(e)
                    bullets.remove(b)
                    enemies.append(Enemy())  # respawn new enemy

        WIN.fill((0,0,0))  # black sky
        player.draw()
        for e in enemies:
            e.draw()
        for b in bullets:
            b.draw()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()

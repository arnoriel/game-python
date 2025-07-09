import pygame
import random
import sys

pygame.init()

# Konstanta
WIDTH, HEIGHT = 800, 600
GROUND_Y = 500
FPS = 60
GRAVITY = 0.6
JUMP_FORCE = -12
MAX_JUMPS = 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Petualangan Kode Mario 🚀")
clock = pygame.time.Clock()

# Warna
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SKIN = (210, 180, 140)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
ENEMY_COLOR = (100, 0, 0)

# Kelas Player
class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, GROUND_Y - 70, 50, 70)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.running_frame = 0
        self.frame_count = 0
        self.score = 0
        self.jump_count = 0
        self.is_jumping = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -5
        if keys[pygame.K_RIGHT]:
            self.vel_x = 5
        if keys[pygame.K_SPACE]:
            if self.jump_count < MAX_JUMPS and not self.is_jumping:
                self.vel_y = JUMP_FORCE
                self.jump_count += 1
                self.is_jumping = True
        else:
            self.is_jumping = False

    def update(self, obstacles):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += GRAVITY

        self.on_ground = False
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if self.vel_y > 0:
                    self.rect.bottom = obs.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
            self.jump_count = 0

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.vel_x != 0:
            self.frame_count += 1
            if self.frame_count % 5 == 0:
                self.running_frame = (self.running_frame + 1) % 2
        else:
            self.running_frame = 0

    def draw(self, surface):
        x, y = self.rect.topleft
        pygame.draw.rect(surface, SKIN, (x + 10, y, 30, 20))  # kepala
        pygame.draw.rect(surface, GREEN, (x + 10, y, 30, 10))  # topi
        pygame.draw.circle(surface, BLACK, (x + 20, y + 10), 2)  # mata
        pygame.draw.circle(surface, BLACK, (x + 30, y + 10), 2)

        # Animasi lompat vs lari
        if not self.on_ground:
            pygame.draw.rect(surface, RED, (x, y + 20, 50, 30))  # baju lompat
            pygame.draw.rect(surface, BLUE, (x, y + 50, 50, 20))  # celana lompat
        elif self.running_frame == 0:
            pygame.draw.rect(surface, RED, (x, y + 20, 50, 30))
            pygame.draw.rect(surface, BLUE, (x, y + 50, 50, 20))
        else:
            pygame.draw.rect(surface, (255, 100, 100), (x, y + 20, 50, 30))
            pygame.draw.rect(surface, (100, 100, 255), (x, y + 50, 50, 20))

        # Tangan
        pygame.draw.rect(surface, SKIN, (x - 10, y + 20, 10, 20))
        pygame.draw.rect(surface, SKIN, (x + 50, y + 20, 10, 20))

        # Kaki
        pygame.draw.rect(surface, BROWN, (x, y + 70, 20, 10))
        pygame.draw.rect(surface, BROWN, (x + 30, y + 70, 20, 10))

# Koin
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def draw(self, surface):
        pygame.draw.circle(surface, GOLD, self.rect.center, 10)

# Musuh
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.direction = -1

    def update(self):
        self.rect.x += self.direction * 2
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, ENEMY_COLOR, self.rect)
        pygame.draw.rect(surface, BLACK, (self.rect.x + 10, self.rect.y + 10, 20, 5))
        pygame.draw.rect(surface, BLACK, (self.rect.x + 15, self.rect.y + 25, 10, 10))

# Inisialisasi
player = Player()
platforms = [pygame.Rect(300, 420, 100, 20), pygame.Rect(600, 370, 100, 20)]
coins = []
enemies = []

# Game Loop
running = True
while running:
    screen.fill(WHITE)
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gambar tanah
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

    # Update dan gambar platform
    for p in platforms:
        p.x -= 3
        pygame.draw.rect(screen, (120, 120, 120), p)
    platforms = [p for p in platforms if p.right > 0]
    if platforms[-1].x < WIDTH - 300:
        platforms.append(pygame.Rect(WIDTH, random.randint(300, 450), 100, 20))

    # Infinite coins
    for coin in coins[:]:
        coin.rect.x -= 3
        if player.rect.colliderect(coin.rect):
            coins.remove(coin)
            player.score += 1
        else:
            coin.draw(screen)
    if len(coins) < 10 and random.random() < 0.05:
        coins.append(Coin(WIDTH + random.randint(0, 200), random.randint(200, 450)))

    # Infinite enemies
    for enemy in enemies[:]:
        enemy.rect.x -= 3
        enemy.update()
        if player.rect.colliderect(enemy.rect):
            if player.vel_y > 0:
                enemies.remove(enemy)
                player.vel_y = JUMP_FORCE / 1.5
            else:
                print("GAME OVER")
                running = False
        enemy.draw(screen)
    if random.random() < 0.01:
        enemies.append(Enemy(WIDTH + random.randint(50, 300), GROUND_Y - 40))

    # Update player
    player.handle_input()
    player.update(platforms)
    player.draw(screen)

    # Tampilkan skor
    font = pygame.font.SysFont(None, 30)
    score_text = font.render(f"Coins: {player.score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()

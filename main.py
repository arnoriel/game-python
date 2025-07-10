import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
GROUND_Y = 500
FPS = 60
GRAVITY = 0.6
JUMP_FORCE = -12
MAX_JUMPS = 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Python")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SKIN = (210, 180, 140)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
ENEMY_COLOR = (100, 0, 0)
SKY = (135, 206, 235)
GRASS_GREEN = (50, 205, 50)
SUN_YELLOW = (255, 255, 0)
CLOUD_COLOR = (255, 255, 255)
TREE_BROWN = (101, 67, 33)
LEAF_GREEN = (34, 139, 34)

game_state = "menu"
paused = False
high_score = 0

clouds = [[random.randint(0, WIDTH), random.randint(50, 150)] for _ in range(5)]
trees = []

def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y) if center else (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_background(move=True):
    screen.fill(SKY)
    pygame.draw.circle(screen, SUN_YELLOW, (700, 80), 50)
    for cloud in clouds:
        pygame.draw.ellipse(screen, CLOUD_COLOR, (cloud[0], cloud[1], 80, 40))
        if move:
            cloud[0] -= 1
            if cloud[0] < -100:
                cloud[0] = WIDTH + random.randint(50, 150)
                cloud[1] = random.randint(50, 150)
    for tree in trees[:]:
        if move:
            tree["x"] -= 1
        if tree["x"] + 50 < 0:
            trees.remove(tree)
        else:
            pygame.draw.rect(screen, TREE_BROWN, (tree["x"] + 20, GROUND_Y - 60, 10, 60))
            pygame.draw.circle(screen, LEAF_GREEN, (tree["x"] + 25, GROUND_Y - 70), 25)
    if move and random.random() < 0.005:
        trees.append({"x": WIDTH + random.randint(0, 300)})

def draw_menu():
    draw_background(move=False)
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y - 5, WIDTH, 5))
    player.draw(screen)
    play_btn = draw_text(screen, "Mainkan", 40, GREEN, WIDTH//2, 250)
    exit_btn = draw_text(screen, "Keluar", 40, RED, WIDTH//2, 320)
    draw_text(screen, "Game Python", 60, BLACK, WIDTH//2, 100)
    draw_text(screen, "Kontrol: arah kanan dan kiri untuk gerak, Spasi untuk lompat", 30, BLACK, WIDTH//2, 400)
    draw_text(screen, "Tekan 'P' untuk pause, 'R' untuk resume", 25, BLACK, WIDTH//2, 440)
    return play_btn, exit_btn

def draw_game_over():
    global high_score
    draw_background()
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y - 5, WIDTH, 5))
    draw_text(screen, "GAME OVER", 70, RED, WIDTH//2, 130)
    draw_text(screen, f"Total Coin: {player.score}", 40, BLACK, WIDTH//2, 200)
    if player.score > high_score:
        high_score = player.score
    draw_text(screen, f"Highscore: {high_score}", 35, BLACK, WIDTH//2, 240)
    retry_btn = draw_text(screen, "Coba Lagi", 40, GREEN, WIDTH//2, 310)
    menu_btn = draw_text(screen, "Kembali ke Menu", 40, BLUE, WIDTH//2, 360)
    return retry_btn, menu_btn

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
        if keys[pygame.K_LEFT]: self.vel_x = -5
        if keys[pygame.K_RIGHT]: self.vel_x = 5
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
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, WIDTH)
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            self.running_frame = (self.running_frame + 1) % 2

    def draw(self, surface):
        x, y = self.rect.topleft
        pygame.draw.rect(surface, SKIN, (x + 10, y, 30, 20))
        pygame.draw.rect(surface, GREEN, (x + 10, y, 30, 10))
        pygame.draw.circle(surface, BLACK, (x + 20, y + 10), 2)
        pygame.draw.circle(surface, BLACK, (x + 30, y + 10), 2)
        pygame.draw.rect(surface, RED, (x, y + 20, 50, 30))
        pygame.draw.rect(surface, BLUE, (x, y + 50, 50, 20))
        if self.running_frame == 0:
            pygame.draw.rect(surface, SKIN, (x - 10, y + 20, 10, 20))
            pygame.draw.rect(surface, SKIN, (x + 50, y + 25, 10, 15))
            pygame.draw.rect(surface, BROWN, (x, y + 70, 20, 10))
            pygame.draw.rect(surface, BROWN, (x + 30, y + 65, 20, 10))
        else:
            pygame.draw.rect(surface, SKIN, (x - 10, y + 25, 10, 15))
            pygame.draw.rect(surface, SKIN, (x + 50, y + 20, 10, 20))
            pygame.draw.rect(surface, BROWN, (x, y + 65, 20, 10))
            pygame.draw.rect(surface, BROWN, (x + 30, y + 70, 20, 10))

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def draw(self, surface):
        pygame.draw.circle(surface, GOLD, self.rect.center, 10)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.direction = -1
        self.is_dead = False
        self.death_timer = 0

    def update(self):
        if self.is_dead:
            self.death_timer += 1
            return
        self.rect.x += self.direction * 2
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1

    def draw(self, surface):
        if self.is_dead:
            if self.death_timer % 4 < 2:
                pygame.draw.rect(surface, WHITE, self.rect)
        else:
            pygame.draw.rect(surface, ENEMY_COLOR, self.rect)
            pygame.draw.rect(surface, BLACK, (self.rect.x + 10, self.rect.y + 10, 20, 5))
            pygame.draw.rect(surface, BLACK, (self.rect.x + 15, self.rect.y + 25, 10, 10))

player = Player()
platforms = [pygame.Rect(300, 420, 100, 20), pygame.Rect(600, 370, 100, 20)]
coins = []
enemies = []
coin_spawn_tracker = set()

running = True
while running:
    screen.fill(WHITE)
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button.collidepoint(mouse_pos):
                    player = Player()
                    platforms = [pygame.Rect(300, 420, 100, 20), pygame.Rect(600, 370, 100, 20)]
                    coins = []
                    enemies = []
                    coin_spawn_tracker = set()
                    trees = []
                    game_state = "play"
                elif exit_button.collidepoint(mouse_pos):
                    running = False
        elif game_state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if retry_button.collidepoint(mouse_pos):
                    player = Player()
                    platforms = [pygame.Rect(300, 420, 100, 20), pygame.Rect(600, 370, 100, 20)]
                    coins = []
                    enemies = []
                    coin_spawn_tracker = set()
                    trees = []
                    game_state = "play"
                elif menu_button.collidepoint(mouse_pos):
                    game_state = "menu"

    if game_state == "menu":
        play_button, exit_button = draw_menu()
    elif game_state == "play":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            paused = True
        if keys[pygame.K_r]:
            paused = False

        if paused:
            draw_text(screen, "PAUSED", 70, RED, WIDTH // 2, HEIGHT // 2)
            pygame.display.flip()
            continue

        draw_background()
        pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y - 5, WIDTH, 5))

        for p in platforms:
            p.x -= 3
            pygame.draw.rect(screen, (120, 120, 120), p)
        platforms = [p for p in platforms if p.right > 0]

        if platforms[-1].x < WIDTH - 300:
            new_platform = pygame.Rect(WIDTH, random.randint(300, 450), 100, 20)
            platforms.append(new_platform)
            if random.random() < 0.1:
                stack_height = random.randint(2, 3)
                for i in range(stack_height):
                    coins.append(Coin(new_platform.x + new_platform.width // 2 - 10,
                                      new_platform.y - 25 - (i * 30)))
            else:
                coins.append(Coin(new_platform.x + new_platform.width // 2 - 10,
                                  new_platform.y - 25))

        for coin in coins[:]:
            coin.rect.x -= 3
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                player.score += 1
            else:
                coin.draw(screen)

        for enemy in enemies[:]:
            enemy.rect.x -= 3
            enemy.update()
            if enemy.is_dead and enemy.death_timer > 15:
                enemies.remove(enemy)
                continue
            if player.rect.colliderect(enemy.rect):
                if player.vel_y > 0 and not enemy.is_dead:
                    enemy.is_dead = True
                    player.vel_y = JUMP_FORCE / 1.5
                elif not enemy.is_dead:
                    game_state = "game_over"
            enemy.draw(screen)

        if random.random() < 0.01:
            enemies.append(Enemy(WIDTH + random.randint(50, 300), GROUND_Y - 40))

        player.handle_input()
        player.update(platforms)
        player.draw(screen)

        score_text = pygame.font.SysFont(None, 30).render(f"Coins: {player.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

    elif game_state == "game_over":
        retry_button, menu_button = draw_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()
import pygame
import random
import math
import sys

pygame.init()

# =========================================
# НАСТРОЙКИ
# =========================================
WIDTH, HEIGHT = 960, 640
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON MAZE")

clock = pygame.time.Clock()

# =========================================
# ЦВЕТА
# =========================================
BLACK = ( 5, 5, 15)
NEON_BLUE = (0, 180, 255)
NEON_GREEN = (0, 255, 120)
NEON_RED = (255, 70, 70)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)

# =========================================
# ШРИФТЫ
# =========================================
title_font = pygame.font.SysFont("Arial", 70)
menu_font = pygame.font.SysFont("Arial", 40)
game_font = pygame.font.SysFont("Arial", 30)

# =========================================
# НАСТРОЙКИ ЛАБИРИНТА
# =========================================
CELL_SIZE = 39
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

maze = []

# =========================================
# ИГРОК
# =========================================
player_x = CELL_SIZE + 20
player_y = CELL_SIZE + 20

player_radius = 8
player_speed = 5

# =========================================
# СОБАКА AI
# =========================================
dog_x = WIDTH - 120
dog_y = HEIGHT - 120

dog_radius = 12
dog_speed = 2

# =========================================
# УРОВНИ
# =========================================
current_level = 1
max_levels = 5

# =========================================
# TRAIL SYSTEM
# =========================================
trail = []

# =========================================
# GAME STATES
# =========================================
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3

game_state = MENU

# =========================================
# ГЕНЕРАЦИЯ ЛАБИРИНТА
# =========================================
def generate_maze():

    global maze

    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]

    stack = []

    start_x = 1
    start_y = 1

    maze[start_y][start_x] = 0
    stack.append((start_x, start_y))

    directions = [
        (0, -2),
        (0, 2),
        (-2, 0),
        (2, 0)
    ]

    while stack:

        x, y = stack[-1]

        neighbors = []

        for dx, dy in directions:

            nx = x + dx
            ny = y + dy

            if 1 <= nx < COLS - 1 and 1 <= ny < ROWS - 1:

                if maze[ny][nx] == 1:
                    neighbors.append((nx, ny, dx, dy))

        if neighbors:

            nx, ny, dx, dy = random.choice(neighbors)

            maze[y + dy // 2][x + dx // 2] = 0
            maze[ny][nx] = 0

            stack.append((nx, ny))

        else:
            stack.pop()

generate_maze()


# =========================================
# ПОИСК ТОЧКИ ВЫХОДА
# =========================================
def find_exit():

    for y in range(ROWS - 2, 0, -1):

        for x in range(COLS - 2, 0, -1):

            if maze[y][x] == 0:

                return (
                    x * CELL_SIZE + CELL_SIZE // 2,
                    y * CELL_SIZE + CELL_SIZE // 2
                )

    return WIDTH - 60, HEIGHT - 60


exit_x, exit_y = find_exit()

# =========================================
# SPAWN СОБАКИ
# =========================================
def find_dog_spawn():

    possible_positions = []

    for y in range(ROWS):

        for x in range(COLS):

            if maze[y][x] == 0:

                px = x * CELL_SIZE + CELL_SIZE // 2
                py = y * CELL_SIZE + CELL_SIZE // 2

                distance = math.hypot(
                    px - player_x,
                    py - player_y
                )

                if distance > 250:
                    possible_positions.append((px, py))

    if possible_positions:
        return random.choice(possible_positions)

    return CELL_SIZE * 2, CELL_SIZE * 2

# =========================================
# ПРОВЕРКА СТЕН
# =========================================
def can_move(x, y):

    grid_x = int(x // CELL_SIZE)
    grid_y = int(y // CELL_SIZE)

    if grid_x < 0 or grid_y < 0:
        return False

    if grid_x >= COLS or grid_y >= ROWS:
        return False

    return maze[grid_y][grid_x] == 0

# =========================================
# GLOW
# =========================================
def draw_glow(surface, color, pos, radius):

    for i in range(8, 0, -1):

        glow_surface = pygame.Surface(
            (radius * 6, radius * 6),
            pygame.SRCALPHA
        )

        alpha = 3

        pygame.draw.circle(
            glow_surface,
            (*color, alpha),
            (radius * 3, radius * 3),
            radius + i * 10
        )

        surface.blit(
            glow_surface,
            (
                pos[0] - radius * 3,
                pos[1] - radius * 3
            )
        )

# =========================================
# TRAIL EFFECT
# =========================================
def update_trail():

    global trail

    trail.append([player_x, player_y, 100])

    for particle in trail:

        particle[2] -= 2

    trail = [p for p in trail if p[2] > 0]

def draw_trail():

    for particle in trail:

        x, y, life = particle

        glow_surface = pygame.Surface(
            (100, 100),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow_surface,
            (0, 255, 255, life),
            (50, 50),
            20
        )

        screen.blit(glow_surface, (x - 50, y - 50))

# =========================================
# ОТРИСОВКА ЛАБИРИНТА
# =========================================
def draw_maze():

    for y in range(ROWS):

        for x in range(COLS):

            if maze[y][x] == 1:

                rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                # glow
                draw_glow(
                    screen,
                    NEON_BLUE,
                    rect.center,
                    12
                )

                pygame.draw.rect(
                    screen,
                    NEON_BLUE,
                    rect,
                    2
                )
# =========================================
# AI СОБАКА
# =========================================
def update_dog():

    global dog_x, dog_y

    dx = player_x - dog_x
    dy = player_y - dog_y

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    speed = dog_speed

    # уровни усиливают собаку
    speed += current_level * 0.3

    # движение
    next_x = dog_x + dx * speed
    next_y = dog_y + dy * speed

    moved = False

    if can_move(next_x, dog_y):
        dog_x = next_x
        moved = True

    if can_move(dog_x, next_y):
        dog_y = next_y
        moved = True

    # если застряла
    if not moved:

        for _ in range(10):

            angle = random.uniform(0, math.pi * 2)

            random_x = dog_x + math.cos(angle) * 20
            random_y = dog_y + math.sin(angle) * 20

            if can_move(random_x, random_y):

                dog_x = random_x
                dog_y = random_y
                break

# =========================================
# FOG SYSTEM
# =========================================
def draw_fog():

    fog = pygame.Surface((WIDTH, HEIGHT))
    fog.fill(BLACK)

    fog.set_alpha(75)

    light_surface = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        light_surface,
        (0, 0, 0, 0),
        (int(player_x), int(player_y)),
        120
    )

    fog.blit(light_surface, (0, 0))

    screen.blit(fog, (0, 0))

# =========================================
# MENU
# =========================================
def draw_menu():

    screen.fill(BLACK)

    title = title_font.render(
        "NEON MAZE",
        True,
        NEON_BLUE
    )

    start = menu_font.render(
        "PRESS SPACE TO START",
        True,
        WHITE
    )

    controls = game_font.render(
        "W A S D - MOVE",
        True,
        GRAY
    )

    screen.blit(title, (350, 250))
    screen.blit(start, (360, 400))
    screen.blit(controls, (470, 470))

# =========================================
# GAME OVER SCREEN
# =========================================
def draw_game_over():

    screen.fill(BLACK)

    text = title_font.render(
        "GAME OVER",
        True,
        NEON_RED
    )

    retry = menu_font.render(
        "PRESS R TO RESTART",
        True,
        WHITE
    )

    screen.blit(text, (360, 300))
    screen.blit(retry, (360, 420))

# =========================================
# WIN SCREEN
# =========================================
def draw_win():

    screen.fill(BLACK)

    text = title_font.render(
        "YOU ESCAPED",
        True,
        NEON_GREEN
    )

    retry = menu_font.render(
        "PRESS R TO PLAY AGAIN",
        True,
        WHITE
    )

    screen.blit(text, (320, 300))
    screen.blit(retry, (330, 420))

# =========================================
# RESET GAME
# =========================================
def reset_game():

    global player_x
    global player_y
    global dog_x
    global dog_y
    global current_level
    global dog_speed

    player_x = CELL_SIZE + 20
    player_y = CELL_SIZE + 20

    

    current_level = 1
    dog_speed = 2

    generate_maze()
dog_x, dog_y = find_dog_spawn()
exit_x, exit_y = find_exit()

# =========================================
# MAIN LOOP
# =========================================
running = True

while running:

    clock.tick(FPS)

    # =====================================
    # EVENTS
    # =====================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # START GAME
        if game_state == MENU:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    game_state = PLAYING

        # RESTART
        if game_state in [GAME_OVER, WIN]:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    reset_game()
                    game_state = MENU

    # =====================================
    # MENU
    # =====================================
    if game_state == MENU:

        draw_menu()

    # =====================================
    # GAME
    # =====================================
    elif game_state == PLAYING:

        screen.fill(BLACK)

        # =============================
        # PLAYER MOVEMENT
        # =============================
        keys = pygame.key.get_pressed()

        move_x = 0
        move_y = 0

        if keys[pygame.K_w]:
            move_y = -player_speed

        if keys[pygame.K_s]:
            move_y = player_speed

        if keys[pygame.K_a]:
            move_x = -player_speed

        if keys[pygame.K_d]:
            move_x = player_speed

        next_x = player_x + move_x
        next_y = player_y + move_y

        if can_move(next_x, player_y):
            player_x = next_x

        if can_move(player_x, next_y):
            player_y = next_y

        # =============================
        # UPDATE
        # =============================
        update_trail()
        update_dog()

        # =============================
        # DRAW MAZE
        # =============================
        draw_maze()

        # =============================
        # EXIT
        # =============================
        draw_glow(
            screen,
            NEON_GREEN,
            (exit_x, exit_y),
            25
        )

        pygame.draw.circle(
            screen,
            NEON_GREEN,
            (exit_x, exit_y),
            10
        )

        # =============================
        # TRAIL
        # =============================
        draw_trail()

        # =============================
        # PLAYER
        # =============================
        draw_glow(
            screen,
            WHITE,
            (int(player_x), int(player_y)),
            20
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(player_x), int(player_y)),
            player_radius
        )

        # =============================
        # DOG
        # =============================
        draw_glow(
            screen,
            NEON_RED,
            (int(dog_x), int(dog_y)),
            20
        )

        pygame.draw.circle(
            screen,
            NEON_RED,
            (int(dog_x), int(dog_y)),
            dog_radius
        )

        # =============================
        # HUD
        # =============================
        level_text = game_font.render(
            f"LEVEL {current_level}",
            True,
            WHITE
        )

        screen.blit(level_text, (20, 20))

        # =============================
        # FOG
        # =============================
        draw_fog()

        # =============================
        # COLLISION DOG
        # =============================
        dog_distance = math.hypot(
            player_x - dog_x,
            player_y - dog_y
        )

        if dog_distance < 20:
            game_state = GAME_OVER

        # =============================
        # WIN LEVEL
        # =============================
        exit_distance = math.hypot(
            player_x - exit_x,
            player_y - exit_y
        )

        if exit_distance < 20:

            current_level += 1

            if current_level > max_levels:

                game_state = WIN

            else:

                dog_speed += 0.5

                generate_maze()

                

                player_x = CELL_SIZE + 20
                player_y = CELL_SIZE + 20

                

    # =====================================
    # GAME OVER
    # =====================================
    elif game_state == GAME_OVER:

        draw_game_over()

    # =====================================
    # WIN
    # =====================================
    elif game_state == WIN:

        draw_win()

    pygame.display.flip()

pygame.quit()
sys.exit()
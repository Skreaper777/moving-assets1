import pygame
import sys
import math
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = "1800,100"

# ----------------------------- НАСТРОЙКИ -----------------------------
# Путь к тайлсету комнаты
TILESET_PATH = r"C:\Users\stasr\PycharmProjects\Game\play-assets\mnt\data\Modern_Interiors\Modern tiles_Free\Interiors_free\48x48\Room_Builder_free_48x48.png"
# Путь к спрайт-листу Адама
ADAM_SPRITE_PATH = r"mnt/data/Modern_Interiors/Modern tiles_Free/Characters_free/Adam_run_16x16.png"

# Размеры плитки комнаты
TILE_W, TILE_H = 48, 48
# Размер комнаты в плитках
MAP_COLS, MAP_ROWS = 12, 8

# **Размеры фрейма Адама** (важно: высота 32px, а не 16!)
FRAME_W, FRAME_H = 16, 32
SCALE = 2
# *Масштабированные размеры*
SCALED_W, SCALED_H = FRAME_W * SCALE, FRAME_H * SCALE
ANIM_SPEED = 0.12

# Окно
WINDOW_WIDTH = MAP_COLS * TILE_W
WINDOW_HEIGHT = MAP_ROWS * TILE_H
# ---------------------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Комната и Адам")

# 1) Загружаем тайлсет комнаты и режем на плитки
tileset = pygame.image.load(TILESET_PATH).convert_alpha()
tiles = []
for y in range(tileset.get_height() // TILE_H):
    for x in range(tileset.get_width()  // TILE_W):
        rect = pygame.Rect(x * TILE_W, y * TILE_H, TILE_W, TILE_H)
        tiles.append(tileset.subsurface(rect))

# 2) Генерируем карту: 0 — пол, 1 — стена. Рамка + дверь внизу по центру
game_map = [[0] * MAP_COLS for _ in range(MAP_ROWS)]
for r in range(MAP_ROWS):
    for c in range(MAP_COLS):
        if r == 0 or r == MAP_ROWS - 1 or c == 0 or c == MAP_COLS - 1:
            game_map[r][c] = 1
door_c = MAP_COLS // 2
game_map[MAP_ROWS - 1][door_c] = 0  # дверь

# 3) Загружаем спрайт-лист Адама и режем на 4 направления × 6 кадров
adam_sheet = pygame.image.load(ADAM_SPRITE_PATH).convert_alpha()

def slice_adam(sheet):
    frames = [[] for _ in range(4)]
    for direction in range(4):
        for i in range(6):
            idx = direction * 6 + i
            rect = pygame.Rect(idx * FRAME_W, 0, FRAME_W, FRAME_H)
            img = sheet.subsurface(rect)
            img = pygame.transform.scale(img, (SCALED_W, SCALED_H))
            frames[direction].append(img)
    return frames

adam_frames = slice_adam(adam_sheet)

# 4) Стартовая позиция Адама — над дверью, ноги на уровне нижней плитки
adam_x = door_c * TILE_W + TILE_W // 2
adam_y = (MAP_ROWS - 1) * TILE_H
speed = 2

# Анимация
frame_index = 0
anim_timer = 0
current_dir = 3  # вниз

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # Движение Адама (включая диагонали)
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:   dx -= speed
    if keys[pygame.K_RIGHT]:  dx += speed
    if keys[pygame.K_UP]:     dy -= speed
    if keys[pygame.K_DOWN]:   dy += speed

    # Нормализуем скорость, чтобы при диагонали не бежать быстрее
    if dx and dy:
        norm = math.hypot(dx, dy)
        dx = dx / norm * speed
        dy = dy / norm * speed

    moving = dx != 0 or dy != 0

    # Определяем направление для анимации
    if dx > 0:       current_dir = 0
    elif dx < 0:     current_dir = 2
    elif dy < 0:     current_dir = 1
    elif dy > 0:     current_dir = 3

    # Проверяем столкновения со стенами
    new_rect = pygame.Rect(
        adam_x + dx - SCALED_W // 2,
        adam_y + dy - SCALED_H,
        SCALED_W, SCALED_H
    )
    collision = False
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            if game_map[r][c] == 1:
                wall = pygame.Rect(c * TILE_W, r * TILE_H, TILE_W, TILE_H)
                if new_rect.colliderect(wall):
                    collision = True
                    break
        if collision:
            break

    if not collision:
        adam_x += dx
        adam_y += dy

    # Обновление кадра анимации
    if moving:
        anim_timer += ANIM_SPEED
        if anim_timer >= 1:
            anim_timer = 0
            frame_index = (frame_index + 1) % 6
    else:
        frame_index = 0

    # ---- Отрисовка ----
    screen.fill((0, 0, 0))
    # 1) Плитки комнаты
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            tile_i = 4 if game_map[r][c] == 0 else 1  # поправь индексы по своему тайлсету
            screen.blit(tiles[tile_i], (c * TILE_W, r * TILE_H))
    # 2) Адам
    frame_img = adam_frames[current_dir][frame_index]
    draw_x = adam_x - SCALED_W // 2
    draw_y = adam_y - SCALED_H
    screen.blit(frame_img, (draw_x, draw_y))

    pygame.display.flip()

pygame.quit()
sys.exit()

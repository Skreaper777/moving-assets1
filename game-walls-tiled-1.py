import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1800,100"

import pygame
import sys
import math
import json

# 1) Загружаем конфиг
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

WINDOW_WIDTH   = cfg["window_size"]["width"]
WINDOW_HEIGHT  = cfg["window_size"]["height"]
BG_COLOR       = tuple(cfg["background_color"])

TILESET_PATH     = cfg["tileset_path"]
ADAM_SPRITE_PATH = cfg["adam_sprite_path"]

TILE_W, TILE_H = cfg["tile_size"]["w"], cfg["tile_size"]["h"]

# 2) Инициализация Pygame и окно
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Комната и Адам")

# 3) Загружаем карту из Tiled export (map.json)
with open("map.json", encoding="utf-8") as f:
    map_data = json.load(f)

MAP_COLS = map_data["width"]
MAP_ROWS = map_data["height"]

# Проверяем размер тайла в map.json
if map_data["tilewidth"] != TILE_W or map_data["tileheight"] != TILE_H:
    raise RuntimeError("Несовпадение размеров тайлов между map.json и config.json")

# Читаем слой-тайлмап
layer = next(l for l in map_data["layers"] if l["type"] == "tilelayer")
map_gids = layer["data"]  # длина = MAP_COLS * MAP_ROWS

# 4) Загружаем tileset и вырезаем все уникальные GID
tileset = pygame.image.load(TILESET_PATH).convert_alpha()
ts = map_data["tilesets"][0]
firstgid = ts["firstgid"]
cols = ts["columns"]

tiles = {}
for gid in set(map_gids):
    if gid == 0:
        continue  # пусто
    index = gid - firstgid
    if index < 0:
        continue  # не наш тайл
    x = (index % cols) * TILE_W
    y = (index // cols) * TILE_H
    rect = pygame.Rect(x, y, TILE_W, TILE_H)
    tiles[gid] = tileset.subsurface(rect)

# 5) Нарезаем спрайт-лист Адама
FRAME_W, FRAME_H = 16, 32
SCALE = 2
SCALED_W, SCALED_H = FRAME_W * SCALE, FRAME_H * SCALE
ANIM_SPEED = 0.12
speed = 2

adam_sheet = pygame.image.load(ADAM_SPRITE_PATH).convert_alpha()
def slice_adam(sheet):
    frames = [[] for _ in range(4)]
    for direction in range(4):
        for i in range(6):
            idx = direction * 6 + i
            rect = pygame.Rect(idx * FRAME_W, 0, FRAME_W, FRAME_H)
            img = sheet.subsurface(rect)
            frames[direction].append(
                pygame.transform.scale(img, (SCALED_W, SCALED_H))
            )
    return frames

adam_frames = slice_adam(adam_sheet)

# Стартовая позиция Адама — над дверью в центре
door_c = MAP_COLS // 2
adam_x = door_c * TILE_W + TILE_W // 2
adam_y = (MAP_ROWS - 1) * TILE_H

frame_index = 0
anim_timer = 0
current_dir = 3  # вниз

clock = pygame.time.Clock()
running = True

# 6) Игровой цикл
while running:
    dt = clock.tick(60) / 1000
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # Движение
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:   dx -= speed
    if keys[pygame.K_RIGHT]:  dx += speed
    if keys[pygame.K_UP]:     dy -= speed
    if keys[pygame.K_DOWN]:   dy += speed

    # Нормализация диагонали
    if dx and dy:
        n = math.hypot(dx, dy)
        dx, dy = dx / n * speed, dy / n * speed

    moving = (dx != 0 or dy != 0)

    # Выбор направления анимации
    if dx > 0:       current_dir = 0
    elif dx < 0:     current_dir = 2
    elif dy < 0:     current_dir = 1
    elif dy > 0:     current_dir = 3

    # Проверка столкновений: любые gid>0 — стена
    new_rect = pygame.Rect(
        adam_x + dx - SCALED_W // 2,
        adam_y + dy - SCALED_H,
        SCALED_W, SCALED_H
    )
    collision = False
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            gid = map_gids[r * MAP_COLS + c]
            if gid > 0:
                wall = pygame.Rect(c * TILE_W, r * TILE_H, TILE_W, TILE_H)
                if new_rect.colliderect(wall):
                    collision = True
                    break
        if collision:
            break

    if not collision:
        adam_x += dx
        adam_y += dy

    # Анимация кадров
    if moving:
        anim_timer += ANIM_SPEED
        if anim_timer >= 1:
            anim_timer = 0
            frame_index = (frame_index + 1) % 6
    else:
        frame_index = 0

    # Отрисовка
    screen.fill(BG_COLOR)

    # 1) Рисуем тайлы по GID
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            gid = map_gids[r * MAP_COLS + c]
            img = tiles.get(gid)
            if img:
                screen.blit(img, (c * TILE_W, r * TILE_H))

    # 2) Рисуем Адама
    frame = adam_frames[current_dir][frame_index]
    screen.blit(frame, (adam_x - SCALED_W // 2, adam_y - SCALED_H))

    pygame.display.flip()

pygame.quit()
sys.exit()

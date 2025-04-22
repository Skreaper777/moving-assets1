import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1800,100"

import pygame
import sys
import math
import json

# 1) Загружаем конфиг
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

# 2) Извлекаем настройки
WINDOW_WIDTH   = cfg["window_size"]["width"]
WINDOW_HEIGHT  = cfg["window_size"]["height"]
BG_COLOR       = tuple(cfg["background_color"])

TILESET_PATH     = cfg["tileset_path"]
ADAM_SPRITE_PATH = cfg["adam_sprite_path"]

TILE_W, TILE_H   = cfg["tile_size"]["w"], cfg["tile_size"]["h"]
MAP_COLS, MAP_ROWS = cfg["map_size"]["cols"], cfg["map_size"]["rows"]

# Вместо tile_ids теперь пиксельные координаты тайлов
tile_defs = cfg["tile_defs"]
game_map  = cfg["game_map"]

# Параметры Адама
FRAME_W, FRAME_H = 16, 32    # высота 32px
SCALE            = 2
SCALED_W = FRAME_W * SCALE
SCALED_H = FRAME_H * SCALE
ANIM_SPEED = 0.12
speed = 2

# Pygame и окно
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Комната и Адам")

# 3) Загружаем тайлсет и сразу вырезаем нужные тайлы по пикселям
tileset = pygame.image.load(TILESET_PATH).convert_alpha()
tiles = {}
for name, pos in tile_defs.items():
    px, py = pos["px"], pos["py"]
    rect = pygame.Rect(px, py, TILE_W, TILE_H)
    tiles[name] = tileset.subsurface(rect)

# 4) Нарезаем спрайт-лист Адама как раньше
adam_sheet = pygame.image.load(ADAM_SPRITE_PATH).convert_alpha()
def slice_adam(sheet):
    frames = [[] for _ in range(4)]
    for direction in range(4):
        for i in range(6):
            idx = direction*6 + i
            rect = pygame.Rect(idx*FRAME_W, 0, FRAME_W, FRAME_H)
            img = sheet.subsurface(rect)
            img = pygame.transform.scale(img, (SCALED_W, SCALED_H))
            frames[direction].append(img)
    return frames

adam_frames = slice_adam(adam_sheet)

# 5) Стартовая позиция Адама (над дверью)
door_c = MAP_COLS // 2
adam_x = door_c * TILE_W + TILE_W//2
adam_y = (MAP_ROWS - 1) * TILE_H

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

    # --- движение Адама ---
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:   dx -= speed
    if keys[pygame.K_RIGHT]:  dx += speed
    if keys[pygame.K_UP]:     dy -= speed
    if keys[pygame.K_DOWN]:   dy += speed

    if dx and dy:
        norm = math.hypot(dx, dy)
        dx, dy = dx/norm*speed, dy/norm*speed

    moving = (dx != 0 or dy != 0)

    # выбираем направление анимации
    if dx > 0:       current_dir = 0
    elif dx < 0:     current_dir = 2
    elif dy < 0:     current_dir = 1
    elif dy > 0:     current_dir = 3

    # проверяем столкновения
    new_rect = pygame.Rect(
        adam_x + dx - SCALED_W//2,
        adam_y + dy - SCALED_H,
        SCALED_W, SCALED_H
    )
    collision = False
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            key = game_map[r][c]
            if key != "floor":
                wall = pygame.Rect(c*TILE_W, r*TILE_H, TILE_W, TILE_H)
                if new_rect.colliderect(wall):
                    collision = True
                    break
        if collision: break

    if not collision:
        adam_x += dx
        adam_y += dy

    # обновляем кадр анимации
    if moving:
        anim_timer += ANIM_SPEED
        if anim_timer >= 1:
            anim_timer = 0
            frame_index = (frame_index + 1) % 6
    else:
        frame_index = 0

    # ---- отрисовка ----
    screen.fill(BG_COLOR)

    # 1) рисуем тайлы комнаты по ключам из game_map
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            key = game_map[r][c]
            img = tiles.get(key)
            if img:
                screen.blit(img, (c*TILE_W, r*TILE_H))

    # 2) рисуем Адама
    frame = adam_frames[current_dir][frame_index]
    draw_x = adam_x - SCALED_W//2
    draw_y = adam_y - SCALED_H
    screen.blit(frame, (draw_x, draw_y))

    pygame.display.flip()

pygame.quit()
sys.exit()

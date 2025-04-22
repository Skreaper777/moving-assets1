import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1800,100"

import pygame, sys, math, json

# 1) Загружаем config.json
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

WINDOW_WIDTH    = cfg["window_size"]["width"]
WINDOW_HEIGHT   = cfg["window_size"]["height"]
BG_COLOR        = tuple(cfg["background_color"])
TILESET_PATH    = cfg["tileset_path"]
ADAM_SPRITE_PATH= cfg["adam_sprite_path"]
TILE_W, TILE_H  = cfg["tile_size"]["w"], cfg["tile_size"]["h"]

# 2) Инициализация Pygame и окно
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Комната и Адам")

# 3) Загружаем map.json из Tiled
with open("map.json", encoding="utf-8") as f:
    map_data = json.load(f)

MAP_COLS = map_data["width"]
MAP_ROWS = map_data["height"]
if map_data["tilewidth"] != TILE_W or map_data["tileheight"] != TILE_H:
    raise RuntimeError("Несовпадение размеров тайлов")

layer     = next(l for l in map_data["layers"] if l["type"] == "tilelayer")
map_gids  = layer["data"]  # одномерный список длины MAP_COLS*MAP_ROWS

# 4) Вырезаем все тайлы и парсим collision‑объекты

# 4.1) Загружаем tileset и вырезаем каждый gid из map_gids
tileset = pygame.image.load(TILESET_PATH).convert_alpha()
ts       = map_data["tilesets"][0]
firstgid = ts["firstgid"]
cols_ts  = ts["columns"]
tilecount = ts.get("tilecount", cols_ts * (ts["imageheight"] // TILE_H))

tiles = {}        # gid -> Surface
coll_shapes = {}  # gid -> list of Rect

unique_gids = {gid for gid in map_gids if gid > 0}
for gid in unique_gids:
    idx = gid - firstgid
    if idx < 0 or idx >= tilecount:
        continue
    x0 = (idx % cols_ts) * TILE_W
    y0 = (idx // cols_ts) * TILE_H
    tiles[gid] = tileset.subsurface(pygame.Rect(x0, y0, TILE_W, TILE_H))

# 4.2) Парсим collision‑shapes, если они есть
for tile in ts.get("tiles", []):
    local_id = tile["id"]
    gid = firstgid + local_id
    if gid not in unique_gids:
        continue
    objs = tile.get("objectgroup", {}).get("objects", [])
    shapes = []
    for o in objs:
        shapes.append(pygame.Rect(o["x"], o["y"], o["width"], o["height"]))
    if shapes:
        coll_shapes[gid] = shapes

# 5) Нарезаем спрайты Адама
FRAME_W, FRAME_H = 16, 32
SCALE = 2
SCALED_W, SCALED_H = FRAME_W * SCALE, FRAME_H * SCALE
ANIM_SPEED = 0.12
speed = 2

adam_sheet = pygame.image.load(ADAM_SPRITE_PATH).convert_alpha()
def slice_adam(sheet):
    frames = [[] for _ in range(4)]
    for d in range(4):
        for i in range(6):
            idx = d*6 + i
            surf = sheet.subsurface(pygame.Rect(idx*FRAME_W, 0, FRAME_W, FRAME_H))
            surf = pygame.transform.scale(surf, (SCALED_W, SCALED_H))
            frames[d].append(surf)
    return frames

adam_frames = slice_adam(adam_sheet)

# стартовая позиция Адама над дверью
door_c = MAP_COLS // 2
adam_x = door_c * TILE_W + TILE_W//2
adam_y = (MAP_ROWS - 1) * TILE_H

frame_index = 0
anim_timer  = 0
current_dir = 3  # вниз

clock = pygame.time.Clock()
running = True

# 6) Игровой цикл
while running:
    dt = clock.tick(60) / 1000
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # — движение
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:   dx -= speed
    if keys[pygame.K_RIGHT]:  dx += speed
    if keys[pygame.K_UP]:     dy -= speed
    if keys[pygame.K_DOWN]:   dy += speed
    if dx and dy:
        n = math.hypot(dx, dy)
        dx, dy = dx/n*speed, dy/n*speed
    moving = (dx != 0 or dy != 0)

    # — направление анимации
    if dx > 0:       current_dir = 0
    elif dx < 0:     current_dir = 2
    elif dy < 0:     current_dir = 1
    elif dy > 0:     current_dir = 3

    # — предполагаемый новый Rect для Адама
    new_rect = pygame.Rect(
        adam_x + dx - SCALED_W//2,
        adam_y + dy - SCALED_H,
        SCALED_W, SCALED_H
    )

    # — проверка коллизий с фоллбэком
    collision = False
    c0 = max(0, new_rect.left   // TILE_W)
    c1 = min(MAP_COLS, new_rect.right  // TILE_W + 1)
    r0 = max(0, new_rect.top    // TILE_H)
    r1 = min(MAP_ROWS, new_rect.bottom // TILE_H + 1)

    for r in range(r0, r1):
        for c in range(c0, c1):
            gid = map_gids[r*MAP_COLS + c]
            if gid == 0:
                continue

            # если есть точные формы — проверяем их
            shapes = coll_shapes.get(gid)
            if shapes:
                for shape in shapes:
                    abs_r = pygame.Rect(
                        c*TILE_W + shape.x,
                        r*TILE_H + shape.y,
                        shape.w, shape.h
                    )
                    if new_rect.colliderect(abs_r):
                        collision = True
                        break
            else:
                # фоллбэк: весь тайл
                abs_r = pygame.Rect(c*TILE_W, r*TILE_H, TILE_W, TILE_H)
                if new_rect.colliderect(abs_r):
                    collision = True

            if collision:
                break
        if collision:
            break

    if not collision:
        adam_x += dx
        adam_y += dy

    # — анимация кадров
    if moving:
        anim_timer += ANIM_SPEED
        if anim_timer >= 1:
            anim_timer = 0
            frame_index = (frame_index + 1) % 6
    else:
        frame_index = 0

    # — отрисовка
    screen.fill(BG_COLOR)
    # тайлы
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            gid = map_gids[r*MAP_COLS + c]
            img = tiles.get(gid)
            if img:
                screen.blit(img, (c*TILE_W, r*TILE_H))
    # Адам
    frame = adam_frames[current_dir][frame_index]
    screen.blit(frame, (adam_x - SCALED_W//2, adam_y - SCALED_H))

    pygame.display.flip()

pygame.quit()
sys.exit()

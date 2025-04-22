import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1800,100"

import pygame, sys, math, json

# ----------------------- 1) Настройки из config.json -----------------------
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

WINDOW_WIDTH   = cfg["window_size"]["width"]
WINDOW_HEIGHT  = cfg["window_size"]["height"]
BG_COLOR       = tuple(cfg["background_color"])

TILESET_PATH     = cfg["tileset_path"]
ADAM_SPRITE_PATH = cfg["adam_sprite_path"]

TILE_W, TILE_H   = cfg["tile_size"]["w"], cfg["tile_size"]["h"]
# ---------------------------------------------------------------------------

# Инициализируем Pygame и окно **до** загрузки любых изображений
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Комната и Адам")

# ----------------------- 2) Загрузка карты из Tiled -------------------------
MAP_JSON_PATH = "map.json"
with open(MAP_JSON_PATH, encoding="utf-8") as f:
    map_data = json.load(f)

MAP_COLS = map_data["width"]
MAP_ROWS = map_data["height"]

if map_data["tilewidth"] != TILE_W or map_data["tileheight"] != TILE_H:
    raise RuntimeError("Несовпадение размеров тайла между map.json и config.json")

ts = map_data["tilesets"][0]
firstgid = ts["firstgid"]
gid2key = {}
for t in ts.get("tiles", []):
    gid = firstgid + t["id"]
    for prop in t.get("properties", []):
        if prop["name"] == "key":
            gid2key[gid] = prop["value"]

layer = next(l for l in map_data["layers"] if l["type"] == "tilelayer")
data = layer["data"]

game_map = [
    [ gid2key.get(data[r*MAP_COLS + c], "floor") for c in range(MAP_COLS) ]
    for r in range(MAP_ROWS)
]
# ---------------------------------------------------------------------------

# -------------- 3) Режем тайлы только по ключам из config.json -------------
tile_defs = cfg["tile_defs"]

tileset = pygame.image.load(TILESET_PATH).convert_alpha()
tiles = {}
for name, pos in tile_defs.items():
    px, py = pos["px"], pos["py"]
    rect = pygame.Rect(px, py, TILE_W, TILE_H)
    tiles[name] = tileset.subsurface(rect)
# ---------------------------------------------------------------------------

# ------------------------- 4) Анимация Адама -------------------------------
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
            idx = direction*6 + i
            rect = pygame.Rect(idx*FRAME_W, 0, FRAME_W, FRAME_H)
            img = sheet.subsurface(rect)
            frames[direction].append(
                pygame.transform.scale(img, (SCALED_W, SCALED_H))
            )
    return frames

adam_frames = slice_adam(adam_sheet)

door_c = MAP_COLS // 2
adam_x = door_c * TILE_W + TILE_W//2
adam_y = (MAP_ROWS - 1) * TILE_H

frame_index = 0
anim_timer = 0
current_dir = 3
# ---------------------------------------------------------------------------

# ------------------------- 5) Pygame Loop ----------------------------------
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:   dx -= speed
    if keys[pygame.K_RIGHT]:  dx += speed
    if keys[pygame.K_UP]:     dy -= speed
    if keys[pygame.K_DOWN]:   dy += speed

    if dx and dy:
        n = math.hypot(dx, dy)
        dx, dy = dx/n * speed, dy/n * speed

    moving = dx != 0 or dy != 0

    if dx > 0:      current_dir = 0
    elif dx < 0:    current_dir = 2
    elif dy < 0:    current_dir = 1
    elif dy > 0:    current_dir = 3

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

    if moving:
        anim_timer += ANIM_SPEED
        if anim_timer >= 1:
            anim_timer = 0
            frame_index = (frame_index + 1) % 6
    else:
        frame_index = 0

    screen.fill(BG_COLOR)
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            key = game_map[r][c]
            img = tiles.get(key)
            if img:
                screen.blit(img, (c*TILE_W, r*TILE_H))

    frame = adam_frames[current_dir][frame_index]
    draw_x = adam_x - SCALED_W//2
    draw_y = adam_y - SCALED_H
    screen.blit(frame, (draw_x, draw_y))

    pygame.display.flip()

pygame.quit()
sys.exit()

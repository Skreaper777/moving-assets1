import pygame
import sys
import math

# ----------------------------- НАСТРОЙКИ -----------------------------
TILESET_PATH    = r"C:\Users\stasr\PycharmProjects\Game\play-assets\mnt\data\Modern_Interiors\Modern tiles_Free\Interiors_free\48x48\Room_Builder_free_48x48.png"
ADAM_SPRITE_PATH= r"mnt/data/Modern_Interiors/Modern tiles_Free/Characters_free/Adam_run_16x16.png"

TILE_W, TILE_H   = 48, 48      # размер плитки комнаты
MAP_COLS, MAP_ROWS = 12, 8     # размер комнаты в плитках

# параметры Адама
FRAME_W, FRAME_H = 16, 32      # *высота 32px!*
SCALE            = 2
SCALED_W, SCALED_H = FRAME_W*SCALE, FRAME_H*SCALE
ANIM_SPEED       = 0.12

# окно
WINDOW_WIDTH  = MAP_COLS * TILE_W
WINDOW_HEIGHT = MAP_ROWS * TILE_H
# ---------------------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Комната и Адам")

# 1) Загружаем и режем тайлсет комнаты
tileset = pygame.image.load(TILESET_PATH).convert_alpha()
cols = tileset.get_width() // TILE_W
tiles = [
    tileset.subsurface(pygame.Rect(x*TILE_W, y*TILE_H, TILE_W, TILE_H))
    for y in range(tileset.get_height()//TILE_H)
    for x in range(cols)
]

# 2) Создаём словарь tile_ids — *имена* → индексы в tiles[]
tile_ids = {
    "corner_tl":  0*cols + 0,   # (0,0)
    "edge_top":   0*cols + 1,   # (1,0)
    "corner_tr":  0*cols + 2,   # (2,0)
    "edge_left":  1*cols + 0,   # (0,1)
    "edge_right": 1*cols + 2,   # (2,1)
    "floor":      5*cols + 5,   # (5,5) — ⇐ *пример*, смени по своему
    # …добавь другие нужные: corner_bl, edge_bottom и т.д.
}

# 3) Генерируем карту ключей
game_map = [["floor"]*MAP_COLS for _ in range(MAP_ROWS)]
for r in range(MAP_ROWS):
    for c in range(MAP_COLS):
        # верхняя строка
        if r==0 and c==0:            game_map[r][c] = "corner_tl"
        elif r==0 and c==MAP_COLS-1: game_map[r][c] = "corner_tr"
        elif r==0:                   game_map[r][c] = "edge_top"
        # боковые стены
        elif c==0:                   game_map[r][c] = "edge_left"
        elif c==MAP_COLS-1:          game_map[r][c] = "edge_right"
        # пол остаётся "floor"
# врезаем дверь снизу по центру
door_c = MAP_COLS//2
game_map[MAP_ROWS-1][door_c] = "floor"  # вместо "edge_bottom" 😉

# 4) Загружаем и режем спрайт Адама
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

# 5) Стартовая позиция над дверью (ноги на уровне пола)
adam_x = door_c * TILE_W + TILE_W//2
adam_y = (MAP_ROWS - 1) * TILE_H
speed = 2

# анимация
frame_index = 0
anim_timer  = 0
current_dir = 3  # вниз

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)/1000
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # --- Движение Адама ---
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:   dx -= speed
    if keys[pygame.K_RIGHT]:  dx += speed
    if keys[pygame.K_UP]:     dy -= speed
    if keys[pygame.K_DOWN]:   dy += speed

    if dx and dy:  # *нормализация диагонали*
        norm = math.hypot(dx, dy)
        dx, dy = dx/norm*speed, dy/norm*speed

    moving = dx!=0 or dy!=0

    # выбираем направление
    if dx>0:    current_dir=0
    elif dx<0:  current_dir=2
    elif dy<0:  current_dir=1
    elif dy>0:  current_dir=3

    # проверка столкновений
    new_rect = pygame.Rect(adam_x+dx - SCALED_W//2,
                           adam_y+dy - SCALED_H,
                           SCALED_W, SCALED_H)
    collision = False
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            key = game_map[r][c]
            if key!="floor":  # все не‑floor — это стены
                wall_rect = pygame.Rect(c*TILE_W, r*TILE_H, TILE_W, TILE_H)
                if new_rect.colliderect(wall_rect):
                    collision = True
                    break
        if collision: break

    if not collision:
        adam_x += dx; adam_y += dy

    # обновляем кадр
    if moving:
        anim_timer += ANIM_SPEED
        if anim_timer>=1:
            anim_timer=0
            frame_index = (frame_index+1)%6
    else:
        frame_index=0

    # ---- ОТРИСОВКА ----
    screen.fill((0,0,0))
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            key = game_map[r][c]
            idx = tile_ids.get(key, tile_ids["floor"])
            screen.blit(tiles[idx], (c*TILE_W, r*TILE_H))

    # рисуем Адама
    frame_img = adam_frames[current_dir][frame_index]
    draw_x = adam_x - SCALED_W//2
    draw_y = adam_y - SCALED_H
    screen.blit(frame_img, (draw_x, draw_y))

    pygame.display.flip()

pygame.quit()
sys.exit()

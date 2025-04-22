import pygame
import sys
import math  # для нормализации вектора скорости
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = "1800,100"

# Инициализация Pygame
pygame.init()

# Настройки окна
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Адам бегает по комнате")

# Загрузка спрайт-листа
sprite_sheet = pygame.image.load("mnt/data/Adam_run_16x16.png").convert_alpha()

# Параметры кадров и масштаб
FRAME_WIDTH, FRAME_HEIGHT = 16, 32
SCALE = 2
SCALED_WIDTH, SCALED_HEIGHT = FRAME_WIDTH * SCALE, FRAME_HEIGHT * SCALE
ANIM_SPEED = 0.12

# Нарезка кадров
def slice_frames(sheet):
    frames = [[] for _ in range(4)]
    for direction in range(4):
        for i in range(6):
            idx = direction * 6 + i
            rect = pygame.Rect(idx * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
            frame = sheet.subsurface(rect)
            frames[direction].append(
                pygame.transform.scale(frame, (SCALED_WIDTH, SCALED_HEIGHT))
            )
    return frames

frames = slice_frames(sprite_sheet)

# Позиция и состояние
x, y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
speed = 2
frame_index = 0
animation_timer = 0
current_direction = 3  # вниз
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = dy = 0
    # *Если оба направления*, оба условия сработают
    if keys[pygame.K_LEFT]:
        dx -= speed
    if keys[pygame.K_RIGHT]:
        dx += speed
    if keys[pygame.K_UP]:
        dy -= speed
    if keys[pygame.K_DOWN]:
        dy += speed

    # нормализация скорости при диагонали
    if dx != 0 and dy != 0:
        norm = math.hypot(dx, dy)
        dx = dx / norm * speed
        dy = dy / norm * speed

    moving = (dx != 0 or dy != 0)
    x += dx
    y += dy

    # Ограничение по границам окна
    x = max(SCALED_WIDTH//2,   min(x, WINDOW_WIDTH - SCALED_WIDTH//2))
    y = max(SCALED_HEIGHT,      min(y, WINDOW_HEIGHT))

    # Выбор направления анимации
    if dx > 0:
        current_direction = 0
    elif dx < 0:
        current_direction = 2
    elif dy < 0:
        current_direction = 1
    elif dy > 0:
        current_direction = 3

    # Анимация
    if moving:
        animation_timer += ANIM_SPEED
        if animation_timer >= 1:
            animation_timer = 0
            frame_index = (frame_index + 1) % 6
    else:
        frame_index = 0

    # Отрисовка
    screen.fill((20, 20, 40))
    frame = frames[current_direction][frame_index]
    screen.blit(frame, (x - SCALED_WIDTH//2, y - SCALED_HEIGHT))
    pygame.display.flip()

pygame.quit()
sys.exit()

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Адам бегает по комнате")

# Загрузка спрайт-листа
sprite_sheet = pygame.image.load("mnt/data/Adam_run_16x16.png").convert_alpha()

# Параметры кадров и масштаб
FRAME_WIDTH, FRAME_HEIGHT = 16, 32      # <— высота теперь 32px
SCALE = 2
SCALED_WIDTH, SCALED_HEIGHT = FRAME_WIDTH * SCALE, FRAME_HEIGHT * SCALE
ANIM_SPEED = 0.12

# Нарезка кадров: один ряд из 24 кадров (6 на каждое направление)
def slice_frames(sheet):
    frames = [[] for _ in range(4)]
    for direction in range(4):
        for i in range(6):
            index = direction * 6 + i
            # по Y всегда 0, захватываем высоту 32px
            rect = pygame.Rect(
                index * FRAME_WIDTH,
                0,
                FRAME_WIDTH, FRAME_HEIGHT
            )
            frame = sheet.subsurface(rect)
            frame = pygame.transform.scale(frame, (SCALED_WIDTH, SCALED_HEIGHT))
            frames[direction].append(frame)
    return frames

frames = slice_frames(sprite_sheet)

# Начальные координаты (центр экрана, точка в ногах персонажа)
x, y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
speed = 2

# Состояние анимации
frame_index = 0
animation_timer = 0
current_direction = 3  # вниз
moving = False

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = dy = 0
    moving = False

    if keys[pygame.K_LEFT]:
        dx = -speed; current_direction = 2; moving = True
    elif keys[pygame.K_RIGHT]:
        dx = speed;  current_direction = 0; moving = True
    elif keys[pygame.K_UP]:
        dy = -speed; current_direction = 1; moving = True
    elif keys[pygame.K_DOWN]:
        dy = speed;  current_direction = 3; moving = True

    x += dx; y += dy

    # Ограничиваем, чтобы Адам помещался целиком
    x = max(SCALED_WIDTH // 2, min(x, WINDOW_WIDTH - SCALED_WIDTH // 2))
    y = max(SCALED_HEIGHT,      min(y, WINDOW_HEIGHT))

    # Обновление кадра
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
    draw_x = x - SCALED_WIDTH // 2
    draw_y = y - SCALED_HEIGHT
    screen.blit(frame, (draw_x, draw_y))
    pygame.display.flip()

pygame.quit()
sys.exit()

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Адам бегает по комнате")

# Загрузка кастомного спрайта
sprite_sheet = pygame.image.load("mnt/data/Modern_Interiors/Modern tiles_Free/Characters_free/Adam_run_16x16.png").convert_alpha()

# Параметры кадров
FRAME_WIDTH, FRAME_HEIGHT = 32, 32
SCALE = 2
ANIM_SPEED = 0.15

# Функция нарезки по 3 кадра на 4 направления (вниз, влево, вправо, вверх)
def slice_frames(sheet):
    frames = [[] for _ in range(4)]  # 4 направления
    for i in range(12):
        direction = i // 3
        frame = sheet.subsurface((i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
        frame = pygame.transform.scale(frame, (FRAME_WIDTH * SCALE, FRAME_HEIGHT * SCALE))
        frames[direction].append(frame)
    return frames

frames = slice_frames(sprite_sheet)

# Начальные координаты
x, y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
speed = 2

# Состояние анимации
frame_index = 0
animation_timer = 0
current_direction = 0
moving = False

# Основной игровой цикл
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    moving = False

    if keys[pygame.K_LEFT]:
        dx = -speed
        current_direction = 1
        moving = True
    elif keys[pygame.K_RIGHT]:
        dx = speed
        current_direction = 2
        moving = True
    elif keys[pygame.K_UP]:
        dy = -speed
        current_direction = 3
        moving = True
    elif keys[pygame.K_DOWN]:
        dy = speed
        current_direction = 0
        moving = True

    x += dx
    y += dy

    # Анимация
    if moving:
        animation_timer += ANIM_SPEED
        if animation_timer >= 1:
            animation_timer = 0
            frame_index = (frame_index + 1) % 3
    else:
        frame_index = 1  # центральный кадр

    # Отрисовка
    screen.fill((30, 30, 50))
    screen.blit(frames[current_direction][frame_index], (x, y))
    pygame.display.flip()

# Завершение
pygame.quit()
sys.exit()

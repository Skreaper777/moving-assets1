import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Простая комната")

# Загрузка ассета персонажа
character_img = pygame.image.load("mnt/data/Modern_Interiors/Modern tiles_Free/Characters_free/Adam_16x16.png").convert_alpha()
character_img = pygame.transform.scale(character_img, (32, 32))  # увеличим для наглядности

# Начальные координаты
x, y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
speed = 3

# Основной игровой цикл
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Получаем нажатые клавиши
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    # Отрисовка
    screen.fill((50, 50, 50))  # простой фон
    screen.blit(character_img, (x, y))
    pygame.display.flip()
    clock.tick(60)

# Завершение
pygame.quit()
sys.exit()

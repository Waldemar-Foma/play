import os
import sys
import pygame


pygame.init()

# Для зажатых клавиш генерировать события pygame.KEYDOWN каждые 70 мс
# через 200 мс после зажатия
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 550
HEIGHT = 550

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Перемещение героя")

clock = pygame.time.Clock()

player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()


def load_image(name, colorkey=None):
    fullname = f'data/{name}'

    # Если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is None:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)

    return image


def load_level(filename):
    filename = "data/" + filename
    # Если файл не существует, то выходим
    if not os.path.isfile(filename):
        print(f"Файл с уровнем '{filename}' не найден")
        sys.exit()

    # Читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # Подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # Дополняем каждую строку слева пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None

    # Расширяем карту до размеров экрана
    screen_width = WIDTH // tile_width
    screen_height = HEIGHT // tile_height

    # Дополняем карту уровня до размеров экрана
    for y in range(len(level)):
        if len(level[y]) < screen_width:
            level[y] = level[y].ljust(screen_width, '.')

    # Если высота уровня меньше высоты экрана, добавляем строки
    while len(level) < screen_height:
        level.append('.' * screen_width)

    # Генерация тайлов и игрока
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)

    # Вернём игрока, а также размер поля в клетках
    return new_player, len(level[0]) - 1, len(level) - 1


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ПЕРЕМЕЩЕНИЕ ГЕРОЯ", "",
                  "Нажмите любую клавишу, чтобы начать"]

    background = pygame.transform.scale(load_image('background.jpg'),
                                        (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                terminate()
            elif e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def level_selection_screen():
    intro_text = ["ВЫБОР УРОВНЯ", "",
                  "1. Уровень 1",
                  "2. Уровень 2",
                  "3. Уровень 3",
                  "Нажмите цифру, чтобы выбрать уровень"]

    background = pygame.transform.scale(load_image('background.jpg'),
                                        (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                terminate()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return "map-level1.txt"
                elif e.key == pygame.K_2:
                    return "map-level2.txt"
                elif e.key == pygame.K_3:
                    return "map-level3.txt"
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
player_image = load_image('mario.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * self.pos_x + 15,
                                               tile_height * self.pos_y + 5)

    def update(self):
        self.rect = self.image.get_rect().move(tile_width * self.pos_x + 15,
                                               tile_height * self.pos_y + 5)


start_screen()

# Выбор уровня
level_filename = level_selection_screen()

# Загрузка уровня
field = load_level(level_filename)
player, level_x, level_y = generate_level(field)

running = True

while running:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            pos_x, pos_y = player.pos_x, player.pos_y
            if e.key == pygame.K_LEFT and \
                    pos_x > 0 and field[pos_y][pos_x - 1] != "#":
                player.pos_x -= 1
            if e.key == pygame.K_RIGHT and \
                    pos_x < level_x and field[pos_y][pos_x + 1] != "#":
                player.pos_x += 1
            if e.key == pygame.K_UP and \
                    pos_y > 0 and field[pos_y - 1][pos_x] != "#":
                player.pos_y -= 1
            if e.key == pygame.K_DOWN and \
                    pos_y < level_y and field[pos_y + 1][pos_x] != "#":
                player.pos_y += 1
            if e.key == pygame.K_a and \
                    pos_x > 0 and field[pos_y][pos_x - 1] != "#":
                player.pos_x -= 1
            if e.key == pygame.K_d and \
                    pos_x < level_x and field[pos_y][pos_x + 1] != "#":
                player.pos_x += 1
            if e.key == pygame.K_w and \
                    pos_y > 0 and field[pos_y - 1][pos_x] != "#":
                player.pos_y -= 1
            if e.key == pygame.K_s and \
                    pos_y < level_y and field[pos_y + 1][pos_x] != "#":
                player.pos_y += 1
            player_group.update()

    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)

terminate()
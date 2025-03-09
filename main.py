import pygame
import random
import os
import sys

# Инициализация Pygame
pygame.init()
FPS = 50
size = WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Мартышкины запасы")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREEN = (144, 238, 144)
BROWN = (160, 82, 45)

# Загрузка звука (банан пойман)
catch_sound = pygame.mixer.Sound(os.path.join('data', 'catch.wav'))

# Функция-обертка загружает изображение по имени файла
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

# Завершает игру и закрывает окно
def terminate():
    pygame.quit()
    sys.exit()

# Отображает стартовый экран с инструкциями
def start_screen():
    intro_text = [
        "Помоги мартышке собрать как можно больше бананов",
        "Правила игры:",
        "Стрелки влево/вправо/вверх/вниз для перемещения",
        "За пойманный банан +3 очка",
        "За упавший банан штраф -2 очка"
    ]

    # Загрузка фона и его отображение
    fon = pygame.transform.scale(load_image('fon.jpg'), size)
    screen.blit(fon, (0, 0))

    # Cоздание поверхности для инструкций
    font = pygame.font.Font(None, 30)
    rect_surface = pygame.Surface((600, 220), pygame.SRCALPHA)
    rect_surface.fill((255, 255, 0, 150))

    pygame.draw.rect(screen, pygame.Color(BLACK), (130, 60, 600, 220), 2)
    screen.blit(rect_surface, (130, 60))

    # Отображение текста инструкций
    text_coord = 70
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color(BROWN))
        intro_rect = string_rendered.get_rect()
        text_coord += 15
        intro_rect.top = text_coord
        intro_rect.x = 150
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # Создание кнопки "Начать игру"
    start_button = pygame.Rect(300, 400, 200, 50)
    pygame.draw.rect(screen, WHITE, start_button)
    button_text = font.render("Начать игру", 1, pygame.Color(BROWN))
    button_rect = button_text.get_rect()
    button_rect.center = start_button.center
    screen.blit(button_text, button_rect)

    pygame.display.flip() # Обновление экрана

    # Цикл, ожиданющий, пока игрок не начнет игру
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if start_button.collidepoint(event.pos):
                        return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True

        pygame.display.flip()
        clock.tick(FPS)

# Отображает экран завершения игры
def end_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), size)
    screen.blit(fon, (0, 0))

    rect_surface = pygame.Surface((600, 220), pygame.SRCALPHA)
    rect_surface.fill((255, 255, 0, 150))

    pygame.draw.rect(screen, pygame.Color(BLACK), (130, 60, 600, 220), 2)
    screen.blit(rect_surface, (130, 60))

# Класс для создания объектов бананов
class Banana(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = load_image('banana.png')
        self.rect = self.image.get_rect() # Получаем прямоугольник для управления позицией
        self.rect.x = x # Устанавливаем начальную позицию
        self.rect.y = y
        self.speed = speed # Скорость падения

    # Обновление позиции банана
    def update(self):
        self.rect.y += self.speed # Движение вниз по оси Y
        if self.rect.y > HEIGHT: # Удаление бабана, если он выходит за нижнюю границу экрана
            self.kill()

# Класс для создания объектов обезьянки
class Monkey(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = {'right': [], 'left': [], 'stand': [], 'up': []} # Кадры для обезьянки
        self.cut_sheet(load_image('monkey_sheet10x2.png'), 10, 2) # Вырезаем кадры из спрайт-листа
        self.cur_frame = 0 # Указатель текущего кадра
        self.image = self.frames['stand'][self.cur_frame] # Первоначальное изображение
        self.rect = self.image.get_rect(topleft=(x, y)) # Получаем прямоугольник для управления позицией
        self.direction = 'stand' # Направление изначально "стоит"
        self.standing_frame = len(self.frames['stand']) - 1 # Кадр для "стоит"
    # Разделяет спрайт-лист на отдельные кадры
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        frame_index = 0
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                if frame_index < 8:
                    self.frames['right'].append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
                elif frame_index < 16:
                    self.frames['left'].append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
                elif frame_index == 17:
                    self.frames['up'].append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
                elif frame_index == 19:
                    self.frames['stand'].append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
                frame_index += 1

    # Обновление состояния обезьянки
    def update(self):
        # Проверяем границы по оси Х
        if self.rect.x < 0:
            self.rect.x = 0
            self.direction = 'stand'
        elif self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width
            self.direction = 'stand'

        keys = pygame.key.get_pressed() # Получаем состояние клавиш
        if keys[pygame.K_UP] and self.rect.y > 300:
            self.rect.y -= 5
            self.direction = 'up'
        if keys[pygame.K_DOWN] and self.rect.y > 0:
            self.rect.y += 5
            self.direction = 'up'
        # Проверяем границы по оси Y
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.direction = 'up'

        # Подбираем изображения в зависимости от направления
        if self.direction == 'right':
            self.cur_frame = (self.cur_frame + 1) % len(self.frames['right'])
            self.image = self.frames['right'][self.cur_frame]
            self.rect.x += 5
        elif self.direction == 'left':
            self.cur_frame = (self.cur_frame + 1) % len(self.frames['left'])
            self.image = self.frames['left'][self.cur_frame]
            self.rect.x -= 5
        elif self.direction == 'stand':
            self.image = self.frames['stand'][self.standing_frame]
        elif self.direction == 'up':
            self.image = self.frames['up'][self.standing_frame]

    # Управляет напрвлением обезьянки
    def move(self, direction):
        self.direction = direction
        if direction == 'right':
            self.cur_frame = 0 # Сбрасываем кадр
        elif direction == 'left':
            self.cur_frame = 0
        elif direction == 'stand':
            self.cur_frame = self.standing_frame


# Основной класс игры
class Game:
    def __init__(self):
        self.score = 0 # Очки игрока
        self.level = 0 # Уровень игры
        self.monkey = Monkey(WIDTH // 2, HEIGHT - 160)
        self.bananas = pygame.sprite.Group() # Группа для бананов
        self.all_sprites = pygame.sprite.Group(self.monkey) # Группа для всех спрайты
        self.font = pygame.font.Font(None, 36)
        self.game_over = False # Состояние окончания игры

    # Создание нового уровня с бананами
    def new_level(self):
        self.bananas.empty() # Удаление старых бананов
        for _ in range(5 + self.level):
            x = random.randint(0, WIDTH - 50)
            y = random.randint(0, HEIGHT - 300)
            speed = 1 + self.level * 0.5 # Увеличение скорости
            banana = Banana(x, y, speed) # Создаем банан
            self.all_sprites.add(banana) # Добавляем в группу спрайтов
            self.bananas.add(banana) # Добавляем в группу бананов

    # Обновление состояний всех спрайтов и проверки столкновений...
    def update(self):
        self.all_sprites.update()

        # Проверка на столкновение обезьянки с бананами
        hits = pygame.sprite.spritecollide(self.monkey, self.bananas, True)
        for hit in hits:
            self.score += 3
            catch_sound.play()

        # Проверка на упавшие бананы
        for banana in self.bananas:
            if banana.rect.bottom >= HEIGHT:
                self.score -= 2
                banana.kill()
        # Если все бананы собраны - переходим на след.уровень
        if len(self.bananas) == 0:
            self.level += 1
            self.new_level()

        # Проверка условий окончания игры
        if self.score < -20 or self.level == 10:
            self.game_over = True

    # Отрисовка игровых объектов
    def draw(self):
        screen.fill(LIGHT_GREEN)
        self.all_sprites.draw(screen)

        score_text = self.font.render(f"Счет: {self.score}", True, BLACK)
        level_text = self.font.render(f"Уровень: {self.level + 1}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        # Если игра окончена, отражаем экран конца игры
        if self.game_over:
            end_screen()
            monkey_image = load_image('monkey_sheet10x2.png')
            if self.score <= 0:
                result_text = self.font.render("Вы проиграли!", True, BROWN)
                screen.blit(monkey_image.subsurface(pygame.Rect(840, 152, 105, 152)),
                            (WIDTH // 2 - 50, HEIGHT // 2 + 60))
            else:
                result_text = self.font.render("Вы победили!", True, BROWN)
                screen.blit(monkey_image.subsurface(pygame.Rect(630, 152, 105, 152)),
                            (WIDTH // 2 - 50, HEIGHT // 2 + 60))
            score_result_text = self.font.render(f"Ваш счет: {self.score}", True, BROWN)
            restart_text = self.font.render("Нажмите SPACE для перезапуска", True, BROWN)
            screen.blit(result_text, (320, 100))
            screen.blit(score_result_text, (320, 150))
            screen.blit(restart_text, (220, 210))

    # Главный игровой цикл
    def run(self):
        self.new_level()
        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_over:
                        self.__init__()
                    if event.key == pygame.K_RIGHT:
                        self.monkey.move('right')
                    elif event.key == pygame.K_LEFT:
                        self.monkey.move('left')
                    else:
                        self.monkey.move('stand')

            if not self.game_over:
                self.update()
            self.draw()
            pygame.display.flip()

# Точка входа в игру
def main():
    if start_screen(): # Если игрок нажал начать игру
        game = Game() # Создаем объект игры
        game.run() # Запуск игрового цикла


if __name__ == '__main__':
    main() # Запуск программы

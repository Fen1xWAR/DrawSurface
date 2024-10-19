import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def load_fdf_file(filename: str):
    """Загрузить файл .fdf и вернуть numpy массив с высотами и цветами."""
    try:
        with open(filename, 'rb') as file:
            content = file.read().decode('utf-8-sig')  # Чтение и удаление BOM
    except Exception as e:
        raise FileNotFoundError(f"Не удалось прочитать файл: {e}")

    lines = content.strip().splitlines()  # Разделить содержимое файла на строки
    matrix = []  # Инициализация списка для хранения высот и цветов

    for line in lines:
        row = []  # Инициализация списка для хранения значений в строке
        for item in line.split():  # Разделить строку на элементы
            if ',' in item:  # Если элемент содержит запятую (высота и цвет)
                height, color = item.split(',')
                height = float(height.strip())  # Преобразование высоты в float
                color = color.strip()  # Удаление пробелов вокруг цвета
                row.append(np.array([height, color], dtype=object))  # Добавление списка (высота, цвет) в строку
            else:  # Если элемент содержит только высоту
                row.append(float(item.strip()))  # Преобразование высоты в float
        matrix.append(row)  # Добавление строки в матрицу
    # Проверка, что все строки имеют одинаковую длину
    if len(set(map(len, matrix))) != 1:
        raise ValueError("Все строки во входных данных должны иметь одинаковую длину.")

    return np.array(matrix, dtype=object)  # Возврат матрицы в виде numpy массива


def convert_hex_to_rgb(hex_color):
    """Преобразовать шестнадцатеричный цвет в RGB кортеж."""
    hex_color = hex_color.lower().replace('0x', '')  # Приведение к нижнему регистру и удаление '0x'

    r = int(hex_color[0:2] or '0', 16)  # Извлечение значения красного цвета
    g = int(hex_color[2:4] or '0', 16)  # Извлечение значения зеленого цвета
    b = int(hex_color[4:6] or '0', 16)  # Извлечение значения синего цвета

    return (r / 255.0, g / 255.0, b / 255.0)  # Возврат RGB кортежа


def create_vertices_and_colors(matrix, scale_z):
    """Сгенерировать вершины и цвета на основе матрицы высот."""
    rows, cols = matrix.shape[0], matrix.shape[1]  # Получение размеров матрицы
    vertices = []  # Инициализация списка для вершин
    colors = []  # Инициализация списка для цветов
    step = 2 / (max(rows, cols) - 1)  # Вычисление шага для распределения вершин

    for i in range(rows):
        for j in range(cols):
            x = -1 + j * step  # Вычисление координаты x
            y = 1 - i * step  # Вычисление координаты y
            if isinstance(matrix[i, j], np.ndarray):  # Если элемент - список (высота, цвет)
                height, color = matrix[i, j]  # Извлечение высоты и цвета
                height = height * scale_z  # Масштабирование высоты
                color = convert_hex_to_rgb(color)  # Преобразование цвета в RGB
            else:  # Если только высота
                height = matrix[i, j] * scale_z  # Масштабирование высоты
                color = (1.0, 1.0, 1.0)  # Цвет по умолчанию - белый

            vertices.append((x, y, height))  # Добавление вершины в список
            colors.append(color)  # Добавление цвета в список
    return np.array(vertices, dtype='float32'), np.array(colors, dtype='float32')  # Возврат массивов вершин и цветов


def create_edges(rows, cols):
    """Сгенерировать рёбра для сетки."""
    edges = []  # Инициализация списка для рёбер
    for i in range(rows):
        for j in range(cols - 1):
            edges.append((i * cols + j, i * cols + j + 1))  # Горизонтальные рёбра

    for j in range(cols):
        for i in range(rows - 1):
            edges.append((i * cols + j, (i + 1) * cols + j))  # Вертикальные рёбра
    return np.array(edges, dtype='uint32')  # Возврат массива рёбер


def draw_plane(vertices, colors, edges):
    """Нарисовать 3D плоскость с использованием OpenGL."""

    #Объявляем буферы
    vertex_buffer = glGenBuffers(1)  # Создание буфера для вершин
    color_buffer = glGenBuffers(1)  # Создание буфера для цветов
    edge_buffer = glGenBuffers(1)  # Создание буфера для ребер


    #Заполняем буферы
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)  # Привязка буфера вершин
    glVertexPointer(3, GL_FLOAT, 0, None)  # Указание формата вершин
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)  # Заполнение буфера вершин
    glEnableClientState(GL_VERTEX_ARRAY)  # Включение состояния массива вершин

    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)  # Привязка буфера цветов
    glColorPointer(3, GL_FLOAT, 0, None)  # Указание формата цветов
    glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)  # Заполнение буфера цветов
    glEnableClientState(GL_COLOR_ARRAY)  # Включение состояния массива цветов

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, edge_buffer)  # Привязка буфера ребер
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, edges.nbytes, edges, GL_STATIC_DRAW)  # Заполнение буфера ребер

    #Рендер линий
    glDrawElements(GL_LINES, len(edges) * 2, GL_UNSIGNED_INT, None)  # Рендеринг линий


    # Освобождение буферов
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    glDeleteBuffers(1, [vertex_buffer])
    glDeleteBuffers(1, [color_buffer])
    glDeleteBuffers(1, [edge_buffer])


def main_program(matrix):
    """Основная программа для инициализации pygame и OpenGL и запуска цикла рендеринга."""
    pygame.init()  # Инициализация pygame
    display = (800, 600)  # Размер окна
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | GL_DEPTH_BUFFER)  # Установка режима отображения
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)  # Установка перспективной проекции
    glEnable(GL_DEPTH_TEST)  # Включение теста глубины

    glTranslatef(0.0, 0.0, -10)  # Перемещение по оси Z

    heights = []  # Инициализация списка для высот
    for row in matrix:
        for el in row:
            heights.append(el[0] if isinstance(el, np.ndarray) else el)  # Сбор высот в список

    min_height = min(heights)  # Минимальная высота
    max_height = max(heights)  # Максимальная высота

    # Динамическое вычисление scale_z
    height_range = max_height - min_height  # Разница между максимальной и минимальной высотой
    scale_z = 0.5 / height_range if height_range != 0 else 1.0  # Масштабирование по высоте

    vertices, colors = create_vertices_and_colors(matrix, scale_z)  # Создание вершин и цветов
    edges = create_edges(matrix.shape[0], matrix.shape[1])  # Создание рёбер

    rot_x, rot_y = 0, 0  # Начальные углы поворота
    zoom = 5 # Начальное значение зума
    mouse_down = False  # Флаг для отслеживания нажатия кнопки мыши
    last_pos = None  # Последняя позиция мыши

    while True:  # Основной цикл программы
        for event in pygame.event.get():  # Обработка событий pygame
            if event.type == pygame.QUIT:  # Проверка на выход
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                mouse_down = True  # Установка флага нажатия
                last_pos = pygame.mouse.get_pos()  # Сохранение позиции мыши
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Если кнопка мыши отпущена
                mouse_down = False  # Сброс флага нажатия
            elif event.type == pygame.MOUSEMOTION and mouse_down:  # Если мышь перемещается с нажатой кнопкой
                current_pos = pygame.mouse.get_pos()  # Получение текущей позиции мыши
                dx, dy = current_pos[0] - last_pos[0], current_pos[1] - last_pos[1]  # Вычисление смещения
                rot_x += dy * 0.5  # Обновление угла вращения по оси X
                rot_y += dx * 0.5  # Обновление угла вращения по оси Y
                last_pos = current_pos  # Обновление последней позиции мыши
            elif event.type == pygame.MOUSEWHEEL:  # Если прокручивается колесо мыши
                zoom += event.y  * 0.1  # Изменение значения зума

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Очистка буферов цвета и глубины

        glPushMatrix()  # Сохранение текущей матрицы
        glTranslatef(0.0, 0.0, zoom)  # Применение трансляции по оси Z
        glRotatef(rot_x, 1, 0, 0)  # Применение вращения по оси X
        glRotatef(rot_y, 0, 1, 0)  # Применение вращения по оси Y



        draw_plane(vertices, colors, edges)  # Рендеринг плоскости



        glPopMatrix()  # Восстановление сохранённой матрицы

        pygame.display.flip()  # Обновление окна
        pygame.time.wait(10)  # Задержка для управления частотой кадров


if __name__ == "__main__":
    matrix = load_fdf_file('maps/42.fdf')
    main_program(matrix)  # Запуск основной программы

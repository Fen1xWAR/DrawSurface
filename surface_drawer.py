"""Основной файл реализующий отрисовку карту высот."""
import numpy as np
import pygame
import pygame.locals
import OpenGL.GL
import OpenGL.GLU


def load_fdf_file(filename: str):
    """Загрузка fdf файла."""
    try:
        with open(filename, 'rb') as file:
            content = file.read().decode('utf-8-sig')  # Чтение и удаление BOM
    except Exception as e:
        raise FileNotFoundError(f"Не удалось прочитать файл: {e}")

    lines = content.strip().splitlines()
    matrix = []  # Инициализация списка для хранения высот и цветов

    for line in lines:
        row = []  # Инициализация списка для хранения значений в строке
        for item in line.split():  # Разделить строку на элементы
            if ',' in item:  # Если элемент содержит запятую (высота и цвет)
                height, color = item.split(',')
                height = float(height.strip())  # Преобразование высоты в float
                color = color.strip()  # Удаление пробелов вокруг цвета
                # Добавление списка (высота, цвет) в строку
                row.append(np.array([height, color], dtype=object))
            else:  # Если элемент содержит только высоту
                row.append(float(item.strip()))
        matrix.append(row)  # Добавление строки в матрицу

    if len(set(map(len, matrix))) != 1:
        raise (ValueError
               ("Все строки во входных данных должны иметь одинаковую длину."))
    # Возврат матрицы в виде numpy массива
    return np.array(matrix, dtype=object)


def convert_hex_to_rgb(hex_color):
    """Конвертация 0x цвета в RGB кортеж."""
    # Приведение к нижнему регистру и удаление '0x'
    hex_color = hex_color.lower().replace('0x', '')
    r = int(hex_color[0:2] or '0', 16)  # Извлечение значения красного цвета
    g = int(hex_color[2:4] or '0', 16)  # Извлечение значения зеленого цвета
    b = int(hex_color[4:6] or '0', 16)  # Извлечение значения синего цвета

    return (r / 255.0, g / 255.0, b / 255.0)  # Возврат RGB кортежа


def create_vertices_and_colors(matrix, scale_z):
    """Генерация вершин и цветов на основе матрицы высот."""
    rows, cols = matrix.shape[0], matrix.shape[1]  # Получение размеров матрицы
    vertices = []  # Инициализация списка для вершин
    colors = []  # Инициализация списка для цветов
    # Вычисление шага для распределения вершин
    step = 2 / (max(rows, cols) - 1)

    for i in range(rows):
        for j in range(cols):
            x = -1 + j * step  # Вычисление координаты x
            y = 1 - i * step  # Вычисление координаты y
            # Если элемент - список (высота, цвет)
            if isinstance(matrix[i, j], np.ndarray):
                height, color = matrix[i, j]  # Извлечение высоты и цвета
                height = height * scale_z  # Масштабирование высоты
                color = convert_hex_to_rgb(color)  # Преобразование цвета в RGB
            else:  # Если только высота
                height = matrix[i, j] * scale_z  # Масштабирование высоты
                color = (1.0, 1.0, 1.0)  # Цвет по умолчанию - белый

            vertices.append((x, y, height))  # Добавление вершины в список
            colors.append(color)  # Добавление цвета в список
    # Возврат массивов вершин и цветов
    return (np.array(vertices, dtype='float32'),
            np.array(colors, dtype='float32'))


def create_edges(rows, cols):
    """Генерация рёбер для сетки."""
    edges = []  # Инициализация списка рёбер
    for i in range(rows):
        for j in range(cols - 1):
            # Горизонтальные рёбра
            edges.append((i * cols + j, i * cols + j + 1))

    for j in range(cols):
        for i in range(rows - 1):
            # Вертикальные рёбра
            edges.append((i * cols + j, (i + 1) * cols + j))
    return np.array(edges, dtype='uint32')  # Возврат массива рёбер


def draw_plane(vertices, colors, edges):
    """Рисуем 3D плоскость с использованием OpenGL."""
    vertex_buffer = OpenGL.GL.glGenBuffers(1)  # Создание буфера для вершин
    color_buffer = OpenGL.GL.glGenBuffers(1)  # Создание буфера для цветов
    edge_buffer = OpenGL.GL.glGenBuffers(1)  # Создание буфера для ребер

    # Привязка буфера вершин
    OpenGL.GL.glBindBuffer(OpenGL.GL.GL_ARRAY_BUFFER, vertex_buffer)
    # Указание формата вершин
    OpenGL.GL.glVertexPointer(3, OpenGL.GL.GL_FLOAT, 0, None)
    # Заполнение буфера вершин
    OpenGL.GL.glBufferData(OpenGL.GL.GL_ARRAY_BUFFER, vertices.nbytes,
                           vertices, OpenGL.GL.GL_STATIC_DRAW)
    # Включение состояния массива вершин
    OpenGL.GL.glEnableClientState(OpenGL.GL.GL_VERTEX_ARRAY)

    # Привязка буфера цветов
    OpenGL.GL.glBindBuffer(OpenGL.GL.GL_ARRAY_BUFFER, color_buffer)
    # Указание формата цветов
    OpenGL.GL.glColorPointer(3, OpenGL.GL.GL_FLOAT, 0, None)
    # Заполнение буфера цветов
    OpenGL.GL.glBufferData(OpenGL.GL.GL_ARRAY_BUFFER,
                           colors.nbytes, colors, OpenGL.GL.GL_STATIC_DRAW)
    # Включение состояния массива цветов
    OpenGL.GL.glEnableClientState(OpenGL.GL.GL_COLOR_ARRAY)

    # Привязка буфера ребер
    OpenGL.GL.glBindBuffer(OpenGL.GL.GL_ELEMENT_ARRAY_BUFFER, edge_buffer)
    # Заполнение буфера ребер
    OpenGL.GL.glBufferData(OpenGL.GL.GL_ELEMENT_ARRAY_BUFFER,
                           edges.nbytes, edges, OpenGL.GL.GL_STATIC_DRAW)
    # Рендеринг линий
    OpenGL.GL.glDrawElements(OpenGL.GL.GL_LINES, len(edges) * 2,
                             OpenGL.GL.GL_UNSIGNED_INT, None)

    OpenGL.GL.glBindBuffer(OpenGL.GL.GL_ARRAY_BUFFER, 0)
    OpenGL.GL.glBindBuffer(OpenGL.GL.GL_ELEMENT_ARRAY_BUFFER, 0)

    OpenGL.GL.glDeleteBuffers(1, [vertex_buffer])
    OpenGL.GL.glDeleteBuffers(1, [color_buffer])
    OpenGL.GL.glDeleteBuffers(1, [edge_buffer])


def main_program(matrix):
    """Основная функция отрисовки."""
    pygame.init()  # Инициализация pygame
    display = (800, 600)  # Размер окна
    pygame.display.set_caption('Surface Drawer')
    # Установка режима отображения
    (pygame.display.set_mode
     (display, pygame.DOUBLEBUF | pygame.OPENGL | OpenGL.GL.GL_DEPTH_BUFFER))
    # Установка перспективной проекции
    OpenGL.GLU.gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    # Включение теста глубины
    OpenGL.GL.glEnable(OpenGL.GL.GL_DEPTH_TEST)

    OpenGL.GL.glTranslatef(0.0, 0.0, -10)  # Перемещение по оси Z

    heights = [el[0] if isinstance(el, np.ndarray)
               else el for row in matrix for el in row]
    min_height = min(heights)  # Минимальная высота
    max_height = max(heights)  # Максимальная высота

    # Разница между максимальной и минимальной высотой
    height_range = max_height - min_height
    # Масштабирование по высоте
    scale_z = 0.5 / height_range if height_range != 0 else 1.0

    # Создание вершин и цветов
    vertices, colors = create_vertices_and_colors(matrix, scale_z)
    # Создание рёбер
    edges = create_edges(matrix.shape[0], matrix.shape[1])

    rot_x, rot_y = 0, 0  # Начальные углы поворота
    zoom = 5  # Начальное значение зума
    mouse_down = False  # Флаг для отслеживания нажатия кнопки мыши
    last_pos = None  # Последняя позиция мыши

    running = True  # Флаг для работы основного цикла рендеринга

    while running:
        for event in pygame.event.get():  # Цикл событий внутри окна рендер
            if event.type == pygame.QUIT:
                running = False
            # Нажатие ЛКМ
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                last_pos = pygame.mouse.get_pos()
            # Отжатие ЛКМ
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
            # Движение с зажатой ЛКМ
            elif event.type == pygame.MOUSEMOTION and mouse_down:
                current_pos = pygame.mouse.get_pos()
                dx, dy = (current_pos[0] - last_pos[0],
                          current_pos[1] - last_pos[1])
                rot_x += dy * 0.5
                rot_y += dx * 0.5
                last_pos = current_pos
            # Реакция на колесико мышки
            elif event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 0.1

        OpenGL.GL.glClear(OpenGL.GL.GL_COLOR_BUFFER_BIT |
                          OpenGL.GL.GL_DEPTH_BUFFER_BIT)

        OpenGL.GL.glPushMatrix()
        OpenGL.GL.glTranslatef(0.0, 0.0, zoom)
        OpenGL.GL.glRotatef(rot_x, 1, 0, 0)
        OpenGL.GL.glRotatef(rot_y, 0, 1, 0)

        draw_plane(vertices, colors, edges)

        OpenGL.GL.glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.display.quit()  # Закрытие окна рендеринга

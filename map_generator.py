"""Файл реализующий преобразование картинки в формат fdf."""
import os
from PIL import Image, UnidentifiedImageError
import numpy as np
import sys


def get_image(path):
    """Загрузка файла изображения."""
    while True:
        try:
            image = Image.open(path)
            break
        except FileNotFoundError:
            (print
             ('\033[31mFile not found.'
              ' Please enter a valid image path!\033[m'))
        except UnidentifiedImageError:
            (print
             ('\033[31mInvalid image format.'
              ' Please select a valid image file!\033[m'))
        except (KeyboardInterrupt):
            (print
             ('\033[33m\n\nKeyboardInterrupt: '
              'Program terminated by the user.\033[m'))
            sys.exit()
    return image


def parse_without_color(image):
    """Парсинг чб изображения."""
    image_matrix = np.array(image)
    grayscale_values\
        = np.mean(image_matrix, axis=2).astype(int)  # усредняем по каналам RGB
    relief_map = []

    color_map = {
        -1: '0x333E65',
        0: '0x626A87',
        1: '0x878EA2'
    }

    for row in grayscale_values:
        parsed_row\
            = [(f"{int(val)},"
                f"{color_map[0 if val == 0 else (1 if val > 0 else -1)]}"
                f"") for val in row]
        relief_map.append(parsed_row)

    return relief_map


def change_extension(file_path, new_extension):
    """Создание пути для исходного fdf."""
    base = os.path.splitext(os.path.basename(file_path))[0]
    return f"{base}.{new_extension}"


def main(path):
    """Функция для обработки изображения и создания карты рельефа."""
    image = get_image(path)

    image_matrix = np.array(image)
    use_default_color = False

    try:
        # Преобразуем изображение сразу для работы
        avg_matrix \
            = np.mean(image_matrix, axis=2)  # Среднее значение яркости пикселя
        height_matrix \
            = (np.round
               (np.log(avg_matrix + 1)).astype(int))
        # Применяем логарифм и округляем

        # Извлекаем цвета из каждого пикселя
        colors_matrix = image_matrix[:, :, :3]  # RGB каналы
        hex_colors \
            = (np.apply_along_axis
               (lambda rgb: f'0x{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}',
                2, colors_matrix))

        # Создаём карту рельефа
        relief_map = [[f'{h},{c}' for h, c in zip(height_row, color_row)]
                      for height_row, color_row in
                      zip(height_matrix, hex_colors)]

    except Exception as e:
        (print
         (f'\033[31mError processing image: {str(e)}.'
          f' Using default color scheme.\033[m'))
        use_default_color = True

    if use_default_color:
        relief_map = parse_without_color(image)  # Обработка чб

    # Сохранение карты рельефа
    fdf_path = change_extension(path, 'fdf')
    with open(fdf_path, 'w') as file:
        file.writelines(" ".join(row) + '\n' for row in relief_map)

    print(f"\033[32m\nThe map '{fdf_path}' was created successfully!!\033[m")
    return fdf_path

"""В этом файле реализован UI загрузки файлов."""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QMessageBox,
)
import map_generator
import surface_drawer


class MainWindow(QMainWindow):
    """Главное окно приложения для выбора карты."""

    def __init__(self):
        """Инициализирует главное окно и загружает файлы из указанной папки."""
        super().__init__()
        self.folder_path = "test_maps"
        self.init_ui()
        self.load_files()

    def init_ui(self):
        """Настраивает заголовок окна, его размер и компоновку."""
        self.setWindowTitle("Map selection")
        self.setGeometry(100, 100, 800, 400)

        # Основной виджет и компоновка
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Левая панель: кнопка для загрузки файла
        left_layout = QVBoxLayout()
        self.create_button("Загрузить файл", self.load_file, left_layout)
        layout.addLayout(left_layout)

        # Правая панель: список файлов и кнопка открытия
        right_layout = QVBoxLayout()
        self.file_list = QListWidget(self)
        right_layout.addWidget(self.file_list)
        self.create_button("Открыть", self.open_file, right_layout)
        layout.addLayout(right_layout)

    def create_button(self, text, callback, layout):
        """Создание кнопки с привязкой к обработчику."""
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def load_file(self):
        """Открытие окна для выбора изображения и обработка файла."""
        fname, _ = (QFileDialog.getOpenFileName
                    (self, 'Открыть файл', '',
                     "Изображения (*.jpg *.png *.jpeg)"))

        if fname:
            try:
                fdf_path = map_generator.main(fname)
                (surface_drawer.main_program
                 (surface_drawer.load_fdf_file(fdf_path)))
            except Exception as e:
                (QMessageBox.critical
                 (self, "Ошибка", f"Не удалось обработать файл: {e}"))

    def load_files(self):
        """Загрузка файлов из папки."""
        if not os.path.exists(self.folder_path):
            (QMessageBox.warning
             (self, "Ошибка", f"Папка {self.folder_path} не найдена."))
            return

        files = sorted(os.listdir(self.folder_path))
        if files:
            self.file_list.addItems(files)
        else:
            (QMessageBox.information
             (self, "Информация", "Папка пуста."))

    def open_file(self):
        """Открытие выбранного файла из списка."""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_name = (os.path.join
                         (self.folder_path, selected_item.text()))
            try:
                (surface_drawer.main_program
                 (surface_drawer.load_fdf_file(file_name)))
            except Exception as e:
                (QMessageBox.critical
                 (self, "Ошибка", f"Не удалось открыть файл: {e}"))
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите файл для открытия.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Loader")
        self.setGeometry(100, 100, 800, 400)

        # Основной виджет
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # В layout для главного окна (горизонтальный)
        self.layout = QHBoxLayout(self.central_widget)

        # Левая часть
        self.left_widget = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_widget)

        self.load_button = QPushButton("Загрузить файл", self)
        self.load_button.clicked.connect(self.load_file)
        self.left_layout.addWidget(self.load_button)

        self.layout.addWidget(self.left_widget)

        # Правая часть
        self.right_widget = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_widget)

        self.file_list = QListWidget(self)
        self.right_layout.addWidget(self.file_list)

        self.open_button = QPushButton("Открыть", self)
        self.open_button.clicked.connect(self.open_file)
        self.right_layout.addWidget(self.open_button)

        self.layout.addWidget(self.right_widget)

        self.load_files()

    def load_file(self):
        # Открытие диалогового окна для выбора изображения
        print("Loading file...")

        fname = QFileDialog.getOpenFileName(self, 'Открыть файл','c:\\', "Изображения (*.jpg *.png)")
        map_generator.main(fname[0])

    def load_files(self):
        # Загрузка файлов из папки test_maps
        folder_path = "test_maps"
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            self.file_list.addItems(files)
        else:
            QMessageBox.warning(self, "Ошибка", f"Папка {folder_path} не найдена.")

    def open_file(self):
        # Открытие выбранного файла
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_name = selected_item.text()

            QMessageBox.information(self, "Открыть файл", f"Файл: {file_name}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите файл для открытия.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QListWidget, QFileDialog,
                             QMessageBox, QTabWidget, QSpinBox, QFormLayout, QSizePolicy,
                             QFrame, QListWidgetItem, QDialog)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize


class SuccessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поздравление")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Поздравляем! Вы успешно прошли слайд-шоу!")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-size: 16px;")

        self.btn_close = QPushButton("Завершить")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                min-width: 100px;
            }
        """)

        layout.addWidget(self.label)
        layout.addWidget(self.btn_close)

        self.btn_close.clicked.connect(self.accept)


class ImageCodeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_selected = None

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # Стилизация для темного режима
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QPushButton {
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QListWidget {
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 14px;
                background-color: #353535;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 14px;
                background-color: #353535;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

        # Кнопки добавления/удаления изображений
        self.btn_add = QPushButton("➕ Добавить изображения")
        self.btn_add.setStyleSheet("background-color: #4CAF50;")
        self.btn_remove = QPushButton("❌ Удалить выбранное")
        self.btn_remove.setStyleSheet("background-color: #f44336;")
        self.btn_move_up = QPushButton("⬆ Вверх")
        self.btn_move_up.setStyleSheet("background-color: #2196F3;")
        self.btn_move_down = QPushButton("⬇ Вниз")
        self.btn_move_down.setStyleSheet("background-color: #2196F3;")

        # Настройка размеров кнопок
        self.btn_add.setMinimumHeight(40)
        self.btn_remove.setMinimumHeight(40)
        self.btn_move_up.setMinimumHeight(30)
        self.btn_move_down.setMinimumHeight(30)

        # Горизонтальная линия разделения
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #444;")

        # Список изображений с паролями
        self.list_images = QListWidget()
        self.list_images.setMinimumHeight(300)
        self.list_images.setSelectionMode(QListWidget.SingleSelection)

        # Горизонтальная линия разделения
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #444;")

        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)

        move_btn_layout = QHBoxLayout()
        move_btn_layout.addWidget(self.btn_move_up)
        move_btn_layout.addWidget(self.btn_move_down)

        # Форма для кода с рамкой
        code_frame = QFrame()
        code_frame.setFrameShape(QFrame.StyledPanel)
        code_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        code_layout = QVBoxLayout(code_frame)

        self.code_input = QLineEdit()
        self.code_input.setMinimumHeight(40)
        self.btn_save_code = QPushButton("💾 Сохранить код")
        self.btn_save_code.setStyleSheet("background-color: #FF9800;")
        self.btn_save_code.setMinimumHeight(40)

        code_layout.addWidget(QLabel("Код для перехода:"))
        code_layout.addWidget(self.code_input)
        code_layout.addWidget(self.btn_save_code)

        # Соединение сигналов
        self.btn_add.clicked.connect(self.add_images)
        self.btn_remove.clicked.connect(self.remove_image)
        self.btn_move_up.clicked.connect(self.move_up)
        self.btn_move_down.clicked.connect(self.move_down)
        self.btn_save_code.clicked.connect(self.save_code)
        self.list_images.currentItemChanged.connect(self.update_code_display)

        # Добавление виджетов в основной layout
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(line1)
        self.layout.addWidget(self.list_images)
        self.layout.addWidget(line2)
        self.layout.addLayout(move_btn_layout)
        self.layout.addWidget(code_frame)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        # Данные
        self.images = []
        self.codes = {}

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выберите изображения", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if files:
            # Всегда начинаем нумерацию с 1
            start_num = len(self.images) + 1

            for i, file in enumerate(files, start=start_num):
                self.images.append(file)
                self.codes[file] = str(i)
                self.add_image_to_list(file)

    def add_image_to_list(self, file_path):
        """Полная версия метода добавления изображения в список"""
        item = QListWidgetItem()
        self.list_images.addItem(item)
        self.setup_list_item(item, file_path)

        # Если это первый элемент, выделяем его
        if self.list_images.count() == 1:
            self.list_images.setCurrentRow(0)

    def setup_list_item(self, item, file_path):
        """Создает и настраивает виджет для элемента списка"""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Иконка изображения
        icon_label = QLabel()
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Название файла
        name_label = QLabel(os.path.basename(file_path))
        name_label.setStyleSheet("font-weight: bold;")

        # Пароль
        code_label = QLabel(f"Код: {self.codes.get(file_path, '')}")
        code_label.setStyleSheet("color: #FF9800;")

        layout.addWidget(icon_label)
        layout.addWidget(name_label, stretch=1)
        layout.addWidget(code_label)
        layout.setContentsMargins(5, 5, 5, 5)

        item.setSizeHint(widget.sizeHint())
        self.list_images.setItemWidget(item, widget)

        # Применяем стиль выделения, если элемент выбран
        if self.list_images.currentItem() == item:
            widget.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; border-radius: 3px;")

    def remove_image(self):
        if not self.images:  # Если список пуст
            return

        current_row = self.list_images.currentRow()
        if 0 <= current_row < len(self.images):
            try:
                # Получаем и удаляем изображение
                removed_image = self.images.pop(current_row)

                # Удаляем из интерфейса
                self.list_images.takeItem(current_row)

                # Удаляем код, если существует
                self.codes.pop(removed_image, None)

                # Обновляем отображение кода, если удалили текущий элемент
                if self.list_images.currentRow() >= 0:
                    self.update_code_display(self.list_images.currentItem(), None)
                else:
                    self.code_input.clear()

            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить изображение: {str(e)}")

    def move_up(self):
        current_row = self.list_images.currentRow()
        if current_row > 0:
            # Получаем текущий элемент и его данные
            current_item = self.list_images.item(current_row)
            current_widget = self.list_images.itemWidget(current_item)
            current_image = self.images[current_row]

            # Получаем предыдущий элемент
            prev_item = self.list_images.item(current_row - 1)
            prev_widget = self.list_images.itemWidget(prev_item)

            # Обновляем данные в списках
            self.images[current_row], self.images[current_row - 1] = (
                self.images[current_row - 1], self.images[current_row]
            )

            # Полностью пересоздаем виджеты для обоих элементов
            self.list_images.removeItemWidget(current_item)
            self.list_images.removeItemWidget(prev_item)

            # Создаем новые виджеты с обновленными данными
            self.setup_list_item(current_item, self.images[current_row])
            self.setup_list_item(prev_item, self.images[current_row - 1])

            # Восстанавливаем выделение
            self.list_images.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.list_images.currentRow()
        if current_row < self.list_images.count() - 1:
            # Получаем текущий элемент и его данные
            current_item = self.list_images.item(current_row)
            current_widget = self.list_images.itemWidget(current_item)
            current_image = self.images[current_row]

            # Получаем следующий элемент
            next_item = self.list_images.item(current_row + 1)
            next_widget = self.list_images.itemWidget(next_item)

            # Обновляем данные в списках
            self.images[current_row], self.images[current_row + 1] = (
                self.images[current_row + 1], self.images[current_row]
            )

            # Полностью пересоздаем виджеты для обоих элементов
            self.list_images.removeItemWidget(current_item)
            self.list_images.removeItemWidget(next_item)

            # Создаем новые виджеты с обновленными данными
            self.setup_list_item(current_item, self.images[current_row])
            self.setup_list_item(next_item, self.images[current_row + 1])

            # Восстанавливаем выделение
            self.list_images.setCurrentRow(current_row + 1)

    def update_code_display(self, current, previous):
        if previous is not None:
            prev_widget = self.list_images.itemWidget(previous)
            if prev_widget:
                prev_widget.setStyleSheet("")

        if current is not None:
            current_widget = self.list_images.itemWidget(current)
            if current_widget:
                current_widget.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; border-radius: 3px;")

            current_row = self.list_images.row(current)
            if current_row >= 0 and self.images:
                current_image = self.images[current_row]
                self.code_input.setText(self.codes.get(current_image, ""))

    def save_code(self):
        current_row = self.list_images.currentRow()
        if current_row >= 0 and self.images:
            current_image = self.images[current_row]
            new_code = self.code_input.text()
            self.codes[current_image] = new_code

            # Обновляем отображение кода в списке
            item = self.list_images.item(current_row)
            widget = self.list_images.itemWidget(item)
            code_label = widget.layout().itemAt(2).widget()
            code_label.setText(f"Код: {new_code}")

            QMessageBox.information(self, "Сохранено", "Код успешно сохранен!")

    def get_config(self):
        return {
            "images": self.images,
            "codes": self.codes
        }

    def set_config(self, config):
        self.images = config.get("images", [])
        self.codes = config.get("codes", {})

        self.list_images.clear()
        for image in self.images:
            self.add_image_to_list(image)


class SlideShowViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.initUI()
        self.current_index = 0
        self.slideshow_active = False

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # Стилизация для темного режима
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 16px;
                background-color: #353535;
                color: #e0e0e0;
            }
            QLabel#image_label {
                border: 2px solid #444;
                border-radius: 5px;
                background-color: #353535;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

        # Изображение
        self.image_label = QLabel()
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Горизонтальная линия разделения
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #444;")

        # Поле для ввода кода с рамкой
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.StyledPanel)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Введите код для перехода...")
        self.code_input.setMinimumHeight(50)

        input_layout.addWidget(QLabel("Код для перехода:"))
        input_layout.addWidget(self.code_input)

        # Горизонтальная линия разделения
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #444;")

        # Кнопки управления
        self.btn_prev = QPushButton("⏪ Назад")
        self.btn_prev.setStyleSheet("background-color: #2196F3;")
        self.btn_next = QPushButton("Вперед ⏩ (Enter)")
        self.btn_next.setStyleSheet("background-color: #4CAF50;")
        self.btn_close = QPushButton("🚪 Закрыть слайд-шоу")
        self.btn_close.setStyleSheet("background-color: #f44336;")

        # Увеличиваем шрифт кнопок
        font = QFont()
        font.setPointSize(12)
        self.btn_prev.setFont(font)
        self.btn_next.setFont(font)
        self.btn_close.setFont(font)

        # Расположение кнопок
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addWidget(self.btn_close)

        # Добавление виджетов в основной layout
        self.layout.addWidget(self.image_label, stretch=5)
        self.layout.addWidget(line1)
        self.layout.addWidget(input_frame, stretch=1)
        self.layout.addWidget(line2)
        self.layout.addLayout(btn_layout, stretch=1)

        self.setLayout(self.layout)

        # Соединение сигналов
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_next.clicked.connect(self.next_image)
        self.btn_close.clicked.connect(self.close_slideshow)
        self.code_input.returnPressed.connect(self.next_image)

    def start_slideshow(self, images, codes):
        if not images:
            QMessageBox.warning(self, "Ошибка", "Нет изображений для показа!")
            return

        self.images = images
        self.codes = codes
        self.current_index = 0
        self.slideshow_active = True
        self.show_image()

    def show_image(self):
        if not self.slideshow_active:
            return

        if self.images and self.current_index < len(self.images):
            pixmap = QPixmap(self.images[self.current_index])
            if not pixmap.isNull():
                self.image_label.setPixmap(
                    pixmap.scaled(
                        self.image_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
                self.code_input.clear()
                self.code_input.setFocus()
            else:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось загрузить изображение: {self.images[self.current_index]}")

    def prev_image(self):
        if not self.slideshow_active:
            return

        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def next_image(self):
        if not self.slideshow_active:
            QMessageBox.warning(self, "Ошибка", "Слайд-шоу не запущено!")
            return

        if not self.images:
            QMessageBox.warning(self, "Ошибка", "Нет изображений для показа!")
            return

        if self.current_index >= len(self.images) - 1:
            # Это последнее изображение - проверяем код
            current_image = self.images[self.current_index]
            required_code = self.codes.get(current_image, "")

            if self.code_input.text() == required_code:
                # Показываем диалог успешного завершения
                success_dialog = SuccessDialog(self)
                success_dialog.exec_()

                # Закрываем слайд-шоу и возвращаемся в редактор
                self.close_slideshow()
                self.parent_window.tabs.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный код!")
            return

        current_image = self.images[self.current_index]
        required_code = self.codes.get(current_image, "")

        if self.code_input.text() == required_code:
            self.current_index += 1
            self.show_image()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный код!")

    def close_slideshow(self):
        self.slideshow_active = False
        self.image_label.clear()
        self.code_input.clear()
        self.parent_window.tabs.setTabEnabled(0, True)
        self.parent_window.tabs.setCurrentIndex(0)
        self.parent_window.tabs.setTabEnabled(1, False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

    def initUI(self):
        self.setWindowTitle("Слайд-шоу с кодами")
        self.setGeometry(100, 100, 1000, 700)

        # Устанавливаем темную палитру для всего приложения
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)

        # Основной стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                background: #353535;
            }
            QTabBar::tab {
                padding: 8px 15px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                background: #353535;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background: #2d2d2d;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover {
                background: #3d3d3d;
            }
            QMessageBox {
                background-color: #2d2d2d;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                min-width: 300px;
            }
        """)

        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 10))

        # Редактор
        self.editor = ImageCodeEditor()

        # Просмотрщик
        self.viewer = SlideShowViewer(self)

        # Кнопка запуска слайд-шоу
        self.btn_start = QPushButton("▶️ Запустить слайд-шоу")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Кнопка сохранения конфигурации
        self.btn_save = QPushButton("💾 Сохранить конфигурацию")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)

        # Добавляем вкладки
        self.tabs.addTab(self.editor, "📝 Редактор")
        self.tabs.addTab(self.viewer, "🖼️ Просмотр")

        # Блокируем вкладку просмотра до запуска слайд-шоу
        self.tabs.setTabEnabled(1, False)

        # Горизонтальная линия разделения
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #444;")

        # Создаем layout для кнопок
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_save)
        btn_layout.setSpacing(20)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(line)
        main_layout.addLayout(btn_layout)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Центральный виджет
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Соединение сигналов
        self.btn_start.clicked.connect(self.start_slideshow)
        self.btn_save.clicked.connect(self.save_config)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def start_slideshow(self):
        config = self.editor.get_config()
        if not config["images"]:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одно изображение!")
            return

        self.viewer.start_slideshow(config["images"], config["codes"])
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)  # Переключаемся на вкладку просмотра
        self.tabs.setTabEnabled(0, False)

    def on_tab_changed(self, index):
        # Если пытаются перейти на вкладку просмотра без запуска слайд-шоу
        if index == 1 and not self.viewer.slideshow_active:
            QMessageBox.warning(self, "Ошибка", "Сначала запустите слайд-шоу!")
            self.tabs.setCurrentIndex(0)

    def save_config(self):
        config = self.editor.get_config()
        try:
            with open("config.json", "w") as f:
                json.dump(config, f)
            QMessageBox.information(self, "Сохранено", "Конфигурация успешно сохранена!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфигурацию: {str(e)}")

    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                self.editor.set_config(config)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить конфигурацию: {str(e)}")

    def resizeEvent(self, event):
        # При изменении размера окна обновляем изображение
        if self.tabs.currentIndex() == 1 and self.viewer.slideshow_active:
            self.viewer.show_image()
        super().resizeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QListWidget, QFileDialog,
                             QTabWidget, QSizePolicy,
                             QFrame, QListWidgetItem, QDialog, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint


class AnimatedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        # Основной виджет уведомления
        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #2d2d2d, stop:1 #1a1a1a);
                border-radius: 12px;
                border: 1px solid #444;
            }
        """)

        # Эффект тени
        self.shadow = QGraphicsDropShadowEffect(self.main_widget)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.main_widget.setGraphicsEffect(self.shadow)

        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Заголовок
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
                border-bottom: 1px solid #444;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Текст сообщения
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)

        # Кнопки
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 10, 0, 0)
        self.button_layout.setSpacing(10)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.message_label)
        self.layout.addLayout(self.button_layout)

        # Анимации
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.scale_anim = QPropertyAnimation(self.main_widget, b"geometry")
        self.scale_anim.setDuration(300)
        self.scale_anim.setEasingCurve(QEasingCurve.OutBack)

        self.setFixedSize(400, 200)

    def showEvent(self, event):
        # Центрируем относительно родительского окна
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

        # Начальное состояние для анимации
        start_rect = QRect(self.main_widget.geometry())
        start_rect.setWidth(10)
        start_rect.setHeight(10)
        start_rect.moveCenter(self.main_widget.geometry().center())

        self.scale_anim.setStartValue(start_rect)
        self.scale_anim.setEndValue(self.main_widget.geometry())

        # Запускаем анимации
        self.opacity_anim.start()
        self.scale_anim.start()

        super().showEvent(event)

    def resizeEvent(self, event):
        self.main_widget.resize(self.size())
        super().resizeEvent(event)

    def addButton(self, text, style=""):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px;
                {style}
            }}
            QPushButton:hover {{
                background: #4a4a4a;
            }}
        """)
        self.button_layout.addWidget(btn)
        return btn


class NotificationManager:
    @staticmethod
    def show_message(parent, title, message, buttons=None, icon=None):
        dialog = AnimatedDialog(parent)
        dialog.title_label.setText(title)
        dialog.message_label.setText(message)

        if buttons is None:
            buttons = [("OK", "background: #4CAF50;")]

        for btn_text, btn_style in buttons:
            btn = dialog.addButton(btn_text, btn_style)
            btn.clicked.connect(dialog.accept)

        result = dialog.exec_()
        return result


class SuccessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 200)

        # Основной виджет
        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #2d2d2d, stop:1 #1a1a1a);
                border-radius: 12px;
                border: 1px solid #444;
            }
        """)

        # Эффект тени
        shadow = QGraphicsDropShadowEffect(self.main_widget)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.main_widget.setGraphicsEffect(shadow)

        # Разметка
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        self.title_label = QLabel("Поздравление")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
                border-bottom: 1px solid #444;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Сообщение
        self.message_label = QLabel("Поздравляем! Вы успешно прошли слайд-шоу!")
        self.message_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)

        # Кнопка
        self.btn_close = QPushButton("Завершить")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                min-width: 100px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Добавляем элементы
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)

        # Анимации
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.scale_anim = QPropertyAnimation(self.main_widget, b"geometry")
        self.scale_anim.setDuration(400)
        self.scale_anim.setEasingCurve(QEasingCurve.OutBack)

        # Соединение сигналов
        self.btn_close.clicked.connect(self.accept)

    def showEvent(self, event):
        # Центрируем относительно родительского окна
        if self.parent():
            parent_center = self.parent().geometry().center()
            self.move(parent_center - QPoint(200, 100))  # 400x200 - размер уведомления

        # Начальное состояние для анимации
        start_rect = QRect(self.main_widget.geometry())
        start_rect.setWidth(10)
        start_rect.setHeight(10)
        start_rect.moveCenter(self.main_widget.geometry().center())

        self.scale_anim.setStartValue(start_rect)
        self.scale_anim.setEndValue(self.main_widget.geometry())

        # Запускаем анимации
        self.opacity_anim.start()
        self.scale_anim.start()

        super().showEvent(event)

    def resizeEvent(self, event):
        self.main_widget.resize(self.size())
        super().resizeEvent(event)


class ImageCodeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_selected = None

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)

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

        self.btn_add = QPushButton("➕ Добавить изображения")
        self.btn_add.setStyleSheet("background-color: #4CAF50;")
        self.btn_remove = QPushButton("❌ Удалить выбранное")
        self.btn_remove.setStyleSheet("background-color: #f44336;")
        self.btn_move_up = QPushButton("⬆ Вверх")
        self.btn_move_up.setStyleSheet("background-color: #2196F3;")
        self.btn_move_down = QPushButton("⬇ Вниз")
        self.btn_move_down.setStyleSheet("background-color: #2196F3;")

        self.btn_add.setMinimumHeight(40)
        self.btn_remove.setMinimumHeight(40)
        self.btn_move_up.setMinimumHeight(30)
        self.btn_move_down.setMinimumHeight(30)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #444;")

        self.list_images = QListWidget()
        self.list_images.setMinimumHeight(300)
        self.list_images.setSelectionMode(QListWidget.SingleSelection)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #444;")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)

        move_btn_layout = QHBoxLayout()
        move_btn_layout.addWidget(self.btn_move_up)
        move_btn_layout.addWidget(self.btn_move_down)

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

        self.btn_add.clicked.connect(self.add_images)
        self.btn_remove.clicked.connect(self.remove_image)
        self.btn_move_up.clicked.connect(self.move_up)
        self.btn_move_down.clicked.connect(self.move_down)
        self.btn_save_code.clicked.connect(self.save_code)
        self.list_images.currentItemChanged.connect(self.update_code_display)

        self.layout.addLayout(btn_layout)
        self.layout.addWidget(line1)
        self.layout.addWidget(self.list_images)
        self.layout.addWidget(line2)
        self.layout.addLayout(move_btn_layout)
        self.layout.addWidget(code_frame)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.images = []
        self.codes = {}

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выберите изображения", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if files:
            start_num = len(self.images) + 1

            for i, file in enumerate(files, start=start_num):
                self.images.append(file)
                self.codes[file] = str(i)
                self.add_image_to_list(file)

    def add_image_to_list(self, file_path):
        item = QListWidgetItem()
        self.list_images.addItem(item)
        self.setup_list_item(item, file_path)

        if self.list_images.count() == 1:
            self.list_images.setCurrentRow(0)

    def setup_list_item(self, item, file_path):
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        icon_label = QLabel()
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        name_label = QLabel(os.path.basename(file_path))
        name_label.setStyleSheet("font-weight: bold;")

        code_label = QLabel(f"Код: {self.codes.get(file_path, '')}")
        code_label.setStyleSheet("color: #FF9800;")

        layout.addWidget(icon_label)
        layout.addWidget(name_label, stretch=1)
        layout.addWidget(code_label)
        layout.setContentsMargins(5, 5, 5, 5)

        item.setSizeHint(widget.sizeHint())
        self.list_images.setItemWidget(item, widget)

        if self.list_images.currentItem() == item:
            widget.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; border-radius: 3px;")

    def remove_image(self):
        try:
            # Проверка наличия элементов
            if not self.images or self.list_images.count() == 0:
                NotificationManager.show_message(
                    self,
                    "Ошибка",
                    "Нет изображений для удаления!",
                    buttons=[("OK", "background: #f44336;")]
                )
                return

            current_row = self.list_images.currentRow()
            if current_row < 0 or current_row >= len(self.images):
                return

            # Блокируем сигналы во время обновления
            self.list_images.blockSignals(True)

            # Получаем данные перед удалением
            image_to_remove = self.images[current_row]

            # Удаляем из словаря кодов
            if image_to_remove in self.codes:
                del self.codes[image_to_remove]

            # Удаляем из списка изображений
            del self.images[current_row]

            # Удаляем из QListWidget
            item = self.list_images.takeItem(current_row)
            if item:
                item = None  # Явное освобождение памяти

            # Обновляем выбор
            new_count = self.list_images.count()
            if new_count > 0:
                new_row = min(current_row, new_count - 1)
                self.list_images.setCurrentRow(new_row)
                self.list_images.blockSignals(False)  # Разблокируем сигналы
                self.update_code_display(self.list_images.currentItem(), None)
            else:
                self.list_images.blockSignals(False)
                self.code_input.clear()

            # Принудительное обновление интерфейса
            QApplication.processEvents()

        except Exception as e:
            self.list_images.blockSignals(False)  # Всегда разблокируем сигналы
            import traceback
            traceback.print_exc()
            NotificationManager.show_message(
                self,
                "Ошибка",
                f"Ошибка при удалении: {str(e)}",
                buttons=[("OK", "background: #f44336;")]
            )

    def move_up(self):
        current_row = self.list_images.currentRow()
        if current_row > 0:
            current_item = self.list_images.item(current_row)
            current_widget = self.list_images.itemWidget(current_item)
            current_image = self.images[current_row]

            prev_item = self.list_images.item(current_row - 1)
            prev_widget = self.list_images.itemWidget(prev_item)

            self.images[current_row], self.images[current_row - 1] = (
                self.images[current_row - 1], self.images[current_row]
            )

            self.list_images.removeItemWidget(current_item)
            self.list_images.removeItemWidget(prev_item)

            self.setup_list_item(current_item, self.images[current_row])
            self.setup_list_item(prev_item, self.images[current_row - 1])

            self.list_images.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.list_images.currentRow()
        if current_row < self.list_images.count() - 1:
            current_item = self.list_images.item(current_row)
            current_widget = self.list_images.itemWidget(current_item)
            current_image = self.images[current_row]

            next_item = self.list_images.item(current_row + 1)
            next_widget = self.list_images.itemWidget(next_item)

            self.images[current_row], self.images[current_row + 1] = (
                self.images[current_row + 1], self.images[current_row]
            )

            self.list_images.removeItemWidget(current_item)
            self.list_images.removeItemWidget(next_item)

            self.setup_list_item(current_item, self.images[current_row])
            self.setup_list_item(next_item, self.images[current_row + 1])

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

            item = self.list_images.item(current_row)
            widget = self.list_images.itemWidget(item)
            code_label = widget.layout().itemAt(2).widget()
            code_label.setText(f"Код: {new_code}")

            NotificationManager.show_message(
                self,
                "Сохранено",
                "Код успешно сохранен!",
                buttons=[("OK", "background: #4CAF50;")]
            )

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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Изображение (максимально растягиваем)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("background-color: #353535;")
        self.layout.addWidget(self.image_label, stretch=10)

        # Нижняя панель с элементами управления
        bottom_panel = QWidget()
        bottom_panel.setStyleSheet("background-color: #2d2d2d;")
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(15, 10, 15, 10)
        bottom_layout.setSpacing(10)

        # Поле для ввода кода
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Введите код для перехода...")
        self.code_input.setStyleSheet("""
            QLineEdit {
                background-color: #353535;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        bottom_layout.addWidget(self.code_input)

        # Кнопки навигации
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        self.btn_prev = QPushButton("⏪ Назад")
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)

        self.btn_next = QPushButton("Вперед ⏩ (Enter)")
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.btn_close = QPushButton("🚪 Закрыть")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_close)
        bottom_layout.addLayout(nav_layout)

        self.layout.addWidget(bottom_panel)
        self.setLayout(self.layout)

        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_next.clicked.connect(self.next_image)
        self.btn_close.clicked.connect(self.close_slideshow)
        self.code_input.returnPressed.connect(self.next_image)

    def start_slideshow(self, images, codes):
        if not images:
            NotificationManager.show_message(
                self,
                "Ошибка",
                "Нет изображений для показа!",
                buttons=[("OK", "background: #f44336;")]
            )
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
                NotificationManager.show_message(
                    self,
                    "Ошибка",
                    f"Не удалось загрузить изображение: {self.images[self.current_index]}",
                    buttons=[("OK", "background: #f44336;")]
                )

    def prev_image(self):
        if not self.slideshow_active:
            return

        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def next_image(self):
        if not self.slideshow_active:
            NotificationManager.show_message(
                self,
                "Ошибка",
                "Слайд-шоу не запущено!",
                buttons=[("OK", "background: #f44336;")]
            )
            return

        if not self.images:
            NotificationManager.show_message(
                self,
                "Ошибка",
                "Нет изображений для показа!",
                buttons=[("OK", "background: #f44336;")]
            )
            return

        if self.current_index >= len(self.images) - 1:
            current_image = self.images[self.current_index]
            required_code = self.codes.get(current_image, "")

            if self.code_input.text() == required_code:
                success_dialog = SuccessDialog(self)
                success_dialog.exec_()
                self.close_slideshow()
                self.parent_window.tabs.setCurrentIndex(0)
            else:
                NotificationManager.show_message(
                    self,
                    "Ошибка",
                    "Неверный код!",
                    buttons=[("OK", "background: #f44336;")]
                )
            return

        current_image = self.images[self.current_index]
        required_code = self.codes.get(current_image, "")

        if self.code_input.text() == required_code:
            self.current_index += 1
            self.show_image()
        else:
            NotificationManager.show_message(
                self,
                "Ошибка",
                "Неверный код!",
                buttons=[("OK", "background: #f44336;")]
            )

    def close_slideshow(self):
        self.slideshow_active = False
        self.image_label.clear()
        self.code_input.clear()
        self.parent_window.tabs.setTabEnabled(0, True)
        self.parent_window.tabs.setCurrentIndex(0)
        self.parent_window.showNormal()

        # Показываем кнопки снова
        self.parent_window.btn_start.show()
        self.parent_window.btn_save.show()

        QTimer.singleShot(50, lambda: [
            self.parent_window.resize(1000, 700),
            self.parent_window.move(100, 100)
        ])
        self.parent_window.tabs.setTabEnabled(1, False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

    def initUI(self):
        self.setWindowTitle("Слайд-шоу с кодами")
        self.setGeometry(100, 100, 1000, 700)

        # Устанавливаем темную палитру
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

        # Стиль для всего приложения
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #e0e0e0;
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
            QStatusBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
        """)

        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 10))

        # Редактор
        self.editor = ImageCodeEditor()

        # Просмотрщик
        self.viewer = SlideShowViewer(self)

        # Добавляем вкладки
        self.tabs.addTab(self.editor, "📝 Редактор")
        self.tabs.addTab(self.viewer, "🖼️ Просмотр")

        # Блокируем вкладку просмотра до запуска слайд-шоу
        self.tabs.setTabEnabled(1, False)

        # Кнопки управления
        self.btn_start = QPushButton("▶️ Запустить слайд-шоу")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                min-width: 200px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.btn_save = QPushButton("💾 Сохранить конфигурацию")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                min-width: 200px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)

        # Горизонтальная линия разделения
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #444;")

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(line)

        # Layout для кнопок
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_save)
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
            NotificationManager.show_message(
                self,
                "Ошибка",
                "Добавьте хотя бы одно изображение!",
                buttons=[("OK", "background: #f44336;")]
            )
            return

        # Скрываем кнопки перед запуском
        self.btn_start.hide()
        self.btn_save.hide()

        self.viewer.start_slideshow(config["images"], config["codes"])
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)
        self.tabs.setTabEnabled(0, False)
        self.showFullScreen()

    def on_tab_changed(self, index):
        if index == 1 and not self.viewer.slideshow_active:
            NotificationManager.show_message(
                self,
                "Ошибка",
                "Сначала запустите слайд-шоу!",
                buttons=[("OK", "background: #f44336;")]
            )
            self.tabs.setCurrentIndex(0)

    def save_config(self):
        config = self.editor.get_config()
        try:
            with open("config.json", "w") as f:
                json.dump(config, f)
            NotificationManager.show_message(
                self,
                "Сохранено",
                "Конфигурация успешно сохранена!",
                buttons=[("OK", "background: #4CAF50;")]
            )
        except Exception as e:
            NotificationManager.show_message(
                self,
                "Ошибка",
                f"Не удалось сохранить конфигурацию: {str(e)}",
                buttons=[("OK", "background: #f44336;")]
            )

    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                self.editor.set_config(config)
        except Exception as e:
            NotificationManager.show_message(
                self,
                "Ошибка",
                f"Не удалось загрузить конфигурацию: {str(e)}",
                buttons=[("OK", "background: #f44336;")]
            )

    def resizeEvent(self, event):
        if self.tabs.currentIndex() == 1 and self.viewer.slideshow_active:
            self.viewer.show_image()
        super().resizeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Устанавливаем темную тему для всех диалогов
    app.setStyleSheet("""
        QDialog {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QToolTip {
            background-color: #353535;
            color: #e0e0e0;
            border: 1px solid #444;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

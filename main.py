import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QListWidget, QFileDialog,
                             QTabWidget, QSizePolicy,
                             QFrame, QListWidgetItem, QDialog, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QPointF


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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #1a0a1a, stop:1 #0a0a2a);
                border-radius: 12px;
                border: 2px solid #ff3355;
            }
        """)

        # Эффект тени
        self.shadow = QGraphicsDropShadowEffect(self.main_widget)
        self.shadow.setBlurRadius(25)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(255, 50, 50, 150))
        self.main_widget.setGraphicsEffect(self.shadow)

        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Заголовок
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
                border-bottom: 2px solid #ff3355;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Текст сообщения
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ff3355, stop:1 #cc0022);
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #ffffff;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px;
                {style}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ff5375, stop:1 #dd2042);
                border: 2px solid #ffffff;
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
            buttons = [("OK 👍", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3366ff, stop:1 #2244cc);")]

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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #1a0a1a, stop:1 #0a0a2a);
                border-radius: 12px;
                border: 2px solid #3366ff;
            }
        """)

        # Эффект тени
        shadow = QGraphicsDropShadowEffect(self.main_widget)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(50, 50, 255, 150))
        self.main_widget.setGraphicsEffect(shadow)

        # Разметка
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        self.title_label = QLabel("🎉 Поздравление 🎉")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
                border-bottom: 2px solid #3366ff;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Сообщение
        self.message_label = QLabel("Поздравляем! Вы успешно прошли слайд-шоу! 🏆")
        self.message_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)

        # Кнопка
        self.btn_close = QPushButton("Завершить 🚀")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #3366ff, stop:1 #2244cc);
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                min-width: 100px;
                border-radius: 5px;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #4488ff, stop:1 #3366dd);
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
            self.move(parent_center - QPoint(200, 100))

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
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QPushButton {
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QListWidget {
                border: 2px solid #3366ff;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                background-color: #1a0a1a;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #0a0a2a;
                border: 2px solid #ff3355;
                border-radius: 3px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3366ff;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                background-color: #1a0a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QFrame {
                color: #ff3355;
            }
        """)

        self.btn_add = QPushButton("➕ Добавить изображения")
        self.btn_add.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #3366ff, stop:1 #2244cc);
            color: white;
        """)
        self.btn_remove = QPushButton("❌ Удалить выбранное")
        self.btn_remove.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #ff3355, stop:1 #cc0022);
            color: white;
        """)
        self.btn_move_up = QPushButton("⬆ Вверх")
        self.btn_move_up.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #3366ff, stop:1 #2244cc);
            color: white;
        """)
        self.btn_move_down = QPushButton("⬇ Вниз")
        self.btn_move_down.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #3366ff, stop:1 #2244cc);
            color: white;
        """)

        self.btn_add.setMinimumHeight(40)
        self.btn_remove.setMinimumHeight(40)
        self.btn_move_up.setMinimumHeight(30)
        self.btn_move_down.setMinimumHeight(30)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #ff3355;")

        self.list_images = QListWidget()
        self.list_images.setMinimumHeight(300)
        self.list_images.setSelectionMode(QListWidget.SingleSelection)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #ff3355;")

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
                background-color: #1a0a1a;
                border: 2px solid #3366ff;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        code_layout = QVBoxLayout(code_frame)

        self.code_input = QLineEdit()
        self.code_input.setMinimumHeight(40)
        self.btn_save_code = QPushButton("💾 Сохранить код")
        self.btn_save_code.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #ff3355, stop:1 #cc0022);
            color: white;
        """)
        self.btn_save_code.setMinimumHeight(40)

        code_layout.addWidget(QLabel("🔑 Код для перехода (оставьте пустым для перехода без кода):"))
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
        name_label.setStyleSheet("font-weight: bold; color: #ffffff;")

        code_label = QLabel(f"🔓 Код: {self.codes.get(file_path, '')}")
        code_label.setStyleSheet("color: #ff3355; font-weight: bold;")

        layout.addWidget(icon_label)
        layout.addWidget(name_label, stretch=1)
        layout.addWidget(code_label)
        layout.setContentsMargins(5, 5, 5, 5)

        item.setSizeHint(widget.sizeHint())
        self.list_images.setItemWidget(item, widget)

        if self.list_images.currentItem() == item:
            widget.setStyleSheet("background-color: #0a0a2a; border: 2px solid #ff3355; border-radius: 3px;")

    def remove_image(self):
        try:
            if not self.images or self.list_images.count() == 0:
                NotificationManager.show_message(
                    self,
                    "Ошибка 😕",
                    "Нет изображений для удаления!",
                    buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
                )
                return

            current_row = self.list_images.currentRow()
            if current_row < 0 or current_row >= len(self.images):
                return

            self.list_images.blockSignals(True)
            image_to_remove = self.images[current_row]

            if image_to_remove in self.codes:
                del self.codes[image_to_remove]

            del self.images[current_row]
            item = self.list_images.takeItem(current_row)
            if item:
                item = None

            new_count = self.list_images.count()
            if new_count > 0:
                new_row = min(current_row, new_count - 1)
                self.list_images.setCurrentRow(new_row)
                self.list_images.blockSignals(False)
                self.update_code_display(self.list_images.currentItem(), None)
            else:
                self.list_images.blockSignals(False)
                self.code_input.clear()

            QApplication.processEvents()

        except Exception as e:
            self.list_images.blockSignals(False)
            import traceback
            traceback.print_exc()
            NotificationManager.show_message(
                self,
                "Ошибка 😨",
                f"Ошибка при удалении: {str(e)}",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
                current_widget.setStyleSheet("background-color: #0a0a2a; border: 2px solid #ff3355; border-radius: 3px;")

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
            code_label.setText(f"🔓 Код: {new_code}")

            NotificationManager.show_message(
                self,
                "Сохранено ✅",
                "Код успешно сохранен!",
                buttons=[("OK 👍", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3366ff, stop:1 #2244cc);")]
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

        # Изображение
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("background-color: #0a0a0a;")
        self.layout.addWidget(self.image_label, stretch=10)

        # Нижняя панель с элементами управления
        bottom_panel = QWidget()
        bottom_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #1a0a1a, stop:1 #0a0a2a);
                border-top: 2px solid #ff3355;
            }
        """)
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(20, 20, 20, 20)
        bottom_layout.setSpacing(25)

        # Увеличенное поле для ввода кода
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("🔑 ВВЕДИТЕ КОД ДЛЯ ПЕРЕХОДА...")
        self.code_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a0a1a;
                color: #ffffff;
                border: 3px solid #3366ff;
                border-radius: 10px;
                padding: 25px;
                font-size: 28px;
                font-weight: bold;
                min-height: 80px;
                property-alignment: AlignCenter;
            }
        """)
        # Устанавливаем фиксированную высоту (примерно в 3 раза больше исходной)
        self.code_input.setFixedHeight(100)
        bottom_layout.addWidget(self.code_input)

        # Кнопки навигации (остаются без изменений)
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(15)

        self.btn_prev = QPushButton("⏪ Назад")
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #3366ff, stop:1 #2244cc);
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #ffffff;
                font-size: 18px;
                min-width: 120px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #4488ff, stop:1 #3366dd);
            }
        """)

        self.btn_next = QPushButton("Вперед ⏩ (Enter)")
        self.btn_next.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #3366ff, stop:0.5 #cc00ff, stop:1 #ff3355);
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #ffffff;
                font-size: 18px;
                min-width: 180px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #4488ff, stop:0.5 #dd22ff, stop:1 #ff5375);
            }
        """)

        self.btn_close = QPushButton("🚪 Закрыть")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ff3355, stop:1 #cc0022);
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #ffffff;
                font-size: 18px;
                min-width: 120px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ff5375, stop:1 #dd2042);
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
                "Ошибка 😕",
                "Нет изображений для показа!",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
                    "Ошибка 😨",
                    f"Не удалось загрузить изображение: {self.images[self.current_index]}",
                    buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
                "Ошибка 😕",
                "Слайд-шоу не запущено!",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
            )
            return

        if not self.images:
            NotificationManager.show_message(
                self,
                "Ошибка 😕",
                "Нет изображений для показа!",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
                    "Ошибка ❌",
                    "Неверный код!",
                    buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
                "Ошибка ❌",
                "Неверный код!",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
            )

    def close_slideshow(self):
        self.slideshow_active = False
        self.image_label.clear()
        self.code_input.clear()
        self.parent_window.tabs.setTabEnabled(0, True)
        self.parent_window.tabs.setCurrentIndex(0)
        self.parent_window.showNormal()

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
        self.setWindowTitle("🎮 Игровое слайд-шоу с кодами 🎮")
        self.setGeometry(100, 100, 1000, 700)

        # Устанавливаем темную палитру с градиентом
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(10, 10, 10))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(26, 10, 26))
        dark_palette.setColor(QPalette.AlternateBase, QColor(10, 10, 42))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(26, 10, 26))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(51, 102, 255))
        dark_palette.setColor(QPalette.Highlight, QColor(51, 102, 255))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(dark_palette)

        # Стиль для всего приложения
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #0a0a0a, stop:1 #050515);
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #3366ff;
                border-radius: 5px;
                padding: 5px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #1a0a1a, stop:1 #0a0a2a);
            }
            QTabBar::tab {
                padding: 8px 15px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #1a0a1a, stop:1 #0a0a2a);
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #3366ff;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #2a1a2a, stop:1 #1a1a3a);
                border-bottom: 2px solid #ff3355;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #2a1a2a, stop:1 #1a1a3a);
            }
            QStatusBar {
                background-color: #0a0a0a;
                color: #ffffff;
                font-weight: bold;
            }
        """)

        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 10, QFont.Bold))

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
        self.btn_start = QPushButton("🎮 Запустить слайд-шоу 🎮")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ff3355, stop:1 #cc0022);
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                min-width: 200px;
                border-radius: 5px;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ff5375, stop:1 #dd2042);
            }
        """)

        self.btn_save = QPushButton("💾 Сохранить конфигурацию")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #3366ff, stop:1 #2244cc);
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                min-width: 200px;
                border-radius: 5px;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #4488ff, stop:1 #3366dd);
            }
        """)

        # Горизонтальная линия разделения
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #ff3355;")

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
                self.editor,
                "Ошибка 😕",
                "Добавьте хотя бы одно изображение!",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
                self.editor,
                "Ошибка 😕",
                "Сначала запустите слайд-шоу!",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
            )
            self.tabs.setCurrentIndex(0)

    def save_config(self):
        config = self.editor.get_config()
        try:
            with open("config.json", "w") as f:
                json.dump(config, f)
            NotificationManager.show_message(
                self.editor,
                "Сохранено ✅",
                "Конфигурация успешно сохранена!",
                buttons=[("OK 👍", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3366ff, stop:1 #2244cc);")]
            )
        except Exception as e:
            NotificationManager.show_message(
                self.editor,
                "Ошибка 😨",
                f"Не удалось сохранить конфигурацию: {str(e)}",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
            )

    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                self.editor.set_config(config)
        except Exception as e:
            NotificationManager.show_message(
                self.editor,
                "Ошибка 😨",
                f"Не удалось загрузить конфигурацию: {str(e)}",
                buttons=[("OK 👌", "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3355, stop:1 #cc0022);")]
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
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #0a0a0a, stop:1 #050515);
            color: #ffffff;
        }
        QToolTip {
            background-color: #1a0a1a;
            color: #ffffff;
            border: 2px solid #ff3355;
            font-weight: bold;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

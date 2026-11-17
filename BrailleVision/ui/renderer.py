
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QFont, QFontMetricsF, QPainter, QColor
from PySide6.QtCore import Qt, Signal


class BrailleRenderer(QWidget):
    columns_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.setMinimumSize(0, 0)

        self.font = QFont("Consolas")
        self.font.setPixelSize(10)

        self.source_width = 0
        self.source_height = 0
        self.columns = 120

        self.mask = None
        self.colors = None

    def set_source_size(self, width, height):
        self.source_width = width
        self.source_height = height
        self.update_columns()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_columns()

    def update_columns(self):
        if not self.source_width or not self.source_height:
            return

        metrics = QFontMetricsF(self.font)

        char_width = max(
            1, metrics.horizontalAdvance("⣿")
        )
        char_height = max(1, metrics.lineSpacing())

        available_width = max(1, self.width() - 16)
        available_height = max(1, self.height() - 16)

        width_columns = int(
            available_width / char_width
        )

        row_ratio = (
            0.7 * self.source_height / self.source_width
        )

        height_columns = int(
            available_height / (char_height * row_ratio)
        )

        new_columns = max(
            20,
            min(width_columns, height_columns, 200)
        )

        if new_columns != self.columns:
            self.columns = new_columns
            self.columns_changed.emit(new_columns)

    def render(self, data):
        if data is None:
            return

        self.mask, self.colors = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(
            self.rect(),
            QColor(0, 0, 0)
        )

        if self.mask is None or self.colors is None:
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(self.font)
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "BrailleVision"
            )
            return

        painter.setFont(self.font)

        metrics = QFontMetricsF(self.font)

        char_width = metrics.horizontalAdvance("⣿")
        line_height = metrics.lineSpacing()

        rows, columns = self.mask.shape

        total_width = char_width * columns
        total_height = line_height * rows

        start_x = (self.width() - total_width) / 2
        start_y = (self.height() - total_height) / 2

        baseline_offset = metrics.ascent()

        # Vẽ từng ký tự với màu RGB riêng
        for y in range(rows):
            baseline = int(
                start_y + y * line_height + baseline_offset
            )

            x_pos = start_x

            for x in range(columns):
                value = int(self.mask[y, x])
                r, g, b = map(
                    int, self.colors[y, x]
                )

                painter.setPen(QColor(r, g, b))

                char = chr(0x2800 + value)

                painter.drawText(
                    int(x_pos),
                    baseline,
                    char
                )

                x_pos += char_width

        painter.end()

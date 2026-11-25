from PyQt6.QtCore import QRect, QSize, QPoint, Qt
from PyQt6.QtWidgets import (
    QLayout, QSizePolicy
)


class ColumnLayout(QLayout):
    def __init__(self, parent=None, spacing=-1):
        super().__init__(parent)
        self.setSpacing(spacing)
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, test_only=False)

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom(),
        )
        return size

    def sizeHint(self):
        return self.minimumSize()

    def do_layout(self, rect, test_only):
        # gets available rectangle for doing things
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        # current cursor positions
        cursor_x = effective_rect.x()
        cursor_y = effective_rect.y()
        # width of widest widget in row
        delta_y = 0
        spacing = self.spacing()

        for item in self._items:
            widget = item.widget()
            # set margins of the widgets
            space_x = space_y = spacing
            if widget is not None and spacing < 0:
                style = widget.style()

                control_type = item.controlType()
                space_x = style.layoutSpacing(
                    control_type, control_type, Qt.Orientation.Horizontal
                )
                space_y = style.layoutSpacing(
                    control_type, control_type, Qt.Orientation.Vertical
                )

            next_x = cursor_x + item.sizeHint().width() + space_x
            # checks if the length goes over
            if next_x - space_x > effective_rect.right() and delta_y > 0:
                cursor_x = effective_rect.x()
                cursor_y += delta_y + space_y
                next_x = cursor_x + item.sizeHint().width() + space_x
                delta_y = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(cursor_x, cursor_y), item.sizeHint()))

            cursor_x = next_x
            delta_y = max(delta_y, item.sizeHint().height())

        return cursor_y + delta_y - rect.y() + bottom
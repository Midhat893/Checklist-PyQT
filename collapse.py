# Add this to a new file, e.g., collapsible_groupbox.py
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class CollapsibleGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.content_widget)
        self.setLayout(self.main_layout)
        self.collapsed = True
        self.content_widget.setVisible(False)  # Collapsed by default

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)

    def mousePressEvent(self, event):
        if event.position().y() < 30:  # Click on title bar
            self.toggle()
        super().mousePressEvent(event)

    def toggle(self):
        self.collapsed = not self.collapsed
        self.content_widget.setVisible(not self.collapsed)
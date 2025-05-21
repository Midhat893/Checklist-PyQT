from PyQt6.QtWidgets import QWidget, QVBoxLayout
from main import ChecklistProcessor


class Placement_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = ChecklistProcessor(
            self,
            "PLACEMENT",
            "place_relay",
            "place_checkbox",
            "place_na_checklist",
            "place_download"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.processor)
        self.setLayout(layout)
     
    def load_checklist(self, file_path):
        return self.processor.process_checklist(file_path)

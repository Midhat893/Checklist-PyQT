from PyQt6.QtWidgets import QWidget, QVBoxLayout
from main import ChecklistProcessor


class Power_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = ChecklistProcessor(
            self,
            "POWER PLANES",
            "power_relay",
            "power_checkbox",
            "power_na_checklist",
            "power_download"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.processor)
        self.setLayout(layout)
     
    def load_checklist(self, file_path):
        return self.processor.process_checklist(file_path)

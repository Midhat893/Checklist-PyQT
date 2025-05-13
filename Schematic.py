from PyQt6.QtWidgets import QWidget, QVBoxLayout
from main import ChecklistProcessor

class Schematic_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = ChecklistProcessor(
            self,
            "SCHEMATIC",
            "Sch_relay",
            "sch_checkbox",
            "sch_na_checkbox",
            "sch_download"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.processor)
        self.setLayout(layout)
        
    def load_checklist(self, file_path):
        return self.processor.process_checklist(file_path)
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from main import ChecklistProcessor

class FAB_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = ChecklistProcessor(
            self,
            "FABRICATION",
            "fab_relay",
            "fab_checkbox",
            "fab_na_checkbox",
            "fab_download"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.processor)
        self.setLayout(layout)
        
    def load_checklist(self, file_path):
        return self.processor.process_checklist(file_path)
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from main import ChecklistProcessor


class BOM_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = ChecklistProcessor(
            self,
            "BOM",
            "bom_relay",
            "bom_checkbox",
            "bom_na_checklist",
            "bom_download"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.processor)
        self.setLayout(layout)
     
    def load_checklist(self, file_path):
        return self.processor.process_checklist(file_path)

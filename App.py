import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QLabel, QLineEdit, QFileDialog,
                            QPushButton)
from PyQt6.QtGui import QIcon
from Schematic import Schematic_Tab
from BOM import BOM_Tab

class ChecklistApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧾 Checklist Auto-Filter")
        self.setGeometry(100, 100, 1000, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.welcome_tab = QWidget()
        self.schematic_tab = Schematic_Tab()
        self.bom_tab = BOM_Tab()
        
        self.tabs.addTab(self.welcome_tab, "Welcome Page")
        self.tabs.addTab(self.schematic_tab, "SCHEMATIC")
        self.tabs.addTab(self.bom_tab, "BOM")
        
        # Setup welcome tab
        self.setup_welcome_tab()
        
    def setup_welcome_tab(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("CHECKLIST FOR DESIGN AND QA")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # File upload
        self.upload_btn = QPushButton("Upload your checklist (Excel file)")
        self.upload_btn.clicked.connect(self.handle_file_upload)
        layout.addWidget(self.upload_btn)
        
        # Designer name
        self.name_label = QLabel("Designer Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        self.dark_mode_enabled = False
        self.toggle_dark_mode_btn = QPushButton("Toggle Dark Mode")
        self.toggle_dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.toggle_dark_mode_btn)
        
        self.welcome_tab.setLayout(layout)
        
    def handle_file_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Excel File",
            "",
            "Excel Files (*.xlsm *.xlsx)"
        )
        
        if file_path:
            # Load file in both tabs
            if not self.schematic_tab.load_checklist(file_path):
                return
            if not self.bom_tab.load_checklist(file_path):
                return
            self.tabs.setCurrentIndex(1)  # Switch to Schematic tab
    
    def apply_qss(self, qss_file):
        try:
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load QSS: {e}")

    def toggle_dark_mode(self):
        if self.dark_mode_enabled:
            self.apply_qss("light-mode.qss")
            self.toggle_dark_mode_btn.setText("Enable Dark Mode")
        else:
            self.apply_qss("dark-mode.qss")
            self.toggle_dark_mode_btn.setText("Disable Dark Mode")
        self.dark_mode_enabled = not self.dark_mode_enabled


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("light-mode.qss", "r") as file:
        app.setStyleSheet(file.read())
    window = ChecklistApp()
    window.show()
    sys.exit(app.exec())
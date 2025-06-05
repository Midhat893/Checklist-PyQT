import pandas as pd
import re
from io import BytesIO
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QGroupBox, QScrollArea, QComboBox, QLabel,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from collapse import CollapsibleGroupBox


class ChecklistProcessor(QWidget):
    def __init__(self, parent_widget, page_name, relay_key, desc_key, na_key, download_key):
        super().__init__(parent_widget)
        self.parent = parent_widget
        self.page_name = page_name
        self.relay_key = relay_key
        self.desc_key = desc_key
        self.na_key = na_key
        self.download_key = download_key
        self.checkbox_states = {}
        self.df = None

        self.customers = ["Intel", "Xilinx", "AMD", "Nvidia", "Hi-Silicon", "Advantest", "Mellanox", "Yamaichi"]
        self.testers = ["93K", "T2K", "Ultraflex"]

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.project_combo = QComboBox()
        self.project_combo.addItem("All")
        self.project_combo.currentTextChanged.connect(self.update_ui)
        self.project_label = QLabel("Select Project Type:")

        self.tester_combo = QComboBox()
        self.tester_combo.addItem("All")
        self.tester_combo.currentTextChanged.connect(self.update_ui)
        self.tester_label = QLabel("Select Tester Type:")

        self.relay_checkbox = QCheckBox("Does your design use relays")
        self.relay_checkbox.setObjectName(self.relay_key)
        self.relay_checkbox.stateChanged.connect(self.update_ui)

        self.layout.addWidget(self.project_label)
        self.layout.addWidget(self.project_combo)
        self.layout.addWidget(self.tester_label)
        self.layout.addWidget(self.tester_combo)
        self.layout.addWidget(self.relay_checkbox)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.download_btn = QPushButton("📥 Download Filtered Checklist")
        self.download_btn.setObjectName(self.download_key)
        self.download_btn.clicked.connect(self.download_checklist)
        self.layout.addWidget(self.download_btn)

    def get_base_serial(self, serial):
        match = re.match(r'^(\d+)', str(serial))
        return match.group(1) if match else str(serial)

    #A little change from the original code
    def is_relay_related(self, description):
        description = str(description).lower()
        ignore_patterns = [r'and/or.*?\b{}']
        for pattern in ignore_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return False
        return 'relay' in description

    def extract_customers(self, description):
        description = str(description).lower()
        result = []
        ignore_phrases = [
            r'for reference.*?\b{}',
            r'for e.g..*?\b{}',
            r'for example.*?\b{}',
            r'QA Only.*?\b{}'
            ]
        for cust in self.customers:
            cust_lower = cust.lower()
            if any(re.search(phrase.format(cust_lower), description) for phrase in ignore_phrases):
                continue
            if re.search(rf'\b{cust_lower}\b', description, re.IGNORECASE):
                result.append(cust)
        return result

    def extract_testers(self, description):
        description = str(description).lower()
        result = []
        ignore_phrases =[
            r'for reference.*?\b{}',
            r'for e.g..*?\b{}',
            r'For example.*?\b{}'
            ]
        for tester in self.testers:
            tester_lower = tester.lower()
            if any(re.search(phrase.format(tester_lower), description) for phrase in ignore_phrases):
                continue
            if re.search(rf'\b{tester_lower}\b', description, re.IGNORECASE):
                    result.append(tester)
        return result

    def process_checklist(self, file_path):
        try:
            self.df = pd.read_excel(file_path, sheet_name=self.page_name, usecols="A,B,D,E,F", skiprows=1)
            required_cols = ["S.No", "Description", "D1"]
            if not all(col in self.df.columns for col in required_cols):
                QMessageBox.critical(self.parent, "Error", "Excel must contain 'S.No', 'Description' and 'D1' columns.")
                return False
            self.prepare_data()
            self.update_ui()
            return True
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to process file: {str(e)}")
            return False

    def prepare_data(self):
        self.df["Base_SNo"] = self.df["S.No"].apply(self.get_base_serial)
        self.df["Applies_To_Extracted"] = self.df["Description"].apply(self.extract_customers)
        self.df["Applies_To_ExtractedTester"] = self.df["Description"].apply(self.extract_testers)

        current_heading = self.page_name
        section_headings = []
        for _, row in self.df.iterrows():
            sno = str(row["S.No"]).strip()
            desc = str(row["Description"]).strip() if not pd.isna(row["Description"]) else ""
            if not sno or sno.lower() == "nan":
                current_heading = desc
            section_headings.append(current_heading)
        self.df["Section_Heading"] = section_headings

        self.project_combo.clear()
        self.project_combo.addItem("All")
        all_projects = sorted(set(c for sub in self.df["Applies_To_Extracted"] for c in sub))
        self.project_combo.addItems(all_projects)

        self.tester_combo.clear()
        self.tester_combo.addItem("All")
        all_testers = sorted(set(t for sub in self.df["Applies_To_ExtractedTester"] for t in sub))
        self.tester_combo.addItems(all_testers)

    def get_valid_sections(self, selected_project, selected_tester):
        if "Section_Heading" not in self.df.columns:
            return self.page_name
        valid_sections = set()
        for heading in self.df["Section_Heading"].unique():
            if not heading:
                continue
            customers = self.extract_customers(heading)
            testers = self.extract_testers(heading)
            if (selected_project in customers or
                selected_tester in testers or
                (not customers and not testers)):
                valid_sections.add(heading)
        return valid_sections

    def get_relevant_bases(self, valid_sections, selected_project, selected_tester):
        relevant_bases = set()
        for _, row in self.df.iterrows():
            heading = row["Section_Heading"]
            base = row["Base_SNo"]
            sno = str(row["S.No"]).strip()
            is_main = sno == base
            if not is_main or heading not in valid_sections:
                continue
            applies = row["Applies_To_Extracted"]
            testers = row["Applies_To_ExtractedTester"]
            desc = str(row["Description"]).lower()
            is_generic = not applies and not testers and not re.search(r'qa only', desc)
            if (selected_project in applies or selected_project == "All" or
                selected_tester in testers or selected_tester == "All" or
                is_generic):
                relevant_bases.add((heading, base))
        return relevant_bases

    def update_ui(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        if self.df is None:
            return

        selected_project = self.project_combo.currentText()
        selected_tester = self.tester_combo.currentText()
        uses_relays = self.relay_checkbox.isChecked()

        valid_sections = self.get_valid_sections(selected_project, selected_tester)
        relevant_bases = self.get_relevant_bases(valid_sections, selected_project, selected_tester)

        for heading, group in self.df.groupby("Section_Heading", sort=False):
            if heading not in valid_sections:
                continue

            points = group[group["S.No"].notna() &
                           (~group["S.No"].astype(str).str.strip().str.lower().isin(["", "nan"]))]

            if points.empty:
                continue

            group_box = CollapsibleGroupBox(heading)
            for idx, row in points.iterrows():
                base = row["Base_SNo"]
                if (heading, base) not in relevant_bases:
                    continue
                desc = str(row["Description"]).strip()
                if not desc or (not uses_relays and self.is_relay_related(desc)):
                    continue

                item_widget = QWidget()
                item_layout = QHBoxLayout()

                desc_checkbox = QCheckBox()
                desc_checkbox.setObjectName(f"{self.desc_key}_{idx}")

                desc_label = QLabel(desc)
                desc_label.setWordWrap(True)
                desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

                na_checkbox = QCheckBox("NA")
                na_checkbox.setObjectName(f"{self.na_key}_{idx}")

                item_layout.addWidget(desc_checkbox, alignment=Qt.AlignmentFlag.AlignTop)
                item_layout.addWidget(desc_label, stretch=5)
                item_layout.addWidget(na_checkbox, alignment=Qt.AlignmentFlag.AlignTop)

                desc_checkbox.stateChanged.connect(
                    lambda state, idx=idx: self.update_checkbox_state(state, idx, "Checked"))
                na_checkbox.stateChanged.connect(
                    lambda state, idx=idx: self.update_checkbox_state(state, idx, "NA"))

                desc_checkbox.toggled.connect(lambda checked, na=na_checkbox: na.setChecked(False) if checked else None)
                na_checkbox.toggled.connect(lambda checked, desc=desc_checkbox: desc.setChecked(False) if checked else None)

                item_widget.setLayout(item_layout)
                group_box.addWidget(item_widget)

            self.scroll_layout.addWidget(group_box)

    def update_checkbox_state(self, state, idx, value):
        if self.df is not None and idx in self.df.index:
            if state == Qt.CheckState.Checked.value:
                self.df.at[idx, "D1"] = value
            else:
                self.df.at[idx, "D1"] = ""

    def download_checklist(self):
        if self.df is None:
            QMessageBox.warning(self.parent, "Warning", "No checklist data to download!")
            return

        filtered_df = self.df.drop(columns=[
            "Applies_To_Extracted", "Applies_To_ExtractedTester",
            "Base_SNo", "Section_Heading"
        ])

        output = BytesIO()
        filtered_df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        filename, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save Checklist",
            f"Checklist_{self.project_combo.currentText()}_AutoNA.xlsx",
            "Excel Files (*.xlsx)"
        )

        if filename:
            try:
                with open(filename, 'wb') as f:
                    f.write(output.getvalue())
                QMessageBox.information(self.parent, "Success", "Checklist saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.parent, "Error", f"Failed to save file: {str(e)}")

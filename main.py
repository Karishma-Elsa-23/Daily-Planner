# Final cute planner version with full UI enhancements

import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCalendarWidget, QDialog, QCheckBox, QPushButton, QLineEdit, QTextEdit,
    QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DATA_DIR = "./planner_data"
os.makedirs(DATA_DIR, exist_ok=True)

class EditableCheckItem(QWidget):
    def __init__(self, text, done, save_callback):
        super().__init__()
        self.save_callback = save_callback

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(done)
        self.checkbox.stateChanged.connect(self.update_strike)

        self.line_edit = QLineEdit(text)
        self.line_edit.setFont(QFont("Segoe UI", 11))
        self.line_edit.editingFinished.connect(self.save_callback)

        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setFixedSize(30, 30)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)
        self.update_strike()

    def set_delete_callback(self, callback):
        self.delete_btn.clicked.connect(callback)

    def update_strike(self):
        font = self.line_edit.font()
        font.setStrikeOut(self.checkbox.isChecked())
        self.line_edit.setFont(font)
        self.save_callback()

    def get_data(self):
        return {"text": self.line_edit.text(), "done": self.checkbox.isChecked()}


class PlannerDialog(QDialog):
    def __init__(self, date, parent=None):
        super().__init__(parent)
        self.date_str = date.toString("yyyy-MM-dd")
        self.setWindowTitle(f"Planner - {self.date_str}")
        self.setMinimumSize(750, 850)
        self.setStyleSheet("""
            QDialog {
                background-color: #fdfcfa;
            }
        """)

        self.data = {"checklist": [], "water": 0, "vitamins": [], "sleep": 0, "notes": ""}
        self.widgets = {"checklist": [], "vitamins": []}
        self.load_data()

        layout = QVBoxLayout()

        layout.addWidget(self.section_label("Checklist"))
        self.checklist_layout = QVBoxLayout()
        layout.addLayout(self.checklist_layout)
        self.checklist_input = QLineEdit()
        self.checklist_input.setPlaceholderText("Add new checklist item...")
        self.checklist_input.returnPressed.connect(self.add_checklist_item_from_input)
        layout.addWidget(self.checklist_input)

        layout.addWidget(self.section_label("Water Tracker"))
        self.water_buttons = []
        water_layout = QHBoxLayout()
        for i in range(8):
            btn = QPushButton("🥛")
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("font-size: 24px; border: none;")
            btn.clicked.connect(lambda _, b=btn, i=i: self.toggle_water(i))
            self.water_buttons.append(btn)
            water_layout.addWidget(btn)
        layout.addLayout(water_layout)

        layout.addWidget(self.section_label("Multivitamins"))
        self.vitamin_layout = QVBoxLayout()
        layout.addLayout(self.vitamin_layout)

        self.add_vitamin_button = QPushButton("+")
        self.add_vitamin_button.setFixedSize(30, 30)
        self.add_vitamin_button.clicked.connect(self.add_blank_vitamin)
        layout.addWidget(self.add_vitamin_button, alignment=Qt.AlignLeft)

        layout.addWidget(self.section_label("Hours of Sleep"))
        self.sleep_layout = QHBoxLayout()
        self.sleep_group = QButtonGroup()
        for i in range(1, 9):
            btn = QPushButton("🌙")
            btn.setFixedSize(30, 30)
            btn.setCheckable(True)
            btn.setStyleSheet("font-size: 18px; border-radius: 15px;")
            btn.clicked.connect(lambda _, h=i: self.set_sleep_hours(h))
            self.sleep_group.addButton(btn, i)
            self.sleep_layout.addWidget(btn)
        layout.addLayout(self.sleep_layout)

        layout.addWidget(self.section_label("Notes"))
        self.notes_box = QTextEdit()
        self.notes_box.setPlaceholderText("Write your thoughts...")
        self.notes_box.textChanged.connect(self.save_data)
        self.notes_box.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                background-color: #fffdfc;
            }
        """)
        layout.addWidget(self.notes_box)

        self.setLayout(layout)
        self.load_widgets()

    def section_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        return lbl

    def data_path(self):
        return os.path.join(DATA_DIR, f"{self.date_str}.json")

    def load_data(self):
        try:
            with open(self.data_path(), "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                "checklist": [],
                "water": 0,
                "vitamins": [
                    {"text": "Vitamin B", "done": False},
                    {"text": "Vitamin C", "done": False},
                    {"text": "Iron", "done": False},
                    {"text": "Omega 3 Fatty Acid", "done": False},
                    {"text": "Biotin", "done": False}
                ],
                "sleep": 0,
                "notes": ""
            }

    def save_data(self):
        self.data["checklist"] = [w.get_data() for w in self.widgets["checklist"]]
        self.data["vitamins"] = [w.get_data() for w in self.widgets["vitamins"]]
        self.data["notes"] = self.notes_box.toPlainText()
        with open(self.data_path(), "w") as f:
            json.dump(self.data, f, indent=2)

    def load_widgets(self):
        for item in self.data["checklist"]:
            self.add_checklist_item(item["text"], item["done"])
        for item in self.data["vitamins"]:
            self.add_vitamin_item(item["text"], item["done"])
        self.notes_box.setText(self.data.get("notes", ""))
        self.update_water_buttons()
        self.update_sleep_buttons()

    def add_checklist_item_from_input(self):
        text = self.checklist_input.text().strip()
        if text:
            self.add_checklist_item(text, False)
            self.checklist_input.clear()
            self.save_data()

    def add_checklist_item(self, text, done):
        widget = EditableCheckItem(text, done, self.save_data)
        self.checklist_layout.addWidget(widget)
        self.widgets["checklist"].append(widget)
        widget.set_delete_callback(lambda: self.remove_item("checklist", widget))

    def add_blank_vitamin(self):
        self.add_vitamin_item("New Vitamin", False)
        self.save_data()

    def add_vitamin_item(self, text, done):
        widget = EditableCheckItem(text, done, self.save_data)
        widget.line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #fdf6f0;
                border: 1px solid #e1cfcf;
                border-radius: 15px;
                padding: 6px 12px;
            }
        """)
        self.vitamin_layout.addWidget(widget)
        self.widgets["vitamins"].append(widget)
        widget.set_delete_callback(lambda: self.remove_item("vitamins", widget))

    def remove_item(self, category, widget):
        if widget in self.widgets[category]:
            self.widgets[category].remove(widget)
        widget.setParent(None)
        widget.deleteLater()
        self.save_data()

    def toggle_water(self, index):
        self.data["water"] = index + 1 if self.data["water"] != index + 1 else index
        self.update_water_buttons()
        self.save_data()

    def update_water_buttons(self):
        for i, btn in enumerate(self.water_buttons):
            if i < self.data["water"]:
                btn.setStyleSheet("font-size: 24px; color: #3daee9;")
            else:
                btn.setStyleSheet("font-size: 24px; color: black;")

    def set_sleep_hours(self, hours):
        self.data["sleep"] = hours
        self.update_sleep_buttons()
        self.save_data()

    def update_sleep_buttons(self):
        for i, btn in enumerate(self.sleep_group.buttons(), 1):
            if i == self.data["sleep"]:
                btn.setStyleSheet("font-size: 18px; border-radius: 15px; background-color: #fff3cd; border: 1px solid #ffeeba;")
                btn.setChecked(True)
            else:
                btn.setStyleSheet("font-size: 18px; border-radius: 15px;")


class CalendarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Planner")
        self.setMinimumSize(800, 600)

        widget = QWidget()
        layout = QVBoxLayout()

        calendar = QCalendarWidget()
        calendar.clicked.connect(self.show_planner)

        layout.addWidget(QLabel("Select a date:"))
        layout.addWidget(calendar)

        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def show_planner(self, date):
        dialog = PlannerDialog(date, self)
        dialog.exec_()


app = QApplication([])
app.setStyleSheet("""
    QWidget {
        font-family: 'Segoe UI';
        font-size: 13pt;
    }
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border-radius: 10px;
        border: 1px solid #aaa;
    }
    QCheckBox::indicator:checked {
        background-color: #94d3a2;
        border: 1px solid #7bbf8b;
    }
""")
win = CalendarWindow()
win.show()
app.exec_()

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QLabel, QListWidget
from PySide6.QtCore import Qt, QRect, QCoreApplication, QEvent
import sys
import json
import os
import time

class KeymapEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keymap Editor")
        self.resize(400, 300)
        self.center_window()
        self.keymap_data = self.load_keymap_json()
        self.recording = False
        self.recorded_macro = []
        self.last_key_time = None
        self.record_target_button = None
        self.record_dialog = None
        self.record_btn = None
        self.record_macro_list = None
        self.init_ui()

    def center_window(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def load_keymap_json(self):
        json_path = os.path.join(os.path.dirname(__file__), "keymap.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {}

    def save_keymap_json(self):
        json_path = os.path.join(os.path.dirname(__file__), "keymap.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.keymap_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        self.button1 = QPushButton("Tombol 1")
        self.button1.clicked.connect(lambda: self.show_dialog("0"))
        h_layout.addStretch()
        h_layout.addWidget(self.button1)
        h_layout.addStretch()

        v_layout.addStretch()
        v_layout.addLayout(h_layout)
        v_layout.addStretch()

        central_widget.setLayout(v_layout)

    def show_dialog(self, button_id):
        button_data = self.keymap_data.get("buttons", {}).get(button_id, None)
        if button_data:
            name = button_data.get("name", "Unknown")
            description = button_data.get("description", "")
            macro = button_data.get("macro", [])
            macro_str = "\n".join(
                [f'{i+1}. {action.get("action", "")}: {action.get("keys", action.get("text", ""))} (delay: {action.get("delay", 0)}ms)'
                 for i, action in enumerate(macro)]
            )
            text = f'Nama: {name}\nDeskripsi: {description}\nMacro:\n{macro_str}'
        else:
            text = "Data tombol tidak ditemukan di keymap.json."

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Info Tombol {int(button_id)+1}")
        layout = QVBoxLayout(dialog)
        label = QLabel(text)
        layout.addWidget(label)

        record_btn = QPushButton("Record Macro")
        layout.addWidget(record_btn)
        record_btn.clicked.connect(lambda: self.start_record_macro(dialog, button_id, record_btn))

        close_btn = QPushButton("Tutup")
        layout.addWidget(close_btn)
        close_btn.clicked.connect(dialog.close)

        dialog.setLayout(layout)
        dialog.exec()

    def start_record_macro(self, dialog, button_id, record_btn):
        if not self.recording:
            self.recording = True
            self.recorded_macro = []
            self.current_keys = []  # Reset keys array
            self.last_key_time = time.time()
            self.record_target_button = button_id
            self.record_dialog = dialog
            self.record_btn = record_btn

            record_btn.setText("Stop")
            self.record_macro_list = QListWidget()
            self.record_macro_list.setMinimumHeight(120)
            self.record_macro_list.addItem("Recording started... Press keys to record")
            dialog.layout().insertWidget(2, self.record_macro_list)
            
            # Install event filter on both dialog and application
            dialog.installEventFilter(self)
            QApplication.instance().installEventFilter(self)
            
            # Also install on all child widgets
            for child in dialog.findChildren(QWidget):
                child.installEventFilter(self)
            
            self.grabKeyboard()
        else:
            self.recording = False
            record_btn.setText("Record Macro")
            self.releaseKeyboard()
            
            # Remove event filters
            if self.record_dialog:
                self.record_dialog.removeEventFilter(self)
                # Remove from all child widgets
                for child in self.record_dialog.findChildren(QWidget):
                    child.removeEventFilter(self)
            QApplication.instance().removeEventFilter(self)
            
            self.save_recorded_macro_per_button(self.record_target_button)
            self.record_target_button = None
            self.record_dialog = None
            self.record_btn = None
            self.record_macro_list = None
            dialog.close()
    def eventFilter(self, obj, event):
        if self.recording and event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if self.recording:
            now = time.time()
            delay = int((now - self.last_key_time) * 1000) if self.last_key_time else 0
            self.last_key_time = now
            
            # Get individual key components
            key_name = ""
            modifiers = event.modifiers()
            key = event.key()
            
            # Handle modifier keys individually
            if modifiers & Qt.ControlModifier:
                key_name = "Ctrl"
            elif modifiers & Qt.AltModifier:
                key_name = "Alt"
            elif modifiers & Qt.ShiftModifier:
                key_name = "Shift"
            elif modifiers & Qt.MetaModifier:
                key_name = "Win"
            else:
                # Handle regular keys
                text = event.text().upper()
                if text and text.isprintable():
                    key_name = text
                else:
                    # Special keys mapping
                    qt_key_map = {
                        Qt.Key_Tab: "Tab",
                        Qt.Key_Return: "Enter",
                        Qt.Key_Enter: "Enter",
                        Qt.Key_Escape: "Esc",
                        Qt.Key_Backspace: "Backspace",
                        Qt.Key_Delete: "Delete",
                        Qt.Key_Space: "Space",
                        Qt.Key_Left: "Left",
                        Qt.Key_Right: "Right",
                        Qt.Key_Up: "Up",
                        Qt.Key_Down: "Down",
                        Qt.Key_F1: "F1",
                        Qt.Key_F2: "F2",
                        Qt.Key_F3: "F3",
                        Qt.Key_F4: "F4",
                        Qt.Key_F5: "F5",
                        Qt.Key_F6: "F6",
                        Qt.Key_F7: "F7",
                        Qt.Key_F8: "F8",
                        Qt.Key_F9: "F9",
                        Qt.Key_F10: "F10",
                        Qt.Key_F11: "F11",
                        Qt.Key_F12: "F12",
                    }
                    key_name = qt_key_map.get(key, "")
            
            if key_name:
                # Add individual key to the keys array
                if not hasattr(self, 'current_keys'):
                    self.current_keys = []
                
                self.current_keys.append(key_name)
                
                # Add to recorded macro as simple array format
                if len(self.recorded_macro) == 0:
                    self.recorded_macro.append({
                        "keys": [key_name],
                        "delay": delay
                    })
                else:
                    self.recorded_macro[0]["keys"].append(key_name)
                
                if self.record_macro_list is not None:
                    # Update display to show current keys array
                    keys_display = " -> ".join(self.current_keys)
                    self.record_macro_list.clear()
                    self.record_macro_list.addItem(f'Keys: [{keys_display}] (delay: {delay}ms)')

    def save_recorded_macro_per_button(self, button_id):
        if self.recorded_macro:
            self.keymap_data.setdefault("buttons", {}).setdefault(button_id, {})["macro"] = self.recorded_macro
            self.save_keymap_json()
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Record Selesai")
            msg_box.setText(f"Macro berhasil direkam dan disimpan ke tombol {int(button_id)+1}.")
            msg_box.setIcon(QMessageBox.NoIcon)
            msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeymapEditorWindow()
    window.show()
    sys.exit(app.exec())

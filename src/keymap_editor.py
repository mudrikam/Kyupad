from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, 
                               QHBoxLayout, QMessageBox, QDialog, QLabel, QListWidget, QLineEdit, 
                               QTextEdit, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, QRect, QCoreApplication, QEvent, QTimer
import sys
import json
import os
import time
import subprocess
import platform

class ButtonEditDialog(QDialog):
    def __init__(self, parent, button_id):
        super().__init__(parent)
        self.parent_window = parent
        self.button_id = button_id
        self.recording = False
        self.recorded_macro = []
        self.current_keys = []
        self.last_key_time = None
        self.record_macro_list = None
        
        # Load current button data
        self.button_data = self.parent_window.keymap_data.get("buttons", {}).get(button_id, {
            "name": f"Button {int(button_id)+1}",
            "description": "",
            "macro": []
        })
        
        self.setWindowTitle(f"Edit Tombol {int(button_id)+1}")
        self.setModal(True)
        self.resize(500, 450)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Name input
        layout.addWidget(QLabel("Nama Tombol:"))
        self.name_input = QLineEdit(self.button_data.get("name", ""))
        layout.addWidget(self.name_input)
        
        # Description input
        layout.addWidget(QLabel("Deskripsi:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(60)
        self.desc_input.setPlainText(self.button_data.get("description", ""))
        layout.addWidget(self.desc_input)
        
        # Current macro display
        layout.addWidget(QLabel("Macro Saat Ini:"))
        self.current_macro_display = QListWidget()
        self.current_macro_display.setWordWrap(True)
        self.update_macro_display()
        layout.addWidget(self.current_macro_display)
        
        # Record button
        self.record_btn = QPushButton("Record Macro Baru")
        layout.addWidget(self.record_btn)
        self.record_btn.clicked.connect(self.toggle_recording)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Simpan")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        
        clear_btn = QPushButton("Hapus Macro")
        clear_btn.clicked.connect(self.clear_macro)
        button_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Batal")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_macro_display(self):
        self.current_macro_display.clear()
        macro = self.button_data.get("macro", [])
        
        if not macro:
            self.current_macro_display.addItem("(Tidak ada macro)")
            return
        
        for i, action in enumerate(macro):
            if "keys" in action and isinstance(action["keys"], list):
                keys_display = " → ".join(action["keys"])
                delay = action.get("delay", 0)
                self.current_macro_display.addItem(f"{i+1}. Keys: {keys_display} (delay: {delay}ms)")
    
    def save_changes(self):
        # Update button data
        self.button_data["name"] = self.name_input.text().strip() or f"Button {int(self.button_id)+1}"
        self.button_data["description"] = self.desc_input.toPlainText().strip()
        
        # Save to parent keymap
        self.parent_window.keymap_data.setdefault("buttons", {})[self.button_id] = self.button_data
        self.parent_window.save_keymap_json()
        self.parent_window.update_button_text(self.button_id, self.button_data["name"])
        
        self.close()
    
    def clear_macro(self):
        self.button_data["macro"] = []
        self.update_macro_display()
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.recorded_macro = []
        self.current_keys = []
        self.last_key_time = time.time()
        
        self.record_btn.setText("Stop Recording")
        self.record_macro_list = QListWidget()
        self.record_macro_list.setMinimumHeight(120)
        self.record_macro_list.addItem("🔴 Recording... Press any keys!")
        self.record_macro_list.addItem("(This dialog is now capturing keyboard)")
        self.layout().insertWidget(-2, self.record_macro_list)  # Insert before button layout
        
        # Set focus to this dialog
        self.setFocus()
        self.activateWindow()
        
        print("Recording started in custom dialog")
    
    def stop_recording(self):
        self.recording = False
        self.record_btn.setText("Record Macro Baru")
        
        if self.recorded_macro:
            self.button_data["macro"] = self.recorded_macro
            self.update_macro_display()
        
        # Remove recording list if exists
        if self.record_macro_list:
            self.record_macro_list.setParent(None)
            self.record_macro_list = None
    
    def keyPressEvent(self, event):
        print(f"ButtonEditDialog keyPressEvent: Recording={self.recording}, Key={event.key()}")
        
        if self.recording:
            self.process_key_event(event, "press")
        
        # Don't call super().keyPressEvent() when recording to prevent default behavior
        if not self.recording:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        print(f"ButtonEditDialog keyReleaseEvent: Recording={self.recording}, Key={event.key()}")
        
        if self.recording:
            self.process_key_event(event, "release")
        
        # Don't call super().keyReleaseEvent() when recording to prevent default behavior
        if not self.recording:
            super().keyReleaseEvent(event)
    
    def process_key_event(self, event, action_type):
        now = time.time()
        delay = int((now - self.last_key_time) * 1000) if self.last_key_time else 0
        self.last_key_time = now
        
        key_name = ""
        key = event.key()
        
        print(f"Processing {action_type} key in dialog: {key}, text: '{event.text()}'")
        
        # Check for modifier keys first
        if key in [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta]:
            if key == Qt.Key_Control:
                key_name = "Ctrl"
            elif key == Qt.Key_Alt:
                key_name = "Alt"
            elif key == Qt.Key_Shift:
                key_name = "Shift"
            elif key == Qt.Key_Meta:
                key_name = "Win"
        else:
            # Try to get key name from text first
            text = event.text()
            if text and text.isprintable() and len(text) == 1:
                key_name = text.upper()
            else:
                # If no text, try direct key code mapping for letters and numbers
                if Qt.Key_A <= key <= Qt.Key_Z:
                    key_name = chr(key)  # Convert key code to letter
                elif Qt.Key_0 <= key <= Qt.Key_9:
                    key_name = chr(key)  # Convert key code to number
                else:
                    # Special keys mapping
                    qt_key_map = {
                        Qt.Key_Tab: "Tab",
                        Qt.Key_Return: "Enter",
                        Qt.Key_Enter: "Enter",
                        Qt.Key_Escape: "Escape",
                        Qt.Key_Backspace: "Backspace",
                        Qt.Key_Delete: "Delete",
                        Qt.Key_Space: "Space",
                        Qt.Key_Left: "Left",
                        Qt.Key_Right: "Right",
                        Qt.Key_Up: "Up",
                        Qt.Key_Down: "Down",
                        Qt.Key_F1: "F1", Qt.Key_F2: "F2", Qt.Key_F3: "F3", Qt.Key_F4: "F4",
                        Qt.Key_F5: "F5", Qt.Key_F6: "F6", Qt.Key_F7: "F7", Qt.Key_F8: "F8",
                        Qt.Key_F9: "F9", Qt.Key_F10: "F10", Qt.Key_F11: "F11", Qt.Key_F12: "F12",
                    }
                    key_name = qt_key_map.get(key, "")
        
        print(f"Key name determined: '{key_name}' ({action_type})")
        
        if key_name:
            # Add action type to the key name for clarity
            full_key_action = f"{key_name}_{action_type}"
            self.current_keys.append(full_key_action)
            
            if len(self.recorded_macro) == 0:
                self.recorded_macro.append({
                    "keys": [full_key_action],
                    "delay": delay
                })
            else:
                self.recorded_macro[0]["keys"].append(full_key_action)
            
            if self.record_macro_list:
                keys_display = " → ".join(self.current_keys)
                self.record_macro_list.clear()
                self.record_macro_list.addItem(f'🔴 Recording: {keys_display}')
                self.record_macro_list.addItem(f'Total: {len(self.current_keys)} events')
                self.record_macro_list.addItem(f'Last delay: {delay}ms')
            
            print(f"Key {action_type} recorded in dialog: {full_key_action}")
        else:
            print(f"Key not recognized in dialog: {key} (text: '{event.text()}')")

class KeymapEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kyupad Keymap Editor")
        self.resize(600, 500)
        self.center_window()
        self.keymap_data = self.load_keymap_json()
        self.buttons = {}  # Store button references
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
            return {"buttons": {}, "settings": {}}

    def save_keymap_json(self):
        json_path = os.path.join(os.path.dirname(__file__), "keymap.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.keymap_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving keymap: {e}")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Kyupad Keymap Editor - 4x4 Layout")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create 4x4 grid of buttons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        for row in range(4):
            for col in range(4):
                button_id = str(row * 4 + col)
                button_data = self.keymap_data.get("buttons", {}).get(button_id, {
                    "name": f"Button {int(button_id)+1}",
                    "description": "",
                    "macro": []
                })
                
                button = QPushButton(button_data.get("name", f"Button {int(button_id)+1}"))
                button.setMinimumSize(120, 80)
                
                # Connect button to edit dialog
                button.clicked.connect(lambda checked, bid=button_id: self.show_edit_dialog(bid))
                
                # Store button reference
                self.buttons[button_id] = button
                
                grid_layout.addWidget(button, row, col)
        
        # Add grid to main layout
        main_layout.addLayout(grid_layout)
        
        # Status bar
        status_label = QLabel("Klik tombol untuk mengedit nama, deskripsi, dan macro")
        status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(status_label)
        
        central_widget.setLayout(main_layout)
    
    def update_button_text(self, button_id, text):
        """Update button text when name changes"""
        if button_id in self.buttons:
            self.buttons[button_id].setText(text)
    
    def show_edit_dialog(self, button_id):
        """Show edit dialog for the specified button"""
        dialog = ButtonEditDialog(self, button_id)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeymapEditorWindow()
    window.show()
    sys.exit(app.exec())

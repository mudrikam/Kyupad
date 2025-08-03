from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, 
                               QHBoxLayout, QMessageBox, QDialog, QLabel, QListWidget, QLineEdit, 
                               QTextEdit, QGridLayout, QScrollArea, QComboBox, QSpinBox, QGroupBox,
                               QTableWidget, QTableWidgetItem, QHeaderView)
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
        
        self.setWindowTitle(f"Edit Button {int(button_id)+1}")
        self.setModal(True)
        self.resize(600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Name input
        layout.addWidget(QLabel("Button Name:"))
        self.name_input = QLineEdit(self.button_data.get("name", ""))
        layout.addWidget(self.name_input)
        
        # Description input
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(60)
        self.desc_input.setPlainText(self.button_data.get("description", ""))
        layout.addWidget(self.desc_input)
        
        # Current macro display
        layout.addWidget(QLabel("Current Macro:"))
        self.current_macro_display = QTableWidget()
        self.current_macro_display.setColumnCount(1)
        self.current_macro_display.setHorizontalHeaderLabels(["Key Events"])
        
        # Set column widths
        header = self.current_macro_display.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Set selection behavior
        self.current_macro_display.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.current_macro_display.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        self.update_macro_display()
        layout.addWidget(self.current_macro_display)
        
        # Manual macro input - single line
        manual_layout = QHBoxLayout()
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_macro)
        manual_layout.addWidget(clear_btn)
        
        # Modifier keys
        manual_layout.addWidget(QLabel("Modifier:"))
        self.modifier_combo = QComboBox()
        self.modifier_combo.addItems([
            "None", "Ctrl", "Alt", "Shift", "Win",
            "Ctrl+Shift", "Ctrl+Alt", "Alt+Shift", "Win+Shift"
        ])
        manual_layout.addWidget(self.modifier_combo)
        
        # Main key
        self.main_key_combo = QComboBox()
        self.main_key_combo.setEditable(True)
        key_options = [
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "Enter", "Space", "Tab", "Escape", "Backspace", "Delete",
            "Left", "Right", "Up", "Down", "Home", "End", "PageUp", "PageDown",
            "Insert", "PrintScreen", "Pause", "CapsLock", "NumLock", "ScrollLock"
        ]
        self.main_key_combo.addItems(key_options)
        manual_layout.addWidget(self.main_key_combo)
        
        # Delay input
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(0, 10000)
        self.delay_spinbox.setValue(100)
        self.delay_spinbox.setSuffix(" ms")
        manual_layout.addWidget(self.delay_spinbox)
        
        # Add button
        add_manual_btn = QPushButton("Add")
        add_manual_btn.clicked.connect(self.add_manual_macro)
        manual_layout.addWidget(add_manual_btn)
        
        # Record button
        self.record_btn = QPushButton("Record")
        self.record_btn.clicked.connect(self.toggle_recording)
        manual_layout.addWidget(self.record_btn)
        
        layout.addLayout(manual_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        
        delete_selected_btn = QPushButton("Delete Selected")
        delete_selected_btn.clicked.connect(self.delete_selected_action)
        button_layout.addWidget(delete_selected_btn)
        
        close_btn = QPushButton("Cancel")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_macro_display(self):
        self.current_macro_display.setRowCount(0)
        macro = self.button_data.get("macro", [])
        
        if not macro:
            self.current_macro_display.setRowCount(1)
            self.current_macro_display.setItem(0, 0, QTableWidgetItem("(No macro)"))
            return
        
        # Filter only key actions, skip consumer/special actions
        key_actions = []
        for action in macro:
            if "keys" in action and isinstance(action["keys"], list):
                key_actions.append(action)
        
        if not key_actions:
            self.current_macro_display.setRowCount(1)
            self.current_macro_display.setItem(0, 0, QTableWidgetItem("(No key actions)"))
            return
        
        self.current_macro_display.setRowCount(len(key_actions))
        
        for i, action in enumerate(key_actions):
            # Create a widget container for the row
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 2, 5, 2)
            row_layout.setSpacing(5)
            
            # Create buttons for each key in this action
            keys = action.get("keys", [])
            for key_event in keys:
                key_button = QPushButton(key_event)
                key_button.setMaximumHeight(25)
                key_button.setMinimumWidth(60)
                
                # Style the button based on key type
                if "_press" in key_event:
                    key_name = key_event.replace("_press", "")
                    key_button.setText(f"↓{key_name}")
                    key_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 10px;")
                elif "_release" in key_event:
                    key_name = key_event.replace("_release", "")
                    key_button.setText(f"↑{key_name}")
                    key_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; font-size: 10px;")
                
                row_layout.addWidget(key_button)
            
            # Add delay info at the end
            delay = action.get("delay", 0)
            if delay > 0:
                delay_label = QLabel(f"({delay}ms)")
                delay_label.setStyleSheet("color: #666; font-size: 10px;")
                row_layout.addWidget(delay_label)
            
            row_layout.addStretch()
            
            # Set the widget to the table cell
            self.current_macro_display.setCellWidget(i, 0, row_widget)
        
        # Auto-resize rows
        self.current_macro_display.resizeRowsToContents()
    
    def save_changes(self):
        # Update button data
        self.button_data["name"] = self.name_input.text().strip() or f"Button {int(self.button_id)+1}"
        self.button_data["description"] = self.desc_input.toPlainText().strip()
        
        # Save to parent keymap
        self.parent_window.keymap_data.setdefault("buttons", {})[self.button_id] = self.button_data
        self.parent_window.save_keymap_json()
        self.parent_window.update_button_text(self.button_id, self.button_data["name"])
        
        self.close()
    
    def delete_selected_action(self):
        current_row = self.current_macro_display.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Select an action to delete!")
            return
        
        # Check if there are actual macro actions (not the empty state)
        if not self.button_data.get("macro", []):
            QMessageBox.warning(self, "Error", "No macro to delete!")
            return
        
        # Filter only key actions
        key_actions = []
        key_action_indices = []
        for i, action in enumerate(self.button_data.get("macro", [])):
            if "keys" in action and isinstance(action["keys"], list):
                key_actions.append(action)
                key_action_indices.append(i)
        
        if current_row < len(key_action_indices):
            original_index = key_action_indices[current_row]
            del self.button_data["macro"][original_index]
            self.update_macro_display()
        else:
            QMessageBox.warning(self, "Error", "Invalid action!")
    
    def add_manual_macro(self):
        # Get selected modifier and main key
        modifier = self.modifier_combo.currentText()
        main_key = self.main_key_combo.currentText().strip()
        delay = self.delay_spinbox.value()
        
        if not main_key:
            QMessageBox.warning(self, "Error", "Please enter a main key!")
            return
        
        # Build complete key sequence with proper press/release pairs
        keys = []
        
        # Add modifier press events
        if modifier != "None":
            if "+" in modifier:
                # Multiple modifiers - press each one
                modifier_keys = modifier.split("+")
                for mod in modifier_keys:
                    keys.append(f"{mod}_press")
            else:
                # Single modifier
                keys.append(f"{modifier}_press")
        
        # Add main key press and release
        keys.append(f"{main_key}_press")
        keys.append(f"{main_key}_release")
        
        # Add modifier release events (in reverse order)
        if modifier != "None":
            if "+" in modifier:
                # Multiple modifiers - release in reverse order
                modifier_keys = modifier.split("+")
                for mod in reversed(modifier_keys):
                    keys.append(f"{mod}_release")
            else:
                # Single modifier
                keys.append(f"{modifier}_release")
        
        # Create macro action
        new_action = {
            "keys": keys,
            "delay": delay
        }
        
        # Add to macro
        if not self.button_data["macro"]:
            self.button_data["macro"] = []
        
        self.button_data["macro"].append(new_action)
        
        # Update display
        self.update_macro_display()
        
        # Reset inputs
        self.modifier_combo.setCurrentIndex(0)
        self.main_key_combo.setCurrentIndex(0)
        self.delay_spinbox.setValue(100)
    
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

        self.record_btn.setText("Stop")
        self.record_macro_list = QListWidget()
        self.record_macro_list.setMinimumHeight(120)
        self.record_macro_list.setWordWrap(True)
        self.record_macro_list.addItem("🔴 Recording... Press any keys!")
        self.record_macro_list.addItem("(This dialog is now capturing keyboard)")
        self.layout().insertWidget(-2, self.record_macro_list)  # Insert before button layout

        # Set focus to this dialog
        self.setFocus()
        self.activateWindow()

        print("Recording started in custom dialog")
    
    def stop_recording(self):
        self.recording = False
        self.record_btn.setText("Record")
        
        if self.recorded_macro:
            # Add new recorded action to existing macro instead of overwriting
            if not self.button_data["macro"]:
                self.button_data["macro"] = []
            
            # Add the recorded action to the macro list
            self.button_data["macro"].extend(self.recorded_macro)
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

    def clear_macro(self):
        self.button_data["macro"] = []
        self.update_macro_display()

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

        main_layout = QVBoxLayout()

        # --- Settings/info area ---
        settings_group = QGroupBox("Device Information & Settings")
        settings_layout = QGridLayout()

        # Version (read-only)
        settings_layout.addWidget(QLabel("Version:"), 0, 0)
        self.version_label = QLabel(str(self.keymap_data.get("version", "?")))
        settings_layout.addWidget(self.version_label, 0, 1)

        # Bluetooth enabled (editable)
        settings_layout.addWidget(QLabel("Bluetooth Enabled:"), 1, 0)
        self.bluetooth_combo = QComboBox()
        self.bluetooth_combo.addItems(["True", "False"])
        bt_enabled = self.keymap_data.get("settings", {}).get("auto_reconnect", True)
        self.bluetooth_combo.setCurrentText("True" if bt_enabled else "False")
        settings_layout.addWidget(self.bluetooth_combo, 1, 1)

        # Sleep timeout (editable)
        settings_layout.addWidget(QLabel("Sleep Timeout (min):"), 2, 0)
        self.sleep_spinbox = QSpinBox()
        self.sleep_spinbox.setRange(1, 999)
        self.sleep_spinbox.setValue(self.keymap_data.get("settings", {}).get("sleep_timeout_minutes", 30))
        settings_layout.addWidget(self.sleep_spinbox, 2, 1)

        # Device ID (editable)
        settings_layout.addWidget(QLabel("Device ID:"), 3, 0)
        self.device_id_spinbox = QSpinBox()
        self.device_id_spinbox.setRange(1, 9999)
        self.device_id_spinbox.setValue(self.keymap_data.get("settings", {}).get("device_id", 1))
        settings_layout.addWidget(self.device_id_spinbox, 3, 1)

        # Device Name (editable)
        settings_layout.addWidget(QLabel("Device Name:"), 4, 0)
        self.device_name_edit = QLineEdit(self.keymap_data.get("settings", {}).get("device_name", "Kyupad-1"))
        settings_layout.addWidget(self.device_name_edit, 4, 1)

        # Auto reconnect (editable)
        settings_layout.addWidget(QLabel("Auto Reconnect:"), 5, 0)
        self.auto_reconnect_combo = QComboBox()
        self.auto_reconnect_combo.addItems(["True", "False"])
        auto_reconnect = self.keymap_data.get("settings", {}).get("auto_reconnect", True)
        self.auto_reconnect_combo.setCurrentText("True" if auto_reconnect else "False")
        settings_layout.addWidget(self.auto_reconnect_combo, 5, 1)

        # Power save mode (editable)
        settings_layout.addWidget(QLabel("Power Save Mode:"), 6, 0)
        self.power_save_combo = QComboBox()
        self.power_save_combo.addItems(["True", "False"])
        power_save = self.keymap_data.get("settings", {}).get("power_save_mode", True)
        self.power_save_combo.setCurrentText("True" if power_save else "False")
        settings_layout.addWidget(self.power_save_combo, 6, 1)

        # Save button
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_basic_settings)
        settings_layout.addWidget(self.save_settings_btn, 7, 0, 1, 2)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # --- Grid of buttons ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        for row in range(4):
            for col in range(4):
                button_id = str(row * 4 + col)
                button_data = self.keymap_data.get("buttons", {}).get(button_id, {})
                btn_text = button_data.get("name", f"Macro {int(button_id)+1}")
                btn_color = button_data.get("button_color", "#CCCCCC")
                btn = QPushButton(btn_text)
                btn.setMinimumSize(80, 60)
                btn.setStyleSheet(f"background-color: {btn_color}; color: white; font-weight: bold; font-size: 14px;")
                btn.clicked.connect(lambda checked, bid=button_id: self.show_edit_dialog(bid))
                self.buttons[button_id] = btn
                grid_layout.addWidget(btn, row, col)
        main_layout.addLayout(grid_layout)
        central_widget.setLayout(main_layout)

    def save_basic_settings(self):
        # Save settings from UI to keymap_data and file
        settings = self.keymap_data.setdefault("settings", {})
        settings["sleep_timeout_minutes"] = self.sleep_spinbox.value()
        settings["device_id"] = self.device_id_spinbox.value()
        settings["device_name"] = self.device_name_edit.text().strip() or "Kyupad-1"
        settings["auto_reconnect"] = self.auto_reconnect_combo.currentText() == "True"
        settings["power_save_mode"] = self.power_save_combo.currentText() == "True"
        # Bluetooth enabled is mapped to auto_reconnect for simplicity
        settings["auto_reconnect"] = self.bluetooth_combo.currentText() == "True"
        self.save_keymap_json()
        QMessageBox.information(self, "Settings Saved", "Basic settings have been saved.")
    # Removed duplicate init_ui method. Only the correct version with settings/info area remains.
    
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

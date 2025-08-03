import json
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import digitalio
import board
import microcontroller
import gc

# Bluetooth imports - will gracefully handle if not available
try:
    import adafruit_ble
    from adafruit_ble.advertising import Advertisement
    from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
    from adafruit_ble.services.hid import HIDService
    from adafruit_ble.services.deviceinfo import DeviceInfoService
    BLUETOOTH_AVAILABLE = True
    print("Bluetooth libraries loaded successfully")
except ImportError as e:
    BLUETOOTH_AVAILABLE = False
    print(f"Bluetooth not available: {e}")

class KyupadFirmware:
    def __init__(self):
        print("Initializing Kyupad...")
        
        self.keymap = self.load_keymap()
        self.settings = self.keymap.get('settings', {})
        
        self.device_id = self.settings.get('device_id', 1)
        self.device_name = f"Kyupad-{self.device_id}"
        
        print(f"Device ID: {self.device_id}")
        print(f"Device Name: {self.device_name}")
        
        try:
            # ESP32-S3 Zero Super Mini pinout
            self.row_pins = [board.GPIO1, board.GPIO2, board.GPIO3, board.GPIO4]
            self.col_pins = [board.GPIO5, board.GPIO6, board.GPIO7, board.GPIO8]
            # Status LED pin for ESP32-S3
            self.status_led_pin = board.GPIO9
        except AttributeError as e:
            print(f"Pin assignment error: {e}")
            print("Trying alternative ESP32-S3 pin names...")
            try:
                self.row_pins = [board.IO1, board.IO2, board.IO3, board.IO4]
                self.col_pins = [board.IO5, board.IO6, board.IO7, board.IO8]
                self.status_led_pin = board.IO9
            except AttributeError:
                print("Trying legacy ESP32-C3 pin names...")
                try:
                    self.row_pins = [board.GP2, board.GP3, board.GP4, board.GP5]
                    self.col_pins = [board.GP6, board.GP7, board.GP8, board.GP9]
                    self.status_led_pin = None
                except AttributeError:
                    print("All pin assignment attempts failed. Check board pinout.")
                    microcontroller.reset()
        
        self.rows = []
        self.cols = []
        
        # Initialize row pins (outputs)
        for pin in self.row_pins:
            row = digitalio.DigitalInOut(pin)
            row.direction = digitalio.Direction.OUTPUT
            row.value = False
            self.rows.append(row)
        
        # Initialize column pins (inputs with pull-up)
        for pin in self.col_pins:
            col = digitalio.DigitalInOut(pin)
            col.direction = digitalio.Direction.INPUT
            col.pull = digitalio.Pull.UP
            self.cols.append(col)
        
        # Initialize status LED if available (ESP32-S3 feature)
        self.status_led = None
        if hasattr(self, 'status_led_pin') and self.status_led_pin:
            try:
                self.status_led = digitalio.DigitalInOut(self.status_led_pin)
                self.status_led.direction = digitalio.Direction.OUTPUT
                self.status_led.value = False
                print("Status LED initialized on GPIO9")
            except Exception as e:
                print(f"Status LED initialization failed: {e}")
                self.status_led = None
        
        self.connection_mode = self.settings.get('connection_mode', 'usb')  # 'usb', 'bluetooth', or 'auto'
        self.bluetooth_enabled = BLUETOOTH_AVAILABLE and self.connection_mode in ['bluetooth', 'auto']
        
        # Initialize HID interfaces
        self.keyboard = None
        self.ble = None
        self.hid_service = None
        self.is_connected = False
        
        if self.bluetooth_enabled:
            self.init_bluetooth()
        else:
            self.init_usb()
        
        self.key_states = [[False for _ in range(4)] for _ in range(4)]
        self.last_scan_time = time.monotonic()
        self.last_connection_check = time.monotonic()
        
        self.debounce_delay = self.settings.get('debounce_ms', 50) / 1000.0
        self.macro_speed = self.settings.get('macro_playback_speed', 1.0)
        
        print(f"{self.device_name} Firmware initialized")
        print(f"Connection mode: {self.connection_mode}")
        print(f"Loaded {len(self.keymap.get('buttons', {}))} button mappings")
        print(f"Board: ESP32-S3 Zero Super Mini (optimized)")
        
        # ESP32-S3 specific optimizations
        self.enable_esp32s3_optimizations()
        
        gc.collect()

    def enable_esp32s3_optimizations(self):
        """Enable ESP32-S3 specific optimizations"""
        try:
            # Try to optimize for ESP32-S3 dual-core performance
            print("Applying ESP32-S3 optimizations...")
            
            # Reduce scan delay for faster response (ESP32-S3 can handle it)
            if self.debounce_delay > 0.01:  # 10ms minimum for ESP32-S3
                self.debounce_delay = max(0.01, self.debounce_delay * 0.5)
                print(f"Optimized debounce delay: {self.debounce_delay*1000:.1f}ms")
            
            # Enable status LED blinking if available
            if self.status_led:
                self.led_blink_counter = 0
                print("Status LED ready for connection indication")
                
        except Exception as e:
            print(f"ESP32-S3 optimization failed: {e}")

    def update_status_led(self):
        """Update status LED based on connection state (ESP32-S3 feature)"""
        if not self.status_led:
            return
            
        try:
            if self.bluetooth_enabled:
                if self.is_connected:
                    # Solid on when connected
                    self.status_led.value = True
                else:
                    # Slow blink when advertising
                    self.led_blink_counter = (self.led_blink_counter + 1) % 200
                    self.status_led.value = self.led_blink_counter < 100
            else:
                # Fast blink for USB mode
                self.led_blink_counter = (self.led_blink_counter + 1) % 40
                self.status_led.value = self.led_blink_counter < 20
        except Exception as e:
            print(f"Status LED update failed: {e}")

    def init_bluetooth(self):
        """Initialize Bluetooth HID connection"""
        try:
            print(f"Initializing Bluetooth HID for {self.device_name}...")
            
            # Create BLE instance
            self.ble = adafruit_ble.BLERadio()
            
            # Create HID service
            self.hid_service = HIDService()
            
            # Create device info service with ESP32-S3 specific info
            device_info = DeviceInfoService(
                software_revision=adafruit_ble.__version__,
                manufacturer="Kyupad",
                model=f"ESP32-S3 4x4 Macropad #{self.device_id}"
            )
            
            # Create advertisement
            advertisement = ProvideServicesAdvertisement(self.hid_service)
            advertisement.appearance = 961  # HID Keyboard
            advertisement.complete_name = self.device_name
            
            # Initialize HID keyboard only
            self.keyboard = Keyboard(self.hid_service.devices)
            
            # Start advertising
            self.ble.start_advertising(advertisement)
            print(f"Bluetooth advertising started as '{self.device_name}'")
            print(f"Pair with '{self.device_name}' in your device's Bluetooth settings")
            
        except Exception as e:
            print(f"Bluetooth initialization failed: {e}")
            print("Falling back to USB mode...")
            self.bluetooth_enabled = False
            self.init_usb()

    def init_usb(self):
        """Initialize USB HID connection"""
        try:
            print(f"Initializing USB HID for {self.device_name}...")
            self.keyboard = Keyboard(usb_hid.devices)
            self.is_connected = True
            print(f"USB HID initialized successfully for {self.device_name}")
        except Exception as e:
            print(f"USB HID initialization failed: {e}")
            print("Make sure USB HID is enabled in boot.py")
            microcontroller.reset()

    def check_connection_status(self):
        """Check and update connection status"""
        current_time = time.monotonic()
        
        # Check connection every 2 seconds
        if current_time - self.last_connection_check < 2.0:
            return
        
        self.last_connection_check = current_time
        
        if self.bluetooth_enabled and self.ble:
            was_connected = self.is_connected
            self.is_connected = self.ble.connected
            
            if not was_connected and self.is_connected:
                print(f"✅ {self.device_name} Bluetooth connected!")
                # Stop advertising when connected
                self.ble.stop_advertising()
                
            elif was_connected and not self.is_connected:
                print(f"❌ {self.device_name} Bluetooth disconnected. Restarting advertising...")
                # Restart advertising when disconnected
                try:
                    advertisement = ProvideServicesAdvertisement(self.hid_service)
                    advertisement.appearance = 961
                    advertisement.complete_name = self.device_name
                    self.ble.start_advertising(advertisement)
                except Exception as e:
                    print(f"Failed to restart advertising: {e}")

    def load_keymap(self):
        try:
            with open('keymap.json', 'r') as f:
                keymap_data = json.load(f)
            print("Keymap loaded successfully")
            return keymap_data
        except OSError:
            print("keymap.json not found, creating default...")
            fallback = {
                "buttons": {str(i): {"name": f"Key{i}", "macro": [{"action": "key", "keys": "Space", "delay": 0}], "description": f"Button {i}"} 
                           for i in range(16)},
                "settings": {
                    "debounce_ms": 50, 
                    "macro_playback_speed": 1.0,
                    "connection_mode": "auto",
                    "device_id": 1,
                    "device_name": "Kyupad-1"
                }
            }
            try:
                with open('keymap.json', 'w') as f:
                    json.dump(fallback, f)
                print("Default keymap.json created")
            except OSError:
                print("Could not create keymap.json")
            return fallback
        except Exception as e:
            print(f"Error loading keymap: {e}")
            return {
                "buttons": {str(i): {"name": f"Key{i}", "macro": [{"action": "key", "keys": "Space", "delay": 0}], "description": f"Button {i}"} 
                           for i in range(16)},
                "settings": {
                    "debounce_ms": 50, 
                    "macro_playback_speed": 1.0,
                    "connection_mode": "auto",
                    "device_id": 1,
                    "device_name": "Kyupad-1"
                }
            }

    def parse_macro_array(self, macro_array):
        if not isinstance(macro_array, list):
            return self.parse_macro_legacy(macro_array)
        
        parsed_actions = []
        for action in macro_array:
            if not isinstance(action, dict):
                continue
                
            # Support new simple format with keys array
            if 'keys' in action and isinstance(action['keys'], list):
                keys_array = action['keys']
                delay = action.get('delay', 0)
                
                # Process each key in the array - only keyboard keys
                for key in keys_array:
                    # Check if this is a press/release action
                    if '_' in key and (key.endswith('_press') or key.endswith('_release')):
                        key_name, action = key.rsplit('_', 1)
                        keycode = self.get_keycode(key_name)
                        if keycode:
                            parsed_actions.append(('key_action', keycode, action, delay))
                    else:
                        # Regular keyboard keys - treat as press+release
                        keycode = self.get_keycode(key)
                        if keycode:
                            parsed_actions.append(('keyboard', keycode, delay))
                            
            # Support legacy format with action type
            else:
                action_type = action.get('action', 'key')
                keys = action.get('keys', '')
                delay = action.get('delay', 0)
                
                if action_type == 'key':
                    parsed = self.parse_macro_legacy(keys)
                    if parsed:
                        parsed_actions.append(('key', parsed, delay))
        
        return parsed_actions

    def parse_macro_legacy(self, macro_string):
        if not macro_string:
            return None
        
        parts = macro_string.split('+')
        modifiers = []
        key = None
        
        for part in parts:
            part = part.strip()
            if part == 'Ctrl':
                modifiers.append(Keycode.CONTROL)
            elif part == 'Alt':
                modifiers.append(Keycode.ALT)
            elif part == 'Shift':
                modifiers.append(Keycode.SHIFT)
            elif part == 'Win':
                modifiers.append(Keycode.GUI)
            else:
                key = self.get_keycode(part)
        
        if key is not None:
            return ('keyboard', modifiers, key)
        
        return None

    def get_keycode(self, key_string):
        key_map = {
            'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D,
            'E': Keycode.E, 'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H,
            'I': Keycode.I, 'J': Keycode.J, 'K': Keycode.K, 'L': Keycode.L,
            'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O, 'P': Keycode.P,
            'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
            'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X,
            'Y': Keycode.Y, 'Z': Keycode.Z,
            'Tab': Keycode.TAB, 'Space': Keycode.SPACE, 'Enter': Keycode.ENTER,
            'Escape': Keycode.ESCAPE, 'Backspace': Keycode.BACKSPACE,
            'Delete': Keycode.DELETE, 'Home': Keycode.HOME, 'End': Keycode.END,
            'PageUp': Keycode.PAGE_UP, 'PageDown': Keycode.PAGE_DOWN,
            'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3, 'F4': Keycode.F4,
            'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7, 'F8': Keycode.F8,
            'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11, 'F12': Keycode.F12,
            '0': Keycode.ZERO, '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE,
            '4': Keycode.FOUR, '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN,
            '8': Keycode.EIGHT, '9': Keycode.NINE,
            # Modifier keys
            'Ctrl': Keycode.CONTROL,
            'Alt': Keycode.ALT,
            'Shift': Keycode.SHIFT,
            'Win': Keycode.GUI
        }
        
        return key_map.get(key_string, None)

    def scan_matrix(self):
        current_time = time.monotonic()
        
        if current_time - self.last_scan_time < self.debounce_delay:
            return
        
        # Update status LED (ESP32-S3 feature)
        self.update_status_led()
        
        for row_idx in range(4):
            self.rows[row_idx].value = True
            # Shorter delay for ESP32-S3 (faster GPIO)
            time.sleep(0.00005)  # 50μs instead of 100μs
            
            for col_idx in range(4):
                pressed = not self.cols[col_idx].value
                
                if pressed != self.key_states[row_idx][col_idx]:
                    self.key_states[row_idx][col_idx] = pressed
                    
                    if pressed:
                        self.handle_key_press(row_idx, col_idx)
            
            self.rows[row_idx].value = False
        
        self.last_scan_time = current_time

    def handle_key_press(self, row, col):
        # Skip if not connected (for Bluetooth mode)
        if self.bluetooth_enabled and not self.is_connected:
            print(f"{self.device_name}: Not connected - ignoring key press")
            return
            
        button_index = row * 4 + col
        button_key = str(button_index)
        
        if button_key in self.keymap.get('buttons', {}):
            button_data = self.keymap['buttons'][button_key]
            macro = button_data.get('macro', [])
            name = button_data.get('name', f'Button{button_index}')
            
            connection_type = "BT" if self.bluetooth_enabled else "USB"
            print(f"[{self.device_name}-{connection_type}] Key pressed: {name} (Button {button_index})")
            
            # Brief LED flash on key press (ESP32-S3 feature)
            if self.status_led and self.is_connected:
                self.status_led.value = False
                time.sleep(0.05)
                self.status_led.value = True
            
            self.execute_macro(macro)
        else:
            print(f"{self.device_name}: Unknown button {button_index} pressed")

    def execute_macro(self, macro):
        if isinstance(macro, list):
            parsed_actions = self.parse_macro_array(macro)
            for action_tuple in parsed_actions:
                if len(action_tuple) >= 3:
                    action_type = action_tuple[0]
                    
                    # Extract delay - could be at different positions depending on action type
                    if len(action_tuple) == 4 and action_type == 'key_action':
                        _, keycode, press_release, delay = action_tuple
                    else:
                        delay = action_tuple[-1]  # Last element is always delay
                    
                    if delay > 0:
                        time.sleep((delay / 1000.0) / self.macro_speed)
                    
                    try:
                        if action_type == 'key':
                            self.execute_keyboard_action(action_tuple[1])
                        elif action_type == 'keyboard':
                            # New simple format - single key press+release
                            self.keyboard.press(action_tuple[1])
                            time.sleep(0.01)
                            self.keyboard.release_all()
                        elif action_type == 'key_action':
                            # Press/release action
                            _, keycode, press_release, delay = action_tuple
                            if press_release == 'press':
                                self.keyboard.press(keycode)
                            elif press_release == 'release':
                                self.keyboard.release(keycode)
                    except Exception as e:
                        print(f"{self.device_name}: Error executing macro action: {e}")
        else:
            parsed = self.parse_macro_legacy(macro)
            if parsed:
                self.execute_keyboard_action(parsed)

    def execute_keyboard_action(self, parsed_action):
        if parsed_action[0] == 'keyboard':
            modifiers = parsed_action[1]
            key = parsed_action[2]
            
            if modifiers:
                self.keyboard.press(*modifiers, key)
                time.sleep(0.01)
                self.keyboard.release_all()
            else:
                self.keyboard.press(key)
                time.sleep(0.01)
                self.keyboard.release_all()

    def run(self):
        print(f"{self.device_name} started - scanning for key presses...")
        print("Matrix scan active...")
        print("ESP32-S3 optimized firmware running...")
        
        if self.bluetooth_enabled:
            print(f"🔵 {self.device_name} Bluetooth mode - waiting for device pairing...")
        else:
            print(f"🔌 {self.device_name} USB mode - ready for input")
        
        # Initialize LED counter for ESP32-S3
        if not hasattr(self, 'led_blink_counter'):
            self.led_blink_counter = 0
        
        while True:
            try:
                # Check connection status periodically
                if self.bluetooth_enabled:
                    self.check_connection_status()
                
                # Scan matrix for key presses
                self.scan_matrix()
                
                # Faster scan rate for ESP32-S3 (dual-core advantage)
                time.sleep(0.0005)  # 500μs instead of 1ms
                
            except KeyboardInterrupt:
                print(f"{self.device_name} firmware stopped by user")
                if self.status_led:
                    self.status_led.value = False
                break
            except Exception as e:
                print(f"{self.device_name}: Error in main loop: {e}")
                time.sleep(0.1)
                gc.collect()

if __name__ == "__main__":
    try:
        kyupad = KyupadFirmware()
        kyupad.run()
        
    except Exception as e:
        print(f"Failed to start Kyupad firmware: {e}")
        import traceback
        traceback.print_exception(type(e), e, e.__traceback__)
        microcontroller.reset()
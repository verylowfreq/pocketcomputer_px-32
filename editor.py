import time
import px
from px import clcd, keyboard


class FullScreenEditor:
    MODE_EDIT = 0
    MODE_MENU = 1
    MODE_INPUT = 2

    def __init__(self, display:px.CLCD, keyboard:px.Keyboard):
        self.display = display
        self.keyboard = keyboard
        self.lines = [""]
        self.cursor_x, self.cursor_y = 0, 0
        self.scroll_top, self.scroll_left = 0, 0
        self.display_rows, self.display_cols = 4, 20
        self.filename = ""
        self.mode = self.MODE_EDIT
        self.menu_items = ["Run", "Save As", "Load", "New"]
        self.menu_selection = 0
        self.input_buffer, self.input_prompt = "", ""
        self.on_input_complete = None

    def show_message(self, message):
        self.display.show_cursor(False, False)
        self.display.set_cursor(3, 0)
        self.display.print(message[:self.display_cols - 2])
        time.sleep(1.5)

    def prompt_for_input(self, prompt, initial_value, callback):
        self.input_prompt = prompt
        self.input_buffer = initial_value
        self.on_input_complete = callback
        self.mode = self.MODE_INPUT

    def save_file(self, filename):
        if not filename:
            self.mode = self.MODE_EDIT; return
        try:
            with open(filename, "w") as f:
                f.write("\n".join(self.lines))
            self.filename = filename
            self.show_message("Saved: " + filename)
        except OSError as e:
            self.show_message("Save Error")
        self.mode = self.MODE_EDIT

    def load_file(self, filename):
        if not filename:
            self.mode = self.MODE_EDIT
            return
        try:
            with open(filename, "r") as f:
                content = f.read()
            self.lines = content.split('\n') if content else [""]
            self.filename = filename
            self.cursor_x, self.cursor_y = 0, 0
            self.scroll_top, self.scroll_left = 0, 0
            self.show_message("Loaded: " + filename)
            time.sleep_ms(1000)
        except OSError:
            self.show_message("Load Error")
        self.mode = self.MODE_EDIT
    
    def run_script(self):
        script_code = "\n".join(self.lines)
        try:
            clcd.set_cursor(0, 0)
            exec(script_code)
            self.show_message("Script executed.")
        except Exception as e:
            self.show_message("Exec Error" + str(e))

    def _draw_editor(self):
        self.display.show_cursor(True, False)
        if self.cursor_y < self.scroll_top:
            self.scroll_top = self.cursor_y
        if self.cursor_y >= self.scroll_top + self.display_rows:
            self.scroll_top = self.cursor_y - self.display_rows + 1
        if self.cursor_x < self.scroll_left:
            self.scroll_left = self.cursor_x
        if self.cursor_x >= self.scroll_left + self.display_cols:
            self.scroll_left = self.cursor_x - self.display_cols + 1
        for i in range(self.display_rows):
            line_idx = self.scroll_top + i
            self.display.set_cursor(i, 0)
            line_str = ""
            if line_idx < len(self.lines):
                text = self.lines[line_idx]
                start = self.scroll_left if line_idx == self.cursor_y else 0
                line_str = text[start : start + self.display_cols]
            while len(line_str) < self.display_cols: line_str += " "
            self.display.print(line_str)
        self.display.set_cursor(self.cursor_y - self.scroll_top, self.cursor_x - self.scroll_left)

    def _draw_menu(self):
        self.display.show_cursor(False, False)
        self.display.clear()
        for i, item in enumerate(self.menu_items):
            self.display.set_cursor(i, 0)
            prefix = "> " if i == self.menu_selection else "  "
            self.display.print(prefix + item)

    def _draw_input_prompt(self):
        self.display.show_cursor(True, False)
        self.display.clear()
        self.display.set_cursor(0, 0); self.display.print(self.input_prompt)
        self.display.set_cursor(1, 0); self.display.print("> " + self.input_buffer)
        self.display.set_cursor(1, 2 + len(self.input_buffer))

    def update_display(self):
        if self.mode == self.MODE_EDIT: self._draw_editor()
        elif self.mode == self.MODE_MENU: self._draw_menu()
        elif self.mode == self.MODE_INPUT: self._draw_input_prompt()

    def process_edit_keypress(self, key):
        current_line = self.lines[self.cursor_y]
        if isinstance(key, str) and key not in ['\n', '\b']:
            self.lines[self.cursor_y] = current_line[:self.cursor_x] + key + current_line[self.cursor_x:]
            self.cursor_x += 1
        elif key == '\n':
            self.lines[self.cursor_y] = current_line[:self.cursor_x]
            self.cursor_y += 1
            self.lines.insert(self.cursor_y, current_line[len(current_line) - len(current_line) + self.cursor_x:])
            self.cursor_x = 0
        elif key == '\b':
            if self.cursor_x > 0:
                self.lines[self.cursor_y] = current_line[:self.cursor_x - 1] + current_line[self.cursor_x:]
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                prev_line_len = len(self.lines[self.cursor_y - 1])
                self.lines[self.cursor_y - 1] += current_line; self.lines.pop(self.cursor_y)
                self.cursor_y -= 1; self.cursor_x = prev_line_len
        elif key == self.keyboard.KC_UP:
            if self.cursor_y > 0: self.cursor_y -= 1
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
        elif key == self.keyboard.KC_DOWN:
            if self.cursor_y < len(self.lines) - 1: self.cursor_y += 1
            self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
        elif key == self.keyboard.KC_LEFT:
            if self.cursor_x > 0:
                self.cursor_x -= 1
            elif self.cursor_y > 0:
                self.cursor_y -= 1
                self.cursor_x = len(self.lines[self.cursor_y])
            self.display.set_cursor(self.cursor_y, self.cursor_x)
        elif key == self.keyboard.KC_RIGHT:
            if self.cursor_x < len(current_line):
                self.cursor_x += 1
            elif self.cursor_y < len(self.lines) - 1:
                self.cursor_y += 1
                self.cursor_x = 0
            self.display.set_cursor(self.cursor_y, self.cursor_x)
        if key in [self.keyboard.KC_UP, self.keyboard.KC_DOWN, '\n', '\b']:
            self.scroll_left = 0

    def process_menu_keypress(self, key):
        if key == self.keyboard.KC_UP:
            self.menu_selection = (self.menu_selection - 1 + len(self.menu_items)) % len(self.menu_items)
        elif key == self.keyboard.KC_DOWN:
            self.menu_selection = (self.menu_selection + 1) % len(self.menu_items)
        elif key == self.keyboard.KC_MENU:
            self.mode = self.MODE_EDIT
        elif key == '\n':
            item = self.menu_items[self.menu_selection]
            if item == "New":
                self.filename = ""
                self.lines = [""]
                self.cursor_x = 0
                self.cursor_y = 0
                self.mode = self.MODE_EDIT

            elif item == "Save As":
                self.prompt_for_input("Save As:", self.filename, self.save_file)

            elif item == "Load":
                self.prompt_for_input("Load File:", "", self.load_file)

            elif item == "Run":
                self.run_script()
                self.mode = self.MODE_EDIT

    def process_input_keypress(self, key):
        if isinstance(key, str) and key not in ['\n', '\b']:
            self.input_buffer += key
        elif key == '\b':
            self.input_buffer = self.input_buffer[:-1]
        elif key == '\n':
            self.on_input_complete(self.input_buffer)
        elif key == self.keyboard.KC_MENU:
            self.mode = self.MODE_EDIT

    def run(self):
        self.display.clear()

        while True:
            self.update_display()
            key = None
            while key is None:
                keyboard.update()
                key = keyboard.get_new_key()
                time.sleep_ms(10)

            if self.mode == self.MODE_EDIT:
                if key == self.keyboard.KC_MENU:
                    self.mode = self.MODE_MENU
                    self.menu_selection = 0
                elif key == self.keyboard.KC_RUN:
                    self.run_script()
                    self.mode = self.MODE_EDIT
                else: self.process_edit_keypress(key)

            elif self.mode == self.MODE_MENU:
                self.process_menu_keypress(key)

            elif self.mode == self.MODE_INPUT:
                self.process_input_keypress(key)

# ----------------------------------------------------------------
# メイン処理
# ----------------------------------------------------------------
# PIN_SCL = machine.Pin(2); PIN_SDA = machine.Pin(1)
# wire = machine.I2C(0, scl=PIN_SCL, sda=PIN_SDA, freq=400000)
# south = px.SubMCU(wire)
# south.begin()
# keyboard = px.Keyboard()


def show_banner():
    import sys
    import gc

    clcd.clear()
    clcd.set_cursor(0, 0)
    print("PocketComputer PX-32")
    clcd.set_cursor(1, 3)
    print("by Mitsumine Suzu")
    clcd.set_cursor(2, 0)
    print("MicroPython ")
    print(".".join([str(v) for v in sys.implementation.version[0:3]]))
    clcd.set_cursor(3, 0)
    print(sys.platform)
    print(" FREE: ")
    print(gc.mem_alloc())
    clcd.show_cursor(True, False)


def main(banner:bool=False):
    if banner:
        show_banner()
        time.sleep_ms(2000)

    editor = FullScreenEditor(clcd, keyboard)
    editor.run()

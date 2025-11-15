from micropython import const
import os
from px import clcd, keyboard

class Files:
    CLCD_ROWS = 4
    CLCD_COLS = 20

    def __init__(self) -> None:
        self.filelist = []
        self.cursor_index = 0

    def main(self) -> None:
        clcd.show_cursor(False, False)
        self.update_filelist()
        self.draw_file_list()
        while True:
            key = None
            while key is None:
                keyboard.update()
                key = keyboard.get_new_key()
            self.process_input(key)
            self.draw_file_list()


    def update_filelist(self) -> None:
        self.filelist = os.listdir("/")

    def execute_script_from_file(self, filepath:str) -> None:
        with open(filepath, "r") as f:
            content = f.read()
        try:
            clcd.set_cursor(0, 0)
            exec(content)
            time.sleep_ms(1000)
            clcd.set_cursor(3, 0)
            clcd.print("Executed.")
            time.sleep_ms(1000)

        except Exception as e:
            clcd.set_cursor(3, 0)
            print("E:" + str(e))

    def draw_file_list(self) -> None:
        clcd.clear()
        if len(self.filelist) == 0:
            clcd.set_cursor(0, 0)
            clcd.print("(No file)")
            return

        draw_start_idx = 0
        draw_start_idx = (self.cursor_index // self.CLCD_ROWS) * self.CLCD_ROWS
        draw_end_idx = min(len(self.filelist), draw_start_idx + self.CLCD_ROWS)

        files = self.filelist[draw_start_idx:draw_end_idx]
        for i, f in enumerate(files):
            clcd.set_cursor(i, 2)
            clcd.print(f[:self.CLCD_COLS - 3])

        draw_cursor_idx = self.cursor_index - draw_start_idx
        clcd.set_cursor(draw_cursor_idx, 0)
        clcd.print(">")


    def process_input(self, key) -> None:
        if key is None:
            return
        elif isinstance(key, str):
            if key == '\n':
                if len(self.filelist) > 0:
                    # Execute the file
                    filepath = self.filelist[self.cursor_index]
                    self.execute_script_from_file(filepath)
        elif key == keyboard.KC_UP:
            if self.cursor_index > 0:
                self.cursor_index -= 1
        elif key == keyboard.KC_DOWN:
            if self.cursor_index < len(self.filelist) - 1:
                self.cursor_index += 1

def main():
    app = Files()
    app.main()

main()

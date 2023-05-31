import os
import tkinter as tk
from pathlib import Path
from random import randint

import PIL.Image
import PIL.ImageTk
import pystray
import win32api
import win32con
import win32gui
from config import Config


class App:
    def __init__(self, *args, **kwargs) -> None:
        self.root = tk.Tk()
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.root.bind("<Button-1>", self.overlay_move_start)
        self.root.bind("<ButtonRelease-1>", self.overlay_move_stop)
        self.root.bind("<B1-Motion>", self.overlay_drag)
        self.trayicon_menu_clickthrough_state = False

        self.root.overrideredirect(True)
        self.root.config(bg=Config.DARK_BG_IMG_COLOR)
        self.root.attributes(
            "-alpha", 0.75, "-transparentcolor", Config.DARK_BG_IMG_COLOR, "-topmost", 1
        )

        # canvas background
        self.bg_canvas = tk.Canvas(
            self.root, bg=Config.DARK_BG_IMG_COLOR, highlightthickness=0
        )
        img_frame = PIL.ImageTk.PhotoImage(file=str(Config.LIGHT_BG_IMG))
        self.img_id = self.bg_canvas.create_image(0, 0, image=img_frame, anchor="nw")
        self.bg_canvas.pack()
        self.fit_bg_canvas()

        self.text = tk.Label(
            self.root,
            text="",
            fg=Config.LIGHT_TXT_FG_COLOR,
            bg=Config.LIGHT_TXT_BG_COLOR,
            bd=0,
            pady=0,
        )
        self.text.place(x=50, y=50)

        if self.trayicon_menu_clickthrough_state:
            self.set_overlay_clickthrough(self.bg_canvas.winfo_id())
        self.set_trayicon()
        self.update_label_text()
        self.root.mainloop()

    def update_label_text(self):
        self.text["text"] = randint(1000, 100000)
        self.root.after(1000, self.update_label_text)  # run itself again after 1000 ms

    def fit_bg_canvas(self) -> None:
        bbox = self.bg_canvas.bbox(self.img_id)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = self.screenwidth / 2 - w / 2, self.screenheight / 2 - h / 2
        self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.bg_canvas.configure(width=w, height=h)

    # drag overlay
    def overlay_move_start(self, event) -> None:
        self.cursor_x = event.x
        self.cursor_y = event.y

    def overlay_move_stop(self, event):
        self.cursor_x = 0
        self.cursor_y = 0

    def overlay_drag(self, event) -> None:
        delta_x = event.x - self.cursor_x
        delta_y = event.y - self.cursor_y
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{x}+{y}")

    # click through
    def set_overlay_clickthrough(self, hwnd) -> None:
        # https://stackoverflow.com/questions/67544105/click-through-tkinter-windows/67545792#67545792
        try:
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        except Exception as e:
            print(e)

    def unset_overlay_clickthrough(self, hwnd) -> None:
        # https://stackoverflow.com/questions/67544105/click-through-tkinter-windows/67545792#67545792
        try:
            # Calling the function again sets the extended style of the window to zero, reverting to a standard window
            win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 0)
            # Remove the always on top property again, in case always on top was set to false in options
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_NOTOPMOST,
                self.root.winfo_x(),
                self.root.winfo_y(),
                self.root.winfo_width(),
                self.root.winfo_width(),
                0,
            )
        except Exception as e:
            print(e)

    # trayicon
    def set_trayicon(self) -> None:
        image = PIL.Image.open(str(Config.APP_LOGO_ICO))
        self.trayicon = pystray.Icon(
            "MeuTrayIcon",
            image,
            menu=pystray.Menu(
                pystray.MenuItem(
                    "Enable Clickthourght",
                    self.trayicon_menu_click_clickthrough,
                    checked=lambda item: self.trayicon_menu_clickthrough_state,
                ),
                pystray.MenuItem(
                    "Quit",
                    self.trayicon_menu_click_generic,
                ),
            ),
        )
        self.trayicon.run_detached()

    def trayicon_menu_click_clickthrough(self) -> None:
        if self.trayicon_menu_clickthrough_state:
            self.unset_overlay_clickthrough(hwnd=self.bg_canvas.winfo_id())
            self.trayicon_menu_clickthrough_state = False
        else:
            self.set_overlay_clickthrough(hwnd=self.bg_canvas.winfo_id())
            self.trayicon_menu_clickthrough_state = True

    def trayicon_menu_click_generic(self, icon, menu_item) -> None:
        if str(menu_item) == "Quit":
            self.trayicon.stop()
            os._exit(0)
        elif str(menu_item) == "X":
            # print("X was clicked")
            pass


if __name__ == "__main__":
    app = App()

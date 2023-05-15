import os
import time
import tkinter as tk
from functools import partial
from pathlib import Path
from threading import Event, Thread

from config import Config
from infi.systray import SysTrayIcon


class TrayIcon:
    def __init__(self):
        menu_options = ()
        path_icon = str(Path(Config.BASE_IMG_PATH, Config.APP_LOGO_ICO))
        systray = SysTrayIcon(
            path_icon,
            "My System Tray Icon",
            menu_options,
            on_quit=lambda _: os._exit(0),
        )
        systray.start()


class Timer:
    def __init__(self, seconds: int) -> None:
        self.time = seconds
        self.hour = tk.StringVar()
        self.min = tk.StringVar()
        self.sec = tk.StringVar()
        self.btn_start = tk.Button()
        self.btn_reset = tk.Button()
        self.event = Event()


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Deletes Windows' default title bar

        self.root.wm_attributes("-alpha", 0.75)
        self.root.wm_attributes(
            "-transparentcolor", "grey15"
        )  # str_a_ange color to avoid jagged borders
        self.root.wm_attributes("-topmost", True)
        self.root.bind("<Button-1>", self.click)
        self.root.bind("<B1-Motion>", self.drag)

        self.font = Config.FONT_DEFAULT
        self.font_label = Config.FONT_LABEL
        self.font_input = Config.FONT_INPUT
        self.font_btn = Config.FONT_BTN

        self.bgframe = BackgroundImgFrame()
        self.bgframe.pack(side="top", fill="both", expand=True)

        self._padx = 0
        self._offsetx = 0
        self._offsety = 0
        self.timers = []
        for seconds in Config.TIMERS:
            self.timers.append(Timer(seconds=seconds))
        self.set_overlay_content()

        TrayIcon()
        self.root.eval("tk::PlaceWindow . center")
        self.root.mainloop()

    def click(self, event) -> None:
        self._offsetx = event.x
        self._offsety = event.y

    def drag(self, event) -> None:
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry("+{x}+{y}".format(x=x, y=y))

    ###############################################################
    def set_overlay_content(self) -> None:
        row_y = 50

        # LOGO
        image = tk.PhotoImage(file=str(Path(Config.BASE_IMG_PATH, Config.APP_LOGO_PNG)))
        image_logo = image.subsample(9)
        self.logo = tk.Label(
            self.root, border=0, bg=Config.DARK_BG_COLOR, image=image_logo
        )
        self.logo.image = image_logo  # type: ignore
        self.logo.place(x=11, y=13)
        self.logo_label = tk.Label(
            self.root,
            text="Timer",
            font=self.font_label,
            fg=Config.DARK_FG_COLOR,
            bg=Config.DARK_BG_COLOR,
            bd=0,
            pady=0,
        )
        self.logo_label.place(x=37, y=13)

        # TOP BUTTONS
        self.button_reset_all = tk.Button(
            self.root,
            text="Reset",
            font=self.font_btn,
            fg=Config.DARK_FG_COLOR,
            bg=Config.DARK_BG_COLOR,
            bd=0,
            pady=0,
            command=self.timers_reset_all,
        )
        self.button_reset_all.place(x=106, y=10)
        self.button_quit = tk.Button(
            self.root,
            text="Quit",
            font=self.font_btn,
            fg=Config.DARK_FG_COLOR,
            bg=Config.DARK_BG_COLOR,
            bd=0,
            pady=0,
            command=self.quit_app,
        )
        self.button_quit.place(x=165, y=10)

        # Hour
        self.header_hour_text = tk.StringVar()
        self.header_hour_text.set("Hour")
        self.header_hour_label = self._create_label(
            self.header_hour_text, 10, Config.DARK_HEAD_TEXT_FG
        )
        self.header_hour_label.place(x=self._padx + 10, y=row_y)

        # Min
        self.header_min_text = tk.StringVar()
        self.header_min_text.set("Min")
        self.header_min_label = self._create_label(
            self.header_min_text, 10, Config.DARK_HEAD_TEXT_FG
        )
        self.header_min_label.place(x=self._padx + 45, y=row_y)

        # Sec
        self.header_sec_text = tk.StringVar()
        self.header_sec_text.set("Sec")
        self.header_sec_label = self._create_label(
            self.header_sec_text, 10, Config.DARK_HEAD_TEXT_FG
        )
        self.header_sec_label.place(x=self._padx + 80, y=row_y)

        for idx, seconds in enumerate(Config.TIMERS):
            self.create_timer_row(idx, seconds)

    def create_timer_row(self, idx: int, seconds: int) -> None:
        row_y = 80 + (idx * 40)

        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        self.timers[idx].hour.set(str(h))
        self.timers[idx].min.set(str(m))
        self.timers[idx].sec.set(str(s))

        hour_entry = tk.Entry(
            self.root,
            width=3,
            font=self.font_input,
            textvariable=self.timers[idx].hour,
        )
        hour_entry.place(x=self._padx + 10, y=row_y)

        min_entry = tk.Entry(
            self.root,
            width=3,
            font=self.font_input,
            textvariable=self.timers[idx].min,
        )
        min_entry.place(x=self._padx + 45, y=row_y)

        sec_entry = tk.Entry(
            self.root,
            width=3,
            font=self.font_input,
            textvariable=self.timers[idx].sec,
        )
        sec_entry.place(x=self._padx + 80, y=row_y)

        # button [start] [reset]
        self.timers[idx].btn_start = tk.Button(
            self.root,
            text="Start",
            font=self.font_btn,
            fg=Config.DARK_FG_COLOR,
            bg=Config.DARK_BG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.timer_start, idx=idx),
        )
        self.timers[idx].btn_start.place(x=self._padx + 120, y=row_y)

        self.timers[idx].btn_reset = tk.Button(
            self.root,
            text="Reset",
            font=self.font_btn,
            fg=Config.DARK_FG_COLOR,
            bg=Config.DARK_BG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.timer_reset, idx=idx),
        )
        self.timers[idx].btn_reset.place(x=self._padx + 165, y=row_y)

    def _create_label(self, text: tk.StringVar, size: int, color: str) -> tk.Label:
        return tk.Label(
            self.root,
            textvariable=text,
            font=self.font_label,
            fg=color,
            bg=Config.DARK_BG_COLOR,
            bd=0,
            padx=0,
            pady=0,
        )

    # Button Commands
    def timer_start(self, idx: int) -> None:
        try:
            self.timers[idx].btn_start["text"] = "Stop"
            self.timers[idx].btn_start["command"] = partial(self.timer_stop, idx=idx)
            self.timers[idx].btn_reset["state"] = "disabled"

            thread = Thread(target=self.task_timer, args=(idx,))
            thread.start()
        except:
            print("Please input the right value (numbers only)")

    def timer_stop(self, idx: int) -> None:
        self.timers[idx].event.set()
        self.timers[idx].btn_reset["state"] = "normal"

    def timer_reset(self, idx: int) -> None:
        self.timers[idx].event.clear()
        for i, timer in enumerate(self.timers):
            if i == idx:
                self.timers[idx].btn_start["text"] = "Start"
                self.timers[idx].btn_start["state"] = "normal"
                self.timers[idx].btn_start["command"] = partial(
                    self.timer_start, idx=idx
                )
                self.timers[idx].btn_reset["state"] = "normal"

                m, s = divmod(self.timers[idx].time, 60)
                h, m = divmod(m, 60)
                self.timers[idx].hour.set(str(h))
                self.timers[idx].min.set(str(m))
                self.timers[idx].sec.set(str(s))
                return None

    def timers_reset_all(self) -> None:
        for idx, timer in enumerate(self.timers):
            self.timer_stop(idx)
            self.timers[idx].btn_start["state"] = "normal"
            self.timers[idx].btn_start["text"] = "Start"
            self.timers[idx].btn_start["command"] = partial(self.timer_start, idx=idx)

            m, s = divmod(self.timers[idx].time, 60)
            h, m = divmod(m, 60)
            self.timers[idx].hour.set(str(h))
            self.timers[idx].min.set(str(m))
            self.timers[idx].sec.set(str(s))

    def quit_app(self) -> None:
        os._exit(0)

    # Thread Task: timer
    def task_timer(self, idx: int) -> None:
        seconds = (
            int(self.timers[idx].hour.get()) * 3600
            + int(self.timers[idx].min.get()) * 60
            + int(self.timers[idx].sec.get())
        )
        while seconds > -1:
            if self.timers[idx].event.is_set():
                self.timers[idx].event.clear()
                self.timers[idx].btn_start["text"] = "Start"
                self.timers[idx].btn_start["command"] = partial(
                    self.timer_start, idx=idx
                )
                self.timers[idx].btn_reset["state"] = "normal"
                self.root.update()
                break
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            self.timers[idx].hour.set("{0:2d}".format(h))
            self.timers[idx].min.set("{0:2d}".format(m))
            self.timers[idx].sec.set("{0:2d}".format(s))
            self.root.update()
            time.sleep(1)
            if seconds == 0:
                self.timers[idx].btn_start["text"] = "Done"
                self.timers[idx].btn_start["state"] = "disabled"
                self.timers[idx].btn_start["command"] = None

                self.timers[idx].btn_reset["state"] = "normal"
                break
            seconds -= 1


class BackgroundImgFrame(tk.Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        image = tk.PhotoImage(file=str(Path(Config.BASE_IMG_PATH, Config.DARK_BG_IMG)))
        self.background_image = image.zoom(2).subsample(3)
        self.background = tk.Label(
            self, border=0, bg="grey15", image=self.background_image
        )
        self.background.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = App()

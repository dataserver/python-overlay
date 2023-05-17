import os
import tkinter as tk
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from random import randint

import PIL.Image
import PIL.ImageTk
import pystray
import vlc
import win32api
import win32con
import win32gui
from config import Config


class App:
    def __init__(self, *args, **kwargs) -> None:
        self.root = tk.Tk()
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.root.bind("<Button-1>", self.overlay_click)
        self.root.bind("<B1-Motion>", self.overlay_drag)
        self.trayicon_menu_clickthrough_state = False
        self.playlist = []
        self.volume = 50
        # Create a basic vlc instance
        self.current_music_index = 1
        self.media_player = vlc.MediaListPlayer()
        self.instance_player = vlc.Instance()
        self.media_list = self.instance_player.media_list_new()  # type: ignore

        self.parsem3u(Config.M3U_PLAYLIST)

        self.vlc_is_paused = False

        _color_bg = "grey15"  # same color to make it works
        self.root.overrideredirect(True)
        self.root.config(bg=Config.LIGHT_BG_COLOR)
        self.root.attributes(
            "-alpha", 0.75, "-transparentcolor", _color_bg, "-topmost", 1
        )

        # canvas background
        self.bg_canvas = tk.Canvas(self.root, bg=_color_bg, highlightthickness=0)
        img_frame = PIL.ImageTk.PhotoImage(file=str(Config.LIGHT_BG_IMG))
        self.img_id = self.bg_canvas.create_image(0, 0, image=img_frame, anchor="nw")
        self.bg_canvas.pack()
        self.fit_bg_canvas()

        self.text = tk.Label(
            self.root,
            text="",
            font=Config.FONT_BTN,
            fg=Config.LIGHT_FG_COLOR,
            bg=Config.LIGHT_BG_COLOR,
            bd=0,
            pady=0,
            wraplength=250,
            justify="center",
        )
        self.text.place(x=50, y=50)

        self.button_quit = tk.Button(
            self.root,
            text="x",
            font=Config.FONT_BTN,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=lambda: os._exit(0),
        )
        self.button_quit.place(x=290, y=5)

        _control_x_pad = 70
        _control_y_pad = 100
        # https://unicode.org/emoji/charts/emoji-list.html
        # ⏩⏭▶ ◀⏪⏮ ⏹⏸
        #  🔇 🔉 🔈 🔊
        # play
        self.button_play_pause = tk.Button(
            self.root,
            text="▶",
            font=Config.FONT_BTN_MEDIA_CONTROL,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.media_btn_command, btn="play_pause"),
        )
        self.button_play_pause.place(x=_control_x_pad + 0, y=_control_y_pad)
        # prev
        self.button_prev = tk.Button(
            self.root,
            text="⏮",
            font=Config.FONT_BTN_MEDIA_CONTROL,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.media_btn_command, btn="prev"),
        )
        self.button_prev.place(x=_control_x_pad + 30, y=_control_y_pad)
        # stop
        self.button_stop = tk.Button(
            self.root,
            text="⏹",
            font=Config.FONT_BTN_MEDIA_CONTROL,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.media_btn_command, btn="stop"),
        )
        self.button_stop.place(x=_control_x_pad + 60, y=_control_y_pad)
        # next
        self.button_next = tk.Button(
            self.root,
            text="⏭",
            font=Config.FONT_BTN_MEDIA_CONTROL,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.media_btn_command, btn="next"),
        )
        self.button_next.place(x=_control_x_pad + 90, y=_control_y_pad)
        # volume down
        self.button_vol_down = tk.Button(
            self.root,
            text="🔉",
            font=Config.FONT_BTN_MEDIA_CONTROL,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.media_btn_command, btn="vol_down"),
        )
        self.button_vol_down.place(x=_control_x_pad + 120, y=_control_y_pad)
        # volume up
        self.button_vol_up = tk.Button(
            self.root,
            text="🔊",
            font=Config.FONT_BTN_MEDIA_CONTROL,
            fg=Config.DARK_BG_COLOR,
            bg=Config.DARK_FG_COLOR,
            bd=0,
            pady=0,
            command=partial(self.media_btn_command, btn="vol_up"),
        )
        self.button_vol_up.place(x=_control_x_pad + 150, y=_control_y_pad)

        if self.trayicon_menu_clickthrough_state:
            self.set_overlay_clickthrough(self.bg_canvas.winfo_id())
        self.set_trayicon()
        self.update_label_text()
        self.root.mainloop()

    # VLC
    def parsem3u(self, path: Path):
        infile = open(str(path), "r")
        line = infile.readline()
        if not line.startswith("#EXTM3U"):
            return

        for line in infile:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                # pull length and title from #EXTINF line
                length, title = line.split("#EXTINF:")[1].split(",", 1)
            elif len(line) != 0:
                # pull song path from all other, non-blank lines
                media = self.instance_player.media_new(line)  # type: ignore
                self.media_list.add_media(media)
        infile.close()
        self.media_player.set_media_list(self.media_list)  # type: ignore

    def media_btn_command(self, btn: str) -> None:
        def clamp(val: int, min: int, max: int) -> int:
            if val < min:
                return min
            if val > max:
                return max
            return val

        # print(f"action: {btn}")
        if btn == "play_pause":
            if self.media_player.is_playing():  # type: ignore
                self.media_player.pause()  # type: ignore
                self.button_play_pause["text"] = "▶"
                self.vlc_is_paused = True
            else:
                self.media_player.play()  # type: ignore
                self.button_play_pause["text"] = "⏸"
                self.vlc_is_paused = False

        elif btn == "stop":
            self.button_play_pause["text"] = "▶"
            self.media_player.stop()  # type: ignore
        elif btn == "prev":
            self.button_play_pause["text"] = "⏸"
            self.media_player.previous()  # type: ignore
        elif btn == "next":
            self.button_play_pause["text"] = "⏸"
            self.media_player.next()  # type: ignore
        elif btn == "vol_down":
            self.volume = clamp(self.volume - 5, 0, 100)
            self.media_player.get_media_player().audio_set_volume(self.volume)  # type: ignore
        elif btn == "vol_up":
            self.volume = clamp(self.volume + 5, 0, 100)
            self.media_player.get_media_player().audio_set_volume(self.volume)  # type: ignore
        else:
            pass

    def update_label_text(self):
        item = self.media_player.get_media_player().get_media()  # type: ignore
        if item is not None:
            song = item.get_meta(0)
            singer = item.get_meta(1)
            self.text["text"] = f"{singer} - {song}"
        self.root.after(1000, self.update_label_text)  # run itself again after 1000 ms

    def fit_bg_canvas(self) -> None:
        bbox = self.bg_canvas.bbox(self.img_id)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = self.screenwidth / 2 - w / 2, self.screenheight / 2 - h / 2
        self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.bg_canvas.configure(width=w, height=h)

    # drag overlay
    def overlay_click(self, event) -> None:
        self._offsetx = event.x
        self._offsety = event.y

    def overlay_drag(self, event) -> None:
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry("+{x}+{y}".format(x=x, y=y))

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

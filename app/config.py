import os
from dataclasses import dataclass
from pathlib import Path

# for VLC demo
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")


@dataclass
class Config:
    BASE_PATH: Path = Path(__file__).parent

    APP_LOGO_PNG: Path = Path(BASE_PATH, "img", "clock.png")
    APP_LOGO_ICO: Path = Path(BASE_PATH, "img", "clock.ico")
    M3U_PLAYLIST: Path = Path(BASE_PATH, "playlist.m3u")

    LIGHT_BG_IMG: Path = Path(BASE_PATH, "img", "window_light.png")
    LIGHT_BG_IMG_COLOR: str = "#FFFFFF"
    LIGHT_HEAD_TEXT_FG: str = "yellow"
    LIGHT_TXT_BG_COLOR: str = "#FFFFFF"
    LIGHT_TXT_FG_COLOR: str = "#1F1F1F"
    LIGHT_BTN_FG_COLOR: str = "#FFFFFF"
    LIGHT_BTN_BG_COLOR: str = "#262626"

    DARK_BG_IMG: Path = Path(BASE_PATH, "img", "window_dark.png")
    DARK_BG_IMG_COLOR: str = "#262626"
    DARK_HEAD_TEXT_FG: str = "yellow"
    DARK_TXT_BG_COLOR: str = "#262626"
    DARK_TXT_FG_COLOR: str = "#FFFFFF"
    DARK_BTN_FG_COLOR: str = "#FFFFFF"
    DARK_BTN_BG_COLOR: str = "#262626"

    FONT_DEFAULT: tuple = ("Segoe UI", 10, "normal")
    FONT_LABEL: tuple = ("Segoe UI", 10, "normal")
    FONT_INPUT: tuple = ("Tahoma", 10, "bold")
    FONT_BTN: tuple = ("Segoe UI", 10, "bold")
    FONT_BTN_MEDIA_CONTROL: tuple = ("Segoe UI", 11, "normal")

    TIMERS: tuple = (5, 60, 300, 600, 1200, 3600)  # in seconds

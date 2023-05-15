from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    BASE_PATH: Path = Path(__file__).parent
    BASE_IMG_PATH: Path = Path(BASE_PATH, "img")

    APP_LOGO_PNG: str = "clock.png"
    APP_LOGO_ICO: str = "clock.ico"

    LIGHT_BG_IMG: str = "window_dark.png"
    LIGHT_HEAD_TEXT_FG: str = "yellow"
    LIGHT_BG_COLOR: str = "#FFFFFF"
    LIGHT_FG_COLOR: str = "#1F1F1F"

    DARK_BG_IMG: str = "window_light.png"
    DARK_HEAD_TEXT_FG: str = "yellow"
    DARK_BG_COLOR: str = "#1F1F1F"
    DARK_FG_COLOR: str = "#FFFFFF"

    TIMERS: tuple = (5, 60, 300, 600, 1200, 3600)  # in seconds
    FONT_DEFAULT: tuple = ("Segoe UI", 10, "normal")
    FONT_LABEL: tuple = ("Segoe UI", 10, "normal")
    FONT_INPUT: tuple = ("Tahoma", 10, "bold")
    FONT_BTN: tuple = ("Segoe UI", 10, "bold")

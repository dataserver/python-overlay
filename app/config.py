from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    BASE_PATH: Path = Path(__file__).parent
    BASE_IMG_PATH: Path = Path(BASE_PATH, "img")

    APP_BG_IMG: str = "window.png"
    APP_BG_COLOR: str = "#1F1F1F"
    APP_LOGO_PNG: str = "clock.png"
    APP_LOGO_ICO: str = "clock.ico"

    APP_BTN_BG_COLOR: str = "#1F1F1F"
    APP_BTN_FG_COLOR: str = "#FFFFFF"
    TIMERS: tuple = (5, 60, 300, 600, 1200, 3600)  # in seconds

    FONT_DEFAULT: tuple = ("Segoe UI", 10, "normal")
    FONT_LABEL: tuple = ("Segoe UI", 10, "normal")
    FONT_INPUT: tuple = ("Tahoma", 10, "bold")
    FONT_BTN: tuple = ("Segoe UI", 10, "bold")

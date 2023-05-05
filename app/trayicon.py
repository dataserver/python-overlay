import os
from pathlib import Path

from config import Config
from infi.systray import SysTrayIcon

# https://github.com/Infinidat/infi.systray
# def hello(sysTrayIcon):
#     print("Hello World.")


class TrayIcon:

    """System tray icon"""

    def __init__(self):
        # menu_options = (('Show', None, lambda _: print('Show')),
        #                 ('Hide', None, lambda _: print('Hide')),
        #                 ('Hello', "hello.ico", hello)
        #                 )
        menu_options = ()
        path_icon = str(Path(Config.BASE_IMG_PATH, Config.APP_LOGO_ICO))

        systray = SysTrayIcon(
            path_icon,
            "My System Tray Icon",
            menu_options,
            on_quit=lambda _: os._exit(0),
        )
        systray.start()

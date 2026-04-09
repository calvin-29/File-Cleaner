import pystray
import PIL.Image
import os
from sort import sorting
from threading import Thread
import sys

tray_running = False
last_time = None

def background(app, configs, scrollable_frame, save_folder):
    global tray_running, last_time

    def open_app(icon, q):
        global tray_running

        if q.text == "Open":
            app.after(0, app.deiconify)
            icon.stop()
            tray_running = False

        elif q.text == "Close":
            icon.stop()
            app.destroy()
    
    if not tray_running:
        path = os.path.dirname(sys.executable) if hasattr(sys, "frozen") else os.path.dirname(os.path.abspath(__file__))
        icon = pystray.Icon(
            name="Organize files in the shadows",
            icon=PIL.Image.open(os.path.join(path, "file_clean.png")),
            title="File Cleaner",
            menu=pystray.Menu(
                pystray.MenuItem("Open", open_app),
                pystray.MenuItem("Close", open_app)
            )
        )
        Thread(target=icon.run, daemon=True).start()
        tray_running = True
    
    home_download = os.path.join(os.path.expanduser("~"), "Downloads")
    dirr = configs["last_folder"] if configs["last_folder"] else home_download

    if app.winfo_exists():
        if app.state() == "withdrawn":
            if last_time != os.path.getmtime(dirr):
                sorting(app, dirr, False, configs, save_folder, scrollable_frame)
                last_time = os.path.getmtime(dirr)
            app.after(5000, lambda: background(app, configs, scrollable_frame, save_folder))

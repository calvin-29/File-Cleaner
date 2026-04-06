import pystray
import PIL.Image
import os
import sys
from sort import sorting
from threading import Thread

def get_folder_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

tray_running = False
app_open = False
last_size = None

def background(app, configs, scrollable_frame, save_folder):
    global tray_running, last_size, app_open

    def open_app(icon, q):
        global tray_running

        if q.text == "Open":
            app.after(0, app.deiconify)
            app_open = True

        elif q.text == "Close":
            icon.stop()
            app.destroy()
    
    app.withdraw()

    if not tray_running:
        icon = pystray.Icon(
            name="Organize files in the shadows",
            icon=PIL.Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_clean.png")),
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
    
    if last_size != get_folder_size(dirr):
        sorting(app, dirr, False, configs, save_folder, scrollable_frame)
        last_size = get_folder_size(dirr)
    if not app_open:
        app.after(100000, lambda: background(app, configs, scrollable_frame, save_folder))

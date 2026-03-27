import pystray
import PIL.Image
import os
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
last_size = None

def background(app, configs, scrollable_frame, save_folder):
    global tray_running, last_size

    def open_app(icon, q):
        global tray_running

        if q.text == "Open":
            app.after(0, app.deiconify)

        elif q.text == "Close":
            app.destroy()
            icon.stop()

            tray_running = False

    app.withdraw()

    if not tray_running:
        icon = pystray.Icon(
            name="Organize files in the shadows",
            icon=PIL.Image.open("file_clean.png"),
            title="File Cleaner",
            menu=pystray.Menu(
                pystray.MenuItem("Open", open_app),
                pystray.MenuItem("Close", open_app)
            )
        )
        Thread( target=icon.run, daemon=True).start()
        tray_running = True

    home_download = os.path.join(os.path.expanduser("~"), "Downloads")
    dirr = configs["last_folder"] if configs["last_folder"] else home_download
    
    
    print(last_size == get_folder_size(dirr))
    print(last_size, get_folder_size(dirr))
    if last_size != get_folder_size(dirr):
        sorting(app, dirr, False, configs, save_folder, scrollable_frame)
        last_size = get_folder_size(dirr)
    app.after(100000, lambda: background(app, configs, scrollable_frame, save_folder))


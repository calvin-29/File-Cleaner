#  import necessary modules
import os
import json 
import sys
from tkinter import (Tk, Label, Button, Frame, Canvas,
                      Scrollbar, messagebox, filedialog, PhotoImage
                    )
from sort import sorting, create_folders
from settings import config, remove_config, setting
from back import background
from startup import setup_startup

# name:list_of_extenstions
configs = {
    "folders" : ["Folders", "Images", "Audios", "Videos", "Others", "Apps", "Compressed", "Documents"],
    "images" : [".jpg", ".png", ".gif", ".webp", ".jfif"],
    "audios" : [".mp3", ".flac", ".ogg", ".wav"],
    "apps" : [".msi", ".exe"],
    "videos" : [".mp4", ".mkv", ".mov", ".avi", "webm", "ts", ".asf", ".wmv"],
    "compressed" : [".zip", ".7z", ".tar", ".wim", "gz"],
    "documents" : [".docx", ".pptx", ".txt", ".rtf", ".chm", ".html", ".htm", ".mhtml", ".pdf"],
    "last_folder": "",
    "start": False
}

save_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "CCU Software", "File Cleaner")

# create save folder if not available
if not os.path.exists(save_folder):
    os.makedirs(save_folder, exist_ok=True)

# load the config file, if not available create it
try:
    with open(os.path.join(save_folder, "config.json"), "r") as f:
        configs = json.load(f)
except FileNotFoundError:
    with open(os.path.join(save_folder, "config.json"), "w") as f:
        json.dump(configs, f, indent=4)
# if it is empty or edited, put the default configuration
except json.decoder.JSONDecodeError:
     with open(os.path.join(save_folder, "config.json"), "w") as f:
        json.dump(configs, f, indent=4)

# function to open directory
def open_dir(dir=None, can_open=True):
    home_download = os.path.join(os.path.expanduser("~"), "Downloads")
    directory = ""
    if dir == None:
        directory = filedialog.askdirectory(initialdir=home_download)
    else:
        directory = dir
    # if it is not cancelled create folders and sort files
    if directory != "":
        configs["last_folder"] = directory
        with open(os.path.join(save_folder, "config.json"), "w") as f:
            json.dump(configs, f, indent=4)
        create_folders(directory, configs, scrollable_frame)
        sorting(app, directory, can_open, configs, save_folder, scrollable_frame)

# function to clear all the labels in the log frame
def clear():
    for i in scrollable_frame.winfo_children():
        i.destroy()

# function to update the canvas region when the scrollbar is moved
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

#  main app configuration
app = Tk()
app.geometry("540x450+100+100")
app.title("File Organizer")
app.config(bg="darkblue")
app.iconphoto(True, PhotoImage(file=os.path.join(os.path.split(__file__)[0], "file_clean.png")))

#  Create a top frame for the buttons and label
top_frame = Frame(app, bg="darkblue")
top_frame.pack(side="top", fill="x")

#  Header label
lbl = Label(top_frame, text="File Organizer", fg="white", bg="darkblue", font="Consolas 13 bold")
lbl.pack(side="top", pady=30)

#  Buttons inside top_frame
btn = Button(top_frame, text="Open Directory", fg="white", bg="black", font="Consolas 11", command=open_dir)
btn.pack(side="left", padx=5, ipadx=3, ipady=3)

btn2 = Button(top_frame, text="Clear", fg="white", bg="red", font="Consolas 11", command=clear)
btn2.pack(side="left", padx=5, ipadx=3, ipady=3)

btn3 = Button(top_frame, text="Add Config", fg="white", bg="green", font="Consolas 11", command=lambda: config(app, save_folder, configs))
btn3.pack(side="left", padx=5, ipadx=3, ipady=3)

btn4 = Button(top_frame, text="Remove Config", fg="white", bg="red", font="Consolas 11", command=lambda: remove_config(app, save_folder, configs))
btn4.pack(side="left", padx=5, ipadx=3, ipady=3)

btn5 = Button(top_frame, text="Settings", fg="white", bg="black", font="Consolas 11", command=lambda: setting(app, save_folder, configs))
btn5.pack(side="left", padx=5, ipadx=3, ipady=3)

#  Log label
lbl2 = Label(app, text="Logs", fg="white", bg="darkblue", font="Consolas 13 bold")
lbl2.pack(side="top", padx=10, pady=13)

#  Now add the canvas below everything
canvas = Canvas(app)
canvas.pack(side="top", fill="both", expand=True, padx=10, pady=5)

#  scrollbar to scroll through events
scrollbar = Scrollbar(canvas, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

#  frame that events are stored
scrollable_frame = Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="center")

# update frame when configured
scrollable_frame.bind("<Configure>", update_scroll_region)
 
# Check startup configuration
setup_startup(configs)

def back():
    if messagebox.askyesno("Confirm", "Do you want to run in background", parent=app):
        background(app, configs, scrollable_frame, save_folder)
    else:
        app.destroy()

if len(sys.argv) == 2 and sys.argv[1] == "-background":
    background(app, configs, scrollable_frame, save_folder)
else:
    app.protocol("WM_DELETE_WINDOW", back)
app.mainloop()
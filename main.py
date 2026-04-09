#  import necessary modules
import os
import json 
import sys
from tkinter import (Tk, Label, Button, Frame, Canvas, Menu,
                      Scrollbar, messagebox, filedialog, PhotoImage
                    )
from sort import sorting, create_folders
from settings import see_config, setting
from back import background
from startup import setup_startup

# name:list_of_extenstions
configs = {
    "folders" : ["Folders", "Images", "Audios", "Videos", "Others", "Apps", "Compressed", "Documents"],
    "images" : [".jpg", ".png", ".gif", ".webp", ".jfif"],
    "audios" : [".mp3", ".flac", ".ogg", ".wav"],
    "apps" : [".msi", ".exe"],
    "videos" : [".mp4", ".mkv", ".mov", ".avi", ".webm", ".ts", ".asf", ".wmv"],
    "compressed" : [".zip", ".7z", ".tar", ".wim", ".gz"],
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

path = os.path.dirname(sys.executable) if hasattr(sys, "frozen") else os.path.dirname(os.path.abspath(__file__))
app.iconphoto(True, PhotoImage(file=os.path.join(path, "file_clean.png")))

menu = Menu(app)

comm = Menu(tearoff=0)
comm.add_command(label="Open Folder", command=open_dir)
comm.add_command(label="Show configs", command=lambda: see_config(app, save_folder, configs))
comm.add_command(label="Settings", command=lambda: setting(app, save_folder, configs))

menu.add_cascade(label="Commands", menu=comm)

app.config(menu=menu)

#  Header label
lbl = Label(app, text="File Organizer", fg="white", bg="black", font="Consolas 16 bold")
lbl.pack(side="top", pady=30, ipadx=10, ipady=10)

#btn frame for the clear btn
btn_frame = Frame(app, bg="darkblue")
btn_frame.pack(side="top", fill="x")

btn2 = Button(btn_frame, text="❌", fg="white", bg="red", font="Consolas 6", command=clear)
btn2.pack(side="right", padx=5, ipadx=3, ipady=3)

logs_frame = Frame(app)
top_frame = Frame(logs_frame)

#  Now add the canvas below everything
canvas = Canvas(top_frame)
canvas.pack(side="left", fill="both", expand=True)

#  scrollbar to scroll through events
y_scrollbar = Scrollbar(top_frame, orient="vertical", command=canvas.yview)
y_scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=y_scrollbar.set)

x_scrollbar = Scrollbar(logs_frame, orient="horizontal", command=canvas.xview)
x_scrollbar.pack(side="bottom", fill="x")
canvas.configure(xscrollcommand=x_scrollbar.set)

#  frame that events are stored
scrollable_frame = Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="center")

# update frame when configured
scrollable_frame.bind("<Configure>", update_scroll_region)

top_frame.pack(expand=True, fill="both")
logs_frame.pack(side="bottom", expand=True, fill="both", padx=10, pady=10)

# Check startup configuration
setup_startup(configs)

def back():
    if messagebox.askyesno("Confirm", "Do you want to run in background", parent=app):
        app.withdraw()
        background(app, configs, scrollable_frame, save_folder)
    else:
        app.destroy()

if len(sys.argv) == 2 and sys.argv[1] == "-background":
    app.withdraw()
    background(app, configs, scrollable_frame, save_folder)
else:
    app.protocol("WM_DELETE_WINDOW", back)
app.mainloop()
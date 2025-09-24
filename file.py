#  import necessary modules
import os, shutil, time, json, pystray, PIL.Image, filecmp
from tkinter import (Tk, Label, Button, Frame, Canvas, Scrollbar, messagebox, filedialog, 
                      Toplevel, Entry, PhotoImage, Checkbutton, IntVar
                    )

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

log_file = f"\n{time.strftime('%a %b %d %Y %H:%M:%S')}\n"
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
# if it is empty, put the default configuration
except json.decoder.JSONDecodeError:
     with open(os.path.join(save_folder, "config.json"), "w") as f:
        json.dump(configs, f, indent=4)

# function to create folders
def create_folders(base_dir):
    for i in configs["folders"]:
        #  create folder if it doesn't exist
        if not os.path.exists(os.path.join(base_dir, i)):
            os.mkdir(os.path.join(base_dir, i))
            add_lbls(f"Created {i} folder")

# function to move files to folders
def move(path, new_path):
    # return True if it was successful, else return False if it wasn't
    try:
        shutil.move(path, new_path)
        return True
    except PermissionError:
        messagebox.showerror("Unable to move file", "Permission denied")
        return False
    except FileNotFoundError:
        messagebox.showerror("Unable to move file", "File is not found")
        return False
    except shutil.Error as e:
        messagebox.showerror("Unable to move file", e)

# function to sort the files according to their configured extensions
def sort(base_dir, can_open):
    global log_file
    for i in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, i)):
            if i not in configs["folders"]:
                if move(os.path.join(base_dir, i), os.path.join(base_dir, "Folders")):
                    add_lbls(f"Moved {i} to Folders")
        else:
            if "." in i:
                ext = os.path.splitext(i)[1].lower()
            else:
                ext = ""
            val = list(configs.values())[:len(configs.values())-2]
            for j in val:
                if ext in j:
                    ans = [items for items, values in configs.items() if values == j]
                    if move(os.path.join(base_dir, i), os.path.join(base_dir, ans[0].capitalize())):
                        add_lbls(f"Moved {i} to {ans[0]}")
    """
        After the first loop, the unknown files will remain, now the loop will run to put them in Others
    """
    for i in os.listdir(base_dir):
        if os.path.isfile(os.path.join(base_dir, i)):
            if move(os.path.join(base_dir, i), os.path.join(base_dir, "Others")):
                add_lbls(f"Moved {i} to Others")
    #  add log to the log file
    with open(os.path.join(save_folder, "log.txt"), "a") as f:
        f.write(log_file)
    #  reset the log file for a new session
    log_file = ""
    #  open explorer if done
    if can_open:
        if messagebox.askyesno("Open Explorer", "Scan is Done\nWould you like to open explorer"):
            os.startfile(base_dir)

# function to open directory
def open_dir(dir=None, can_open=True):
    home_download = os.path.join(os.path.expanduser("~"), "Downloads")
    directory = ""
    if dir == None:
        directory = filedialog.askdirectory(initialdir=home_download)
    else:
        directory = dir
    configs["last_folder"] = directory
    with open(os.path.join(save_folder, "config.json"), "w") as f:
        json.dump(configs, f, indent=4)
    # if it is not cancelled create folders and sort files
    if directory != "":
        create_folders(directory)
        sort(directory, can_open)

# function to add label to the log frame and add test to the session's log file
def add_lbls(text:str):
    global log_file
    Label(scrollable_frame, text=text, font="Consolas 10").pack(anchor="w")
    log_file += f"{text}\n"

# function to clear all the labels in the log frame
def clear():
    for i in scrollable_frame.winfo_children():
        i.destroy()

# function to update the canvas region when the scrollbar is moved
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# function to create the dialog for configuration settings
def config():
    # dialog main configurations
    app2 = Toplevel(app)
    app2.transient(app)
    app2.grab_set()
    app2.config(bg="black")
    app2.geometry(f"424x136+{app.winfo_x()}+{app.winfo_y()}")
    
    label = Label(app2, text="Name:", fg="white", bg="black", font="Consolas 12")
    label.grid(column=0, row=0, ipadx=5, ipady=5)
    name = Entry(app2, font="Consolas 11")
    name.grid(column=1, row=0, padx=5, pady=5)

    label2 = Label(app2, text="Extensions\n (Use commas to seperate):", bg="black", fg="white", font="Consolas 12")
    label2.grid(column=0, row=1, ipadx=5, ipady=5)
    extensions = Entry(app2, font="Consolas 11")
    extensions.grid(column=1, row=1, padx=5, pady=5)

    submit = Button(app2, text="Submit", bg="green", fg="white", font="Consolas 12", width=10, 
                    command=lambda: submit_info(name.get(), extensions.get(), app2))
    submit.grid(column=0, row=2, columnspan=2, pady=7)

    app2.bind("<KeyPress>", lambda e: submit_info(name.get(), extensions.get(), app2) if e.keysym == "Return" else "nothing")
    app.wait_window(app2)

# function to submit information from config dialog
def submit_info(name:str, extension:str, parent:any):
    global configs
    def write(mode):
        ext = []
        for i in extension.split(","):
            if not i.startswith(".") or i.startswith(" .") :
                if " " in i:
                    i = "."+i[1:]
                else:
                    i = "."+i
            ext.append(i)
        for i in ext:
            ext
        
        if mode == 0:
            configs["folders"].append(name.capitalize())
            configs[name.lower()] = ext
        elif mode == 1:
            for k in ext:
                configs[name].append(k)

        with open(os.path.join(save_folder, "config.json"), "w") as f:
            json.dump(configs, f, indent=4)
        parent.destroy()
    
    if name.strip() != "" and extension.strip() != "":
        if name in configs.keys():
            if messagebox.askyesno("Naming Error", "This will add to an existing configuration\nWill you proceed"):
                write(1)
        else:
            write(0)
    else:
        messagebox.showerror("Invalid Input", "Name/Extension can not be empty")

def remove_config():
    top = Toplevel(app)
    top.title("Remove Config")
    top.geometry(f"300x100+{app.winfo_x()}+{app.winfo_y()}")
    top.transient(app)
    top.grab_set()
    Label(top, text="Category to remove:", font="Consolas 11").pack(pady=5)
    entry = Entry(top, font="Consolas 11")
    entry.pack(pady=5)
    def confirm():
        name = entry.get().strip().lower()
        nope = ["folders", "images", "audios", "apps", "videos", "compressed", "documents"]
        if name in configs.keys() and name not in nope:
            configs["folders"].remove(name.capitalize())
            del configs[name]
            print(configs)
            with open(os.path.join(save_folder, "config.json"), "w") as f:
                json.dump(configs, f, indent=4)
            top.destroy()
        else:
            messagebox.showerror("Error", "Invalid category name")
    Button(top, text="Remove", command=confirm).pack(pady=5)
    top.bind("<KeyPress>", lambda e: confirm() if e.keysym == "Return" else "nothing")
    app.wait_window(top)

def setting():
    def load():
        start = True if var.get() == 1 else False
        configs["start"] = start
        with open(os.path.join(save_folder, "config.json"), "w") as f:
            json.dump(configs, f, indent=4)
    setting_app = Toplevel(app)
    setting_app.geometry(f"300x100+{app.winfo_x()}+{app.winfo_y()}")
    setting_app.config(bg="black")
    setting_app.title("Settings")
    setting_app.transient(app)
    var = IntVar(setting_app)
    Label(setting_app, text="Select favourable options", bg="black", fg="white").pack(pady=20)
    check1 = Checkbutton(setting_app, text="Run in background when computer starts", onvalue=1,
                         offvalue=0, variable=var, command=load)
    if configs["start"]:
        var.set(1)
    check1.pack()
    app.wait_window(setting_app)
    setting_app.mainloop()

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

btn3 = Button(top_frame, text="Add Config", fg="white", bg="green", font="Consolas 11", command=config)
btn3.pack(side="left", padx=5, ipadx=3, ipady=3)

btn4 = Button(top_frame, text="Remove Config", fg="white", bg="red", font="Consolas 11", command=remove_config)
btn4.pack(side="left", padx=5, ipadx=3, ipady=3)

btn5 = Button(top_frame, text="Settings", fg="white", bg="black", font="Consolas 11", command=setting)
btn5.pack(side="left", padx=5, ipadx=3, ipady=3)

#  Log label
lbl2 = Label(app, text="Logs", fg="white", bg="darkblue", font="Consolas 13 bold")
lbl2.pack(side="top", padx=10, pady=13)

#  Now add the canvas below everything
canvas = Canvas(app, bg="white")
canvas.pack(side="top", fill="both", expand=True, padx=10, pady=5)

#  scrollbar to scroll through events
scrollbar = Scrollbar(canvas, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

#  frame that events are stored
scrollable_frame = Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# update frame when configured
scrollable_frame.bind("<Configure>", update_scroll_region)
 
# Ensure startup configuration is enabled
if configs["start"]:
    env_path = os.path.join(os.environ["USERPROFILE"], "Documents", "Finished Projects",
                             "Python", "File-Cleaner", ".virtual", "Scripts", "activate")
    
    # Content for the batch file
    bat_content = f'@echo off\ncall "{env_path}"\npythonw "{__file__}"'

    # Create the batch file in the current directory
    with open("run.bat", "w") as bat_file:
        bat_file.write(bat_content)

    # Define the Startup folder path
    startup_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", 
                                "Windows", "Start Menu", "Programs", "Startup", "run.bat")
    
    # If the batch file does not exist or the content differs, move the new batch file to the startup folder
    if not os.path.exists(startup_path) or not filecmp.cmp("run.bat", startup_path):
        shutil.move("run.bat", startup_path)
        print("Batch file has been placed in the Startup folder.")
    else:
        print("The batch file already exists with the same content.")

def background():
    def open_app(icon, query):
        global re_open
        app.after(0, app.deiconify)
        icon.stop()
        re_open = True

    app.withdraw()
    icon = pystray.Icon(name="Organize files in the shadows", icon=PIL.Image.open("file_clean.png"), 
                 title="File Cleaner", menu = pystray.Menu(pystray.MenuItem("Open", open_app))
            )
    icon.run()
    open_dir(os.path.join(os.path.expanduser("~"), "Downloads"), False)
    if not re_open:
        app.after(500, background)

def back():
    if messagebox.askyesno("Confirm", "Do you want to run in background"):
        background()
    else:
        app.destroy()

app.protocol("WM_DELETE_WINDOW", back)
app.mainloop()
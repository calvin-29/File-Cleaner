import os
import shutil
from tkinter import messagebox, Label
import time

log_file = ""

# function to add label to the log frame and add test to the session's log file
def add_lbls(text:str, scrollable_frame):
    global log_file
    Label(scrollable_frame, text=text, font="Consolas 10").pack(anchor="w")
    log_file += f"{text}\n"

# function to move files to folders
def move(path, new_path, app):
    # return True if it was successful, else return False if it wasn't
    try:
        shutil.move(path, new_path)
    except PermissionError:
        messagebox.showerror("Unable to move file", "Permission denied", parent=app)
        return False
    except FileNotFoundError:
        messagebox.showerror("Unable to move file", "File is not found", parent=app)
        return False
    except shutil.Error as e:
        messagebox.showerror("Unable to move file", e, parent=app)
        return False
    else:
        return True

# function to create folders
def create_folders(base_dir, configs, scrollable_frame):
    global log_file
    for i in configs["folders"]:
        #  create folder if it doesn't exist
        if not os.path.exists(os.path.join(base_dir, i)):
            os.mkdir(os.path.join(base_dir, i))
            add_lbls(f"Created {i} folder", scrollable_frame)

# function to sort the files according to their configured extensions
def sorting(app, base_dir, can_open, configs, save_folder, scrollable_frame):
    global log_file
    log_file = f"\n{time.strftime('%a %b %d %Y %H:%M:%S')}\n"

    create_folders(base_dir, configs, scrollable_frame)
    files = os.listdir(base_dir)
    for i in files:
        if os.path.isdir(os.path.join(base_dir, i)):
            if i not in configs["folders"]:
                if move(os.path.join(base_dir, i), os.path.join(base_dir, "Folders"), app):
                    add_lbls(f"Moved {i} to Folders", scrollable_frame)
                else:
                    continue
        else:
            if not is_safe(os.path.join(base_dir, i)):
                continue
            ext = os.path.splitext(i)[1].lower() if "." in i  else " "
            val = {
                k: v for k, v in configs.items()
                if k not in ["folders", "last_folder", "start"]
            }
            for j in val.values():
                if ext in j:
                    ans = [items for items, values in configs.items() if values == j]
                    if move(os.path.join(base_dir, i), os.path.join(base_dir, ans[0].capitalize()), app):
                        add_lbls(f"Moved {i} to {ans[0]}", scrollable_frame)
                    else:
                        continue
    """
        After the first loop, the unknown files will remain, now the loop will run to put them in Others
    """
    for i in os.listdir(base_dir):
        path = os.path.join(base_dir, i)
        if os.path.isfile(path):
            if not is_safe(path):
                continue
            ext = os.path.splitext(i)[1].lower() if "." in i  else " "
            val = {
                k: v for k, v in configs.items()
                if k not in ["folders", "last_folder", "start"]
            }
            moved = False
            for j in val.values():
                if ext in j:
                    # move to category
                    moved = True
                    break
            if not moved:
                if move(os.path.join(base_dir, i), os.path.join(base_dir, "Others"), app):
                    add_lbls(f"Moved {i} to Others", scrollable_frame)
                else:
                    continue
    #  add log to the log file and prevent duplicate dates
    path = os.path.join(save_folder, "log.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            if log_file not in f.readlines():
                with open(path, "a+") as f:
                    f.write(log_file)
    #  reset the log file for a new session
    log_file = ""
    #  open explorer if done
    if can_open:
        if messagebox.askyesno("Open Explorer", "Scan is Done\nWould you like to open explorer", parent=app):
            os.startfile(base_dir)

def is_safe(path):
    if os.path.exists(path):
        name = path.lower()

        # 1. Extension check
        if name.endswith((".crdownload", ".part", ".tmp")):
            return False

        # 2. Open check
        try:
            with open(path, "rb"):
                pass
        except:
            return False
        
        # if nothing is false return true
        return True

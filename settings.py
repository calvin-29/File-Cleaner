from tkinter import (Toplevel, Entry, Checkbutton, Frame,
                     IntVar, Label, Button, messagebox,
                     Scrollbar, Listbox, Menu)
import os
import json
from startup import setup_startup

def clear_custom(save_folder, configs):
    def_configs = {
        "folders" : ["Folders", "Images", "Audios", "Videos", "Others", "Apps", "Compressed", "Documents"],
        "images" : [".jpg", ".png", ".gif", ".webp", ".jfif"],
        "audios" : [".mp3", ".flac", ".ogg", ".wav"],
        "apps" : [".msi", ".exe"],
        "videos" : [".mp4", ".mkv", ".mov", ".avi", ".webm", ".ts", ".asf", ".wmv"],
        "compressed" : [".zip", ".7z", ".tar", ".wim", "gz"],
        "documents" : [".docx", ".pptx", ".txt", ".rtf", ".chm", ".html", ".htm", ".mhtml", ".pdf"],
        "last_folder": configs["last_folder"],
        "start": configs["start"]
    }
    with open(os.path.join(save_folder, "config.json"), "w") as f:
        json.dump(def_configs, f, indent=4)

def show_popup(event, listbox:Listbox, func_option):
    menu = Menu(listbox, tearoff=0)

    index = listbox.nearest(event.y)
    listbox.selection_clear(0, "end")
    listbox.selection_set(index)
    listbox.activate(index)
    
    name = listbox.get(index)
    name = name[:name.index('-')].strip().lower()
    parent, configs, save_folder = func_option

    menu.add_command(label="Add Config", command=lambda: add_config(parent, configs, save_folder, listbox))
    menu.add_command(label="Remove Config", command=lambda: delete_config(name, configs, save_folder, listbox))
    menu.add_command(label="Clear all custom config", command=lambda: clear_custom(save_folder, configs))

    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

def delete_config(name, configs, save_folder, listbox):
    nope = ["folders", "images", "audios", "apps", "videos", "compressed", "documents"]
    if name in configs.keys() and name not in nope:
        configs["folders"].remove(name.capitalize())
        del configs[name]
        with open(os.path.join(save_folder, "config.json"), "w") as f:
            json.dump(configs, f, indent=4)
        arrange(listbox, configs)
    else:
        if name in nope:
            messagebox.showerror("Error", f'Cannot delete default category "{name.capitalize()}"')
        else:
            messagebox.showerror("Error", "Invalid category name")

def add_config(parent, configs, save_folder, listbox):
    app = Toplevel(parent)
    app.transient(parent)
    app.resizable(0,0)
    app.config(bg="black")

    Label(app, text="Name:", fg="white",
           bg="black", font="Consolas 11").grid(row=0, column=0, padx=10, pady=(10,0))
    name = Entry(app, font=("Segeo UI", 11))
    name.grid(row=0, column=1, padx=10, pady=(10,0))

    Label(app, text="Extensions:\n(.blend, .nxt)", 
          fg="white", bg="black", font="Consolas 11").grid(row=1, column=0, padx=10)
    ext = Entry(app, font=("Segeo UI", 11))
    ext.grid(row=1, column=1, padx=10)

    Button(app, text="Submit", bg="green", fg="white", font="Consolas 11",
            command=lambda: submit_info(
                name.get().strip(), ext.get().strip(), app, save_folder, configs, listbox
    )).grid(row=2, column=0, columnspan=2, padx=10, pady=(0,10))

    x = parent.winfo_x()+(parent.winfo_width()//2-160)
    y = parent.winfo_y()+(parent.winfo_height()//2-60)+20
    app.geometry(f"320x120+{x}+{y}")
    
    app.grab_set()
    parent.wait_window(app)

def submit_info(name:str, extension:str, parent, save_folder, configs, listbox):
    def write(mode):
        ext = []
        for i in extension.split(","):
            ext.append(i)
        
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
        if name.lower() in configs.keys():
            if messagebox.askyesno("Naming Error", "This will add to an existing configuration\nWill you proceed"):
                write(1)
        else:
            write(0)
        arrange(listbox, configs)
    else:
        messagebox.showerror("Invalid Input", "Name/Extension can not be empty")

def arrange(wid, configs, condition=""):
    vals = {
        i:j for i, j in configs.items()
        if i not in ["start", "last_folder", "folders"]
    }
    wid.delete(0, "end")
    for i, j in vals.items():
        if condition in i or condition in ''.join(j):
            wid.config(font="Verdena 13", bg="darkblue", fg="white")
            i = f"{i[:13]}...{i[-5:]}" if len(i) > 20 else i
            wid.insert("end", f" {i.capitalize()} - {', '.join(j)} ")

def see_config(app, save_folder, configs):
    top = Toplevel(app)
    top.title("All Configurations")
    top.transient(app)
    top.config(bg="black")
    
    search_frame = Frame(top, bg="black")
    lbl = Label(search_frame, font="Consolas 11", text="Search: ", fg="white", bg="black")
    lbl.pack(side="left")
    entry = Entry(search_frame, font="Consolas 11")
    entry.pack(side="left")
    search = Button(search_frame, text="🔍", fg="white", bg="black", command=lambda: arrange(tree, configs, entry.get()))
    search.pack(side="left", padx=(3,0))
    search_frame.pack(anchor="center", pady=10)

    list_frame = Frame(top)
    top_frame = Frame(list_frame)
    tree = Listbox(top_frame, activestyle='none', highlightthickness=0, border=0)
    tree.bind("<Button-3>", lambda e, tr=tree: show_popup(e, tr, (top, configs, save_folder)))
    tree.pack(fill="both", expand=True, side="left")
    
    y_scroll = Scrollbar(top_frame, command=tree.yview)
    y_scroll.pack(side="right", fill="y")
    top_frame.pack(fill="both", expand=True, side="top")

    x_scroll = Scrollbar(list_frame, command=tree.xview, orient="horizontal")
    x_scroll.pack(fill="x", side="bottom")

    tree.config(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
    arrange(tree, configs)
    list_frame.pack(fill="both", expand=True, pady=10, padx=10)

    x = app.winfo_x()+(app.winfo_width()//2-200)
    y = app.winfo_y()+(app.winfo_height()//2-200)+20
    top.geometry(f"400x400+{x}+{y}")
    app.wait_window(top)

def setting(app, save_folder, configs):
    def load():
        configs["start"] = True if var.get() == 1 else False
        with open(os.path.join(save_folder, "config.json"), "w") as f:
            json.dump(configs, f, indent=4)
        setup_startup(configs)
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

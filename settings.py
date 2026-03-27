from tkinter import (Toplevel, Entry, Checkbutton, 
                     IntVar, Label, Button, messagebox)
import os
import json

# function to create the dialog for configuration settings
def config(app, save_folder, configs):
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

    label2 = Label(app2, text="Extensions\n (.pkls, .blend):", bg="black", fg="white", font="Consolas 12")
    label2.grid(column=0, row=1, ipadx=5, ipady=5)
    extensions = Entry(app2, font="Consolas 11")
    extensions.grid(column=1, row=1, padx=5, pady=5)

    submit = Button(app2, text="Submit", bg="green", fg="white", font="Consolas 12", width=10, 
                    command=lambda: submit_info(name.get(), extensions.get(), app2, save_folder, configs))
    submit.grid(column=0, row=2, columnspan=2, pady=7)

    app2.bind("<KeyPress>", lambda e: submit_info(name.get(), extensions.get(), app2, save_folder, configs) if e.keysym == "Return" else "nothing")
    app.wait_window(app2)

# function to submit information from config dialog
def submit_info(name:str, extension:str, parent, save_folder, configs):
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
        if name in configs.keys():
            if messagebox.askyesno("Naming Error", "This will add to an existing configuration\nWill you proceed"):
                write(1)
        else:
            write(0)
    else:
        messagebox.showerror("Invalid Input", "Name/Extension can not be empty")

def remove_config(app, save_folder, configs):
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

def setting(app, save_folder, configs):
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

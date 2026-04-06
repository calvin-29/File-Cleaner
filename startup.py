import os
import sys
import winreg

def setup_startup(configs):
    app_name = "File Cleaner"
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE
    )

    try:
        if configs.get("start"):
            command = f'"{python_exe}" "{script_path}" -background'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
    except Exception as e:
        print(e)
    finally:
        winreg.CloseKey(key)
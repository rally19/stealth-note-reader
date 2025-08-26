import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading
import webbrowser
import os
import sys
import json
import ctypes
from ctypes import wintypes

WINDOW_SIZE = 200
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011

user32 = ctypes.WinDLL('user32', use_last_error=True)

def set_window_display_affinity(hwnd, affinity):
    result = user32.SetWindowDisplayAffinity(hwnd, affinity)
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())

def is_text_file(file_path):
    """Check if a file is likely to be a text file by examining its content"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if not chunk:
                return False
            text_characters = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13))
            return text_characters / len(chunk) > 0.7
    except:
        return False

class StealthNoteApp:
    def __init__(self, root, file_path=None):
        self.root = root
        self.root.title("Stealth Note App")
        self.root.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.config(cursor="arrow")
        self.root.after(100, self.set_affinity)

        self.themes = {
            "light": {"bg": "#FFFFFF", "fg": "#000000"},
            "dark": {"bg": "#2E2E2E", "fg": "#FFFFFF"},
            "blue": {"bg": "#E6F0FF", "fg": "#003366"},
            "green": {"bg": "#E6FFE6", "fg": "#006600"},
            "purple": {"bg": "#F0E6FF", "fg": "#4B0082"}
        }
        self.current_theme = "light"
        self.font_size = 12
        self.font_weight = "normal"
        self.always_on_top = True

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, borderwidth=0, font=("Arial", self.font_size, self.font_weight))
        self.text_area.pack(expand=True, fill='both')
        self.text_area.config(state=tk.DISABLED, cursor="arrow")

        self.text_area.bind("<Button-1>", self.start_move)
        self.text_area.bind("<B1-Motion>", self.do_move)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_file_on_window)

        self.load_settings()

        self.apply_theme()
        self.add_system_tray()

        if file_path:
            self.load_file(file_path)

        self.set_window_icon(self.root)

    def set_affinity(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        set_window_display_affinity(hwnd, WDA_EXCLUDEFROMCAPTURE)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.root.geometry(f"+{x}+{y}")

    def load_file(self, file_path):
        if file_path and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.text_area.config(state=tk.NORMAL)
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert(tk.END, content)
                    self.text_area.config(state=tk.DISABLED)
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="latin-1") as file:
                        content = file.read()
                        self.text_area.config(state=tk.NORMAL)
                        self.text_area.delete("1.0", tk.END)
                        self.text_area.insert(tk.END, content)
                        self.text_area.config(state=tk.DISABLED)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {str(e)}")

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.config(bg=theme["bg"])
        self.text_area.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"], highlightthickness=0)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def toggle_visibility(self):
        if self.root.state() == 'normal':
            self.root.withdraw()
        else:
            self.root.deiconify()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.load_file(file_path)

    def drop_file_on_window(self, event):
        path = event.data.strip('{}')
        if os.path.isfile(path) and (path.lower().endswith(".txt") or is_text_file(path)):
            self.load_file(path)
        else:
            messagebox.showwarning("Invalid File", "Please drop a valid text file.")

    def open_settings(self):
        if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("300x300")
        self.settings_window.resizable(False, False)
        self.settings_window.config(bg="#F0F0F0")

        self.set_window_icon(self.settings_window)

        tab_control = ttk.Notebook(self.settings_window)

        resize_tab = ttk.Frame(tab_control)
        tab_control.add(resize_tab, text="Window")

        ttk.Label(resize_tab, text="Width:").pack(pady=5, anchor='w')
        self.width_entry = ttk.Entry(resize_tab)
        self.width_entry.insert(0, str(self.root.winfo_width()))
        self.width_entry.pack(pady=5, anchor='w')

        ttk.Label(resize_tab, text="Height:").pack(pady=5, anchor='w')
        self.height_entry = ttk.Entry(resize_tab)
        self.height_entry.insert(0, str(self.root.winfo_height()))
        self.height_entry.pack(pady=5, anchor='w')

        ttk.Label(resize_tab, text="Always on Top:").pack(pady=5, anchor='w')
        self.always_on_top_var = tk.StringVar(value="Yes" if self.always_on_top else "No")
        self.always_on_top_combobox = ttk.Combobox(resize_tab, textvariable=self.always_on_top_var, values=["Yes", "No"], state="readonly")
        self.always_on_top_combobox.pack(pady=5, anchor='w')

        font_tab = ttk.Frame(tab_control)
        tab_control.add(font_tab, text="Font Settings")

        ttk.Label(font_tab, text="Font Size:").pack(pady=5, anchor='w')
        self.size_entry = ttk.Entry(font_tab)
        self.size_entry.insert(0, str(self.font_size))
        self.size_entry.pack(pady=5, anchor='w')

        ttk.Label(font_tab, text="Font Weight:").pack(pady=5, anchor='w')
        self.weight_var = tk.StringVar(value=self.font_weight)
        self.weight_combobox = ttk.Combobox(font_tab, textvariable=self.weight_var, values=["normal", "bold"], state="readonly")
        self.weight_combobox.pack(pady=5, anchor='w')

        theme_tab = ttk.Frame(tab_control)
        tab_control.add(theme_tab, text="Theme Settings")

        self.theme_var = tk.StringVar(value=self.current_theme)
        for theme_name in self.themes.keys():
            ttk.Radiobutton(theme_tab, text=theme_name.capitalize(), variable=self.theme_var, value=theme_name).pack(pady=5, anchor='w')

        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        def apply_settings():
            try:
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                if width >= 50 and height >= 50:
                    self.root.geometry(f"{width}x{height}")
                else:
                    messagebox.showerror("Invalid Size", "Width and height must be at least 50px.")
                    return

                self.always_on_top = self.always_on_top_var.get() == "Yes"
                self.root.attributes("-topmost", self.always_on_top)

                size = int(self.size_entry.get())
                if size >= 8:
                    self.font_size = size
                else:
                    messagebox.showerror("Invalid Size", "Font size must be at least 8.")
                    return

                weight = self.weight_var.get()
                if weight in ["normal", "bold"]:
                    self.font_weight = weight
                else:
                    messagebox.showerror("Invalid Weight", "Font weight must be 'normal' or 'bold'.")
                    return

                self.current_theme = self.theme_var.get()
                self.apply_theme()

                self.text_area.config(font=("Arial", self.font_size, self.font_weight))

                self.save_settings()

                # messagebox.showinfo("Success", "Settings applied successfully!")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid values.")

        def close_settings():
            self.settings_window.destroy()

        button_frame = ttk.Frame(self.settings_window)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        ttk.Button(button_frame, text="Close", command=close_settings).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=10)

    def get_base_path(self):
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.path.abspath(".")

    def get_settings_path(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = self.get_base_path()
        
        config_dir = os.path.join(base_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, "settings.json")

    def save_settings(self):
        try:
            settings = {
                "width": self.root.winfo_width(),
                "height": self.root.winfo_height(),
                "font_size": self.font_size,
                "font_weight": self.font_weight,
                "theme": self.current_theme,
                "always_on_top": self.always_on_top
            }
            settings_path = self.get_settings_path()
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_settings(self):
        settings_path = self.get_settings_path()
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                    if "width" in settings and "height" in settings:
                        self.root.geometry(f"{settings['width']}x{settings['height']}")
                    if "font_size" in settings:
                        self.font_size = settings["font_size"]
                    if "font_weight" in settings:
                        self.font_weight = settings["font_weight"]
                    if "theme" in settings:
                        self.current_theme = settings["theme"]
                    if "always_on_top" in settings:
                        self.always_on_top = settings["always_on_top"]
                        self.root.attributes("-topmost", self.always_on_top)
                    
                    self.text_area.config(font=("Arial", self.font_size, self.font_weight))
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading settings: {e}")

    def add_system_tray(self):
        def quit_app(icon, item):
            icon.stop()
            self.root.destroy()

        def open_settings_tray(icon, item):
            self.root.after(0, self.open_settings)

        def toggle_visibility_tray(icon, item):
            self.root.after(0, self.toggle_visibility)

        def open_file_tray(icon, item):
            self.root.after(0, self.open_file)

        icon_image = self.load_icon()
        menu = pystray.Menu(
            item("Show/Hide", toggle_visibility_tray),
            item("Open File", open_file_tray),
            item("Settings", open_settings_tray),
            item("Quit", quit_app)
        )
        self.icon = pystray.Icon("StealthNoteApp", icon_image, "Stealth Note App", menu)

        threading.Thread(target=self.icon.run, daemon=True).start()

    def load_icon(self):
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            else:
                icon_path = "icon.ico"
            return Image.open(icon_path)
        except:
            return Image.new('RGB', (64, 64), color='gray')

    def set_window_icon(self, window):
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            else:
                icon_path = "icon.ico"
            window.iconbitmap(icon_path)
        except:
            pass

class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Stealth Note Reader")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.config(bg="#F0F0F0")

        ttk.Label(root, text="Stealth Note Reader", font=("Segoe UI", 16)).pack(pady=20)

        self.file_path = None
        self.file_label = ttk.Label(root, text="", font=("Segoe UI", 10))
        self.file_label.pack(pady=5)

        self.dnd_select_button = ttk.Button(root, text="Drag and Drop or Select a txt file", command=self.select_file)
        self.dnd_select_button.pack(pady=10)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_file)

        ttk.Button(root, text="Continue", command=self.continue_app).pack(pady=10)

        def open_link(event):
            webbrowser.open_new("https://rally19.github.io/")

        label = ttk.Label(root, text="Made by rally19", font=("Segoe UI", 10), foreground="blue", cursor="hand2")
        label.pack(side=tk.BOTTOM)
        label.bind("<Button-1>", open_link)
        label.pack(side=tk.BOTTOM, pady=10)

        self.set_window_icon(self.root)

    def drop_file(self, event):
        path = event.data.strip('{}')
        if os.path.isfile(path) and (path.lower().endswith(".txt") or is_text_file(path)):
            self.file_path = path
            self.file_label.config(text=os.path.basename(self.file_path))
        else:
            messagebox.showerror("Invalid File", "Please drop a valid text file.")

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))

    def continue_app(self):
        if self.file_path:
            self.root.destroy()
            main_root = TkinterDnD.Tk()
            StealthNoteApp(main_root, self.file_path)
            main_root.mainloop()
        else:
            messagebox.showwarning("No File Selected", "Please select a text file before continuing.")

    def set_window_icon(self, window):
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            else:
                icon_path = "icon.ico"
            window.iconbitmap(icon_path)
        except:
            pass

if __name__ == "__main__":
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    if file_path and os.path.isfile(file_path) and (file_path.lower().endswith(".txt") or is_text_file(file_path)):
        main_root = TkinterDnD.Tk()
        StealthNoteApp(main_root, file_path)
        main_root.mainloop()
    else:
        welcome_root = TkinterDnD.Tk()
        WelcomeWindow(welcome_root)
        welcome_root.mainloop()

# Made by Leonel R. S.
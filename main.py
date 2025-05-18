import tkinter as tk
from tkinter import messagebox
import time
import sys
import subprocess
from PIL import Image, ImageTk


class Launcher:
    def __init__(self):
        self.CORRECT_CODE = "hYwfg"
        # Define global font settings
        self.title_font = ("Arial", 48, "bold")
        self.normal_font = ("Arial", 18)
        self.loading_font = ("Arial", 24)
        self.show_loading_screen()

    def show_loading_screen(self):
        self.loading_root = tk.Tk()
        self.loading_root.title("Beyond The Brush")
        self.loading_root.geometry("1280x720")
        self.loading_root.resizable(False, False)  # Prevent resizing

        canvas = tk.Canvas(self.loading_root, width=1280, height=720)
        canvas.pack()

        # Background - #383232 as requested
        bg_color = "#383232"
        canvas.create_rectangle(0, 0, 1280, 720, fill=bg_color, outline="")

        # Try to load logo image
        try:
            logo_img = Image.open("logo.png")  # Replace with your actual logo filename
            logo_img = logo_img.resize((200, 200))  # Adjust size as needed
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            canvas.create_image(640, 150, image=self.logo_photo)
        except FileNotFoundError:
            print("Logo image not found, using text instead")
            # Loading text with our global title font
            canvas.create_text(640, 150, text="Beyond The Brush",
                               font=self.title_font, fill="white")

        # Loading text with loading font
        canvas.create_text(640, 360, text="Loading...",
                           font=self.loading_font, fill="white")

        # Progress bar
        progress = canvas.create_rectangle(440, 400, 440, 430, fill="#3498db", outline="")

        self.loading_root.update()

        # Animate progress bar
        for i in range(1, 101):
            canvas.coords(progress, 440, 400, 440 + (i * 4), 430)
            self.loading_root.update()
            time.sleep(0.03)

        self.loading_root.destroy()
        self.show_entry_page()

    def show_entry_page(self):
        self.entry_root = tk.Tk()
        self.entry_root.title("Beyond The Brush - Entry")
        self.entry_root.geometry("1280x720")
        self.entry_root.resizable(False, False)  # Prevent resizing

        # Background - #383232
        bg_color = "#383232"
        canvas = tk.Canvas(self.entry_root, width=1280, height=720, bg=bg_color)
        canvas.pack()

        # Try to load logo image instead of title
        try:
            logo_img = Image.open("logo.png")  # Replace with your actual logo filename
            logo_img = logo_img.resize((200, 200))  # Adjust size as needed
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            canvas.create_image(640, 150, image=self.logo_photo)
        except FileNotFoundError:
            print("Logo image not found, using text instead")
            # Title with global title font
            canvas.create_text(640, 150, text="Beyond The Brush",
                               font=self.title_font, fill="white")

        # Role selection
        self.role_var = tk.StringVar(value="student")

        # Using our global normal font for all widgets
        tk.Radiobutton(self.entry_root, text="Student", variable=self.role_var,
                       value="student", font=self.normal_font, bg=bg_color, fg="white",
                       selectcolor=bg_color, activebackground=bg_color,
                       activeforeground="white").place(x=540, y=250)

        tk.Radiobutton(self.entry_root, text="Educator", variable=self.role_var,
                       value="educator", font=self.normal_font, bg=bg_color, fg="white",
                       selectcolor=bg_color, activebackground=bg_color,
                       activeforeground="white").place(x=540, y=300)

        # Code entry
        code_label = tk.Label(self.entry_root, text="Enter Access Code:",
                              font=self.normal_font, bg=bg_color, fg="white")
        code_label.place(x=440, y=370)

        self.code_entry = tk.Entry(self.entry_root, font=self.normal_font, show="*")
        self.code_entry.place(x=440, y=420, width=400)

        # Enter button - #ff00ff (magenta) as requested
        enter_btn = tk.Button(self.entry_root, text="ENTER", font=self.normal_font,
                              command=self.verify_code, bg="#ff00ff", fg="white",
                              activebackground="#cc00cc", activeforeground="white")
        enter_btn.place(x=540, y=500, width=200)

        self.entry_root.bind('<Return>', lambda event: self.verify_code())
        self.code_entry.focus_set()
        self.entry_root.mainloop()

    def verify_code(self):
        entered_code = self.code_entry.get()
        if entered_code == self.CORRECT_CODE:
            self.entry_root.destroy()
            self.launch_VirtualPainter_program()
        else:
            messagebox.showerror("Error", "Incorrect access code. Please try again.")

    def launch_VirtualPainter_program(self):
        # Get the selected role
        role = self.role_var.get()

        # Determine if we're running as a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - pass role as argument
            subprocess.Popen([sys.executable, "VirtualPainter.py", role])
        else:
            # Running as normal Python script
            import VirtualPainter
            VirtualPainter.run_application(role)


if __name__ == "__main__":
    launcher = Launcher()
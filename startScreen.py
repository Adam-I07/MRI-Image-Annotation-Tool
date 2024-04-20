import tkinter as tk
from PIL import Image, ImageTk

class CustomProgressbar:
    def __init__(self, start_menu_window, width=1000, height=20, bg="#cccccc", fg="#555555"):
        self.canvas = tk.Canvas(start_menu_window, width=width, height=height, bg=bg, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both')
        self.width = width
        self.height = height
        self.bg = bg
        self.fg = fg
        self.progress = 0

        # Draw the foreground of the progress bar
        self.foreground = self.canvas.create_rectangle(0, 0, 0, height, fill=self.fg, width=0)

    def update_progress(self, value):
        # Update the length of the progress bar
        self.progress = value
        self.canvas.coords(self.foreground, 0, 0, self.width * (self.progress / 100), self.height)

class PrecisionScanApp:
    def __init__(self, parent_app=None):
        self.parent_app = parent_app
    
    def start_window(self):
        self.parent_app.hide_UI()
        self.start_menu_window = tk.Toplevel()
        self.start_menu_window.geometry('1100x700')
        self.start_menu_window.title('PrecisionScan')
        self.start_menu_window.resizable(0, 0)
        self.start_menu_window.configure(bg='#cccccc')
        # Load the image
        self.logo = Image.open("icons/precision-scan-logo.png")
        self.logo_resized = self.logo.resize((1000, 600))
        self.final_logo = ImageTk.PhotoImage(self.logo_resized)

        # Display the image
        self.logo_label = tk.Label(self.start_menu_window, image=self.final_logo, bg='#cccccc')
        self.logo_label.grid(row=0, column=0, padx=(60, 0), pady=(20, 0))

        # Create a frame for the progress bar to control its placement more precisely
        self.progress_frame = tk.Frame(self.start_menu_window, bg='#cccccc')
        self.progress_frame.grid(row=1, column=0, padx=(50, 0), pady=(0, 0))

        # Create a custom progress bar within the frame
        self.progress = CustomProgressbar(self.progress_frame, bg='#cccccc', fg='#555555')

        # Start the progress bar update
        self.update_progress(0)

    def update_progress(self, value):
        self.progress.update_progress(value)
        if value < 100:
            # Schedule the update_progress function to run after 50ms with the new value
            self.start_menu_window.after(50, self.update_progress, value + 1)
        else:
            # Close the window when the progress reaches 100
            self.start_menu_window.destroy()
            self.parent_app.show_UI()
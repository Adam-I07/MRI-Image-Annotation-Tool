import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor

class PenSettingsDialog:
    def __init__(self, parent, line_width, choose_colour_callback, update_pen_size_callback):
        self.parent = parent  # Reference to the MRIAnnotationTool instance
        self.line_width = line_width
        self.choose_colour_callback = choose_colour_callback
        self.update_pen_size_callback = update_pen_size_callback
        self.create_dialog()

    def create_dialog(self):
        self.pen_setting_window = tk.Toplevel(self.parent.master)  # Use Toplevel instead of Tk to prevent multiple mainloops
        self.pen_setting_window.title('Pen Settings')
        self.pen_setting_window.geometry('200x150')
        self.pen_setting_window.resizable(0, 0)

        pirads_scores_label = ttk.Label(self.pen_setting_window, text="Settings:", font=("Calibri", 20))        
        pirads_scores_label.grid(row=1, column=0, padx=(50, 0), pady=(10, 0))
        top_separator = ttk.Separator(self.pen_setting_window, orient="horizontal")
        top_separator.grid(row=2, column=0, ipadx=50, padx=(50,0), pady=(10,0))
        
        colour_button = ttk.Button(self.pen_setting_window, text="Colour", command=self.choose_colour)
        colour_button.grid(row=3, column=0, padx=(40, 0), pady=(0,0))
        
        choose_pen_size_label = ttk.Label(self.pen_setting_window, text="Pen Size:", font=("Calibri", 12))
        choose_pen_size_label.grid(row=4, column=0, padx=(40, 0), pady=(0,0))
        
        choose_pen_size_scale = tk.Scale(self.pen_setting_window, from_=1, to=10, orient='horizontal', command=self.update_pen_size, showvalue=False)
        choose_pen_size_scale.set(self.line_width)
        choose_pen_size_scale.grid(row=5, column=0, padx=(40, 0), pady=(0,0))
        
        bottom_separator = ttk.Separator(self.pen_setting_window, orient="horizontal")
        bottom_separator.grid(row=6, column=0, ipadx=50, padx=(50,0), pady=(10,0))

    def choose_colour(self):
        chosen_colour = askcolor(color="#ffffff")[1]  # Default to white
        if chosen_colour:
            self.choose_colour_callback(chosen_colour)

    def update_pen_size(self, value):
        self.update_pen_size_callback(value)
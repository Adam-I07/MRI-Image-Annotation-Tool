import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk
import toolTip

class PenSettingsDialog:
    def __init__(self, parent, line_width, choose_colour_callback, update_pen_size_callback):
        self.parent = parent
        self.line_width = line_width
        self.choose_colour_callback = choose_colour_callback
        self.update_pen_size_callback = update_pen_size_callback
        self.create_dialog()

    def create_dialog(self):
        self.pen_setting_window = tk.Toplevel(self.parent.master)  # Use Toplevel instead of Tk to prevent multiple mainloops
        self.pen_setting_window.title('Pen Settings')
        self.pen_setting_window.geometry('200x190')
        self.pen_setting_window.resizable(0, 0)
        self.pen_setting_window.configure(bg='#cccccc')

        pirads_scores_label = tk.Label(self.pen_setting_window, text="Pen Settings:", font=("Calibri", 20), foreground='black', background='#cccccc')        
        pirads_scores_label.grid(row=1, column=0, padx=(35, 0), pady=(10, 0))
        top_separator = ttk.Separator(self.pen_setting_window, orient="horizontal")
        top_separator.grid(row=2, column=0, ipadx=65, padx=(35,0), pady=(10,5))

        self.colour_palette_icon = Image.open("icons/colour-palette.png") 
        self.colour_palette_icon_resized = self.colour_palette_icon.resize((65, 65))
        self.colour_palette_icon_final = ImageTk.PhotoImage(self.colour_palette_icon_resized)
        
        colour_button = tk.Button(self.pen_setting_window, image=self.colour_palette_icon_final, borderwidth=0, highlightthickness=0, width=45, height=45, command=self.choose_colour)
        colour_button.grid(row=3, column=0, padx=(35, 0), pady=(0,0))
        self.create_tool_tip(colour_button, "Choose colour")

        choose_pen_size_label = tk.Label(self.pen_setting_window, text="Pen Size:", font=("Calibri", 12), foreground='black', background='#cccccc')
        choose_pen_size_label.grid(row=4, column=0, padx=(35, 0), pady=(10,0))
        choose_pen_size_scale = tk.Scale(self.pen_setting_window, from_=1, to=10, orient='horizontal', command=self.update_pen_size, showvalue=False)
        choose_pen_size_scale.set(self.line_width)
        choose_pen_size_scale.grid(row=5, column=0, padx=(35, 0), pady=(5,0))
        
        bottom_separator = ttk.Separator(self.pen_setting_window, orient="horizontal")
        bottom_separator.grid(row=6, column=0, ipadx=65, padx=(35,0), pady=(10,0))

    def choose_colour(self):
        chosen_colour = askcolor(color="#ffffff")[1]  # Default to white
        if chosen_colour:
            self.choose_colour_callback(chosen_colour)

    def update_pen_size(self, value):
        self.update_pen_size_callback(value)

    def create_tool_tip(self, widget, text):
            tool_tip = toolTip.ToolTip(widget)  # Create a ToolTip object for the widget
            def enter(event):
                tool_tip.showtip(text)
            def leave(event):
                tool_tip.hidetip()
            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)
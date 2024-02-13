import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import toolTip

class ScanViewer:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.scans_collected = []

    def display_scans(self):
        self.display_scans_window = tk.Toplevel()
        self.display_scans_window.title('Display Scan')
        self.display_scans_window.geometry('340x110')
        self.display_scans_window.resizable(0, 0)
        self.display_scans_window.configure(bg='#cccccc')
        style = ttk.Style()
        style.theme_use('default')

        open_button_icon = Image.open("icons/open-folder.png") 
        open_button_icon_resized = open_button_icon.resize((25, 25))
        open_button_icon_final = ImageTk.PhotoImage(open_button_icon_resized)

        current_folders = []
        save_scan_folder = "saved_scans"
        get_folder_named = os.listdir(save_scan_folder)
        current_folders = get_folder_named
        if '.DS_Store' in current_folders:
            current_folders.remove('.DS_Store')

        display_scan_window_name_label = tk.Label(self.display_scans_window, text="Display Scan", font=("Calibri", 22), foreground='black', background='#cccccc')
        display_scan_window_name_label.grid(row=0, column=0, padx=(50,0), pady=10)
        select_scan_label = tk.Label(self.display_scans_window, text="Select a scan set:", font=("Calibri", 12), foreground='black', background='#cccccc')
        select_scan_label.grid(row=1, column=0, padx=(10,0), sticky='w')
        select_scan_set_combobox = ttk.Combobox(self.display_scans_window, font=('Arial', 12, 'bold'), width=40, values=current_folders)
        select_scan_set_combobox.grid(row=2, column=0, padx=(10,0), sticky='w')
        select_scan_set_combobox['state'] = 'readonly'
        load_scan_button = tk.Button(self.display_scans_window, image=open_button_icon_final, command=lambda: self.display_scan_open(select_scan_set_combobox.get()), borderwidth=0, highlightthickness=0, width=20, height=20)
        load_scan_button.grid(row=2, column=1, padx=(5,0))
        self.create_tool_tip(load_scan_button, "Load Scan Set")

        self.display_scans_window.mainloop()

    def display_scan_open(self, scan_folder_name):
        if scan_folder_name:
            self.scans_collected.clear()  # Clear previous scans
            scans_dir = "saved_scans" + "/" + scan_folder_name
            scans_list = os.listdir(scans_dir)
            scans_list.sort()
            if '.DS_Store' in scans_list:
                scans_list.remove('.DS_Store')
            if f'{scan_folder_name}_annotation_information.json' in scans_list:
                scans_list.remove(f'{scan_folder_name}_annotation_information.json')
            for scan in scans_list:
                scan_path = os.path.join(scans_dir, scan)
                self.scans_collected.append(scan_path)
            if not self.scans_collected:
                messagebox.showwarning('Warning', 'No scans found in the selected folder.')
            else:
                self.parent_app.scans_collective = self.scans_collected
                self.parent_app.current_opened_scan = scan_folder_name
                self.display_scans_window.destroy()
                self.parent_app.load_scan_viewer()  # Update the viewer with the selected scans
        else:
            messagebox.showerror('Error', 'Select a scan set please')
    
    def create_tool_tip(self, widget, text):
        tool_tip = toolTip.ToolTip(widget)  # Create a ToolTip object for the widget
        def enter(event):
            tool_tip.showtip(text)
        def leave(event):
            tool_tip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

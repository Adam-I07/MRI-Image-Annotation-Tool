import tkinter as tk
from tkinter import ttk, messagebox
import os

class ScanViewer:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.scans_collected = []

    def display_scans(self):
        self.display_scans_window = tk.Tk()
        self.display_scans_window.title('Display Scan')
        self.display_scans_window.geometry('430x130')
        self.display_scans_window.resizable(0, 0)

        current_folders = []
        save_scan_folder = "saved_scans"
        get_folder_named = os.listdir(save_scan_folder)
        current_folders = get_folder_named
        if '.DS_Store' in current_folders:
            current_folders.remove('.DS_Store')

        self.display_scan_window_name_label = ttk.Label(self.display_scans_window, text="Display Scan", font=("Caslon", 22))
        self.display_scan_window_name_label.grid(row=0, column=0, padx=(140,0), pady=10)

        self.select_scan_label = ttk.Label(self.display_scans_window, text="Select a scan set:", font=("Calibri", 12))
        self.select_scan_label.grid(row=1, column=0, padx=(10,0), sticky='w')

        self.select_scan_set_combobox = ttk.Combobox(self.display_scans_window, font=('Arial', 12, 'bold'), width=40, values=current_folders)
        self.select_scan_set_combobox.grid(row=2, column=0, padx=(10,0), sticky='w')
        self.select_scan_set_combobox['state'] = 'readonly'

        self.load_scan_button = ttk.Button(self.display_scans_window, text="Load", command=lambda: self.display_scan_open(self.select_scan_set_combobox.get()))
        self.load_scan_button.grid(row=2, column=1)

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
import shutil
import tkinter as tk
from tkinter import ttk
import os
from tkinter import messagebox
from PIL import Image, ImageTk
import toolTip

class ScanSetDelete:
    def __init__(self, parent_app=None):
        self.parent_app = parent_app
        self.current_opened_scan = None
        self.user_result = None
        self.scan_selected_to_delete = None
    
    def delete_scans(self, opened_scan):
        self.delete_scan_window = tk.Toplevel()
        self.delete_scan_window.title('Delete Scan')
        self.delete_scan_window.geometry('340x120')
        self.delete_scan_window.resizable(0, 0)
        self.delete_scan_window.configure(bg='#cccccc')
        style = ttk.Style()
        style.theme_use('default')

        delete_button_icon = Image.open("icons/delete.png") 
        delete_button_icon_resized = delete_button_icon.resize((25, 25))
        delete_button_icon_final = ImageTk.PhotoImage(delete_button_icon_resized)

        current_folders = []
        save_scan_folder = "saved_scans"
        get_folder_named = os.listdir(save_scan_folder)
        current_folders = get_folder_named
        if '.DS_Store' in current_folders:
            current_folders.remove('.DS_Store') 

        delete_scan_window_name_label = tk.Label(self.delete_scan_window, text="Delete Scans", font=("Calibri", 22), foreground='black', background='#cccccc')
        delete_scan_window_name_label.grid(row=0, column=0, padx=(50,0), pady=10)
        select_scan_set_label = tk.Label(self.delete_scan_window, text="Select a scan set to delete:", font=("Calibri", 12), foreground='black', background='#cccccc')
        select_scan_set_label.grid(row=1, column=0, padx=(10,0), sticky='w')
        select_scan_set_folder_combobox = ttk.Combobox(self.delete_scan_window, font=('Arial', 12, 'bold'), width=40, values=current_folders)
        select_scan_set_folder_combobox.grid(row=2, column=0, padx=(10,0), sticky='w')
        select_scan_set_folder_combobox['state'] = 'readonly'
        delete_scan_set_button = tk.Button(self.delete_scan_window, image=delete_button_icon_final, command=lambda: self.delete_scan_file(select_scan_set_folder_combobox.get()), borderwidth=0, highlightthickness=0, width=20, height=20)
        delete_scan_set_button.grid(row=2, column=1, padx=(5,0), pady=(0,5))
        self.create_tool_tip(delete_scan_set_button, "Delete")
        self.current_opened_scan = opened_scan
        self.delete_scan_window.mainloop()

    def delete_scan_file(self, scan_folder_to_delete):
        self.scan_selected_to_delete = scan_folder_to_delete
        if scan_folder_to_delete:
            result = messagebox.askquestion("Confirmation", f"Are you sure you would like to delete {scan_folder_to_delete}?")
            self.user_result = result
            if result == 'yes':
                save_scan_folder = "saved_scans"
                file_path_to_delete = os.path.join(save_scan_folder, scan_folder_to_delete)
                try:
                    shutil.rmtree(file_path_to_delete)
                    if scan_folder_to_delete == self.current_opened_scan:
                        self.parent_app.scans_collective.clear()
                        self.parent_app.refresh_UI() 
                        self.parent_app.load_scan_viewer() 
                    messagebox.showinfo("Deleted", f"{scan_folder_to_delete} has been successfully deleted")
                    self.delete_scan_window.destroy()
                except OSError as e:
                    print(f"Error deleting file {scan_folder_to_delete}: {e}")
        else:
            messagebox.showerror("Error", "Select a scan set to delete.")

    def create_tool_tip(self, widget, text):
        tool_tip = toolTip.ToolTip(widget)  # Create a ToolTip object for the widget
        def enter(event):
            tool_tip.showtip(text)
        def leave(event):
            tool_tip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
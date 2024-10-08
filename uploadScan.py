import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
import cv2 as cv
import json
import pydicom as PDCM
import numpy as np
from PIL import Image, ImageTk
import toolTip
import shutil

class scanUploader:
    def __init__(self):
        self.upload_scan_window = None

    def upload_scans(self):
        self.upload_scan_window = tk.Toplevel()
        self.upload_scan_window.title('Upload Scan')
        self.upload_scan_window.geometry('300x120')
        self.upload_scan_window.resizable(0, 0)
        self.upload_scan_window.configure(bg='#cccccc')

        upload_s_button_icon = Image.open("icons/upload-button.png") 
        upload_s_button_icon_resized = upload_s_button_icon.resize((25, 25))
        upload_s_button_icon_final = ImageTk.PhotoImage(upload_s_button_icon_resized)

        upload_scan_window_name_label = tk.Label(self.upload_scan_window, text="Upload Scans", font=("Calibri", 22), foreground='black', background='#cccccc')
        upload_scan_window_name_label.grid(row=0, column=0, padx=(25, 0), pady=10)
        enter_scan_folder_name_label = tk.Label(self.upload_scan_window, text="Enter a name for the scans:", font=("Calibri", 12), foreground='black', background='#cccccc')
        enter_scan_folder_name_label.grid(row=1, column=0, padx=(10, 0), sticky='w')
        self.enter_scan_name_entry = tk.Entry(self.upload_scan_window, font=('Arial', 10, 'bold'), width=40, background="#cccccc", foreground="black", highlightthickness=0)
        self.enter_scan_name_entry.grid(row=2, column=0, padx=(10, 0), sticky='w')
        scan_name_button = tk.Button(self.upload_scan_window, image=upload_s_button_icon_final, borderwidth=0, highlightthickness=0, width=20, height=20, command=lambda: self.upload_scan_folder(self.enter_scan_name_entry.get()))
        scan_name_button.grid(row=2, column=0, padx=(265,0), pady=(0,3))
        self.create_tool_tip(scan_name_button, "Upload")
        enter_scan_folder_name = tk.Label(self.upload_scan_window, text="Note: Do not enter spaces rather use - or _", font=("Calibri", 8), foreground='black', background='#cccccc')
        enter_scan_folder_name.grid(row=3, column=0, padx=(10, 0), sticky='w')

        self.upload_scan_window.mainloop()

    def save_scan_set_to_json(self, scan_set_name, scan_data):
        # Define the JSON file path for saving scan data
        json_filename = f"saved_scans/{scan_set_name}/{scan_set_name}_annotation_information.json"

        # Open the JSON file and write the scan data to it
        with open(json_filename, 'w') as json_file:
            json.dump(scan_data, json_file)

    def upload_scan_folder(self, scan_folder_name):
        # Check if the scan folder name contains spaces and show an error if it does
        if ' ' in scan_folder_name:
            messagebox.showerror('Error', 'Folder name cannot contain spaces! Please try again with a different folder name.')
            return

        save_scan_folder = "saved_scans"
        get_folder_named = os.listdir(save_scan_folder)
        current_folders = get_folder_named
        # Remove the .DS_Store file from list if it exists (common in macOS)
        if '.DS_Store' in current_folders:
            current_folders.remove('.DS_Store')
        # Check if folder already exists and show an error if it does
        if scan_folder_name in current_folders:
            messagebox.showerror('Error', 'Folder name already exists please enter a new name.')
            return

        try:
            # Create a new folder for the scans
            new_folder_path = os.path.join(save_scan_folder, scan_folder_name)        
        except OSError as e:
            messagebox.showerror('Error', f'Error creating folder: {e}')
            shutil.rmtree(new_folder_path)    

        try:
            # Create directory and handle user interface for selecting scans
            os.makedirs(new_folder_path, exist_ok=True)
            messagebox.showinfo('Select Folder', 'Select the folder where your scans you wish to upload are present.')
            filename = askdirectory()
            current_scans_folder = filename
            input_scans_list = os.listdir(current_scans_folder)
            input_scans_list.sort()
            scan_data = []

            # Process each scan file in the selected directory
            for i, scan_file in enumerate(input_scans_list):
                file_path = os.path.join(current_scans_folder, scan_file)
                file_extension = os.path.splitext(scan_file)[1].lower()
                if file_extension in ['.png', '.jpeg', '.jpg']:
                    image = cv.imread(file_path, cv.IMREAD_UNCHANGED)
                    if image is None:
                        continue  # If the image cannot be read, skip it
                    cv.imwrite(os.path.join(new_folder_path, f"{i:04d}.png"), image)
                    scan_id = f"{i:04d}.png"

                    actual_height, actual_width = image.shape[:2]
                elif file_extension == '.dcm':
                    image, instance_number = self.dicom_to_png(file_path)
                    cv.imwrite(os.path.join(new_folder_path, f"{instance_number - 1:04d}.png"), image)
                    scan_id = f"{instance_number - 1:04d}.png"
                else:
                    continue  # Skip non-image files
                
                # Append scan data with metadata
                scan_data.append({
                    'scan_id': scan_id,
                    'coordinates': [],
                    'lesion_information': []
                })
            
            messagebox.showinfo('Scans Uploaded', 'Scans have been uploaded successfully.')
            self.save_scan_set_to_json(scan_folder_name, scan_data)
            self.upload_scan_window.destroy()
        except OSError as e:
            messagebox.showerror('Error', f'Error creating folder: {e}')
            shutil.rmtree(new_folder_path)

    def dicom_to_png(self, Path):
        # Read DICOM file and extract relevant data for image processing
        DCM_Img = PDCM.read_file(Path)
        rows = DCM_Img.get(0x00280010).value  # Get number of rows from tag (0028, 0010)
        cols = DCM_Img.get(0x00280011).value  # Get number of cols from tag (0028, 0011)
        Instance_Number = int(DCM_Img.get(0x00200013).value)  # Get actual slice instance number from tag (0020, 0013)
        Window_Center = int(DCM_Img.get(0x00281050).value)  # Get window center from tag (0028, 1050)
        Window_Width = int(DCM_Img.get(0x00281051).value)  # G et window width from tag (0028, 1051)
        Window_Max = int(Window_Center + Window_Width / 2)
        Window_Min = int(Window_Center - Window_Width / 2)

        # Rescale values if present in DICOM tags
        if (DCM_Img.get(0x00281052) is None):
            Rescale_Intercept = 0
        else:
            Rescale_Intercept = int(DCM_Img.get(0x00281052).value)

        if (DCM_Img.get(0x00281053) is None):
            Rescale_Slope = 1
        else:
            Rescale_Slope = int(DCM_Img.get(0x00281053).value)

        # Create an image matrix and adjust pixels based on window settings and rescale values
        New_Img = np.zeros((rows, cols), np.uint8)
        Pixels = DCM_Img.pixel_array
        for i in range(0, rows):
            for j in range(0, cols):
                Pix_Val = Pixels[i][j]
                Rescale_Pix_Val = Pix_Val * Rescale_Slope + Rescale_Intercept
                if (Rescale_Pix_Val > Window_Max):  # if intensity is greater than max window
                    New_Img[i][j] = 255
                elif (Rescale_Pix_Val < Window_Min):  # if intensity is less than min window
                    New_Img[i][j] = 0
                else:
                    New_Img[i][j] = int(
                        ((Rescale_Pix_Val - Window_Min) / (Window_Max - Window_Min)) * 255)  # Normalize the intensities
        return New_Img, Instance_Number

    def create_tool_tip(self, widget, text):
        tool_tip = toolTip.ToolTip(widget)  # Create a ToolTip object for the widget
        def enter(event):
            tool_tip.showtip(text)
        def leave(event):
            tool_tip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

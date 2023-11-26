from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import os
import cv2 as cv
import numpy as np
import pydicom as PDCM
from tkinter.filedialog import askdirectory


class FixedSizeWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("MRI Annotation Tool")
        self.master.geometry("1000x700")
        self.master.resizable(0, 0)

        # Frame Creation
        self.menu_frame = ttk.Frame(master, height=100, borderwidth=3, relief='sunken')
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.viewer_frame = ttk.Frame(master, width=700, borderwidth=2, relief='sunken')
        self.viewer_frame.grid(row=1, column=0, sticky='nsew')
        self.pirad_frame = ttk.Frame(master, width=300, borderwidth=2, relief='sunken')
        self.pirad_frame.grid(row=1, column=1, sticky='nsew')

        # Set weight for resizable rows and columns
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        # Menu Widgets and Buttons
        self.menu_title_label = ttk.Label(self.menu_frame, text="MRI Image Annotation Tool", font=("Caslon", 25))
        self.menu_title_label.grid(row=0, column=0, padx=10, pady=10)
        self.upload_scan_button = ttk.Button(self.menu_frame, text="Upload Scans", command=self.upload_scans)
        self.upload_scan_button.grid(row=0, column=1, padx=(140,20))
        self.display_scan_button = ttk.Button(self.menu_frame, text="Display Scans", command=self.display_scans)
        self.display_scan_button.grid(row=0, column=2, padx=(0,20))
        self.delete_scan_button = ttk.Button(self.menu_frame, text="Delete Scans")
        self.delete_scan_button.grid(row=0, column=3, padx=(0,20))
        self.exit_button = ttk.Button(self.menu_frame, text="Exit", command=lambda:self.exit_application)
        self.exit_button.grid(row=0, column=4, padx=(0,10))

        # Viewer Widgets and Buttons
        self.viewer_title_label = ttk.Label(self.viewer_frame, text="Scan Viewer", font=("Caslon", 22))
        self.viewer_title_label.grid(row=0, column=0, padx=250)
        self.scans_collective = []
        self.load_scan_viewer()
        self.viewer_frame.grid_propagate(0)

        # PI-RAD Frame Widgets and Buttons
        self.pirad_title_label = ttk.Label(self.pirad_frame, text="PI-RADS", font=("Caslon", 22))
        self.pirad_title_label.grid(row=0, column=0, padx=100)
        self.pirad_frame.grid_propagate(0)

    # Code to allows the user to exit from the application
    def exit_application(self):
        self.master.destroy()

    #Following code is the start for the Scan Viewer to be displayed on the Main Menu
    def load_scan_viewer(self):
        self.original_xlim = None
        self.original_ylim = None
        self.original_views = None

        # Destroy existing widgets
        if hasattr(self, 'canvas_frame'):
            self.canvas_frame.destroy()
            del self.canvas_frame

        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            del self.canvas

        if hasattr(self, 'toolbar'):
            self.toolbar.destroy()
            del self.toolbar

        if hasattr(self, 'scan_scrollbar'):
            self.scan_scrollbar.destroy()
            del self.scan_scrollbar

        if self.scans_collective:
            self.current_scan_num = 0

            if hasattr(self, 'no_scans_label'):
                self.no_scans_label.destroy()
                del self.no_scans_label

            scan_arr = mpimg.imread(self.scans_collective[self.current_scan_num])

            # Get the actual size of the image
            actual_height, actual_width = scan_arr.shape

            # Create a figure and subplot for displaying scans
            self.f = Figure(figsize=(actual_width / 100, actual_height / 100), dpi=120)
            self.a = self.f.add_subplot(111)

            # Set aspect ratio to 'equal' to display the image in its actual size
            self.a.imshow(scan_arr, cmap='gray', aspect='equal')
            self.a.axis('off')

            # Create a frame for the canvas
            self.canvas_frame = tk.Frame(self.viewer_frame)
            self.canvas_frame.grid(row=2, column=0, padx=(10, 0))

            self.canvas = FigureCanvasTkAgg(self.f, self.canvas_frame)

            # Draw canvas
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=2, column=0, padx=(10, 0))

            # Override the home method to use custom reset_zoom
            self.toolbar_home = self.reset_zoom

            # Bind mouse scroll event to zoom
            self.canvas.mpl_connect('scroll_event', self.on_mouse_scroll) if hasattr(self, 'on_mouse_scroll') else None

            # Create a frame for the toolbar
            self.toolbar_frame = ttk.Frame(self.viewer_frame)

            padx_for_scrollbar = actual_width + (actual_width/2)  # Adjust as needed
            self.scan_scrollbar = ttk.Scale(self.viewer_frame, orient="vertical", from_=1, to=len(self.scans_collective), command=self.next_scan)
            self.scan_scrollbar.grid(row=2, column=0, padx=(padx_for_scrollbar,0))


            self.reset_view_button = ttk.Button(self.viewer_frame, text="Reset", command=self.reset_view)
            self.reset_view_button.grid(row=3, column=0, padx=(0, 200))  # Adjusted the padx here

            # Add a zoom button with rectangle functionality
            self.zoom_button = ttk.Button(self.viewer_frame, text="Zoom", command=self.zoom_to_rectangle)
            self.zoom_button.grid(row=3, column=0)

            # Create a label to display the coordinates
            self.coordinates_label = ttk.Label(self.viewer_frame, text="Coordinates: (0, 0)", font=("Calibri", 12))
            self.coordinates_label.grid(row=3, column=0, padx=(0, 400))

            # Bind mouse motion event to update coordinates label
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

            # Create a new toolbar instance
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
            self.toolbar.update()

            # Initialize a variable to track the zoom rectangle state
            self.zoom_rectangle_active = False

            # Flag to track the source of the zoom
            self.zoom_source = None
        else:
            # Display a message if no scans are available
            self.no_scans_label = ttk.Label(self.viewer_frame, text="No scan set is currently opened.", font=("Caslon", 20))
            self.no_scans_label.grid(row=2, column=0, padx=(10, 0), pady=(200))

    def next_scan(self, scan_number):
        scan_number_int = int(float(scan_number)) - 1
        scan_arr = mpimg.imread(self.scans_collective[scan_number_int])
        self.current_scan_num = scan_number_int

        # Update the displayed scan
        self.a.clear()
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')
        self.canvas.draw()

    def reset_view(self):
        # Get the current NavigationToolbar2Tk instance
        self.toolbar = self.toolbar

        # Reset the view using the NavigationToolbar2Tk's home button
        self.toolbar.home()

        # Update the displayed scan
        self.a.clear()
        scan_arr = mpimg.imread(self.scans_collective[self.current_scan_num])
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')

        # Redraw the canvas
        self.canvas.draw()

    def zoom_to_rectangle(self):
        # Call the zoom_to_rect method from the existing toolbar
        self.toolbar.zoom()
        
        # Update the displayed scan
        self.a.clear()
        scan_arr = mpimg.imread(self.scans_collective[self.current_scan_num])
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')

        # Redraw the canvas
        self.canvas.draw()

    def on_mouse_motion(self, event):
        # Check if the event is a motion event and if xdata and ydata are not None
        if event.name == 'motion_notify_event' and event.xdata is not None and event.ydata is not None:
            # Get the x and y coordinates of the mouse pointer
            x, y = int(event.xdata), int(event.ydata)
        else:
            # Set coordinates to (0, 0) when outside the image
            x, y = 0, 0

        # Update the coordinates label
        self.coordinates_label.config(text=f"Coordinates: ({x}, {y})")
        pass

    def zoom(self, scale, x, y, mouse_zoom=True):
        if mouse_zoom:
            # Calculate the new axis limits after zooming
            new_xlim = [coord * scale - (scale - 1) * x for coord in self.a.get_xlim()]
            new_ylim = [coord * scale - (scale - 1) * y for coord in self.a.get_ylim()]

            # Set the new axis limits
            self.a.set_xlim(new_xlim)
            self.a.set_ylim(new_ylim)
        else:
            # Use the original axis limits when resetting
            self.a.set_xlim(self.original_views.home().intervalx)
            self.a.set_ylim(self.original_views.home().intervaly)

        # Redraw the canvas
        self.canvas.draw()

    def reset_zoom(self, *args):
        # Manually reset the zoom state
        if self.original_xlim is not None and self.original_ylim is not None:
            if self.zoom_source == "button":
                # Reset when zoom initiated by Zoom In button
                self.a.set_xlim(self.original_xlim)
                self.a.set_ylim(self.original_ylim)
            else:
                # Reset when zoom initiated by mouse scroll
                self.a.set_xlim(self.original_views.home().intervalx)
                self.a.set_ylim(self.original_views.home().intervaly)

            # Reset the zoom source flag
            self.zoom_source = None

        # Redraw the canvas
        self.canvas.draw()
    #End of Main Menu Display Viewer Code


    #Following code is the start for the Display Scans
    def display_scans(self):
        self.display_scans_window = tk.Tk()
        self.display_scans_window.title('Display Scan')
        self.display_scans_window.geometry('500x130')
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
        if len(scan_folder_name) == 0:
            messagebox.showerror('Error', 'Select a folder please')
        else:
            self.scans_collective.clear()
            scans_dir = "saved_scans" + "/" + scan_folder_name
            scans_list = os.listdir(scans_dir)
            scans_list.sort()
            if '.DS_Store' in scans_list:
                scans_list.remove('.DS_Store')
            for i in range(0, len(scans_list)):
                scan_name = (f'{scans_dir}/{scans_list[i]}')
                self.scans_collective.append(scan_name)
            
            if not self.scans_collective:
                messagebox.showwarning('Warning', 'No scans found in the selected folder.')
            else:
                self.display_scans_window.destroy()
                self.load_scan_viewer()
                messagebox.showinfo('Success', 'Scans have successully opened for viewing')


    #End of Display Scans code


    #Following code is the start for the Uploading Scans
    def upload_scans(self):
        self.upload_scan_window = tk.Tk()
        self.upload_scan_window.title('Upload Scan')
        self.upload_scan_window.geometry('400x130')
        self.upload_scan_window.resizable(0, 0)

        self.upload_scan_window_name_label = ttk.Label(self.upload_scan_window, text="Upload Scans", font=("Caslon", 22))
        self.upload_scan_window_name_label.grid(row=0, column=0, padx=(140,0), pady=10)
        self.enter_scan_folder_name_label = ttk.Label(self.upload_scan_window, text="Enter a name for the scans:", font=("Calibri", 12))
        self.enter_scan_folder_name_label.grid(row=1, column=0, padx=(10,0), sticky='w')
        self.enter_scan_name_entry = ttk.Entry(self.upload_scan_window, font=('Arial', 10, 'bold'), width=40)
        self.enter_scan_name_entry.grid(row=2, column=0, padx=(10,0), sticky='w')
        self.scan_name_button = ttk.Button(self.upload_scan_window, text="Upload", command=lambda: self.upload_scan_folder(self.enter_scan_name_entry.get()))
        self.scan_name_button.grid(row=2, column=1)
        self.enter_scan_folder_name = ttk.Label(self.upload_scan_window, text="Note: Do not enter spaces rather use - or _", font=("Calibri", 8))
        self.enter_scan_folder_name.grid(row=3, column=0, padx=(10,0), sticky='w')

        self.upload_scan_window.mainloop()
    
    def upload_scan_folder(self, scan_folder_name):
        if scan_folder_name:
            if ' ' in scan_folder_name:
                messagebox.showerror('Error','Folder name cannot contain spaces! Please try again with a different folder name.')
            else:
                save_scan_folder = "saved_scans"
                get_folder_named = os.listdir(save_scan_folder)
                current_folders = get_folder_named
                if '.DS_Store' in current_folders:
                    current_folders.remove('.DS_Store')   
                if scan_folder_name in current_folders:
                    messagebox.showerror('Error', 'Folder name already exists please enter a new name.')
                else:
                    new_folder_path = os.path.join(save_scan_folder, scan_folder_name)
                    try:
                        os.makedirs(new_folder_path)
                        messagebox.showinfo('Select Folder', 'Select the folder where your scans you wish to upload are present.')
                        filename = askdirectory()
                        current_scans_folder = filename
                        
                        input_scans_list = os.listdir(current_scans_folder)
                        input_scans_list.sort()

                        if os.path.isdir(new_folder_path) is False:
                            os.mkdir(new_folder_path)

                        for i in range(0, len(input_scans_list)):
                            dicom_path = os.path.join(current_scans_folder, input_scans_list[i])
                            output_scans, instance_number = self.dicom_to_png(dicom_path)
                            cv.imwrite(os.path.join(new_folder_path, f"{instance_number - 1:04d}.png"), output_scans)
                        
                        messagebox.showinfo('Scans Uploaded', 'Scans have been uploaded successfully.')

                        # Close the upload_scan_window
                        self.upload_scan_window.destroy()
                    except OSError as e:
                        messagebox.showerror('Error', f'Error creating folder: {e}')
        else:
            messagebox.showerror('Error', 'Enter a folder name.')

    def dicom_to_png(self, Path):
        DCM_Img = PDCM.read_file(Path)

        rows = DCM_Img.get(0x00280010).value  # Get number of rows from tag (0028, 0010)
        cols = DCM_Img.get(0x00280011).value  # Get number of cols from tag (0028, 0011)

        Instance_Number = int(DCM_Img.get(0x00200013).value)  # Get actual slice instance number from tag (0020, 0013)

        Window_Center = int(DCM_Img.get(0x00281050).value)  # Get window center from tag (0028, 1050)
        Window_Width = int(DCM_Img.get(0x00281051).value)  # Get window width from tag (0028, 1051)

        Window_Max = int(Window_Center + Window_Width / 2)
        Window_Min = int(Window_Center - Window_Width / 2)

        if (DCM_Img.get(0x00281052) is None):
            Rescale_Intercept = 0
        else:
            Rescale_Intercept = int(DCM_Img.get(0x00281052).value)

        if (DCM_Img.get(0x00281053) is None):
            Rescale_Slope = 1
        else:
            Rescale_Slope = int(DCM_Img.get(0x00281053).value)

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
    
    #Uploading Scans Code Ending


 

if __name__ == "__main__":
    root = tk.Tk()
    app = FixedSizeWindow(root)
    root.mainloop()

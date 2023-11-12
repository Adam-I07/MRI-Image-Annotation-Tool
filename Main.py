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


LARGE_FONT = ("Calibri", 27)


class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.windows = {}

        for i in (MainMenu, UploadScanWindow, AnnotateScanWindow, ScanViewerWindow):
            window = i(container, self)
            self.windows[i] = window
            window.grid(row=0, column=0, sticky="nsew")

        self.display_window(MainMenu)

    def display_window(self, cont):
        window = self.windows[cont]
        window.tkraise()
        if cont == UploadScanWindow:
            window.on_show()
        elif cont == AnnotateScanWindow:
            window.on_show()
        elif cont == MainMenu:
            window.on_show()
        elif cont == ScanViewerWindow:
            window.on_show()


class MainMenu(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label_title = tk.Label(self, text="MRI Image Annotation Tool", font=LARGE_FONT)
        label_title.grid(row=0, column=1)  # Center the title

        button_width = 15

        button_upload_scan_window = ttk.Button(self, text="Upload Scans", width=button_width,  command=lambda: controller.display_window(UploadScanWindow))
        button_upload_scan_window.grid(row=1, column=1)  # Center the button

        button_annotate_scan_window = ttk.Button(self, text="Annotate Scans", width=button_width, command=lambda: controller.display_window(AnnotateScanWindow))
        button_annotate_scan_window.grid(row=2, column=1)  # Center the button

        button_scan_viewer_window = ttk.Button(self, text="Scan Viewer", width=button_width, command=lambda: controller.display_window(ScanViewerWindow))
        button_scan_viewer_window.grid(row=3, column=1)  # Center the button

        button_exit_program = ttk.Button(self, text="Exit", width=button_width, command=self.quit)
        button_exit_program.grid(row=4, column=1)  # Center the button

        # Add column weights to make the buttons expand and center
        for col in range(5):
            self.grid_columnconfigure(col, weight=1)

    def on_show(self):
        self.winfo_toplevel().geometry("400x180")

class UploadScanWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Center the label
        label = tk.Label(self, text="Upload Scans", font=LARGE_FONT)
        label.pack(side="top")

        # Center the "Process Scans" button
        button_process_scans = ttk.Button(self, text="Upload Scans", command=self.process_scans)
        button_process_scans.pack()

        # Center the "Back" button
        button_back_to_start_menu = ttk.Button(self, text="Back", command=lambda: controller.display_window(MainMenu))
        button_back_to_start_menu.pack()


    def on_show(self):
        self.winfo_toplevel().geometry("310x150")

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

    def process_scans(self):
        filename = askdirectory() # show an "Open" dialog box and return the path to the selected file

        input_folder = filename
        output_folder = 'png_scans'

        input_scans_list = os.listdir(input_folder)
        input_scans_list.sort()

        if os.path.isdir(output_folder) is False:
            os.mkdir(output_folder)

        for i in range(0, len(input_scans_list)):
            dicom_path = os.path.join(input_folder, input_scans_list[i])
            output_scans, instance_number = self.dicom_to_png(dicom_path)
            cv.imwrite(os.path.join(output_folder, f"{instance_number - 1:04d}.png"), output_scans)



class AnnotateScanWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Annotate Scan", font=LARGE_FONT)
        label.grid(row=0, column=0)

        button_back_to_start_menu = ttk.Button(self, text="Back", command=lambda: controller.display_window(MainMenu))
        button_back_to_start_menu.grid(row=1, column=1)

    def on_show(self):
        self.winfo_toplevel().geometry("400x400")
    

class ScanViewerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label_frame = tk.Frame(self)
        label_frame.pack(side="top", fill="both", expand=True)

        label = tk.Label(label_frame, text="Scan Viewer", font=LARGE_FONT, anchor='center')
        label.pack(fill='x')

        if scans_collective:
            self.view_error = 0
            self.scan_scrollbar = ttk.Scale(self, orient="vertical", from_=1, to=len(scans_collective), command=self.next_scan)
            self.scan_scrollbar.pack(side="right")

            self.current_scan_num = 0

            scan_arr = mpimg.imread(scans_collective[self.current_scan_num])

            # Get the actual size of the image
            actual_height, actual_width = scan_arr.shape

            # Create a figure and subplot for displaying scans
            self.f = Figure(figsize=(actual_width / 100, actual_height / 100), dpi=150)
            self.a = self.f.add_subplot(111)

            # Set aspect ratio to 'equal' to display the image in its actual size
            self.a.imshow(scan_arr, cmap='gray', aspect='equal')
            self.a.axis('off')

            # Create a frame for the canvas
            self.canvas_frame = tk.Frame(self)
            self.canvas_frame.pack() 

            self.canvas = FigureCanvasTkAgg(self.f, self.canvas_frame)

            # Draw canvas
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()

            # Create a frame for the toolbar
            toolbar_frame = tk.Frame(self)
            toolbar_frame.pack(side="left")

            toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            toolbar.update()

            # Hide unwanted buttons
            toolbar.children['!button5'].pack_forget()
            toolbar.children['!button2'].pack_forget()
            toolbar.children['!button3'].pack_forget()

            # Back button at the bottom right
            button_back_to_main_menu = ttk.Button(self, text="Back", command=lambda: controller.display_window(MainMenu))
            button_back_to_main_menu.pack(side="bottom", anchor="se")

        else:
            self.view_error = 1
            # Display a message if no scans are available
            no_scans_label = tk.Label(self, text="No scans available.", font=tkFont.Font(family="Calibri", size=24),)
            no_scans_label.pack()

            # Back button at the bottom right
            button_back_to_main_menu = ttk.Button(self, text="Back", command=lambda: controller.display_window(MainMenu))
            button_back_to_main_menu.pack()

    def on_show(self):
        if self.view_error == 0:
            canvas_width = (self.f.get_figwidth() * self.f.get_dpi()) + 20
            canvas_height = (self.f.get_figheight() * self.f.get_dpi()) + 80

            self.winfo_toplevel().geometry(f"{int(canvas_width)}x{int(canvas_height)}")
        else:
            self.winfo_toplevel().geometry("320x200")

    def next_scan(self, scan_number):
        scan_number_int = int(float(scan_number)) - 1
        scan_arr = mpimg.imread(scans_collective[scan_number_int])
        self.current_scan_num = scan_number_int

        # Update the displayed scan
        self.a.clear()
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')
        self.canvas.draw()

if __name__ == "__main__":
    scans_dir = 'png_scans'
    scans_list = os.listdir(scans_dir)
    scans_list.sort()
    scans_collective = []
    if '.DS_Store' in scans_list:
        scans_list.remove('.DS_Store')
    for i in range(0, len(scans_list)):
        scan_name = (f'{scans_dir}/{scans_list[i]}')
        scans_collective.append(scan_name)

app = Main()
app.mainloop()

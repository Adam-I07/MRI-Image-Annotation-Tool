import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import ttk
import os


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
        self.winfo_toplevel().geometry("400x200")


class UploadScanWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Upload Scans", font=LARGE_FONT)
        label.grid(row=0, column=1)

        button_back_to_start_menu = ttk.Button(self, text="Back", command=lambda: controller.display_window(MainMenu))
        button_back_to_start_menu.grid(row=1, column=0)

    def on_show(self):
        self.winfo_toplevel().geometry("300x200")


class AnnotateScanWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Annotate Scan", font=LARGE_FONT)
        label.grid(row=0, column=0)

        button_back_to_start_menu = ttk.Button(self, text="Back",command=lambda: controller.display_window(MainMenu))
        button_back_to_start_menu.grid(row=1, column=0)

    def on_show(self):
        self.winfo_toplevel().geometry("300x300")
    

class ScanViewerWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label_frame = tk.Frame(self)
        label_frame.pack(side="top", fill="both", expand=True)

        label = tk.Label(label_frame, text="Scan Viewer", font=LARGE_FONT, anchor='center')
        label.pack(fill='x')

        self.scan_scrollbar = ttk.Scale(self, orient="vertical", from_=1, to=len(scans_collective), command=self.next_scan)
        self.scan_scrollbar.pack(side="right")

        # Initialize current_img_num
        self.current_img_num = 0

        img_arr = mpimg.imread(scans_collective[self.current_img_num])

        # Create a figure and subplot for displaying images
        self.f = Figure(figsize=(4, 4), dpi=100)
        self.a = self.f.add_subplot(111)

        self.a.imshow(img_arr, cmap='gray')

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

    def on_show(self):
        self.winfo_toplevel().geometry("420x480")

    def next_scan(self, image_number):
        image_number_int = int(float(image_number)) - 1
        img_arr = mpimg.imread(scans_collective[image_number_int])
        self.current_img_num = image_number_int

        # Update the displayed image
        self.a.clear()
        self.a.imshow(img_arr, cmap='gray')
        self.canvas.draw()



if __name__ == "__main__":
    scans_dir = 'png_images'
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
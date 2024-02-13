from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import ttk
import os
import numpy as np
import json
import matplotlib.lines as mlines
import uploadScan
import deleteScan
import displayScan
import lesionToggle
import penSetting
from PIL import Image, ImageTk
import toolTip

class MRIAnnotationTool:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1100x700")
        self.master.title("MRI Annotation Tool")
        self.master.resizable(0, 0)
        self.master.configure(bg='#cccccc')

        # Add a variable to track the pen drawing state
        self.drawing = False
        self.prev_x = 0
        self.prev_y = 0
        self.shape_drawing = False 
        self.drawing_active = False
        self.zoom_active = False
        self.undo_active = False
        self.all_annotations = []
        self.current_annotations = []
        self.all_lesions_information = []
        self.current_lesions_used = []
        self.next_lesion_number = None
        self.active_button = None
        self.current_opened_scan = None
        self.current_opened_lesion = None
        self.canvas = None
        self.chosencolour = '#ff0000'
        self.line_width = 2
        self.display_scan_instance =  displayScan.ScanViewer(self)
        self.scans_collective = []

        # Add canvas width and height attributes
        self.canvas_width = 0
        self.canvas_height = 0

        style = ttk.Style()
        style.theme_use('default')

        # Frame Creation
        self.menu_frame = tk.Frame(master, width=50, borderwidth=2, relief='sunken', bg='#cccccc')
        self.menu_frame.grid(row=1, column=0, sticky='nsew')
        self.viewer_frame = tk.Frame(master, width=600, borderwidth=2, relief='sunken', bg='#cccccc')
        self.viewer_frame.grid(row=1, column=1, sticky='nsew')
        self.pirad_frame = tk.Frame(master, width=220, borderwidth=2, relief='sunken', background='#cccccc')
        self.pirad_frame.grid(row=1, column=2, sticky='nsew')

        # Set weight for resizable rows and columns
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        # Viewer Widgets and Buttons
        self.viewer_title_label = tk.Label(self.viewer_frame, text="Scan Viewer", font=("Calibri", 22), foreground='black', background='#cccccc')
        self.viewer_title_label.grid(row=0, column=0, padx=270)
        self.viewer_frame.grid_propagate(0)

        # Tool Widgets and Buttons
        self.display_scan_icon = Image.open("icons/display-scan.png") 
        self.display_scan_icon_resized = self.display_scan_icon.resize((65, 65))
        self.display_scan_icon_final = ImageTk.PhotoImage(self.display_scan_icon_resized)
        self.upload_scan_icon = Image.open("icons/upload-scan.png") 
        self.upload_scan_icon_resized = self.upload_scan_icon.resize((65, 65))
        self.upload_scan_icon_final = ImageTk.PhotoImage(self.upload_scan_icon_resized)
        self.delete_scan_icon = Image.open("icons/delete-scan.png") 
        self.delete_scan_icon_resized = self.delete_scan_icon.resize((65, 65))
        self.delete_scan_icon_final = ImageTk.PhotoImage(self.delete_scan_icon_resized)
        self.exit_icon = Image.open("icons/exit.png") 
        self.exit_icon_resized = self.exit_icon.resize((65, 65))
        self.exit_icon_final = ImageTk.PhotoImage(self.exit_icon_resized)

        self.load_scan_viewer()
        self.tool_title_label = tk.Label(self.menu_frame, text="Menu", font=("Calibri", 22), foreground='black', background='#cccccc')
        self.tool_title_label.grid(row=0, column=0, padx=(26,0), sticky=tk.W)
        self.menu_separator = ttk.Separator(self.menu_frame, orient="horizontal")
        self.menu_separator.grid(row=1, column=0, columnspan=3, ipadx=40, padx=(15,0), pady=(10,0), sticky=tk.W)
        self.upload_scan_button = tk.Button(self.menu_frame, image=self.upload_scan_icon_final, command=self.upload_scans, borderwidth=0, highlightthickness=0, width=45, height=45)
        self.upload_scan_button.grid(row=2, column=0, padx=(30,0), pady=(5,0), sticky=tk.W)
        self.create_tool_tip(self.upload_scan_button, "Upload scan")
        self.display_scan_button = tk.Button(self.menu_frame, image=self.display_scan_icon_final, command=self.display_scans, borderwidth=0, highlightthickness=0, width=45, height=45)
        self.display_scan_button.grid(row=3, column=0, padx=(30, 0), pady=(5,0), sticky=tk.W)
        self.create_tool_tip(self.display_scan_button, "Display scan")
        self.delete_scan_button = tk.Button(self.menu_frame, image=self.delete_scan_icon_final, command=self.delete_scans, borderwidth=0, highlightthickness=0, width=45, height=45)
        self.delete_scan_button.grid(row=4, column=0, padx=(30, 0), pady=(5,0), sticky=tk.W)
        self.create_tool_tip(self.delete_scan_button, "Delete scan")
        self.exit_button = tk.Button(self.menu_frame, image=self.exit_icon_final, command=self.exit_application, borderwidth=0, highlightthickness=0, width=45, height=45)
        self.exit_button.grid(row=5, column=0, padx=(27, 0), pady=(5,0), sticky=tk.W)
        self.create_tool_tip(self.exit_button, "Exit application")
        self.menu_frame.grid_propagate(0)

        # PI-RAD Frame Widgets and Buttons
        self.pirad_title_label = tk.Label(self.pirad_frame, text="PI-RADS", font=("Calibri", 22), foreground='black', background='#cccccc')
        self.pirad_title_label.grid(row=0, column=0, padx=100)
        self.pirad_frame.grid_propagate(0)

    def upload_scans(self):
        scan_uploader = uploadScan.scanUploader()
        scan_uploader.upload_scans()

    def exit_application(self):
        self.master.destroy()

    def display_scans(self):
        self.display_scan_instance.display_scans()
   
    def refresh_UI(self):
        attributes_to_clear = [
            'canvas_frame', 'canvas', 'toolbar_frame', 'scan_scale', 
            'home_view_button', 'zoom_button', 'coordinates_label', 'toolbar',
            'viewing_separator', 'viewing_widgets_label', 'tool_separator', 
            'annotation_tool_label', 'drawing_button', 'colour_button', 
            'undo_button', 'choose_pen_size_label', 'choose_pen_size_scale', 
            'saving_separator', 'saving_label', 'save_annotations_button', 'viewing_separator', 'tool_separator'
            'lesion_separator', 'select_lesion_label', 'select_lesion_combobox', 
            'load_lesion_button', 't2w_separator', 't2_weighted_imaging_label', 
            't2w_peripheral_zone_label', 't2w_peripheral_zone_combobox', 
            't2w_transition_zone_label', 't2w_transition_zone_combobox', 
            'dwi_top_separator', 'diffusion_weighted_imaging_label', 
            'diffusion_weighted_peripheral_zone_label', 'diffusion_weighted_peripheral_zone_combobox', 
            'diffusion_weighted_transition_zone_label', 'diffusion_weighted_transition_zone_combobox', 
            'dynamic_contrast_enhanced_imaging_separator', 'dynamic_contrast_enhanced_imaging_label', 
            'dynamic_contrast_enhanced_imaging_combobox', 'pirads_score_separator', 
            'pirads_scores_label', 'pirad_score_combobox', 'additional_comments_separator', 
            'additional_comments_label', 'additional_comments_textbox', 'toggle_lesion_button', 
            'pen_setting_button']

        for attr in attributes_to_clear:
            if hasattr(self, attr):
                # Special handling for the 'canvas' attribute to use get_tk_widget().destroy()
                if attr == 'canvas' and getattr(self, attr) is not None:
                    getattr(self, attr).get_tk_widget().destroy()
                else:
                    widget = getattr(self, attr)
                    if widget is not None:
                        widget.destroy()
                delattr(self, attr)
    
    #Delete Scans Code 
    def delete_scans(self):
        delete_scan = deleteScan.ScanSetDelete(self)
        delete_scan.delete_scans(self.current_opened_scan)

    def load_scan_viewer(self):
        self.original_xlim = None
        self.original_ylim = None
        self.original_views = None
        self.refresh_UI()
        
        if self.scans_collective:
            self.current_scan = self.scans_collective[0]

            if hasattr(self, 'no_scans_label'):
                self.no_scans_label.destroy()
                del self.no_scans_label

            scan_arr = mpimg.imread(self.current_scan)
            # Get the actual size of the image
            actual_height, actual_width = scan_arr.shape

            # Create a figure and subplot for displaying scans
            self.f = Figure(figsize=(actual_width / 100, actual_height / 100), dpi=120)
            self.a = self.f.add_subplot(111)

            # Set aspect ratio to 'equal' to display the image in its actual size
            self.a.imshow(scan_arr, cmap='gray', aspect='equal')
            self.a.axis('off')

            # Remove extra whitespace around the image
            self.f.subplots_adjust(left=0, right=1, top=1, bottom=0)
            self.a.set_aspect('auto') 

            # Create a frame for the canvas
            self.canvas_frame = tk.Frame(self.viewer_frame)
            self.canvas_frame.grid(row=1, column=0, padx=(20, 0), pady=(10, 0))
            self.canvas = FigureCanvasTkAgg(self.f, self.canvas_frame)

            # Set canvas width and height
            self.canvas_width, self.canvas_height = self.f.get_size_inches() * self.f.dpi

            # Bind mouse button press, release, and motion events for drawing
            self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
            self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
            self.canvas.mpl_connect('motion_notify_event', self.draw_on_canvas)
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

            # Draw canvas
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=2, column=0, padx=(0, 0))

            # Load annotations and PI-RADS for the initial scan
            json_file_path = os.path.join("saved_scans", f"{self.current_opened_scan}", f"{self.current_opened_scan}_annotation_information.json")
            self.load_annotations_from_json(json_file_path)
            self.toolbar_home = self.reset_zoom

            # Load viewer frame, scale and coordinates label
            self.toolbar_frame = ttk.Frame(self.viewer_frame)
            self.scan_scale = tk.Scale(self.viewer_frame, orient="horizontal", from_=1, to=len(self.scans_collective), showvalue=False, command=self.next_scan, background="#cccccc")
            self.scan_scale.grid(row=2, column=0, padx=(0,0), pady=(10,0))
            self.coordinates_label = tk.Label(self.viewer_frame, text="Coordinates: (0, 0)", font=("Calibri", 12), foreground='black', background='#cccccc')
            self.coordinates_label.grid(row=2, column=0, padx=(0, 400), pady=(7,0))

            # Load the icons for buttons using PIL
            self.pen_icon = Image.open("icons/pen.png") 
            self.pen_icon_resized = self.pen_icon.resize((100, 100)) 
            self.pen_icon_final = ImageTk.PhotoImage(self.pen_icon_resized)
            self.undo_icon = Image.open("icons/rubber.png") 
            self.undo_icon_resized = self.undo_icon.resize((55, 55))
            self.undo_icon_final = ImageTk.PhotoImage(self.undo_icon_resized)
            self.setting_icon = Image.open("icons/setting.png") 
            self.setting_icon_resized = self.setting_icon.resize((55, 55))
            self.setting_icon_final = ImageTk.PhotoImage(self.setting_icon_resized)
            self.zoom_icon = Image.open("icons/zoom.png") 
            self.zoom_icon_resized = self.zoom_icon.resize((50, 50))
            self.zoom_icon_final = ImageTk.PhotoImage(self.zoom_icon_resized)
            self.home_icon = Image.open("icons/home.png") 
            self.home_icon_resized = self.home_icon.resize((50, 50))
            self.home_icon_final = ImageTk.PhotoImage(self.home_icon_resized)
            self.load_pirad_icon = Image.open("icons/load-pirad-form.png")
            self.load_pirad_icon_resized = self.load_pirad_icon.resize((50, 50))
            self.load_pirad_icon_final = ImageTk.PhotoImage(self.load_pirad_icon_resized)
            self.toggle_icon = Image.open("icons/toggle.png")
            self.toggle_icon_resized = self.toggle_icon.resize((50, 50))
            self.toggle_icon_final = ImageTk.PhotoImage(self.toggle_icon_resized)
            self.save_icon = Image.open("icons/save.png")
            self.save_icon_resized = self.save_icon.resize((50, 50))
            self.save_icon_final = ImageTk.PhotoImage(self.save_icon_resized)

            # Annotation Tools Widgets
            self.tool_separator = ttk.Separator(self.menu_frame, orient="horizontal")
            self.tool_separator.grid(row=6, column=0, columnspan=3, ipadx=40, padx=(15,0), pady=(5,0), sticky=tk.W)
            self.annotation_tool_label = tk.Label(self.menu_frame, text="Annotation\n  Tools:", font=("Calibri", 14), foreground='black', background='#cccccc')
            self.annotation_tool_label.grid(row=7, column=0, padx=(17, 0), pady=(5, 0), sticky=tk.W)
            self.tool_title_seperator = ttk.Separator(self.menu_frame, orient="horizontal")
            self.tool_title_seperator.grid(row=8, column=0, columnspan=4, ipadx=40, padx=(15,0), pady=(5,0), sticky=tk.W)
            self.drawing_button = tk.Button(self.menu_frame, image=self.pen_icon_final, command=self.activate_drawing, borderwidth=0, highlightthickness=0, width=45, height=45)
            self.drawing_button.grid(row=9, column=0, padx=(30, 0), pady=(5,0), sticky=tk.W)
            self.create_tool_tip(self.drawing_button, "Draw annotation")
            self.undo_button = tk.Button(self.menu_frame, image=self.undo_icon_final, command=self.activate_undo, borderwidth=0, highlightthickness=0, width=45, height=45)
            self.undo_button.grid(row=10, column=0, padx=(30, 0), pady=(0,0), sticky=tk.W)
            self.create_tool_tip(self.undo_button, "Erase annotation")
            self.pen_setting_button = tk.Button(self.menu_frame, image=self.setting_icon_final, command=self.pen_setting, borderwidth=0, highlightthickness=0, width=45, height=45)
            self.pen_setting_button.grid(row=11, column=0, padx=(30, 0), pady=(0,0), sticky=tk.W)
            self.create_tool_tip(self.pen_setting_button, "Pen Settings")

            # Create Viewing Widgets
            self.viewing_separator = ttk.Separator(self.menu_frame, orient="horizontal")
            self.viewing_separator.grid(row=12, column=0, columnspan=4, ipadx=40, padx=(15,0), pady=(5,0), sticky=tk.W)
            self.viewing_widgets_label = tk.Label(self.menu_frame, text="Viewing\n Functionality:", font=("calibri", 14), foreground='black', background='#cccccc')
            self.viewing_widgets_label.grid(row=13, column=0, padx=(5,0), pady=(10,0), sticky=tk.W)
            self.viewing_title_seperator = ttk.Separator(self.menu_frame, orient="horizontal")
            self.viewing_title_seperator.grid(row=14, column=0, columnspan=4, ipadx=40, padx=(15,0), pady=(5,0), sticky=tk.W)
            self.zoom_button = tk.Button(self.menu_frame, image=self.zoom_icon_final, command=self.activate_zoom, borderwidth=0, highlightthickness=0, width=45, height=45)
            self.zoom_button.grid(row=15, column=0, padx=(30,0), pady=(5,0), sticky=tk.W)
            self.create_tool_tip(self.zoom_button, "Zoom")
            self.home_view_button = tk.Button(self.menu_frame, image=self.home_icon_final, command=self.reset_view, borderwidth=0, highlightthickness=0, width=45, height=45)
            self.home_view_button.grid(row=16, column=0, padx=(30, 0), sticky=tk.W)
            self.create_tool_tip(self.home_view_button, "Home View")
            self.end_separator = ttk.Separator(self.menu_frame, orient="horizontal")
            self.end_separator.grid(row=17, column=0, columnspan=4, ipadx=40, padx=(15,0), pady=(10,0), sticky=tk.W)

            # PI-RADS AND Lesions Forms Widgets      
            self.lesion_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.lesion_separator.grid(row=1, column=0, columnspan=4, ipadx=120, pady=(10,0))  
            self.select_lesion_label = tk.Label(self.pirad_frame, text="Select \nLesion:", font=("Calibri", 14), foreground='black', background='#cccccc')        
            self.select_lesion_label.grid(row=2, column=0, padx=(0, 205), pady=(0, 0))         
            self.select_lesion_combobox = ttk.Combobox(self.pirad_frame, values=self.current_lesions_used, state="readonly", width=7)
            self.select_lesion_combobox.grid(row=2, column=0, padx=(0, 50), pady=(0, 0))
            self.load_lesion_button = tk.Button(self.pirad_frame, image=self.load_pirad_icon_final, command=lambda:self.load_chosen_lesion_pirad_information(self.select_lesion_combobox.get()), borderwidth=0, highlightthickness=0, width=45, height=45)
            self.load_lesion_button.grid(row=2, column=0, padx=(100, 0), pady=(0, 0))
            self.create_tool_tip(self.load_lesion_button, "Load Selected Lesions PI-RADS Form")
            self.toggle_lesion_button = tk.Button(self.pirad_frame, image=self.toggle_icon_final, command=lambda: self.toggle_lesion(self.select_lesion_combobox.get()), borderwidth=0, highlightthickness=0, width=45, height=45)
            self.toggle_lesion_button.grid(row=2, column=0, padx=(190, 0), pady=(0, 0))
            self.create_tool_tip(self.toggle_lesion_button, "Toggle Selected Lesion")
            self.t2w_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.t2w_separator.grid(row=3, column=0,columnspan=4, ipadx=120, pady=(0,0))  
            self.t2w_and_dwi_values = ["1", "2", "3", "4", "5"]
            self.t2_weighted_imaging_label = tk.Label(self.pirad_frame, text="T2 Weighted Imgaing (T2W):", font=("Calibri", 13), foreground='black', background='#cccccc')        
            self.t2_weighted_imaging_label.grid(row=4, column=0, padx=(0, 75), pady=(10, 0))
            self.t2w_peripheral_zone_label = tk.Label(self.pirad_frame, text="T2W Peripheral Zone:", font=("Calibri", 12), foreground='black', background='#cccccc')  
            self.t2w_peripheral_zone_label.grid(row=5, column=0, padx=(0, 100), pady=(0, 0))
            self.t2w_peripheral_zone_combobox = ttk.Combobox(self.pirad_frame, values=self.t2w_and_dwi_values, state="readonly", width=5)
            self.t2w_peripheral_zone_combobox.grid(row=6, column=0, padx=(0, 155), pady=(0, 0))
            self.t2w_transition_zone_label = tk.Label(self.pirad_frame, text="T2W Transition Zone:", font=("Calibri", 12), foreground='black', background='#cccccc')  
            self.t2w_transition_zone_label.grid(row=7, column=0, padx=(0, 100), pady=(0, 0))
            self.t2w_transition_zone_combobox = ttk.Combobox(self.pirad_frame, values=self.t2w_and_dwi_values, state="readonly", width=5)
            self.t2w_transition_zone_combobox.grid(row=8, column=0, padx=(0, 155), pady=(0, 0))
            self.dwi_top_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.dwi_top_separator.grid(row=9, column=0,columnspan=4, ipadx=120, pady=(10,0))  
            self.diffusion_weighted_imaging_label = tk.Label(self.pirad_frame, text="Diffusion Weighted Imaging (DWI):", font=("Calibri", 13), foreground='black', background='#cccccc')        
            self.diffusion_weighted_imaging_label.grid(row=10, column=0, padx=(0, 40), pady=(10, 0))
            self.diffusion_weighted_peripheral_zone_label = tk.Label(self.pirad_frame, text="DWI Peripheral Zone:", font=("Calibri", 12), foreground='black', background='#cccccc')  
            self.diffusion_weighted_peripheral_zone_label.grid(row=11, column=0, padx=(0, 100), pady=(0, 0))
            self.diffusion_weighted_peripheral_zone_combobox = ttk.Combobox(self.pirad_frame, values=self.t2w_and_dwi_values, state="readonly", width=5)
            self.diffusion_weighted_peripheral_zone_combobox.grid(row=12, column=0, padx=(0, 155), pady=(0, 0))
            self.diffusion_weighted_transition_zone_label = tk.Label(self.pirad_frame, text="DWI Transition Zone:", font=("Calibri", 12), foreground='black', background='#cccccc')  
            self.diffusion_weighted_transition_zone_label.grid(row=13, column=0, padx=(0, 100), pady=(0, 0))
            self.diffusion_weighted_transition_zone_combobox = ttk.Combobox(self.pirad_frame, values=self.t2w_and_dwi_values, state="readonly", width=5)
            self.diffusion_weighted_transition_zone_combobox.grid(row=14, column=0, padx=(0, 155), pady=(0, 0))
            self.dynamic_contrast_enhanced_imaging_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.dynamic_contrast_enhanced_imaging_separator.grid(row=15, column=0,columnspan=4, ipadx=120, pady=(10,1)) 
            self.dynamic_contrast_enhanced_imaging_label = tk.Label(self.pirad_frame, text="Dynamic Contrast Enhanced \nImaging (DCE):", font=("Calibri", 13), foreground='black', background='#cccccc', anchor="w", justify=tk.LEFT)        
            self.dynamic_contrast_enhanced_imaging_label.grid(row=16, column=0, padx=(0, 75), pady=(5, 0))
            self.dynamic_contrast_enhanced_imaging_values = ["Positive", "Negative"]
            self.dynamic_contrast_enhanced_imaging_combobox = ttk.Combobox(self.pirad_frame, values=self.dynamic_contrast_enhanced_imaging_values, state="readonly", width=8)
            self.dynamic_contrast_enhanced_imaging_combobox.grid(row=17, column=0, padx=(0, 155), pady=(0, 0))
            self.pirads_score_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.pirads_score_separator.grid(row=18, column=0,columnspan=4, ipadx=120, pady=(10,0))
            self.pirads_scores_label = tk.Label(self.pirad_frame, text="PI-RADS Score:", font=("Calibri", 13), foreground='black', background='#cccccc')        
            self.pirads_scores_label.grid(row=19, column=0, padx=(0, 153), pady=(10, 0))
            self.pirads_scores_values = ["1 (Very Low, Cancer is highly unlikely)", "2 (Low, Cancer is unlikely)", "3 (Intermediate, Cancer is equivocal)", "4 (High, Cancer is likely)", "5 (Very High, Cancer is highly likely)"]
            self.pirad_score_combobox = ttk.Combobox(self.pirad_frame, values=self.pirads_scores_values, state="readonly", width=26)
            self.pirad_score_combobox.grid(row=20, column=0, padx=(0, 0), pady=(0, 0))
            self.additional_comments_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.additional_comments_separator.grid(row=21, column=0,columnspan=4, ipadx=120, pady=(10,0))
            self.additional_comments_label = tk.Label(self.pirad_frame, text="Additional Comments:", font=("Calibri", 13), foreground='black', background='#cccccc')        
            self.additional_comments_label.grid(row=22, column=0, padx=(0, 120), pady=(5, 0))
            self.additional_comments_textbox = tk.Text(self.pirad_frame, height=8, width=30, background='#CCCCCC', foreground="black", highlightthickness=1)
            self.additional_comments_textbox.grid(row=23, column=0, padx=(0,0), pady=(0,10))
            self.save_button_separator = ttk.Separator(self.pirad_frame, orient="horizontal")
            self.save_button_separator.grid(row=24, column=0,columnspan=4, ipadx=120, pady=(0,0))
            self.save_annotations_button = tk.Button(self.pirad_frame, image=self.save_icon_final, command=lambda:self.save_current_opened_lesion_pirads(self.current_opened_lesion), borderwidth=0, highlightthickness=0, width=45, height=45)
            self.save_annotations_button.grid(row=30, column=0, padx=(0,0), pady=(5,0))
            self.create_tool_tip(self.save_annotations_button, "Save Annotations")
            
            # Create a new toolbar instance
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
            self.toolbar.update()
            # Initialize a variable to track the zoom rectangle state
            self.zoom_rectangle_active = False
            # Flag to track the source of the zoom
            self.zoom_source = None
        else:
            # Display a message if no scans are available
            self.no_scans_label = tk.Label(self.viewer_frame, text="No scan set is currently opened.", font=("Calibri", 20), foreground='black', background='#cccccc')
            self.no_scans_label.grid(row=2, column=0, padx=(50, 0), pady=(250, 0))

    def next_scan(self, scan_number):
        scan_number_int = int(float(scan_number)) - 1
        self.current_scan = self.scans_collective[scan_number_int]
        scan_arr = mpimg.imread(self.current_scan)

        # Update the displayed scan
        self.a.clear()
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')
        self.a.set_aspect('auto') 

        # Load annotations for the initial scan
        json_file_path = os.path.join("saved_scans", f"{self.current_opened_scan}", f"{self.current_opened_scan}_annotation_information.json")
        self.load_annotations_from_json(json_file_path)
        self.select_lesion_combobox.set('')
        self.select_lesion_combobox['values'] = self.current_lesions_used
        self.t2w_peripheral_zone_combobox.set('')
        self.t2w_transition_zone_combobox.set('')
        self.diffusion_weighted_peripheral_zone_combobox.set('')
        self.diffusion_weighted_transition_zone_combobox.set('')
        self.dynamic_contrast_enhanced_imaging_combobox.set('')
        self.pirad_score_combobox.set('')
        self.additional_comments_textbox.delete('1.0', 'end')

    def reset_view(self):
        # Get the current NavigationToolbar2Tk instance
        self.toolbar = self.toolbar
        # Reset the view using the NavigationToolbar2Tk's home button
        self.toolbar_home()

        # Update the displayed scan
        self.a.clear()
        scan_arr = mpimg.imread(self.current_scan)
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')
        self.a.set_aspect('auto') 

        # Redraw all the lines from self.all_annotations excluding undone lines]
        for sequence in self.all_annotations:
            for line in sequence:
                self.a.add_line(line)
        # Redraw the canvas
        self.canvas.draw()

    
    def activate_zoom(self, deactivate=False):
        if self.drawing_active:
            self.drawing_active = False

        if self.undo_active:
            self.undo_active = False
            # Disconnect the delete_selected_line method from the mouse click event
            if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                self.canvas.mpl_disconnect(self.undo_callback_id)
                self.undo_callback_id = None

        # Toggle the zoom_active state
        self.zoom_active = not deactivate

        # Check the zoom activation state and update the button and label accordingly
        if self.zoom_active:
            self.active_button = self.zoom_button

        # Trigger the "Zoom to Rectangle" functionality directly
        self.toolbar.zoom()


    def activate_undo(self):
        if self.drawing_active:
            self.drawing_active = False
        if self.zoom_active:
            self.activate_zoom(deactivate=True)
        # Toggle the undo_active state
        self.undo_active = not self.undo_active
       # Check the undo activation state and update the button and label accordingly
        if self.undo_active:
            self.active_button = self.undo_button
            # Connect the delete_selected_line method to the mouse click event
            self.undo_callback_id = self.canvas.mpl_connect('button_press_event', self.delete_selected_line)
        else:
            # Disconnect the delete_selected_line method from the mouse click event
            if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                self.canvas.mpl_disconnect(self.undo_callback_id)


    def activate_drawing(self):
        if self.zoom_active:
            self.activate_zoom(deactivate=True)
        
        if self.undo_active:
            self.undo_active = False
            # Disconnect the delete_selected_line method from the mouse click event
            if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                self.canvas.mpl_disconnect(self.undo_callback_id)

        self.active_button = self.drawing_button
        self.drawing = True
        self.drawing_active = not self.drawing_active
        # Update the button appearance based on the activation state
        if self.drawing_active:
            self.active_button = self.drawing_button
            self.drawing = True
        else:
            self.active_button = None
            self.drawing = False
            self.prev_x = None
            self.prev_y = None

            # Add the current list of lines to the list of all lines
            if self.current_annotations:
                self.all_annotations.append(self.current_annotations)
        
    def on_mouse_motion(self, event):
        # Check if the event is a motion event
        if event.name == 'motion_notify_event':
            if event.xdata is not None and event.ydata is not None:
                # Get the x and y coordinates of the mouse pointer
                x, y = int(event.xdata), int(event.ydata)
            else:
                # Set coordinates to (0, 0) when outside the image
                x, y = 0, 0

            # Update the coordinates label
            self.coordinates_label.config(text=f"Coordinates: ({x}, {y})")

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

    def on_mouse_press(self, event):
        if event.name == 'button_press_event':
            if self.active_button == self.drawing_button and event.button == 1:
                self.drawing = True
                # Start a new list for the current sequence of lines
                self.current_annotations = []
                self.next_lesion_number = self.get_next_lesion_number()
            elif self.active_button == self.zoom_button and event.button == 1:
                self.zoom_source = "button"
            elif self.active_button == self.undo_button and event.button == 1:
                # Trigger the undo functionality when the undo button is pressed
                self.undo_last_line()

    def on_mouse_release(self, event):
        if event.name == 'button_release_event':
            if self.active_button == self.drawing_button and event.button == 1:
                self.drawing = False
                self.prev_x = None
                self.prev_y = None
                
                # Check for duplicate lines before appending to all_annotations
                if self.current_annotations:
                    self.all_annotations.append(self.current_annotations)
                    self.create_pirads_form(self.next_lesion_number)
                    self.select_lesion_combobox['values'] = self.current_lesions_used
                    self.run_lesion_check()
                else:
                    if self.next_lesion_number in self.current_lesions_used:
                        self.current_lesions_used.remove(self.next_lesion_number)
                        

    def draw_on_canvas(self, event):
        if event.name == 'motion_notify_event' and self.drawing:
            if event.xdata is not None and event.ydata is not None:
                x, y = int(event.xdata), int(event.ydata)
            else:
                x = self.prev_x
                y = self.prev_y

            # Check if the coordinates are within the valid range
            if x is not None and y is not None and 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
                if event.button == 1 and self.prev_x is not None and self.prev_y is not None:
                    # Check if the line is entirely within the canvas boundaries
                    if 0 <= self.prev_x < self.canvas_width and 0 <= self.prev_y < self.canvas_height:
                        chosen_colour = self.chosencolour
                        chosen_width = self.line_width
                        line = self.a.plot([self.prev_x, x], [self.prev_y, y], linewidth=chosen_width, color=chosen_colour, label=self.next_lesion_number)[0]
                        line.set_color(chosen_colour)
                        line.set_linewidth(chosen_width)
                        self.current_annotations.append(line)
                self.canvas.draw()
                self.prev_x, self.prev_y = x, y
                # Add additional metadata at the folder level
    
    def run_lesion_check(self):
        seen_labels = []
        annotations_checked = []
        for annotations in self.all_annotations:
            # Check if the coordinate set is not empty
            if annotations:
                # Extract the label of the first coordinate in the set
                current_label = annotations[0].get_label()

                # Check if the label is already seen
                if current_label not in seen_labels:
                    seen_labels.append(current_label)
                    annotations_checked.append(annotations)
        self.all_annotations.clear()
        self.all_annotations = annotations_checked
        self.current_lesions_used = list(set(self.current_lesions_used))
        self.current_lesions_used.sort()
        self.select_lesion_combobox['values'] = self.current_lesions_used
        self.canvas.draw()
    
    def get_next_lesion_number(self):
        if not self.current_lesions_used:
            # Handle the case where the list is empty
            next_available_lesion = "lesion-1"
        else:
            used_numbers = [int(lesion.split('-')[1]) for lesion in self.current_lesions_used]
            # Find the first gap in the sequence of numbers
            next_available_number = next((i for i in range(1, max(used_numbers) + 2) if i not in used_numbers), None)
            # Form the next available lesion number
            next_available_lesion = f"lesion-{next_available_number}" if next_available_number is not None else None
        self.current_lesions_used.append(next_available_lesion)
        return next_available_lesion

    def undo_last_line(self):
       # Check if there are any sequences of lines
        if self.all_annotations:
            # Set the callback for the mouse click event to handle line deletion
            self.canvas.mpl_connect('button_press_event', self.delete_selected_line)     

    def delete_selected_line(self, event):
        if event.name == 'button_press_event' and event.button == 1:
            # Check if the figure exists
            if hasattr(self, 'f') and self.f:
                # Check if there are any sequences of lines
                if self.all_annotations:
                    # Transform event coordinates to data coordinates
                    x, y = self.a.transData.inverted().transform([event.x, event.y])

                    # Iterate over all lines and check if the click is on any line
                    for sequence in self.all_annotations:
                        for line in sequence:
                            # Convert line data coordinates to pixel coordinates
                            line_x, line_y = line.get_xdata(), line.get_ydata()
                            line_coords = np.column_stack((line_x, line_y))
                            line_coords_pixels = self.a.transData.transform(line_coords)
                            # Check if the click is on the line
                            if np.any(np.abs(line_coords_pixels[:, 0] - event.x) < 3) and np.any(
                                    np.abs(line_coords_pixels[:, 1] - event.y) < 3):
                                # Remove the entire sequence of lines
                                for line_to_remove in sequence:
                                    line_to_remove.remove()
                                lesion_number = line.get_label()
                                # Remove the entire sequence from the all_annotations list
                                self.remove_sequence(sequence, lesion_number)
                                self.delete_lesion_pirad_form(lesion_number)
                                # Disconnect the delete_selected_line method from the mouse click event
                                if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                                    self.canvas.mpl_disconnect(self.undo_callback_id)
                                    self.undo_callback_id = None
                                return  # No need to check other lines
                    # If the click is not on any line, clear the current lines list
                    self.current_annotations = []
                    self.canvas.draw()
    
    def delete_lesion_pirad_form(self, lesion_to_remove):
        for entry in self.all_lesions_information:
            if entry['lesion-id'] == lesion_to_remove:
                self.current_lesions_used = [lesion_id for lesion_id in self.current_lesions_used if lesion_id != lesion_to_remove]
                self.all_lesions_information.remove(entry)
                self.select_lesion_combobox['values'] = self.current_lesions_used
                if self.select_lesion_combobox.get() == lesion_to_remove:
                    self.select_lesion_combobox.set('')
                    self.t2w_peripheral_zone_combobox.set('')
                    self.t2w_transition_zone_combobox.set('')
                    self.diffusion_weighted_peripheral_zone_combobox.set('')
                    self.diffusion_weighted_transition_zone_combobox.set('')
                    self.dynamic_contrast_enhanced_imaging_combobox.set('')
                    self.pirad_score_combobox.set('')
                    self.additional_comments_textbox.delete('1.0', 'end')
                break
        
    def remove_sequence(self, sequence_to_remove, lesion_to_remove):
        # Create a new list without the specified sequence
        self.all_annotations = [sequence for sequence in self.all_annotations if sequence != sequence_to_remove]
        self.current_lesions_used.remove(lesion_to_remove)
        # Clear the current lines list
        self.current_annotations = []
        # Redraw the canvas
        self.canvas.draw()
    
    def load_annotations_from_json(self, filename):
        self.all_annotations.clear()
        self.current_annotations.clear()
        self.all_lesions_information.clear()
        self.current_lesions_used.clear()

        with open(filename, 'r') as json_file:
            data = json.load(json_file)

        # Filter data for the currently opened scan
        current_scan_id = os.path.basename(self.current_scan)
        current_scan_data = [entry for entry in data if entry.get("scan_id") == current_scan_id]
        for sequence_data in current_scan_data:
            sequence_lines = []
            for annotation_list in sequence_data.get("coordinates", []):
                annotation_lines = []
                for line_data in annotation_list:
                    xdata = np.array(line_data['x'])
                    ydata = np.array(line_data['y'])
                    line_colour = line_data['colour']
                    line_width = line_data['width']
                    lesion_number = line_data['lesion_number']
                    line = mlines.Line2D(xdata, ydata, linewidth=line_width, color=line_colour, label=lesion_number)
                    annotation_lines.append(line)
                
                if annotation_lines:
                    sequence_lines.append(annotation_lines)
                self.current_lesions_used.append(lesion_number)
            if sequence_lines:
                self.all_annotations.extend(sequence_lines)
        # Redraw the canvas
        self.load_pirads_information(current_scan_data)
        self.redraw_canvas()

    def redraw_canvas(self):
         # Check if canvas is initialized
        if self.canvas:
            # Clear the existing lines on the canvas
            for line in self.a.lines:
                line.remove()

            # Redraw all the lines from self.all_lines
            for sequence in self.all_annotations:
                for line in sequence:
                    self.a.add_line(line)
            # Redraw the canvas
            self.canvas.draw()
        else:
            return
    
    def save_current_opened_lesion_pirads(self, current_lesion):
        if current_lesion:
            selected_lesion_index = next((index for index, lesion in enumerate(self.all_lesions_information) if lesion["lesion-id"] == current_lesion), None)
            if selected_lesion_index is not None:
                if (self.t2w_peripheral_zone_combobox.get() == " " or self.t2w_transition_zone_combobox.get() == " " or self.diffusion_weighted_peripheral_zone_combobox.get() == " " or self.diffusion_weighted_transition_zone_combobox.get() == " " or self.dynamic_contrast_enhanced_imaging_combobox.get() == " " or self.pirad_score_combobox.get() == " "):
                    messagebox.showerror('Error', "Make sure all fields of PI-RADS form are filled")
                else:
                    # Update the selected lesion with the modified information
                    self.all_lesions_information[selected_lesion_index]["T2W Peripheral Zone"] = self.t2w_peripheral_zone_combobox.get()
                    self.all_lesions_information[selected_lesion_index]["T2W Transition Zone"] = self.t2w_transition_zone_combobox.get()
                    self.all_lesions_information[selected_lesion_index]["DWI Peripheral Zone"] = self.diffusion_weighted_peripheral_zone_combobox.get()
                    self.all_lesions_information[selected_lesion_index]["DWI Transition Zone"] = self.diffusion_weighted_transition_zone_combobox.get()
                    self.all_lesions_information[selected_lesion_index]["Dynamic Contrast Enhanced Imaging (DCE)"] = self.dynamic_contrast_enhanced_imaging_combobox.get()
                    self.all_lesions_information[selected_lesion_index]["PI-RADS Score"] = self.pirad_score_combobox.get()
                    additional_comments_text = self.additional_comments_textbox.get(1.0, tk.END).strip()
                    self.all_lesions_information[selected_lesion_index]["Additional Comments"] = additional_comments_text

                    # Save the modified information back to the JSON file or your data storage mechanism
                    self.save_annotations()
                    self.save_pirads_information()
        else:
            self.save_annotations()
            self.save_pirads_information()

    def save_annotations(self):
        # Get the scan ID from the current scan file
        scan_to_save = os.path.basename(self.current_scan)
        # Define the JSON file path based on the scan ID
        json_file_path = os.path.join("saved_scans", f"{self.current_opened_scan}", f"{self.current_opened_scan}_annotation_information.json")
        # Read the existing JSON data from the file
        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
        # Remove existing annotations for the current scan_id
        for entry in existing_data:
            if entry["scan_id"] == scan_to_save:
                entry["coordinates"] = []
                break  # Stop searching once the entry is found
        # Save the updated data back to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file)
        if self.all_annotations:
            coordinate_data_to_save = []
            # Add the new annotations for the current scan_id
            for sequence in self.all_annotations:
                sequence_data = []
                for line in sequence:
                    xdata, ydata = line.get_xdata(), line.get_ydata()
                    chosen_colour, chosen_width = line.get_color(), line.get_linewidth()
                    lesion_number = line.get_label()
                    xdata_np, ydata_np = np.array(xdata), np.array(ydata)
                    line_data = {'x': xdata_np.tolist(), 'y': ydata_np.tolist(), 'colour': chosen_colour, 'width': chosen_width, 'lesion_number': lesion_number}
                    sequence_data.append(line_data)
                coordinate_data_to_save.append(sequence_data)
            # Find the entry with the matching scan_id
            for entry in existing_data:
                if entry["scan_id"] == scan_to_save:
                    # Update the coordinates field with the new data
                    entry["coordinates"] = coordinate_data_to_save
                    break  # Stop searching once the entry is found
            # Save the updated annotations to the JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(existing_data, json_file)
        # Redraw the canvas
        self.redraw_canvas()


    def create_pirads_form(self, lesion_number):
        pirads_form_information = {
            "lesion-id": lesion_number, 
            "T2W Peripheral Zone": " ",
            "T2W Transition Zone": " ",
            "DWI Peripheral Zone": " ",
            "DWI Transition Zone": " ",
            "Dynamic Contrast Enhanced Imaging (DCE)": " ",
            "PI-RADS Score": " ",
            "Additional Comments": " "
        }
        self.all_lesions_information.append(pirads_form_information)

    def load_chosen_lesion_pirad_information(self, lesion_to_load):
        if lesion_to_load:
            # Find the selected lesion in self.all_lesions_information
            selected_lesion = next((lesion for lesion in self.all_lesions_information if lesion["lesion-id"] == lesion_to_load), None)
            if selected_lesion:
                self.t2w_peripheral_zone_combobox.set(selected_lesion.get("T2W Peripheral Zone", ""))
                self.t2w_transition_zone_combobox.set(selected_lesion.get("T2W Transition Zone", ""))
                self.diffusion_weighted_peripheral_zone_combobox.set(selected_lesion.get("DWI Peripheral Zone", ""))
                self.diffusion_weighted_transition_zone_combobox.set(selected_lesion.get("DWI Transition Zone", ""))
                self.dynamic_contrast_enhanced_imaging_combobox.set(selected_lesion.get("Dynamic Contrast Enhanced Imaging (DCE)", ""))
                self.pirad_score_combobox.set(selected_lesion.get("PI-RADS Score", ""))
                additional_comments_text = selected_lesion.get("Additional Comments", "")
                self.additional_comments_textbox.delete(1.0, tk.END)  # Clear existing text
                self.additional_comments_textbox.insert(tk.END, additional_comments_text)
                self.current_opened_lesion = lesion_to_load
        else:
            messagebox.showerror('Error', 'Select a lesion to load')

    def load_pirads_information(self, current_scan_data):
        for entry in current_scan_data:
            lesion_information = entry.get("lesion_information", [])
        # Adding lesion information to self.all_lesion_information using lesion ID as key
        for lesion_info in lesion_information:
            self.all_lesions_information.append(lesion_info)
    
    def save_pirads_information(self):
        scan_to_save = os.path.basename(self.current_scan)
        json_file_path = os.path.join("saved_scans", f"{self.current_opened_scan}", f"{self.current_opened_scan}_annotation_information.json")
        # Read the existing JSON data from the file
        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
        for entry in existing_data:
            if entry["scan_id"] == scan_to_save:
                # Update the "lesion_information" field with the information from self.all_lesion_information
                entry["lesion_information"] = []
                break
        # Save the updated data back to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file)
        # Iterate through existing_data to find the entry for the specified scan ID
        for entry in existing_data:
            if entry["scan_id"] == scan_to_save:
                # Update the "lesion_information" field with the information from self.all_lesion_information
                entry["lesion_information"] = self.all_lesions_information
                break
        # Save the updated data back to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file)

    def toggle_lesion(self, lesion_to_toggle):
        # Assuming self.all_annotations, self.canvas, and self.viewer_frame are already defined in your main class
        self.lesion_visibility_manager = lesionToggle.LesionVisibilityManager(self.all_annotations, self.canvas, self.viewer_frame)
        # To toggle a lesion's visibility
        self.lesion_visibility_manager.toggle_lesion(lesion_to_toggle)
    
    def pen_setting(self):
        self.pen_settings_dialog = penSetting.PenSettingsDialog(self, self.line_width, self.choose_colour, self.update_pen_size)

    def choose_colour(self, chosen_colour):
        self.eraser_on = False
        self.chosencolour = chosen_colour
    
    def update_pen_size(self, value):
        # Update the line width when the scale is changed
        self.line_width = int(value)
    
    def create_tool_tip(self, widget, text):
        tool_tip = toolTip.ToolTip(widget)  # Create a ToolTip object for the widget
        def enter(event):
            tool_tip.showtip(text)
        def leave(event):
            tool_tip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    
if __name__ == "__main__":
    root = tk.Tk()
    app = MRIAnnotationTool(root)
    root.mainloop()

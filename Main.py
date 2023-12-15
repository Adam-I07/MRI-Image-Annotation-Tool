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
import shutil
from tkinter.colorchooser import askcolor
import json


class MRIAnnotationTool:
    def __init__(self, master):
        self.master = master
        self.master.title("MRI Annotation Tool")
        self.master.geometry("1100x700")
        self.master.resizable(0, 0)

        # Add a variable to track the pen drawing state
        self.drawing = False
        self.prev_x = None
        self.prev_y = None
        self.pen_active = False
        self.zoom_active = False
        self.undo_active = False
        self.drawn_lines = []
        self.all_lines = []
        self.active_button = None
        self.current_lines = []

        self.current_opened_scan = None

        # Add canvas width and height attributes
        self.canvas_width = 0
        self.canvas_height = 0

        # Frame Creation
        self.menu_frame = ttk.Frame(master, height=100, borderwidth=3, relief='sunken')
        self.menu_frame.grid(row=0, column=0, columnspan=3, sticky='ew')  # Span across all columns

        self.tool_frame = ttk.Frame(master, width=150, borderwidth=2, relief='sunken')
        self.tool_frame.grid(row=1, column=0, sticky='nsew')

        self.viewer_frame = ttk.Frame(master, width=600, borderwidth=2, relief='sunken')
        self.viewer_frame.grid(row=1, column=1, sticky='nsew')

        self.pirad_frame = ttk.Frame(master, width=250, borderwidth=2, relief='sunken')
        self.pirad_frame.grid(row=1, column=2, sticky='nsew')

        # Set weight for resizable rows and columns
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        # Menu Widgets and Buttons
        self.menu_title_label = ttk.Label(self.menu_frame, text="MRI Image Annotation Tool", font=("Caslon", 25))
        self.menu_title_label.grid(row=0, column=0, padx=10, pady=10)
        self.upload_scan_button = ttk.Button(self.menu_frame, text="Upload Scans", command=self.upload_scans)
        self.upload_scan_button.grid(row=0, column=1, padx=(235,20))
        self.display_scan_button = ttk.Button(self.menu_frame, text="Display Scans", command=self.display_scans)
        self.display_scan_button.grid(row=0, column=2, padx=(0,20))
        self.delete_scan_button = ttk.Button(self.menu_frame, text="Delete Scans", command=self.delete_scans)
        self.delete_scan_button.grid(row=0, column=3, padx=(0,20))
        self.exit_button = ttk.Button(self.menu_frame, text="Exit", command=self.exit_application)
        self.exit_button.grid(row=0, column=4, padx=(0,10))

        # Viewer Widgets and Buttons
        self.viewer_title_label = ttk.Label(self.viewer_frame, text="Scan Viewer", font=("Caslon", 22))
        self.viewer_title_label.grid(row=0, column=0, padx=250)
        self.scans_collective = []
        self.load_scan_viewer()
        self.viewer_frame.grid_propagate(0)

        # Tool Widgets and Buttons
        self.tool_title_label = ttk.Label(self.tool_frame, text="Tools", font=("Caslon", 22))
        self.tool_title_label.grid(row=0, column=0, padx=(60,0), sticky=tk.W)
        self.tool_frame.grid_propagate(0)

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

        # Destroy existing widgets in the viewer
        if hasattr(self, 'canvas_frame'):
            self.canvas_frame.destroy()
            del self.canvas_frame

        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            del self.canvas

        if hasattr(self, 'toolbar_frame'):
            self.toolbar_frame.destroy()
            del self.toolbar_frame

        if hasattr(self, 'scan_scale'):
            self.scan_scale.destroy()
            del self.scan_scale

        if hasattr(self, 'reset_view_button'):
            self.reset_view_button.destroy()
            del self.reset_view_button

        if hasattr(self, 'zoom_button'):
            self.zoom_button.destroy()
            del self.zoom_button

        if hasattr(self, 'coordinates_label'):
            self.coordinates_label.destroy()
            del self.coordinates_label

        if hasattr(self, 'toolbar'):
            self.toolbar.destroy()
            del self.toolbar

        if hasattr(self, 'viewing_widgets_label'):
            self.viewing_widgets_label.destroy()
            del self.viewing_widgets_label

        if hasattr(self, 'annotation_tool_label'):
            self.annotation_tool_label.destroy()
            del self.annotation_tool_label
        
        if hasattr(self, 'pen_button'):
            self.pen_button.destroy()
            del self.pen_button
        
        if hasattr(self, 'colour_button'):
            self.colour_button.destroy()
            del self.colour_button

        if hasattr(self, 'undo_button'):
            self.undo_button.destroy()
            del self.undo_button
        
        if hasattr(self, 'choose_pen_size_label'):
            self.choose_pen_size_label.destroy()
            del self.choose_pen_size_label
        
        if hasattr(self, 'choose_pen_size_scale'):
            self.choose_pen_size_scale.destroy()
            del self.choose_pen_size_scale

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

            # Remove extra whitespace around the image
            self.f.subplots_adjust(left=0, right=1, top=1, bottom=0)

            # Create a frame for the canvas
            self.canvas_frame = tk.Frame(self.viewer_frame)
            self.canvas_frame.grid(row=1, column=0, padx=(0, 0), pady=(10, 0))

            self.canvas = FigureCanvasTkAgg(self.f, self.canvas_frame)

            # Set canvas width and height
            self.canvas_width, self.canvas_height = self.f.get_size_inches() * self.f.dpi

             # Bind mouse button press, release, and motion events for drawing
            self.canvas.mpl_connect('scroll_event', self.on_mouse_scroll) if hasattr(self, 'on_mouse_scroll') else None
            self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
            self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
            self.canvas.mpl_connect('motion_notify_event', self.draw_on_canvas)
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

            # Draw canvas
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=2, column=0, padx=(0, 0))

            # Override the home method to use custom reset_zoom
            self.toolbar_home = self.reset_zoom
            self.toolbar_frame = ttk.Frame(self.viewer_frame)

            self.scan_scale = ttk.Scale(self.viewer_frame, orient="horizontal", from_=1, to=len(self.scans_collective), command=self.next_scan)
            self.scan_scale.grid(row=2, column=0, padx=(50,0))

            # Create Viewing Widgets
            self.viewing_widgets_label = ttk.Label(self.tool_frame, text="     Viewing\nFunctionality")
            self.viewing_widgets_label.grid(row=7, column=0, padx=(30,0), pady=(30,0))
            self.reset_view_button = ttk.Button(self.tool_frame, text="Reset", command=self.reset_view)
            self.reset_view_button.grid(row=8, column=0, padx=(30, 0))
            self.zoom_button = ttk.Button(self.tool_frame, text="Zoom", command=self.activate_zoom)
            self.zoom_button.grid(row=9, column=0, padx=(30,0))
            self.coordinates_label = ttk.Label(self.viewer_frame, text="Coordinates: (0, 0)", font=("Calibri", 12))
            self.coordinates_label.grid(row=2, column=0, padx=(0, 310))

            # Annotation Tools Widgets
            self.chosencolour = 'red'
            self.line_width = 2  # Default line width

            self.annotation_tool_label = ttk.Label(self.tool_frame, text="Annotation\n     Tools:", font=("Calibri", 14))
            self.annotation_tool_label.grid(row=1, column=0, padx=(30, 0), pady=(25, 0))
            self.pen_button = ttk.Button(self.tool_frame, text="Pen", command=self.activate_pen)
            self.pen_button.grid(row=2, column=0, padx=(30, 0), pady=(0,0))
            self.colour_button = ttk.Button(self.tool_frame, text="Colour", command=self.choose_colour)
            self.colour_button.grid(row=3, column=0, padx=(30, 0), pady=(0,0))
            self.undo_button = ttk.Button(self.tool_frame, text="Undo", command=self.activate_undo)
            self.undo_button.grid(row=4, column=0, padx=(30, 0), pady=(0,0))
            self.choose_pen_size_label = ttk.Label(self.tool_frame, text="Pen Size:", font=("Calibri", 12))
            self.choose_pen_size_label.grid(row=5, column=0, padx=(30, 0), pady=(0,0))
            self.choose_pen_size_scale = tk.Scale(self.tool_frame, from_=1, to=10, orient='horizontal', command=self.update_pen_size, showvalue=False)
            self.choose_pen_size_scale.set(self.line_width)
            self.choose_pen_size_scale.grid(row=6, column=0, padx=(30, 0), pady=(0,0))                  

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
        self.toolbar_home()

        # Update the displayed scan
        self.a.clear()
        scan_arr = mpimg.imread(self.scans_collective[self.current_scan_num])
        self.a.imshow(scan_arr, cmap='gray', aspect='equal')
        self.a.axis('off')

        # Redraw all the lines from self.all_lines excluding undone lines]
        for sequence in self.all_lines:
            for line in sequence:
                self.a.add_line(line)

        # Redraw the canvas
        self.canvas.draw()

    
    def activate_zoom(self, deactivate=False):
        if self.pen_active:
            self.pen_active = False

        if self.undo_active:
            self.activate_undo()
            # Disconnect the delete_selected_line method from the mouse click event
            if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                self.canvas.mpl_disconnect(self.undo_callback_id)

        # Toggle the zoom_active state
        self.zoom_active = not deactivate

        # Check the zoom activation state and update the button and label accordingly
        if self.zoom_active:
            self.active_button = self.zoom_button

        # Trigger the "Zoom to Rectangle" functionality directly
        self.toolbar.zoom()


    def activate_undo(self):
        if self.pen_active:
            self.pen_active = False
    
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


    def activate_pen(self):
        if self.zoom_active:
            self.activate_zoom(deactivate=True)
        
        if self.undo_active:
            self.undo_active = False
            # Disconnect the delete_selected_line method from the mouse click event
            if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                self.canvas.mpl_disconnect(self.undo_callback_id)

        self.active_button = self.pen_button
        self.drawing = True
        self.pen_active = not self.pen_active
        # Update the button appearance based on the activation state
        if self.pen_active:
            self.active_button = self.pen_button
            self.drawing = True
        else:
            self.active_button = None
            self.drawing = False

        # Toggle pen activation state
        if self.pen_active:
            self.drawing = True
        else:
            self.drawing = False
            self.prev_x = None
            self.prev_y = None

            # Add the current list of lines to the list of all lines
            if self.current_lines:
                self.all_lines.append(self.current_lines)

    def on_mouse_scroll(self, event):
        # Check if the event was a scroll event
        if event.name == 'scroll_event':
            # Calculate the zoom center coordinates based on the mouse pointer location
            x, y = event.x, event.y

            # Zoom in based on the direction of the scroll
            if event.step > 0:
                self.zoom_source = "scroll"
                self.zoom(0.8, x, y, mouse_zoom=True)
        
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

    def zoom(self, scale, x, y, mouse_zoom=True):
        if mouse_zoom:
            # Get the current x and y coordinates of the mouse pointer
            pointer_x, pointer_y = self.canvas.get_tk_widget().winfo_pointerxy()

            # Convert the screen coordinates to figure coordinates
            x, y = pointer_x - self.canvas.get_tk_widget().winfo_rootx(), pointer_y - self.canvas.get_tk_widget().winfo_rooty()
            inv = self.a.transData.inverted()
            x, y = inv.transform([x, y])

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


    def choose_colour(self):
        self.eraser_on = False
        self.chosencolour = askcolor(color=self.chosencolour)[1]

    def on_mouse_press(self, event):
        if event.name == 'button_press_event':
            if self.active_button == self.pen_button and event.button == 1:
                self.drawing = True
                # Start a new list for the current sequence of lines
                self.current_lines = []
            elif self.active_button == self.zoom_button and event.button == 1:
                self.zoom_source = "button"
            elif self.active_button == self.undo_button and event.button == 1:
                # Trigger the undo functionality when the undo button is pressed
                self.undo_last_line()

    def on_mouse_release(self, event):
        if event.name == 'button_release_event':
            if event.button == 1:
                self.drawing = False
                self.prev_x = None
                self.prev_y = None

                # Add the current list of lines to the list of all lines
                if self.current_lines:
                    self.all_lines.append(self.current_lines)

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
                        # Draw a line and add it to the current list of lines
                        line = self.a.plot([self.prev_x, x], [self.prev_y, y], linewidth=self.line_width, color=self.chosencolour)[0]
                        self.current_lines.append(line)

                self.canvas.draw()
                self.prev_x, self.prev_y = x, y

    def update_pen_size(self, value):
        # Update the line width when the scale is changed
        self.line_width = int(value)

    def undo_last_line(self):
       # Check if there are any sequences of lines
        if self.all_lines:
            # Set the callback for the mouse click event to handle line deletion
            self.canvas.mpl_connect('button_press_event', self.delete_selected_line)

    def delete_selected_line(self, event):
        if event.name == 'button_press_event' and event.button == 1:
            # Check if the figure exists
            if hasattr(self, 'f') and self.f:
                # Check if there are any sequences of lines
                if self.all_lines:
                    # Transform event coordinates to data coordinates
                    x, y = self.a.transData.inverted().transform([event.x, event.y])

                    # Iterate over all lines and check if the click is on any line
                    for sequence in self.all_lines:
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
                                # Remove the entire sequence from the all_lines list
                                self.remove_sequence(sequence)

                                # Disconnect the delete_selected_line method from the mouse click event
                                if hasattr(self, 'undo_callback_id') and self.undo_callback_id:
                                    self.canvas.mpl_disconnect(self.undo_callback_id)
                                    self.undo_callback_id = None

                                return  # No need to check other lines

                    # If the click is not on any line, clear the current lines list
                    self.current_lines = []
                    self.canvas.draw()
        
    def remove_sequence(self, sequence_to_remove):
        # Create a new list without the specified sequence
        self.all_lines = [sequence for sequence in self.all_lines if sequence != sequence_to_remove]

        # Clear the current lines list
        self.current_lines = []

        # Redraw the canvas
        self.canvas.draw()

    def clear_drawn_lines(self):
        for line in self.drawn_lines:
            line.remove()
        self.drawn_lines.clear()
    #End of Main Menu Display Viewer Code

    #Following code is the start for the Display Scans
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
                # Check if coordinates_label exists before updating
                if hasattr(self, 'coordinates_label') and self.coordinates_label:
                    # Clear previous coordinates when loading a new set of scans
                    self.coordinates_label.config(text="Coordinates: (0, 0)")

                self.current_opened_scan = scan_folder_name
                self.display_scans_window.destroy()
                self.load_scan_viewer()
        else:
            messagebox.showerror('Error', 'Select a scan set please')
  
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
    
    def save_scan_set_to_json(self, scan_set_name, scan_data):
        # Name the file using the scan set entered by the user
        json_filename = f"saved_scans/{scan_set_name}/{scan_set_name}_annotation_information.json"

        # Open a JSON file in write mode ('w') using a context manager ('with' statement)
        # The file will be automatically closed when the block of code is exited
        with open(json_filename, 'w') as json_file:
            # Use the json.dump function to serialize the Python object (scan_data) 
            # and write it to the specified file (json_file)
            json.dump(scan_data, json_file)

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

                        # Create a list to store scan data
                        scan_data = []

                        for i in range(0, len(input_scans_list)):
                            dicom_path = os.path.join(current_scans_folder, input_scans_list[i])
                            output_scans, instance_number = self.dicom_to_png(dicom_path)
                            cv.imwrite(os.path.join(new_folder_path, f"{instance_number - 1:04d}.png"), output_scans)

                            # Collect scan data
                            scan_data.append({
                                'scan_id': f"{instance_number - 1:04d}.png",
                                'coordinates': [],  # Placeholder for coordinates (to be collected during annotation)
                            })
                        
                        # Save scan data to JSON file
                        self.save_scan_set_to_json(scan_folder_name, scan_data)
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
        Window_Width = int(DCM_Img.get(0x00281051).value)  # G et window width from tag (0028, 1051)

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

    #Delete Scans Code Starting

    def delete_scans(self):
        self.delete_scan_window = tk.Tk()
        self.delete_scan_window.title('Delete Scan')
        self.delete_scan_window.geometry('430x130')
        self.delete_scan_window.resizable(0, 0)

        current_folders = []
        save_scan_folder = "saved_scans"
        get_folder_named = os.listdir(save_scan_folder)
        current_folders = get_folder_named
        if '.DS_Store' in current_folders:
            current_folders.remove('.DS_Store') 

        self.delete_scan_window_name_label = ttk.Label(self.delete_scan_window, text="Delete Scans", font=("Caslon", 22))
        self.delete_scan_window_name_label.grid(row=0, column=0, padx=(140,0), pady=10)
        self.select_scan_set_label = ttk.Label(self.delete_scan_window, text="Select a scan set to delete:", font=("Calibri", 12))
        self.select_scan_set_label.grid(row=1, column=0, padx=(10,0), sticky='w')
        self.select_scan_set_folder_combobox = ttk.Combobox(self.delete_scan_window, font=('Arial', 12, 'bold'), width=40, values=current_folders)
        self.select_scan_set_folder_combobox.grid(row=2, column=0, padx=(10,0), sticky='w')
        self.select_scan_set_folder_combobox['state'] = 'readonly'
        self.delete_scan_set_button = ttk.Button(self.delete_scan_window, text="Delete", command=lambda: self.delete_scan_file(self.select_scan_set_folder_combobox.get()))
        self.delete_scan_set_button.grid(row=2, column=1)

        self.delete_scan_window.mainloop()

    def delete_scan_file(self, scan_folder_to_delete):
        if scan_folder_to_delete:
            result = messagebox.askquestion("Confirmation", f"Are you sure you would like to delete {scan_folder_to_delete}?")
            if result == 'yes':
                save_scan_folder = "saved_scans"
                file_path_to_delete = os.path.join(save_scan_folder, scan_folder_to_delete)
                try:
                    # Check if the deleted scan set is currently open
                    if scan_folder_to_delete == self.current_opened_scan:
                        self.scans_collective.clear()

                        # Destroy existing widgets in the viewer
                        if hasattr(self, 'canvas_frame'):
                            self.canvas_frame.destroy()
                            del self.canvas_frame

                        if hasattr(self, 'canvas'):
                            self.canvas.get_tk_widget().destroy()
                            del self.canvas

                        if hasattr(self, 'toolbar_frame'):
                            self.toolbar_frame.destroy()
                            del self.toolbar_frame

                        if hasattr(self, 'scan_scale'):
                            self.scan_scale.destroy()
                            del self.scan_scale

                        if hasattr(self, 'reset_view_button'):
                            self.reset_view_button.destroy()
                            del self.reset_view_button

                        if hasattr(self, 'zoom_button'):
                            self.zoom_button.destroy()
                            del self.zoom_button

                        if hasattr(self, 'coordinates_label'):
                            self.coordinates_label.destroy()
                            del self.coordinates_label

                        if hasattr(self, 'toolbar'):
                            self.toolbar.destroy()
                            del self.toolbar

                        if hasattr(self, 'viewing_widgets_label'):
                            self.viewing_widgets_label.destroy()
                            del self.viewing_widgets_label

                        if hasattr(self, 'annotation_tool_label'):
                            self.annotation_tool_label.destroy()
                            del self.annotation_tool_label
                        
                        if hasattr(self, 'pen_button'):
                            self.pen_button.destroy()
                            del self.pen_button
                        
                        if hasattr(self, 'colour_button'):
                            self.colour_button.destroy()
                            del self.colour_button

                        if hasattr(self, 'undo_button'):
                            self.undo_button.destroy()
                            del self.undo_button
                        
                        if hasattr(self, 'choose_pen_size_label'):
                            self.choose_pen_size_label.destroy()
                            del self.choose_pen_size_label
                        
                        if hasattr(self, 'choose_pen_size_scale'):
                            self.choose_pen_size_scale.destroy()
                            del self.choose_pen_size_scale

                    shutil.rmtree(file_path_to_delete)
                    messagebox.showinfo("Deleted", f"{scan_folder_to_delete} has been successfully deleted")

                    # Update the viewer if the deleted scan set is currently open
                    if scan_folder_to_delete == self.current_opened_scan:
                        self.load_scan_viewer()

                    self.delete_scan_window.destroy()
                except OSError as e:
                    print(f"Error deleting file {scan_folder_to_delete}: {e}")
        else:
            messagebox.showerror("Error", "Select a scan set to delete.")
    
    #Delete Scans Code Ending


 

if __name__ == "__main__":
    root = tk.Tk()
    app = MRIAnnotationTool(root)
    root.mainloop()

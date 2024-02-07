import tkinter as tk
from tkinter import messagebox

class LesionVisibilityManager:
    def __init__(self, annotations, canvas, viewer_frame):
        """
        Initializes the LesionVisibilityManager with necessary components.

        :param annotations: A reference to the list of all annotations.
        :param canvas: A reference to the matplotlib canvas for drawing.
        :param viewer_frame: A reference to the tkinter frame that contains the viewer.
        """
        self.all_annotations = annotations
        self.canvas = canvas
        self.viewer_frame = viewer_frame

    def toggle_lesion(self, lesion_to_toggle):
        """
        Toggles the visibility of a specific lesion identified by its label.
        :param lesion_to_toggle: The label of the lesion to toggle visibility for.
        """
        if lesion_to_toggle:
            selected_lines = []
            for sequence in self.all_annotations:
                for line in sequence:
                    if line.get_label() == lesion_to_toggle:
                        selected_lines.append(line)
            # Toggle visibility
            self.toggle_visibility(selected_lines)
        else:
            messagebox.showerror('Error', 'Select a lesion to toggle')

    def toggle_visibility(self, lines_to_toggle):
        """
        Toggles the visibility of the specified lines.
        :param lines_to_toggle: A list of lines whose visibility is to be toggled.
        """
        # Toggle visibility of the selected lines
        for line in lines_to_toggle:
            current_visibility = line.get_visible()
            line.set_visible(not current_visibility)
        # Redraw the canvas
        self.canvas.draw()
        self.viewer_frame.after(200, lambda: self.restore_visibility(lines_to_toggle))

    def restore_visibility(self, lines_to_restore):
        """
        Restores the visibility of the specified lines after a delay.
        :param lines_to_restore: A list of lines whose visibility is to be restored.
        """
        # Restore visibility of the selected lines
        for line in lines_to_restore:
            line.set_visible(True)
        # Redraw the canvas
        self.canvas.draw()

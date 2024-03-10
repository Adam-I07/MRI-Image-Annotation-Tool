# semantic_segmentation.py

from segment_anything import SamPredictor, sam_model_registry
import cv2
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk

class SemanticSegmentation:
    def __init__(self, model_type="vit_h", checkpoint_path="segment_anything_checkpoints/sam_vit_h_4b8939.pth"):
        # Load the model
        self.sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        self.predictor = SamPredictor(self.sam)

    def segment_scan(self, image_path):
        # Load the image
        image = cv2.imread(image_path)

        # Verify the image was loaded
        if image is None:
            print("Failed to load image.")
            return

        # Set the image in the predictor
        self.predictor.set_image(image)

        # Generate masks for the entire image
        masks, _, _ = self.predictor.predict(None)  # Using None for automatic mask generation

        # Create a Tkinter window
        window = tk.Toplevel()
        window.title("Semantic Segmentation")
        window.configure(bg='#cccccc')

        # Display the original image with label
        original_img_label = tk.Label(window, text="Original Scan", font=("Calibri", 14), foreground='black', background='#cccccc')
        original_img_label.grid(row=0, column=0)

        original_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        original_photo = ImageTk.PhotoImage(original_img)
        original_label = tk.Label(window, image=original_photo, bg='#cccccc')
        original_label.image = original_photo  # Keep a reference!
        original_label.grid(row=1, column=0)

        # Display the combined mask with label
        combined_label_text = tk.Label(window, text="Segmented Scan", font=("Calibri", 14), foreground='black', background='#cccccc')
        combined_label_text.grid(row=0, column=1)

        combined_mask = np.sum(masks, axis=0)  # Sum all the masks to combine them
        combined_pil_img = Image.fromarray((combined_mask * 255 / len(masks)).astype(np.uint8))
        combined_photo = ImageTk.PhotoImage(combined_pil_img)
        combined_label = tk.Label(window, image=combined_photo, bg='#cccccc')
        combined_label.image = combined_photo  # Keep a reference!
        combined_label.grid(row=1, column=1)

        # Start the Tkinter event loop
        window.mainloop()

# If you want to run this script directly, you can use the following lines
# if __name__ == "__main__":
#     segmenter = SemanticSegmentation()
#     scan_path = 'saved_scans/set2/0001.png'  # Replace with your actual image file name
#     segmenter.segment_scan(scan_path)

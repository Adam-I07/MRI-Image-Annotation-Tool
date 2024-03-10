from segment_anything import SamPredictor, sam_model_registry
import cv2
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk

# Set the model type and the path to the checkpoint file
model_type = "vit_h"
checkpoint_path = "segment_anything_checkpoints/sam_vit_h_4b8939.pth"


# Load the model
sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
predictor = SamPredictor(sam)

# Load your image
scan_path = 'saved_scans/Set4/0018.png'  # Replace with your actual image file name
image = cv2.imread(scan_path)

# Verify the image was loaded
if image is None:
    print("Failed to load image.")
    exit()

# Set the image in the predictor
predictor.set_image(image)

# Generate masks for the entire image
masks, _, _ = predictor.predict(None)  # Using None for automatic mask generation

# Create a Tkinter window
window = tk.Tk()
window.title("Semantic Segmentation")
window.configure(bg='#cccccc')

# Display the original image with label
original_img_label = tk.Label(window, text="Original Scan", font=("Calibri", 14), foreground='black', background='#cccccc')
original_img_label.grid(row=0, column=0, columnspan=2)

original_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
original_photo = ImageTk.PhotoImage(original_img)
original_label = tk.Label(window, image=original_photo)
original_label.image = original_photo  # Keep a reference!
original_label.grid(row=1, column=0, columnspan=2)

# Display masks 1 and 2 with labels
for idx in range(2):
    mask = masks[idx]
    mask_label = tk.Label(window, text=f"Mask {idx + 1}", font=("Calibri", 14), foreground='black', background='#cccccc')
    mask_label.grid(row=0, column=idx + 2)

    pil_img = Image.fromarray((mask * 255).astype(np.uint8))
    photo = ImageTk.PhotoImage(pil_img)
    label = tk.Label(window, image=photo)
    label.image = photo  # Keep a reference!
    label.grid(row=1, column=idx + 2)

# Display Mask 3 with label on the next line
mask_3_label = tk.Label(window, text="Mask 3", font=("Calibri", 14), foreground='black', background='#cccccc')
mask_3_label.grid(row=2, column=0)

mask_3_img = Image.fromarray((masks[2] * 255).astype(np.uint8))
mask_3_photo = ImageTk.PhotoImage(mask_3_img)
mask_3_label_img = tk.Label(window, image=mask_3_photo)
mask_3_label_img.image = mask_3_photo  # Keep a reference!
mask_3_label_img.grid(row=3, column=0)

# Display the combined mask with label
combined_label_text = tk.Label(window, text="Segmented Scan", font=("Calibri", 14), foreground='black', background='#cccccc')
combined_label_text.grid(row=2, column=1, columnspan=2)

combined_mask = np.sum(masks, axis=0)  # Sum all the masks to combine them
combined_pil_img = Image.fromarray((combined_mask * 255 / len(masks)).astype(np.uint8))
combined_photo = ImageTk.PhotoImage(combined_pil_img)
combined_label = tk.Label(window, image=combined_photo)
combined_label.image = combined_photo  # Keep a reference!
combined_label.grid(row=3, column=1, columnspan=2)

# Start the Tkinter event loop
window.mainloop()

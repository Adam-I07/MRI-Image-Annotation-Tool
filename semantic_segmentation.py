from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import cv2
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk

class SemanticSegmentation:
    def __init__(self, model_type="vit_h", checkpoint_path="segment_anything_checkpoints/sam_vit_h_4b8939.pth"):
        # Load the model
        self.sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        self.sam.to(device="cpu")  # Assuming that CPU is the intended device
        self.mask_generator = SamAutomaticMaskGenerator(self.sam)

    def create_mask_image(self, anns, original_image):
        if len(anns) == 0:
            return None, None
        sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)

        mask_img = np.zeros_like(original_image)
        overlay_img = original_image.copy()

        for ann in sorted_anns:
            m = ann['segmentation']
            color_mask = np.random.randint(0, 255, (3,), dtype=np.uint8)
            full_color_mask = np.zeros_like(original_image)
            full_color_mask[m] = color_mask
            blended = cv2.addWeighted(overlay_img, 0.65, full_color_mask, 0.35, 0)
            overlay_img[m] = blended[m]
            mask_img[m] = color_mask

        return Image.fromarray(overlay_img), Image.fromarray(mask_img)

    def segment_scan(self, image_path):
        # Load the image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Verify the image was loaded
        if image is None:
            print("Failed to load image.")
            return
        
        # Resize the image if necessary
        original_height, original_width = image.shape[:2]
        max_size = 600
        if max(original_height, original_width) > max_size:
            # Calculate the scale to resize the image
            scale = max_size / max(original_height, original_width)
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            # Resize the image to new dimensions while maintaining the aspect ratio
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Generate masks for the entire image
        masks = self.mask_generator.generate(image)

        # Generate masks for the entire image
        masks = self.mask_generator.generate(image)

        # Create a Tkinter window
        window = tk.Toplevel()
        window.title("Semantic Segmentation")

        # Generate both overlay and mask images using the provided masks
        overlay_image_pil, mask_image_pil = self.create_mask_image(masks, image)

        # If the overlay image was created successfully, pack it on the left frame
        if overlay_image_pil:
            overlay_image_tk = ImageTk.PhotoImage(image=overlay_image_pil)
            overlay_label = tk.Label(window, image=overlay_image_tk)
            overlay_label.image = overlay_image_tk
            overlay_label.pack(side="left")

        # If the mask image was created successfully, pack it on the right frame
        if mask_image_pil:
            mask_image_tk = ImageTk.PhotoImage(image=mask_image_pil)
            mask_label = tk.Label(window, image=mask_image_tk)
            mask_label.image = mask_image_tk
            mask_label.pack(side="right")

        # Start the Tkinter event loop
        window.mainloop()

# if __name__ == "__main__":
#     segmenter = SemanticSegmentation()
#     segmenter.segment_scan('saved_scans/we/0000.png')
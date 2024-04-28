1. Make sure you have python 3.9 or above installed.
2. Install the following libararies. Pillow, OpenCV, Numpy, Matplotlib, Pydicom, segment_anything. The following are the commands to do this:  
    Mac: pip install opencv-python-headless Pillow numpy matplotlib pydicom torch torchvision, Windows: py -m pip install opencv-python-headless Pillow numpy matplotlib pydicom torch torchvision
    Mac: pip install git+https://github.com/facebookresearch/segment-anything.git, , Windows: py -m pip install git+https://github.com/facebookresearch/segment-anything.git
3. Create a new folder called: segment_anything_checkpoints
4.  Go to the following website: https://github.com/facebookresearch/segment-anything#model-checkpoints and download the "ViT-H SAM model" and once downloaded place the model in the segemnt_anything_checkpoints folder. Make sure the path model is named: "sam_vit_h_4b8939.pth".
5. run main.py
6. click the upload scans button, enter the name you want to name and then select upload and select the file containing the scans (not the individual scan just select the folder)
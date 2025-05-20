import tkinter as tk
import sys
import os
from pathlib import Path

# Check for required libraries
try:
    from PIL import Image, ImageTk, ImageGrab
    import PIL
    print(f"PIL version: {PIL.__version__}")
except ImportError:
    print("ERROR: The Pillow library is required but not installed.")
    print("Please install it using: pip install Pillow")
    print("Exiting application...")
    sys.exit(1)

# Add the parent directory to sys.path to help with imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Ensure the Images directory exists
images_dir = os.path.join(current_dir, "Images")
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    print(f"Created Images directory at: {images_dir}")
else:
    print(f"Using Images directory at: {images_dir}")

# Set the current working directory to ensure relative paths work
os.chdir(current_dir)

from modules.whiteboard_app import DigitalWhiteboard

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalWhiteboard(root)
    root.mainloop()
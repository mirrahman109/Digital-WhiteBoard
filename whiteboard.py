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

# Create a fallback icon if whiteboard_icon.ico doesn't exist
def create_fallback_icon():
    """Create a simple fallback icon if the main icon is missing"""
    try:
        from PIL import Image, ImageDraw
        # Create a simple 32x32 icon
        img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        # Draw a simple whiteboard icon
        draw.rectangle([4, 4, 28, 28], outline=(0, 0, 0), width=2)
        draw.line([8, 12, 24, 12], fill=(0, 0, 0), width=1)
        draw.line([8, 16, 24, 16], fill=(0, 0, 0), width=1)
        draw.line([8, 20, 20, 20], fill=(0, 0, 0), width=1)
        
        icon_path = os.path.join(current_dir, "Images", "fallback_icon.ico")
        img.save(icon_path, format='ICO')
        return icon_path
    except Exception:
        return None

from modules.whiteboard_app import DigitalWhiteboard

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set application icon with fallback
    icon_path = os.path.join(current_dir, "Images", "whiteboard_icon.ico")
    try:
        root.iconbitmap(icon_path)
        print(f"Loaded application icon: {icon_path}")
    except tk.TclError:
        print(f"Warning: Could not load icon from {icon_path}")
        # Try to create and use fallback icon
        fallback_icon = create_fallback_icon()
        if fallback_icon:
            try:
                root.iconbitmap(fallback_icon)
                print(f"Using fallback icon: {fallback_icon}")
            except:
                print("Could not create fallback icon, using default")
        
    app = DigitalWhiteboard(root)
    root.mainloop()
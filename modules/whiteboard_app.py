import tkinter as tk
from tkinter import ttk
import os
import sys

# Ensure PIL is available
try:
    from PIL import Image, ImageTk
except ImportError:
    print("PIL/Pillow is required but not installed.")
    print("Please install it using: pip install Pillow")
    sys.exit(1)

# Change relative imports to absolute imports
from modules.canvas_manager import CanvasManager
from modules.toolbar_manager import ToolbarManager
from modules.page_manager import PageManager
from modules.file_manager import FileManager
from modules.tooltip import ToolTip  # Import the new ToolTip class

class DigitalWhiteboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Whiteboard")
        self.root.geometry("1024x768")

        # Default settings
        self.brush_color = "black"
        self.brush_size = 5
        self.current_tool = "brush"  # brush, eraser, rectangle, circle, line
        self.is_dark_mode = False
        self.grid_visible = False
        self.zoom_level = 1.0

        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Load icons first, before creating managers
        self.load_icons()

        # Create toolbar container first
        self.toolbar_container = ttk.Frame(self.main_container)
        self.toolbar_container.pack(side=tk.TOP, fill=tk.X)

        # Initialize managers in order of dependency
        self.canvas_manager = CanvasManager(self)
        self.file_manager = FileManager(self)
        self.page_manager = PageManager(self)  # Page manager needs the canvas manager
        self.toolbar_manager = ToolbarManager(self)  # Toolbar manager needs the page manager

        # Now create the toolbar once all managers are available
        self.toolbar_manager.create_toolbar(self.toolbar_container)

        # Create canvas
        self.canvas_frame = ttk.Frame(self.main_container)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas_manager.create_canvas(self.canvas_frame)

        # Bind events
        self.setup_bindings()

        # Initialize the first page after everything is set up
        self.page_manager.initialize_page()

    def setup_bindings(self):
        self.canvas_manager.setup_bindings()
        self.root.bind("<Control-z>", lambda e: self.canvas_manager.undo())
        self.root.bind("<Control-y>", lambda e: self.canvas_manager.redo())

    def load_icons(self):
        """Load tool icons from the Images folder"""
        self.icons = {}
        
        # Define the icon files to load - updated with your specific filenames
        icon_files = {
            'brush': 'pencil.png',          # Using pencil.png for brush tool
            'eraser': 'eraser.png',
            'undo': 'undo.png',
            'redo': 'redo.png',
            'clear': 'clear.png',
            'color': 'paint-brush.png',
            'prev': 'left.png',
            'next': 'right.png',
            'new_page': 'new page.png',
            'grid': 'grid-on.png',
            'theme': 'day-mode.png',
            'save': 'save.png',
            'export': 'export.png',         # Added new export icon
            'load': 'open-folder.png'       # Added new load icon
        }
        
        # Use larger icons for better visibility (24x24 instead of 16x16)
        icon_size = (24, 24)
        
        # Print the current directory for debugging
        print(f"Current directory: {os.getcwd()}")
        images_dir = os.path.join(os.getcwd(), 'Images')
        print(f"Looking for images in: {images_dir}")
        
        for name, file in icon_files.items():
            try:
                # Build the complete path
                path = os.path.join('Images', file)
                print(f"Trying to load: {path}")
                
                if os.path.exists(path):
                    image = Image.open(path)
                    # Use larger icon size
                    image = image.resize(icon_size, Image.Resampling.LANCZOS)
                    self.icons[name] = ImageTk.PhotoImage(image)
                    print(f"Successfully loaded: {name}")
                else:
                    print(f"Icon file not found: {path}")
            except Exception as e:
                print(f"Failed to load icon {file}: {e}")
        
        print(f"Loaded {len(self.icons)} icons")

    def set_tool(self, tool):
        """Change the current drawing tool"""
        self.current_tool = tool
        if tool == "eraser":
            self.canvas_manager.canvas.config(cursor="circle")
        else:
            self.canvas_manager.canvas.config(cursor="crosshair")

    def choose_color(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color

    def update_brush_size(self, size):
        """Update the brush size with support for floating point values"""
        # Convert to float first, then to int if needed
        size_float = float(size)
        self.brush_size = size_float  # Keep as float to support sizes like 1.5

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.canvas_manager.set_dark_background(True)
        else:
            self.canvas_manager.set_dark_background(False)

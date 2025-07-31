import tkinter as tk
from tkinter import ttk
from modules.tooltip import ToolTip

class ToolbarManager:
    def __init__(self, app):
        self.app = app
        self.toolbar = None
        self.grid_button = None
        self.theme_button = None
        self.page_label = None
    
    def create_toolbar(self, parent):
        # Create a container frame for the toolbar
        toolbar_container = ttk.Frame(parent)
        toolbar_container.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Create the actual toolbar frame centered in its container
        self.toolbar = ttk.Frame(toolbar_container)
        self.toolbar.pack(side=tk.TOP, fill=None, expand=False, anchor=tk.CENTER)
        
        # Increase button size for better visual comfort
        button_padding = 5      # Slightly increased padding
        button_width = 10       # Larger button width for visual comfort
        
        # Draw tools frame
        tools_frame = ttk.LabelFrame(self.toolbar, text="Tools")
        tools_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create buttons with larger size and tooltips
        brush_btn = ttk.Button(
            tools_frame, 
            image=self.app.icons.get('brush'), 
            command=lambda: self.app.set_tool("brush"),
            width=button_width
        )
        brush_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(brush_btn, "Brush Tool")
        
        eraser_btn = ttk.Button(
            tools_frame, 
            image=self.app.icons.get('eraser'), 
            command=lambda: self.app.set_tool("eraser"),
            width=button_width
        )
        eraser_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(eraser_btn, "Eraser Tool")
        
        # Add shape dropdown menu
        self.create_shape_dropdown(tools_frame, button_width, button_padding)
        
        # Fix the clear button with proper error handling and lambda
        clear_btn = ttk.Button(
            tools_frame, 
            image=self.app.icons.get('clear'), 
            command=lambda: self._safe_clear_canvas(),
            width=button_width
        )
        clear_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(clear_btn, "Clear Canvas")
        
        # Add undo/redo buttons with tooltips
        undo_btn = ttk.Button(
            tools_frame,
            image=self.app.icons.get('undo'),
            command=self.app.canvas_manager.undo,
            width=button_width
        )
        undo_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(undo_btn, "Undo")
        
        redo_btn = ttk.Button(
            tools_frame,
            image=self.app.icons.get('redo'),
            command=self.app.canvas_manager.redo,
            width=button_width
        )
        redo_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(redo_btn, "Redo")
        
        # Options frame
        options_frame = ttk.LabelFrame(self.toolbar, text="Options")
        options_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create color button with tooltip
        color_btn = ttk.Button(
            options_frame, 
            image=self.app.icons.get('color'), 
            command=self.app.choose_color,
            width=button_width
        )
        color_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(color_btn, "Choose Color")
        
        # Restore brush size dropdown with more space
        size_frame = ttk.Frame(options_frame)
        size_frame.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        
        size_label = ttk.Label(size_frame, text="Size:")
        size_label.pack(side=tk.LEFT)
        ToolTip(size_label, "Brush Size")
        
        # Use a combobox for brush size selection
        size_values = [1, 2, 3, 5, 8, 10, 15, 20]
        size_var = tk.StringVar(value=str(self.app.brush_size))
        size_combo = ttk.Combobox(size_frame, textvariable=size_var, values=size_values, width=5)
        size_combo.pack(side=tk.LEFT, padx=3)
        size_combo.bind("<<ComboboxSelected>>", lambda e: self.app.update_brush_size(size_var.get()))
        ToolTip(size_combo, "Select Brush Size")

        # Add dark mode (theme) toggle button beside color and size
        theme_btn = ttk.Button(
            options_frame,
            image=self.app.icons.get('theme'),
            command=self.app.toggle_dark_mode if hasattr(self.app, 'toggle_dark_mode') else None,
            width=button_width
        )
        theme_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(theme_btn, "Toggle Dark/Light Background")
        
        # Add grid toggle button with proper icon and command
        self.grid_button = ttk.Button(
            options_frame,
            image=self.app.icons.get('grid'),
            command=self.toggle_grid,
            width=button_width
        )
        self.grid_button.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(self.grid_button, "Toggle Grid Lines")
        
        # File operations frame
        file_frame = ttk.LabelFrame(self.toolbar, text="File")
        file_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Save button with tooltip
        save_btn = ttk.Button(
            file_frame,
            image=self.app.icons.get('save'),
            command=lambda: self.app.file_manager.save_whiteboard() if hasattr(self.app.file_manager, 'save_whiteboard') else None,
            width=button_width
        )
        save_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(save_btn, "Save Whiteboard")
        
        # Export button with tooltip
        export_btn = ttk.Button(
            file_frame,
            image=self.app.icons.get('export'),
            command=lambda: self.app.file_manager.export_as_image() if hasattr(self.app.file_manager, 'export_as_image') else None,
            width=button_width
        )
        export_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(export_btn, "Export as Image")
        
        # Load button with tooltip
        load_btn = ttk.Button(
            file_frame,
            image=self.app.icons.get('load'),
            command=lambda: self.app.file_manager.load_whiteboard() if hasattr(self.app.file_manager, 'load_whiteboard') else None,
            width=button_width
        )
        load_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(load_btn, "Load Whiteboard")
        
        # Page controls with tooltips
        page_frame = ttk.LabelFrame(self.toolbar, text="Pages")
        page_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        prev_page_btn = ttk.Button(
            page_frame, 
            image=self.app.icons.get('prev'), 
            command=lambda: self.app.page_manager.prev_page() if hasattr(self.app.page_manager, 'prev_page') else None,
            width=button_width
        )
        prev_page_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(prev_page_btn, "Previous Page")
        
        # Add page info label
        self.page_info = ttk.Label(page_frame, text="Page 1/1")
        self.page_info.pack(side=tk.LEFT, padx=button_padding)
        ToolTip(self.page_info, "Current Page / Total Pages")
        
        next_page_btn = ttk.Button(
            page_frame,
            image=self.app.icons.get('next'),
            command=lambda: self.app.page_manager.next_page() if hasattr(self.app.page_manager, 'next_page') else None,
            width=button_width
        )
        next_page_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(next_page_btn, "Next Page")
        
        new_page_btn = ttk.Button(
            page_frame,
            image=self.app.icons.get('new_page'),
            command=lambda: self._safe_add_page(),
            width=button_width
        )
        new_page_btn.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(new_page_btn, "Add New Page")
    
    def update_page_label(self, page_number):
        self.page_label.config(text=f"Page {page_number + 1}")
        
    def update_brush_size_from_combobox(self, event=None):
        """Update brush size from combobox value with error checking"""
        try:
            size_text = self.size_combobox.get()
            size = float(size_text)
            # Ensure size is within reasonable bounds
            size = max(0.5, min(size, 100))  # Limit between 0.5 and 100
            self.app.update_brush_size(size)
            # Update the display to show the accepted value (in case it was clamped)
            self.size_combobox.set(str(self.app.brush_size))
        except ValueError:
            # If conversion fails, reset to current brush size
            self.size_combobox.set(str(self.app.brush_size))
    
    def _safe_add_page(self):
        """Safely call the add_page method with proper error handling"""
        try:
            if hasattr(self.app.page_manager, 'save_current_page'):
                # Save the current page before adding a new one
                self.app.page_manager.save_current_page()
                
            if hasattr(self.app.page_manager, 'add_page'):
                self.app.page_manager.add_page()
            else:
                print("Error: PageManager has no add_page method")
        except Exception as e:
            print(f"Error adding page: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_clear_canvas(self):
        """Safely call the clear_canvas method with proper error handling"""
        try:
            if hasattr(self.app.canvas_manager, 'clear_canvas'):
                self.app.canvas_manager.clear_canvas()
            else:
                print("Error: CanvasManager has no clear_canvas method")
        except Exception as e:
            print(f"Error clearing canvas: {e}")
            import traceback
            traceback.print_exc()
    
    def create_shape_dropdown(self, parent, button_width, button_padding):
        """Create a dropdown menu for shape tools"""
        # Create the main shape button with proper icon and sizing
        self.shape_button = ttk.Button(
            parent,
            image=self.app.icons.get('shape'),  # Fixed: changed from 'shapes' to 'shape'
            width=button_width  # This ensures same width as other buttons
        )
        self.shape_button.pack(side=tk.LEFT, padx=button_padding, pady=button_padding)
        ToolTip(self.shape_button, "Shape Tools")
        
        # Create the dropdown menu
        self.shape_menu = tk.Menu(self.shape_button, tearoff=0)
        
        # Add Rectangle option
        self.shape_menu.add_command(
            label="Rectangle",
            image=self.app.icons.get('rectangle'),
            compound=tk.LEFT,
            command=lambda: self.app.set_tool("rectangle")
        )
        
        # Add Circle option
        self.shape_menu.add_command(
            label="Circle",
            image=self.app.icons.get('circle'),
            compound=tk.LEFT,
            command=lambda: self.app.set_tool("circle")
        )
        
        # Add Line option
        self.shape_menu.add_command(
            label="Line",
            image=self.app.icons.get('line'),
            compound=tk.LEFT,
            command=lambda: self.app.set_tool("line")
        )
        
        # Bind the button to show the dropdown menu
        self.shape_button.configure(command=self.show_shape_menu)
    
    def show_shape_menu(self):
        """Show the shape dropdown menu"""
        try:
            # Get the position of the shape button
            x = self.shape_button.winfo_rootx()
            y = self.shape_button.winfo_rooty() + self.shape_button.winfo_height()
            
            # Show the menu at the button position
            self.shape_menu.post(x, y)
        except Exception as e:
            print(f"Error showing shape menu: {e}")
    
    def toggle_grid(self):
        """Toggle grid visibility on the canvas"""
        try:
            if hasattr(self.app.canvas_manager, 'toggle_grid'):
                self.app.canvas_manager.toggle_grid()
            else:
                print("Error: CanvasManager has no toggle_grid method")
        except Exception as e:
            print(f"Error toggling grid: {e}")

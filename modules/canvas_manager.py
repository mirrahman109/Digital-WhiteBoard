import tkinter as tk
from tkinter import ttk
from collections import deque

class CanvasManager:
    def __init__(self, app):
        self.app = app
        self.canvas = None
        self.h_scrollbar = None
        self.v_scrollbar = None
        
        # Initialize undo/redo stacks
        self.undo_stack = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)
        
        # Drawing state variables
        self.last_x, self.last_y = None, None
        self.shape_start_x, self.shape_start_y = None, None
    
    def create_canvas(self, parent):
        """Create canvas with scrollbars"""
        self.canvas = tk.Canvas(
            parent,
            bg="white",
            width=800,
            height=600,
            scrollregion=(0, 0, 1600, 1200)
        )
        
        # Add scrollbars
        self.h_scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )
        self.v_scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        self.canvas.configure(
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )

        # Grid layout for canvas and scrollbars
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<MouseWheel>", self.zoom_canvas)
    
    def start_draw(self, event):
        self.last_x = self.canvas.canvasx(event.x)
        self.last_y = self.canvas.canvasy(event.y)
        # For shapes, store the initial point separately
        self.shape_start_x = self.last_x
        self.shape_start_y = self.last_y

    def draw(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.app.current_tool in ["brush", "eraser"]:
            color = "white" if self.app.current_tool == "eraser" else self.get_draw_color(self.app.brush_color)
            
            # For eraser tool, handle preserving grid lines differently
            if self.app.current_tool == "eraser":
                # First, identify all items that would be affected by the eraser
                items_at_position = self.canvas.find_overlapping(x-self.app.brush_size/2, y-self.app.brush_size/2, 
                                                               x+self.app.brush_size/2, y+self.app.brush_size/2)
                
                # Only erase non-grid items
                for item in items_at_position:
                    if item and "grid" not in self.canvas.gettags(item):
                        self.canvas.delete(item)
                        # Track the deletion in undo stack - simplified for this example
                        self.undo_stack.append({
                            "type": "erased",
                            "id": item,
                            # We'd need more info to reconstruct
                        })
                        
                self.last_x = x
                self.last_y = y
                return
            
            # Normal drawing tool behavior continues as before
            line = self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                width=self.app.brush_size,
                fill=color,
                capstyle=tk.ROUND,
                smooth=True
            )
            self.undo_stack.append({
                "type": "line",
                "id": line,
                "coords": [self.last_x, self.last_y, x, y],
                "color": color,
                "width": self.app.brush_size
            })
            self.redo_stack.clear()
            self.last_x = x
            self.last_y = y  # Only update for brush/eraser
        
        elif self.app.current_tool in ["rectangle", "circle", "line"]:
            self.canvas.delete("temp_shape")
            # Use shape_start_x/y as the fixed starting point
            if self.app.current_tool == "rectangle":
                self.canvas.create_rectangle(
                    self.shape_start_x, self.shape_start_y, x, y,
                    outline=self.get_draw_color(self.app.brush_color),
                    width=self.app.brush_size,
                    tags="temp_shape"
                )
            elif self.app.current_tool == "circle":
                self.canvas.create_oval(
                    self.shape_start_x, self.shape_start_y, x, y,
                    outline=self.get_draw_color(self.app.brush_color),
                    width=self.app.brush_size,
                    tags="temp_shape"
                )
            elif self.app.current_tool == "line":
                self.canvas.create_line(
                    self.shape_start_x, self.shape_start_y, x, y,
                    fill=self.get_draw_color(self.app.brush_color),
                    width=self.app.brush_size,
                    tags="temp_shape"
                )
        # Do not update self.last_x/self.last_y for shapes

    def stop_draw(self, event):
        if self.app.current_tool in ["rectangle", "circle", "line"]:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            shape = None
            
            # Use shape_start_x/y as the fixed starting point
            if self.app.current_tool == "rectangle":
                shape = self.canvas.create_rectangle(
                    self.shape_start_x, self.shape_start_y, x, y,
                    outline=self.get_draw_color(self.app.brush_color),
                    width=self.app.brush_size
                )
            elif self.app.current_tool == "circle":
                shape = self.canvas.create_oval(
                    self.shape_start_x, self.shape_start_y, x, y,
                    outline=self.get_draw_color(self.app.brush_color),
                    width=self.app.brush_size
                )
            elif self.app.current_tool == "line":
                shape = self.canvas.create_line(
                    self.shape_start_x, self.shape_start_y, x, y,
                    fill=self.get_draw_color(self.app.brush_color),
                    width=self.app.brush_size
                )
            
            if shape:
                self.undo_stack.append({
                    "type": self.app.current_tool,
                    "id": shape,
                    "coords": [self.shape_start_x, self.shape_start_y, x, y],
                    "color": self.get_draw_color(self.app.brush_color),
                    "width": self.app.brush_size
                })
                self.redo_stack.clear()
            
            self.canvas.delete("temp_shape")

    def zoom_canvas(self, event):
        if event.state == 4:  # Check if Ctrl key is pressed
            factor = 1.1 if event.delta > 0 else 0.9
            self.app.zoom_level *= factor
            self.canvas.scale("all", event.x, event.y, factor, factor)

    def undo(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.canvas.delete(action["id"])
            self.redo_stack.append(action)

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            shape = None
            
            if action["type"] in ["rectangle", "circle", "line"]:
                if action["type"] == "rectangle":
                    shape = self.canvas.create_rectangle(
                        *action["coords"],
                        outline=action["color"],
                        width=action["width"]
                    )
                elif action["type"] == "circle":
                    shape = self.canvas.create_oval(
                        *action["coords"],
                        outline=action["color"],
                        width=action["width"]
                    )
                elif action["type"] == "line":
                    shape = self.canvas.create_line(
                        *action["coords"],
                        fill=action["color"],
                        width=action["width"]
                    )
                action["id"] = shape
                self.undo_stack.append(action)

    def clear_canvas(self, maintain_history=True):
        """
        Remove all items from the canvas (except grid lines and background).
        In dark mode, only drawings are deleted, not the background.
        """
        if maintain_history and hasattr(self, "save_state"):
            self.save_state()
        for item_id in self.canvas.find_all():
            tags = self.canvas.gettags(item_id)
            if not tags or 'grid' not in tags:
                self.canvas.delete(item_id)
        if hasattr(self, "redo_stack") and maintain_history:
            self.redo_stack = []
        # Optionally, reset undo stack if you want a true "clear all"
        # if hasattr(self, "undo_stack"):
        #     self.undo_stack = []

    def reset_undo_redo_stacks(self):
        """Reset the undo and redo stacks for a new page"""
        self.undo_stack = []
        self.redo_stack = []
        print("Undo/redo stacks reset")

    def get_canvas_objects(self):
        """Get all objects on the canvas as serializable data"""
        objects = []
        all_items = self.canvas.find_all()
        
        for item_id in all_items:
            # Skip grid lines or other special items
            if 'grid' in self.canvas.gettags(item_id):
                continue
                
            item_type = self.canvas.type(item_id)
            item_coords = self.canvas.coords(item_id)
            item_options = {}
            
            # Get all options for this item
            if item_type == 'line':
                item_options['fill'] = self.canvas.itemcget(item_id, 'fill')
                item_options['width'] = self.canvas.itemcget(item_id, 'width')
            elif item_type in ('oval', 'rectangle'):
                item_options['outline'] = self.canvas.itemcget(item_id, 'outline')
                item_options['width'] = self.canvas.itemcget(item_id, 'width')
                item_options['fill'] = self.canvas.itemcget(item_id, 'fill')
                
            objects.append({
                'type': item_type,
                'coords': item_coords,
                'options': item_options
            })
        
        print(f"Retrieved {len(objects)} canvas objects")
        return objects

    def restore_canvas_objects(self, objects):
        """Restore canvas objects from serialized data"""
        if not objects:
            return
            
        for obj in objects:
            obj_type = obj['type']
            coords = obj['coords']
            options = obj['options']
            
            if obj_type == 'line':
                self.canvas.create_line(coords, **options)
            elif obj_type == 'oval':
                self.canvas.create_oval(coords, **options)
            elif obj_type == 'rectangle':
                self.canvas.create_rectangle(coords, **options)
            # Add handling for other types as needed
                
        print(f"Restored {len(objects)} canvas objects")

    def draw_grid(self):
        self.canvas.delete("grid")
        # Draw vertical lines
        for i in range(0, int(self.canvas.winfo_width()), 20):
            self.canvas.create_line(
                i, 0, i, self.canvas.winfo_height(),
                fill="gray90",
                tags="grid"
            )
        # Draw horizontal lines
        for i in range(0, int(self.canvas.winfo_height()), 20):
            self.canvas.create_line(
                0, i, self.canvas.winfo_width(), i,
                fill="gray90",
                tags="grid"
            )

    def toggle_grid(self):
        self.app.grid_visible = not self.app.grid_visible
        if self.app.grid_visible:
            self.draw_grid()
            self.app.toolbar_manager.grid_button.config(text="Grid Off")
        else:
            self.canvas.delete("grid")
            self.app.toolbar_manager.grid_button.config(text="Grid On")

    def toggle_theme(self):
        self.app.is_dark_mode = not self.app.is_dark_mode
        bg_color = "#2d2d2d" if self.app.is_dark_mode else "white"
        self.canvas.configure(bg=bg_color)
        
        # Update button text based on current theme
        if self.app.is_dark_mode:
            self.app.toolbar_manager.theme_button.config(text="Light")
        else:
            self.app.toolbar_manager.theme_button.config(text="Dark")
            
        # Update all drawing colors on the canvas
        for item in self.canvas.find_all():
            # Skip grid lines
            if "grid" in self.canvas.gettags(item):
                continue
                
            # Get the item type to handle it appropriately
            item_type = self.canvas.type(item)
            
            # Handle fill color for shapes and lines
            try:
                fill = self.canvas.itemcget(item, "fill")
                if fill and fill != "":
                    # Only convert black fill
                    if fill.lower() in ["black", "#000000"]:
                        self.canvas.itemconfig(item, fill="white" if self.app.is_dark_mode else "black")
            except Exception:
                # Item doesn't have fill property
                pass

            # Handle outline color for shapes (rectangles, ovals)
            if item_type in ["rectangle", "oval"]:
                try:
                    outline = self.canvas.itemcget(item, "outline")
                    if outline and outline != "":
                        # Only convert black outline
                        if outline.lower() in ["black", "#000000"]:
                            self.canvas.itemconfig(item, outline="white" if self.app.is_dark_mode else "black")
                except Exception:
                    # Item doesn't have outline property
                    pass

    def set_dark_background(self, enable):
        """Enable or disable dark background mode."""
        if enable:
            self.canvas.config(bg="black")
            self._redraw_for_dark_mode()
        else:
            self.canvas.config(bg="white")
            self._redraw_for_dark_mode()

    def _redraw_for_dark_mode(self):
        """Redraw all objects to adapt to dark/light mode."""
        # Get all items and their colors, then redraw black as white in dark mode
        for item_id in self.canvas.find_all():
            tags = self.canvas.gettags(item_id)
            if 'grid' in tags:
                continue
            item_type = self.canvas.type(item_id)
            if item_type in ("line", "oval", "rectangle"):
                color = self.canvas.itemcget(item_id, "fill" if item_type == "line" else "outline")
                if self.app.is_dark_mode and color == "black":
                    # Change black to white for visibility
                    if item_type == "line":
                        self.canvas.itemconfig(item_id, fill="white")
                    else:
                        self.canvas.itemconfig(item_id, outline="white")
                elif not self.app.is_dark_mode and color == "white":
                    # Change white back to black in light mode
                    if item_type == "line":
                        self.canvas.itemconfig(item_id, fill="black")
                    else:
                        self.canvas.itemconfig(item_id, outline="black")

    def get_draw_color(self, color):
        """Return the color to use for drawing, adapting for dark mode."""
        if self.app.is_dark_mode and color == "black":
            return "white"
        return color

    def export_canvas_as_image(self, filename):
        """
        Export the current canvas as an image file
        
        Args:
            filename: Path to save the exported image
        """
        try:
            # Get the canvas dimensions
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            # Use PIL to take a screenshot of the canvas
            from PIL import ImageGrab
            image = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            
            # Save the image
            image.save(filename)
            
            print(f"Canvas exported as image to: {filename}")
            
            # Show a success message in a messagebox if possible
            try:
                from tkinter import messagebox
                messagebox.showinfo("Export Successful", f"Canvas exported to {filename}")
            except Exception:
                pass
                
        except Exception as e:
            print(f"Error exporting canvas as image: {e}")
            try:
                from tkinter import messagebox
                messagebox.showerror("Export Error", f"Could not export canvas: {str(e)}")
            except Exception:
                pass

import json
import os
from tkinter import filedialog
from PIL import Image

class FileManager:
    def __init__(self, app):
        self.app = app
    
    def save_whiteboard(self):
        """Save the whiteboard to a file with .wb extension (custom JSON format)"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wb",
            filetypes=[("Whiteboard files", "*.wb"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Make sure to save current page before saving the file
                self.app.page_manager.save_current_page()
                
                # Create a data structure to hold all whiteboard state
                data = {
                    "pages": self.app.page_manager.pages,
                    "current_page_index": self.app.page_manager.current_page_index,  # Fixed attribute name
                    "is_dark_mode": self.app.is_dark_mode,
                    "grid_visible": self.app.grid_visible,
                    "version": "1.0"  # Adding version for future compatibility
                }
                
                # Save as JSON with indentation for readability
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                    
                # Show success message
                print(f"Whiteboard saved successfully to {file_path}")
                
                # Show a success message in a messagebox if possible
                try:
                    from tkinter import messagebox
                    messagebox.showinfo("Save Successful", f"Whiteboard saved to {file_path}")
                except Exception:
                    pass
                    
            except Exception as e:
                print(f"Error saving whiteboard: {e}")
                # Show error message in a messagebox if possible
                try:
                    from tkinter import messagebox
                    messagebox.showerror("Save Error", f"Could not save whiteboard: {str(e)}")
                except Exception:
                    pass

    def load_whiteboard(self):
        """Load a previously saved whiteboard file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            defaultextension=".wbrd",
            filetypes=[("Whiteboard files", "*.wbrd"), ("All files", "*.*")]
        )
        
        if filename:
            # Load the whiteboard data
            self.load_file(filename)

    def export_as_image(self):
        """Export the current whiteboard page as an image"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            # Get the canvas and export it as an image
            self.app.canvas_manager.export_canvas_as_image(filename)

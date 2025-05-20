import tkinter as tk

class PageManager:
    def __init__(self, app):
        self.app = app
        self.pages = []
        self.current_page_index = 0

    def initialize_page(self):
        """Initialize the first page"""
        if not self.pages:
            self.add_page(update_ui=False)
        self.update_page_info()
        
    def add_page(self, update_ui=True):
        """Add a new page after the current one"""
        # Create a new page (blank canvas data)
        new_page = {
            "objects": [],
            "undo_stack": [],
            "redo_stack": []
        }
        
        # Insert the new page after the current one
        if not self.pages:
            self.pages.append(new_page)
            self.current_page_index = 0
        else:
            self.current_page_index += 1
            self.pages.insert(self.current_page_index, new_page)
        
        # Update the canvas and UI
        if update_ui:
            # Clear the canvas properly
            self.app.canvas_manager.clear_canvas(maintain_history=False)
            # Update the undo/redo stacks for the new page
            self.app.canvas_manager.reset_undo_redo_stacks()
            self.update_page_info()
            
        print(f"Added page. Now at page {self.current_page_index + 1}/{len(self.pages)}")
    
    def prev_page(self):
        """Go to the previous page if available. If current page is empty, delete it."""
        if self.current_page_index > 0:
            # Check if current page is empty
            current_page = self.pages[self.current_page_index]
            
            # Properly check if page is empty by looking at canvas objects
            canvas_objects = self.app.canvas_manager.get_canvas_objects() if hasattr(self.app.canvas_manager, 'get_canvas_objects') else []
            is_empty = len(canvas_objects) == 0
            
            if is_empty:
                # Remove the empty page
                del self.pages[self.current_page_index]
                self.current_page_index -= 1
                print(f"Deleted empty page. Now at page {self.current_page_index + 1}/{len(self.pages)}")
            else:
                # Save current page state before navigating away
                self.save_current_page()
                self.current_page_index -= 1

            self.load_current_page()
            self.update_page_info()
    
    def next_page(self):
        """Go to the next page if available"""
        if self.current_page_index < len(self.pages) - 1:
            # Save current page state
            self.save_current_page()
            
            # Move to next page
            self.current_page_index += 1
            self.load_current_page()
            self.update_page_info()
            
            print(f"Moved to next page: {self.current_page_index + 1}/{len(self.pages)}")
    
    def save_current_page(self):
        """Save the current canvas state to the current page"""
        if self.pages and 0 <= self.current_page_index < len(self.pages):
            # Get the current canvas objects and history
            current_page = self.pages[self.current_page_index]
            current_page["objects"] = self.app.canvas_manager.get_canvas_objects()
            current_page["undo_stack"] = self.app.canvas_manager.undo_stack
            current_page["redo_stack"] = self.app.canvas_manager.redo_stack
            
            print(f"Saved page {self.current_page_index + 1} with {len(current_page['objects'])} objects")
    
    def load_current_page(self):
        """Load the current page data into the canvas"""
        if self.pages and 0 <= self.current_page_index < len(self.pages):
            # Clear the canvas without adding to history
            self.app.canvas_manager.clear_canvas(maintain_history=False)
            
            # Get the current page data
            current_page = self.pages[self.current_page_index]
            
            # Restore canvas objects
            self.app.canvas_manager.restore_canvas_objects(current_page.get("objects", []))
            
            # Restore undo/redo stacks
            self.app.canvas_manager.undo_stack = current_page.get("undo_stack", [])
            self.app.canvas_manager.redo_stack = current_page.get("redo_stack", [])
            
            print(f"Loaded page {self.current_page_index + 1} with {len(current_page.get('objects', []))} objects")
    
    def update_page_info(self):
        """Update the page info label in the toolbar"""
        if hasattr(self.app.toolbar_manager, 'page_info'):
            page_text = f"Page {self.current_page_index + 1}/{len(self.pages)}"
            self.app.toolbar_manager.page_info.config(text=page_text)
            print(f"Updated page info: {page_text}")
            
    def get_current_page_data(self):
        """Get the data for the current page"""
        if self.pages and 0 <= self.current_page_index < len(self.pages):
            return self.pages[self.current_page_index]
        return None

    def get_canvas_objects(self):
        """Helper method to safely get canvas objects"""
        if hasattr(self.app.canvas_manager, 'get_canvas_objects'):
            return self.app.canvas_manager.get_canvas_objects()
        return []

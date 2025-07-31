import json
import os
from tkinter import filedialog
import tkinter as tk
from PIL import Image

class FileManager:
    def __init__(self, app):
        self.app = app
        self._setup_page_auto_save()
    
    def _setup_page_auto_save(self):
        """Setup automatic saving when pages are switched"""
        try:
            # Hook into page manager's methods if they exist
            if hasattr(self.app.page_manager, 'switch_to_page'):
                original_switch = self.app.page_manager.switch_to_page
                def hooked_switch(page_index):
                    # Save current page before switching
                    self._auto_save_current_page()
                    return original_switch(page_index)
                self.app.page_manager.switch_to_page = hooked_switch
                
            if hasattr(self.app.page_manager, 'load_page'):
                original_load = self.app.page_manager.load_page
                def hooked_load(page_index):
                    # Save current page before loading new one
                    self._auto_save_current_page()
                    return original_load(page_index)
                self.app.page_manager.load_page = hooked_load
                
            print("Auto-save hooks installed")
        except Exception as e:
            print(f"Could not install auto-save hooks: {e}")
    
    def _auto_save_current_page(self):
        """Automatically save the current page's canvas content"""
        try:
            current_page = getattr(self.app.page_manager, 'current_page_index', 0)
            print(f"Auto-saving page {current_page}")
            
            # Ensure we have enough pages
            while len(self.app.page_manager.pages) <= current_page:
                self.app.page_manager.pages.append({
                    "elements": [],
                    "background_color": "#FFFFFF"
                })
            
            # Capture canvas content
            if hasattr(self.app.canvas_manager, 'canvas'):
                canvas = self.app.canvas_manager.canvas
                elements = self._extract_canvas_elements(canvas)
                self.app.page_manager.pages[current_page]["elements"] = elements
                print(f"Auto-saved {len(elements)} elements for page {current_page}")
                
        except Exception as e:
            print(f"Error in auto-save: {e}")
    
    def _extract_canvas_elements(self, canvas):
        """Extract all elements from canvas"""
        elements = []
        try:
            canvas_items = canvas.find_all()
            for item_id in canvas_items:
                try:
                    item_type = canvas.type(item_id)
                    coords = canvas.coords(item_id)
                    
                    if item_type == "line":
                        element = {
                            "type": "line",
                            "points": list(coords),  # Ensure it's a list, not deque
                            "color": canvas.itemcget(item_id, "fill") or "black",
                            "width": int(float(canvas.itemcget(item_id, "width") or "2")),
                            "smooth": canvas.itemcget(item_id, "smooth") == "1"
                        }
                        elements.append(element)
                        
                    elif item_type == "rectangle":
                        if len(coords) >= 4:
                            element = {
                                "type": "rectangle",
                                "x1": float(coords[0]), "y1": float(coords[1]),
                                "x2": float(coords[2]), "y2": float(coords[3]),
                                "outline": canvas.itemcget(item_id, "outline") or "black",
                                "fill": canvas.itemcget(item_id, "fill") or "",
                                "width": int(float(canvas.itemcget(item_id, "width") or "2"))
                            }
                            elements.append(element)
                        
                    elif item_type == "oval":
                        if len(coords) >= 4:
                            element = {
                                "type": "oval",
                                "x1": float(coords[0]), "y1": float(coords[1]),
                                "x2": float(coords[2]), "y2": float(coords[3]),
                                "outline": canvas.itemcget(item_id, "outline") or "black",
                                "fill": canvas.itemcget(item_id, "fill") or "",
                                "width": int(float(canvas.itemcget(item_id, "width") or "2"))
                            }
                            elements.append(element)
                        
                    elif item_type == "text":
                        if len(coords) >= 2:
                            font_info = canvas.itemcget(item_id, "font")
                            try:
                                font_parts = str(font_info).split()
                                font_family = font_parts[0] if font_parts else "Arial"
                                font_size = int(font_parts[1]) if len(font_parts) > 1 else 12
                            except (ValueError, IndexError):
                                font_family = "Arial"
                                font_size = 12
                                
                            element = {
                                "type": "text",
                                "x": float(coords[0]), "y": float(coords[1]),
                                "text": canvas.itemcget(item_id, "text") or "",
                                "color": canvas.itemcget(item_id, "fill") or "black",
                                "font_family": font_family,
                                "font_size": font_size
                            }
                            elements.append(element)
                            
                except Exception as e:
                    print(f"Error extracting element {item_id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting canvas elements: {e}")
            
        return elements

    def save_whiteboard(self):
        """Save the whiteboard to a file with .wb extension (custom JSON format)"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wb",
            filetypes=[("Whiteboard files", "*.wb"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Force save current page one last time
                self._auto_save_current_page()
                
                # Convert pages to JSON-serializable format
                serializable_pages = []
                for page in self.app.page_manager.pages:
                    serializable_page = {
                        "elements": [],
                        "background_color": page.get("background_color", "#FFFFFF")
                    }
                    
                    # Convert elements to serializable format
                    elements = page.get("elements", [])
                    for element in elements:
                        if isinstance(element, dict):
                            serializable_element = {}
                            for key, value in element.items():
                                # Convert deques and other non-serializable types
                                if hasattr(value, '__iter__') and not isinstance(value, (str, dict)):
                                    # Convert deques, lists, tuples to plain lists
                                    try:
                                        serializable_element[key] = list(value)
                                    except (TypeError, ValueError):
                                        # If conversion fails, convert to string
                                        serializable_element[key] = str(value)
                                else:
                                    serializable_element[key] = value
                            
                            # Remove any tkinter-specific properties
                            serializable_element.pop("tkinter_id", None)
                            serializable_page["elements"].append(serializable_element)
                    
                    serializable_pages.append(serializable_page)
                
                # Create data structure
                data = {
                    "pages": serializable_pages,
                    "current_page_index": self.app.page_manager.current_page_index,
                    "is_dark_mode": getattr(self.app, 'is_dark_mode', False),
                    "grid_visible": getattr(self.app, 'grid_visible', False),
                    "version": "1.0"
                }
                
                # Debug output
                total_elements = sum(len(page["elements"]) for page in serializable_pages)
                print(f"Saving {len(serializable_pages)} pages with {total_elements} total elements")
                for i, page in enumerate(serializable_pages):
                    print(f"  Page {i}: {len(page['elements'])} elements")
                
                # Save to file
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                    
                print(f"Whiteboard saved successfully to {file_path}")
                
                try:
                    from tkinter import messagebox
                    messagebox.showinfo("Save Successful", f"Whiteboard saved to {file_path}")
                except Exception:
                    pass
                    
            except Exception as e:
                print(f"Error saving whiteboard: {e}")
                import traceback
                traceback.print_exc()
                try:
                    from tkinter import messagebox
                    messagebox.showerror("Save Error", f"Could not save whiteboard: {str(e)}")
                except Exception:
                    pass

    def load_whiteboard(self):
        """Load a previously saved whiteboard file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            defaultextension=".wb",
            filetypes=[("Whiteboard files", "*.wb"), ("All files", "*.*")]
        )
        
        if filename:
            # Load the whiteboard data
            self.load_file(filename)

    def load_file(self, filename):
        """Load a whiteboard file and restore the state"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            
            # Debug: Print what we're loading
            print(f"Loading whiteboard with {len(data['pages'])} pages")
            for i, page in enumerate(data['pages']):
                elements = page.get('elements', [])
                print(f"  Page {i}: {len(elements)} elements")
                
            # Restore the whiteboard state
            self.app.page_manager.pages = data["pages"]
            self.app.page_manager.current_page_index = data["current_page_index"]
            
            # Restore settings if they exist in the file
            if "is_dark_mode" in data:
                self.app.is_dark_mode = data["is_dark_mode"]
                # Call toggle_dark_mode only if needed
                if hasattr(self.app, 'toggle_dark_mode'):
                    if data["is_dark_mode"] != self.app.is_dark_mode:
                        self.app.toggle_dark_mode()
                    
            if "grid_visible" in data:
                self.app.grid_visible = data["grid_visible"]
                # Call toggle_grid only if needed
                if hasattr(self.app, 'toggle_grid'):
                    if data["grid_visible"] != self.app.grid_visible:
                        self.app.toggle_grid()
            
            # First, ensure we have a canvas and canvas_manager
            if not hasattr(self.app, 'canvas_manager'):
                print("Error: No canvas_manager found in the app")
                return
                
            # Clear the canvas completely
            if hasattr(self.app.canvas_manager, 'canvas'):
                canvas = self.app.canvas_manager.canvas
                canvas.delete("all")  # Clear everything from canvas
                
            # Get the current page data
            current_page_index = self.app.page_manager.current_page_index
            if 0 <= current_page_index < len(self.app.page_manager.pages):
                current_page = self.app.page_manager.pages[current_page_index]
                
                # Apply background color if it exists
                if hasattr(self.app.canvas_manager, 'canvas'):
                    canvas = self.app.canvas_manager.canvas
                    if "background_color" in current_page:
                        canvas.config(bg=current_page.get("background_color", "#FFFFFF"))
                
                # Force immediate redraw of the current page
                if hasattr(self.app.page_manager, 'load_page'):
                    print("Using page_manager.load_page method")
                    self.app.page_manager.load_page(current_page_index)
                else:
                    # Fallback: manually redraw elements
                    print("Manually rendering elements")
                    if hasattr(self.app.canvas_manager, 'canvas'):
                        self._redraw_elements_on_canvas(self.app.canvas_manager.canvas, current_page)
            
            # Force canvas update and refresh
            if hasattr(self.app.canvas_manager, 'canvas'):
                self.app.canvas_manager.canvas.update_idletasks()
                self.app.canvas_manager.canvas.update()
            
            # Update page manager UI if it exists
            if hasattr(self.app.page_manager, 'update_page_display'):
                self.app.page_manager.update_page_display()
            
            # Show success message
            print(f"Whiteboard loaded successfully from {filename}")
            try:
                from tkinter import messagebox
                messagebox.showinfo("Load Successful", f"Whiteboard loaded from {filename}")
            except Exception:
                pass
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error loading whiteboard: {e}")
            # Show error message in a messagebox
            try:
                from tkinter import messagebox
                messagebox.showerror("Load Error", f"Could not load whiteboard: {str(e)}")
            except Exception:
                pass
    
    def _post_load_redraw(self, page_index):
        """Additional redraw after loading to ensure content appears"""
        try:
            # Try multiple approaches to refresh the page
            if hasattr(self.app.page_manager, 'load_page'):
                self.app.page_manager.load_page(page_index)
            elif hasattr(self.app.page_manager, 'show_page'):
                self.app.page_manager.show_page(page_index)
            
            # Force canvas update
            if hasattr(self.app.canvas_manager, 'canvas'):
                self.app.canvas_manager.canvas.update_idletasks()
                self.app.canvas_manager.canvas.update()
                
            print("Post-load redraw completed")
        except Exception as e:
            print(f"Error in post-load redraw: {e}")
    
    def _redraw_elements_on_canvas(self, canvas, page):
        """Manually redraw elements from a page onto the canvas"""
        elements_count = 0
        
        for element in page.get("elements", []):
            elements_count += 1
            element_type = element.get("type")
            
            if element_type == "line":
                # Redraw lines
                points = element.get("points", [])
                if len(points) >= 4:  # Need at least 2 points (x1,y1,x2,y2)
                    color = element.get("color", "black")
                    width = element.get("width", 2)
                    # Create a new canvas item
                    try:
                        line_id = canvas.create_line(
                            points, 
                            fill=color, 
                            width=width, 
                            smooth=element.get("smooth", True),
                            capstyle=tk.ROUND,
                            joinstyle=tk.ROUND
                        )
                        print(f"Drew line with {len(points)//2} points")
                    except Exception as e:
                        print(f"Error drawing line: {e}")
            
            elif element_type == "rectangle":
                # Redraw rectangles
                try:
                    x1, y1 = element.get("x1", 0), element.get("y1", 0)
                    x2, y2 = element.get("x2", 0), element.get("y2", 0)
                    color = element.get("outline", "black")
                    fill = element.get("fill", "")
                    width = element.get("width", 2)
                    canvas.create_rectangle(x1, y1, x2, y2, outline=color, fill=fill, width=width)
                    print(f"Drew rectangle at ({x1},{y1}) to ({x2},{y2})")
                except Exception as e:
                    print(f"Error drawing rectangle: {e}")
            
            elif element_type == "oval":
                # Redraw ovals/circles
                try:
                    x1, y1 = element.get("x1", 0), element.get("y1", 0)
                    x2, y2 = element.get("x2", 0), element.get("y2", 0)
                    color = element.get("outline", "black")
                    fill = element.get("fill", "")
                    width = element.get("width", 2)
                    canvas.create_oval(x1, y1, x2, y2, outline=color, fill=fill, width=width)
                    print(f"Drew oval at ({x1},{y1}) to ({x2},{y2})")
                except Exception as e:
                    print(f"Error drawing oval: {e}")
            
            elif element_type == "text":
                # Redraw text
                try:
                    x, y = element.get("x", 0), element.get("y", 0)
                    text = element.get("text", "")
                    color = element.get("color", "black")
                    font_size = element.get("font_size", 12)
                    font_family = element.get("font_family", "Arial")
                    canvas.create_text(x, y, text=text, fill=color, 
                                     font=(font_family, font_size), anchor="nw")
                    print(f"Drew text '{text}' at ({x},{y})")
                except Exception as e:
                    print(f"Error drawing text: {e}")
        
        print(f"Manually drew {elements_count} elements on canvas")
        
        # Force canvas to update after drawing all elements
        canvas.update_idletasks()
        canvas.update()

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

    def _force_save_current_page(self):
        """Force save the current page by capturing canvas state"""
        try:
            current_page_index = getattr(self.app.page_manager, 'current_page_index', 0)
            
            # Ensure we have enough pages
            while len(self.app.page_manager.pages) <= current_page_index:
                self.app.page_manager.pages.append({
                    "elements": [],
                    "background_color": "#FFFFFF"
                })
            
            # Capture current canvas state
            self._capture_current_canvas_state()
            
            print(f"Force saved current page {current_page_index}")
            
        except Exception as e:
            print(f"Error in force save current page: {e}")

    def _attempt_to_recover_page_content(self):
        """Try to recover content for pages that appear empty"""
        try:
            current_page = self.app.page_manager.current_page_index
            
            # Check if page manager has stored content for other pages
            for i, page in enumerate(self.app.page_manager.pages):
                if len(page.get("elements", [])) == 0 and i != current_page:
                    print(f"Attempting to recover content for empty page {i}")
                    
                    # Try different methods to get page content
                    recovered_content = None
                    
                    # Method 1: Check if page manager has a get_page method
                    if hasattr(self.app.page_manager, 'get_page'):
                        try:
                            recovered_content = self.app.page_manager.get_page(i)
                        except:
                            pass
                    
                    # Method 2: Check if page manager has stored pages differently
                    if not recovered_content and hasattr(self.app.page_manager, 'stored_pages'):
                        try:
                            if i < len(self.app.page_manager.stored_pages):
                                recovered_content = self.app.page_manager.stored_pages[i]
                        except:
                            pass
                    
                    # Method 3: Try to temporarily switch to that page and capture
                    if not recovered_content and hasattr(self.app.page_manager, 'switch_to_page'):
                        try:
                            # Save current page first
                            original_page = current_page
                            
                            # Switch to the empty page
                            self.app.page_manager.switch_to_page(i)
                            
                            # Capture what's on canvas now
                            if hasattr(self.app.canvas_manager, 'canvas'):
                                canvas_items = self.app.canvas_manager.canvas.find_all()
                                if len(canvas_items) > 0:
                                    self._capture_current_canvas_state()
                                    recovered_content = self.app.page_manager.pages[i]
                            
                            # Switch back to original page
                            self.app.page_manager.switch_to_page(original_page)
                            
                        except Exception as e:
                            print(f"Error trying to recover page {i}: {e}")
                            # Make sure we're back on the original page
                            try:
                                self.app.page_manager.switch_to_page(current_page)
                            except:
                                pass
                    
                    if recovered_content and recovered_content.get("elements"):
                        self.app.page_manager.pages[i] = recovered_content
                        print(f"Recovered {len(recovered_content['elements'])} elements for page {i}")
                    else:
                        print(f"Could not recover content for page {i}")
                        
        except Exception as e:
            print(f"Error in attempt to recover page content: {e}")

    def _capture_current_canvas_state(self):
        """Capture current canvas state and save it to the current page"""
        try:
            if not hasattr(self.app, 'canvas_manager') or not hasattr(self.app.canvas_manager, 'canvas'):
                print("No canvas found to capture state from")
                return
                
            canvas = self.app.canvas_manager.canvas
            current_page_index = getattr(self.app.page_manager, 'current_page_index', 0)
            
            # Ensure we have enough pages
            while len(self.app.page_manager.pages) <= current_page_index:
                self.app.page_manager.pages.append({
                    "elements": [],
                    "background_color": "#FFFFFF"
                })
            
            # Get all canvas items
            canvas_items = canvas.find_all()
            elements = []
            
            print(f"Found {len(canvas_items)} items on canvas for page {current_page_index}")
            
            for item_id in canvas_items:
                try:
                    item_type = canvas.type(item_id)
                    coords = canvas.coords(item_id)
                    
                    if item_type == "line":
                        # Get line properties
                        width_str = canvas.itemcget(item_id, "width")
                        width = int(float(width_str)) if width_str else 2
                        
                        element = {
                            "type": "line",
                            "points": coords,
                            "color": canvas.itemcget(item_id, "fill") or "black",
                            "width": width,
                            "smooth": canvas.itemcget(item_id, "smooth") == "1"
                        }
                        elements.append(element)
                        
                    elif item_type == "rectangle":
                        width_str = canvas.itemcget(item_id, "width")
                        width = int(float(width_str)) if width_str else 2
                        
                        element = {
                            "type": "rectangle",
                            "x1": coords[0], "y1": coords[1],
                            "x2": coords[2], "y2": coords[3],
                            "outline": canvas.itemcget(item_id, "outline") or "black",
                            "fill": canvas.itemcget(item_id, "fill") or "",
                            "width": width
                        }
                        elements.append(element)
                        
                    elif item_type == "oval":
                        width_str = canvas.itemcget(item_id, "width")
                        width = int(float(width_str)) if width_str else 2
                        
                        element = {
                            "type": "oval",
                            "x1": coords[0], "y1": coords[1],
                            "x2": coords[2], "y2": coords[3],
                            "outline": canvas.itemcget(item_id, "outline") or "black",
                            "fill": canvas.itemcget(item_id, "fill") or "",
                            "width": width
                        }
                        elements.append(element)
                        
                    elif item_type == "text":
                        font_info = canvas.itemcget(item_id, "font")
                        try:
                            # Parse font info - could be like "Arial 12" or more complex
                            font_parts = str(font_info).split()
                            font_family = font_parts[0] if font_parts else "Arial"
                            font_size = int(font_parts[1]) if len(font_parts) > 1 else 12
                        except (ValueError, IndexError):
                            font_family = "Arial"
                            font_size = 12
                            
                        element = {
                            "type": "text",
                            "x": coords[0], "y": coords[1],
                            "text": canvas.itemcget(item_id, "text") or "",
                            "color": canvas.itemcget(item_id, "fill") or "black",
                            "font_family": font_family,
                            "font_size": font_size
                        }
                        elements.append(element)
                        
                except Exception as e:
                    print(f"Error capturing canvas item {item_id}: {e}")
                    continue
            
            # Update the current page with captured elements
            self.app.page_manager.pages[current_page_index]["elements"] = elements
            print(f"Successfully captured {len(elements)} elements to page {current_page_index}")
            
        except Exception as e:
            print(f"Error capturing canvas state: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_all_pages_content(self):
        """Visit each page and save its content"""
        try:
            if not hasattr(self.app, 'page_manager'):
                print("No page_manager found")
                return
                
            original_page = self.app.page_manager.current_page_index
            total_pages = len(self.app.page_manager.pages)
            
            print(f"Saving content for all {total_pages} pages (currently on page {original_page})")
            
            # First, save the current page's content before switching
            print(f"Saving current page {original_page} before switching...")
            self._capture_current_canvas_state()
            
            # Now go through each page and ensure it has proper content
            for page_index in range(total_pages):
                try:
                    print(f"Processing page {page_index}...")
                    
                    # Switch to this page and load its content
                    if page_index != original_page:
                        print(f"  Switching to page {page_index}")
                        
                        # Clear canvas first to ensure we see only this page's content
                        if hasattr(self.app.canvas_manager, 'canvas'):
                            self.app.canvas_manager.canvas.delete("all")
                        
                        # Try different methods to switch and load the page
                        switched = False
                        
                        # Method 1: Try switch_to_page
                        if hasattr(self.app.page_manager, 'switch_to_page'):
                            try:
                                self.app.page_manager.switch_to_page(page_index)
                                switched = True
                                print(f"    Switched using switch_to_page()")
                            except Exception as e:
                                print(f"    switch_to_page failed: {e}")
                        
                        # Method 2: Try load_page
                        if not switched and hasattr(self.app.page_manager, 'load_page'):
                            try:
                                self.app.page_manager.load_page(page_index)
                                switched = True
                                print(f"    Switched using load_page()")
                            except Exception as e:
                                print(f"    load_page failed: {e}")
                        
                        # Method 3: Manual switching with proper loading
                        if not switched:
                            try:
                                # Set the page index
                                self.app.page_manager.current_page_index = page_index
                                
                                # Try to load the page content manually
                                if page_index < len(self.app.page_manager.pages):
                                    page_data = self.app.page_manager.pages[page_index]
                                    if hasattr(self.app.canvas_manager, 'render_page'):
                                        self.app.canvas_manager.render_page(page_data)
                                    elif hasattr(self.app.canvas_manager, 'load_page_content'):
                                        self.app.canvas_manager.load_page_content(page_data)
                                    else:
                                        # Manually render the page content
                                        self._render_page_content(page_data)
                                
                                # Update the display
                                if hasattr(self.app.page_manager, 'update_display'):
                                    self.app.page_manager.update_display()
                                elif hasattr(self.app.page_manager, 'refresh'):
                                    self.app.page_manager.refresh()
                                
                                switched = True
                                print(f"    Switched manually and loaded page content")
                            except Exception as e:
                                print(f"    Manual switch failed: {e}")
                        
                        if switched:
                            # Give the UI time to update
                            if hasattr(self.app, 'root'):
                                self.app.root.update_idletasks()
                                self.app.root.update()
                                
                            # Small delay to ensure rendering is complete
                            import time
                            time.sleep(0.1)
                            
                            # Now capture the content of this page
                            print(f"    Capturing content for page {page_index}")
                            canvas_items = []
                            if hasattr(self.app.canvas_manager, 'canvas'):
                                canvas_items = self.app.canvas_manager.canvas.find_all()
                            print(f"    Found {len(canvas_items)} items on canvas for page {page_index}")
                            
                            # Only capture if there are items or if this is an empty page we need to preserve
                            self._capture_current_canvas_state()
                        else:
                            print(f"    Could not switch to page {page_index}")
                    else:
                        print(f"  Page {page_index} is current page - content already captured")
                    
                except Exception as e:
                    print(f"Error processing page {page_index}: {e}")
                    continue
            
            # Switch back to the original page and restore its content
            print(f"Switching back to original page {original_page}")
            try:
                # Clear canvas first
                if hasattr(self.app.canvas_manager, 'canvas'):
                    self.app.canvas_manager.canvas.delete("all")
                
                # Switch back
                if hasattr(self.app.page_manager, 'switch_to_page'):
                    self.app.page_manager.switch_to_page(original_page)
                elif hasattr(self.app.page_manager, 'load_page'):
                    self.app.page_manager.load_page(original_page)
                else:
                    self.app.page_manager.current_page_index = original_page
                    # Restore the original page content
                    if original_page < len(self.app.page_manager.pages):
                        page_data = self.app.page_manager.pages[original_page]
                        self._render_page_content(page_data)
                    
                    if hasattr(self.app.page_manager, 'update_display'):
                        self.app.page_manager.update_display()
                
                # Update UI
                if hasattr(self.app, 'root'):
                    self.app.root.update_idletasks()
                    self.app.root.update()
                    
            except Exception as e:
                print(f"Error switching back to original page: {e}")
            
            print("Finished saving all pages content")
            
        except Exception as e:
            print(f"Error in _save_all_pages_content: {e}")
            import traceback
            traceback.print_exc()

    def _render_page_content(self, page_data):
        """Manually render page content on the canvas"""
        try:
            if not hasattr(self.app.canvas_manager, 'canvas'):
                return
                
            canvas = self.app.canvas_manager.canvas
            elements = page_data.get("elements", [])
            
            print(f"    Manually rendering {len(elements)} elements")
            
            # Set background color
            bg_color = page_data.get("background_color", "#FFFFFF")
            canvas.config(bg=bg_color)
            
            # Render each element
            for element in elements:
                try:
                    element_type = element.get("type")
                    
                    if element_type == "line":
                        points = element.get("points", [])
                        if len(points) >= 4:
                            canvas.create_line(
                                points,
                                fill=element.get("color", "black"),
                                width=element.get("width", 2),
                                smooth=element.get("smooth", True),
                                capstyle=tk.ROUND,
                                joinstyle=tk.ROUND
                            )
                    
                    elif element_type == "rectangle":
                        x1, y1 = element.get("x1", 0), element.get("y1", 0)
                        x2, y2 = element.get("x2", 0), element.get("y2", 0)
                        canvas.create_rectangle(
                            x1, y1, x2, y2,
                            outline=element.get("outline", "black"),
                            fill=element.get("fill", ""),
                            width=element.get("width", 2)
                        )
                    
                    elif element_type == "oval":
                        x1, y1 = element.get("x1", 0), element.get("y1", 0)
                        x2, y2 = element.get("x2", 0), element.get("y2", 0)
                        canvas.create_oval(
                            x1, y1, x2, y2,
                            outline=element.get("outline", "black"),
                            fill=element.get("fill", ""),
                            width=element.get("width", 2)
                        )
                    
                    elif element_type == "text":
                        x, y = element.get("x", 0), element.get("y", 0)
                        text = element.get("text", "")
                        font_family = element.get("font_family", "Arial")
                        font_size = element.get("font_size", 12)
                        canvas.create_text(
                            x, y, text=text,
                            fill=element.get("color", "black"),
                            font=(font_family, font_size),
                            anchor="nw"
                        )
                        
                except Exception as e:
                    print(f"      Error rendering element: {e}")
                    continue
            
            # Force canvas update
            canvas.update_idletasks()
            canvas.update()
            
        except Exception as e:
            print(f"Error in _render_page_content: {e}")
    
    def _comprehensive_content_recovery(self):
        """Comprehensive approach to recover all page content"""
        try:
            print("Starting comprehensive content recovery...")
            
            # Step 1: Save current page content
            current_page = self.app.page_manager.current_page_index
            print(f"Current page: {current_page}")
            self._capture_current_canvas_state()
            
            # Step 2: Try to find content in various places
            self._search_for_page_content()
            
            # Step 3: If pages still empty, try to reconstruct from canvas manager
            self._try_canvas_manager_recovery()
            
            # Step 4: Look for undo/redo history
            self._try_history_recovery()
            
            print("Comprehensive content recovery completed")
            
        except Exception as e:
            print(f"Error in comprehensive content recovery: {e}")
            import traceback
            traceback.print_exc()

    def _search_for_page_content(self):
        """Search for page content in various app attributes"""
        try:
            print("Searching for page content in app attributes...")
            
            # Check if page manager has additional storage
            if hasattr(self.app.page_manager, '__dict__'):
                for attr_name, attr_value in self.app.page_manager.__dict__.items():
                    if 'page' in attr_name.lower() and isinstance(attr_value, (list, dict)):
                        print(f"  Found potential page storage: {attr_name}")
                        if isinstance(attr_value, list) and len(attr_value) > 0:
                            # Try to merge this with our pages
                            for i, potential_page in enumerate(attr_value):
                                if i < len(self.app.page_manager.pages) and isinstance(potential_page, dict):
                                    if potential_page.get("elements") and len(potential_page["elements"]) > 0:
                                        print(f"    Recovering {len(potential_page['elements'])} elements for page {i}")
                                        self.app.page_manager.pages[i] = potential_page
            
            # Check canvas manager for stored content
            if hasattr(self.app, 'canvas_manager') and hasattr(self.app.canvas_manager, '__dict__'):
                for attr_name, attr_value in self.app.canvas_manager.__dict__.items():
                    if ('page' in attr_name.lower() or 'content' in attr_name.lower()) and isinstance(attr_value, (list, dict)):
                        print(f"  Found potential canvas storage: {attr_name}")
                        if isinstance(attr_value, list):
                            for i, content in enumerate(attr_value):
                                if i < len(self.app.page_manager.pages) and isinstance(content, dict):
                                    if content.get("elements") and len(content["elements"]) > 0:
                                        print(f"    Recovering from canvas manager for page {i}")
                                        self.app.page_manager.pages[i] = content
            
            # Check if there's a drawing tool manager that might have content
            if hasattr(self.app, 'drawing_tool') and hasattr(self.app.drawing_tool, '__dict__'):
                for attr_name, attr_value in self.app.drawing_tool.__dict__.items():
                    if 'page' in attr_name.lower() and isinstance(attr_value, (list, dict)):
                        print(f"  Found potential drawing tool storage: {attr_name}")
                        
        except Exception as e:
            print(f"Error searching for page content: {e}")

    def _try_canvas_manager_recovery(self):
        """Try to recover content from canvas manager"""
        try:
            print("Trying canvas manager recovery...")
            
            if not hasattr(self.app, 'canvas_manager'):
                return
                
            # Look for any stored canvas states or drawing history
            canvas_manager = self.app.canvas_manager
            
            # Check if canvas manager has methods to get page content
            if hasattr(canvas_manager, 'get_all_pages'):
                try:
                    all_pages = canvas_manager.get_all_pages()
                    if all_pages and len(all_pages) > 0:
                        print(f"  Found {len(all_pages)} pages in canvas manager")
                        for i, page in enumerate(all_pages):
                            if i < len(self.app.page_manager.pages):
                                self.app.page_manager.pages[i] = page
                except Exception as e:
                    print(f"  Error getting pages from canvas manager: {e}")
            
            # Check for drawing history or stroke history
            if hasattr(canvas_manager, 'drawing_history'):
                try:
                    history = canvas_manager.drawing_history
                    if isinstance(history, dict):
                        for page_num, page_history in history.items():
                            if isinstance(page_num, int) and page_num < len(self.app.page_manager.pages):
                                if page_history and len(page_history) > 0:
                                    print(f"  Recovering from drawing history for page {page_num}")
                                    # Convert history to elements format
                                    elements = self._convert_history_to_elements(page_history)
                                    if elements:
                                        self.app.page_manager.pages[page_num]["elements"] = elements
                except Exception as e:
                    print(f"  Error accessing drawing history: {e}")
                    
        except Exception as e:
            print(f"Error in canvas manager recovery: {e}")

    def _try_history_recovery(self):
        """Try to recover from undo/redo history"""
        try:
            print("Trying history recovery...")
            
            # Look for undo/redo managers
            for attr_name in dir(self.app):
                if 'undo' in attr_name.lower() or 'history' in attr_name.lower():
                    history_manager = getattr(self.app, attr_name)
                    if hasattr(history_manager, 'history') or hasattr(history_manager, 'pages'):
                        print(f"  Found potential history in: {attr_name}")
                        try:
                            if hasattr(history_manager, 'get_all_pages'):
                                pages = history_manager.get_all_pages()
                                if pages:
                                    for i, page in enumerate(pages):
                                        if i < len(self.app.page_manager.pages) and page.get("elements"):
                                            print(f"    Recovering from history for page {i}")
                                            self.app.page_manager.pages[i] = page
                        except Exception as e:
                            print(f"    Error accessing history: {e}")
                            
        except Exception as e:
            print(f"Error in history recovery: {e}")

    def _convert_history_to_elements(self, history):
        """Convert drawing history to elements format"""
        try:
            elements = []
            if isinstance(history, list):
                for item in history:
                    if isinstance(item, dict) and item.get("type"):
                        elements.append(item)
            return elements
        except Exception as e:
            print(f"Error converting history to elements: {e}")
            return []

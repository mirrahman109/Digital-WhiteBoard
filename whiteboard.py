import tkinter as tk
from tkinter import colorchooser, filedialog, ttk
from PIL import Image, ImageTk
import json
from collections import deque
import os

class DigitalWhiteboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Whiteboard")
        self.root.geometry("1024x768")

        # Initialize undo/redo stacks
        self.undo_stack = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)

        # Default settings
        self.brush_color = "black"
        self.brush_size = 5
        self.last_x, self.last_y = None, None
        self.current_tool = "brush"  # brush, eraser, rectangle, circle, line
        self.current_page = 0
        self.pages = [{"objects": [], "background": None}]
        self.is_dark_mode = False
        self.grid_visible = False
        self.zoom_level = 1.0

        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create toolbar
        self.create_toolbar()

        # Create canvas
        self.canvas_frame = ttk.Frame(self.main_container)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="white",
            width=800,
            height=600,
            scrollregion=(0, 0, 1600, 1200)
        )
        
        # Add scrollbars
        self.h_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )
        self.v_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
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

        # Bind events
        self.setup_bindings()

        # Load icons
        self.load_icons()

        # Initialize the first page
        self.initialize_page()

    def create_toolbar(self):
        # Tool selection frame
        self.toolbar = ttk.Frame(self.main_container)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)

        # Drawing tools
        self.tools_frame = ttk.LabelFrame(self.toolbar, text="Tools")
        self.tools_frame.pack(side=tk.LEFT, padx=5)

        # Basic tools
        basic_tools = [
            ("Brush", "brush"),
            ("Eraser", "eraser"),
        ]

        for tool_name, tool_value in basic_tools:
            ttk.Button(
                self.tools_frame,
                text=tool_name,
                command=lambda t=tool_value: self.set_tool(t)
            ).pack(side=tk.LEFT, padx=2)
        
        # Shapes dropdown
        shapes_menu = ttk.Menubutton(self.tools_frame, text="Shapes")
        shapes_menu.pack(side=tk.LEFT, padx=2)
        
        dropdown = tk.Menu(shapes_menu, tearoff=0)
        shapes_menu["menu"] = dropdown
        
        shape_tools = [
            ("Rectangle", "rectangle"),
            ("Circle", "circle"),
            ("Line", "line")
        ]
        
        for shape_name, shape_value in shape_tools:
            dropdown.add_command(
                label=shape_name,
                command=lambda t=shape_value: self.set_tool(t)
            )

        # Color and size controls
        self.color_size_frame = ttk.LabelFrame(self.toolbar, text="Color & Size")
        self.color_size_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.color_size_frame,
            text="Color",
            command=self.choose_color
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(self.color_size_frame, text="Size:").pack(side=tk.LEFT)
        self.size_slider = ttk.Scale(
            self.color_size_frame,
            from_=1,
            to=50,
            orient=tk.HORIZONTAL,
            command=self.update_brush_size
        )
        self.size_slider.set(self.brush_size)
        self.size_slider.pack(side=tk.LEFT, padx=5)

        # Page navigation frame
        self.page_frame = ttk.LabelFrame(self.toolbar, text="Pages")
        self.page_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.page_frame,
            text="Previous",
            command=self.previous_page
        ).pack(side=tk.LEFT, padx=2)
        
        self.page_label = ttk.Label(self.page_frame, text="Page 1")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.page_frame,
            text="Next",
            command=self.next_page
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            self.page_frame,
            text="New Page",
            command=self.add_page
        ).pack(side=tk.LEFT, padx=2)

        # View controls frame
        self.view_frame = ttk.LabelFrame(self.toolbar, text="View")
        self.view_frame.pack(side=tk.LEFT, padx=5)

        self.grid_button = ttk.Button(
            self.view_frame,
            text="Grid On",
            command=self.toggle_grid
        )
        self.grid_button.pack(side=tk.LEFT, padx=2)

        self.theme_button = ttk.Button(
            self.view_frame,
            text="Dark",
            command=self.toggle_theme
        )
        self.theme_button.pack(side=tk.LEFT, padx=2)

        # File operations frame
        self.file_frame = ttk.LabelFrame(self.toolbar, text="File")
        self.file_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.file_frame,
            text="Save",
            command=self.save_whiteboard
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            self.file_frame,
            text="Load",
            command=self.load_whiteboard
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            self.file_frame,
            text="Export PNG",
            command=self.export_as_image
        ).pack(side=tk.LEFT, padx=2)

        # Edit operations frame
        self.edit_frame = ttk.LabelFrame(self.toolbar, text="Edit")
        self.edit_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.edit_frame,
            text="Undo",
            command=self.undo
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            self.edit_frame,
            text="Redo",
            command=self.redo
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            self.edit_frame,
            text="Clear",
            command=self.clear_canvas
        ).pack(side=tk.LEFT, padx=2)

    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<MouseWheel>", self.zoom_canvas)
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def load_icons(self):
        """Load tool icons from the Images folder"""
        self.icons = {}
        icon_files = {
            'undo': 'undo.png',
            'redo': 'redo.png',
            'eraser': 'eraser.png',
            'save': 'save.png',
            'add': 'add.png',
            'delete': 'delete.png'
        }
        for name, file in icon_files.items():
            try:
                path = os.path.join('Images', file)
                image = Image.open(path)
                image = image.resize((20, 20), Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Failed to load icon {file}: {e}")

    def initialize_page(self):
        """Initialize or reset the current page"""
        self.canvas.delete("all")
        if self.grid_visible:
            self.draw_grid()
        self.update_page_label()

    def set_tool(self, tool):
        """Change the current drawing tool"""
        self.current_tool = tool
        if tool == "eraser":
            self.canvas.config(cursor="circle")
        else:
            self.canvas.config(cursor="crosshair")

    def start_draw(self, event):
        self.last_x = self.canvas.canvasx(event.x)
        self.last_y = self.canvas.canvasy(event.y)

    def draw(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool in ["brush", "eraser"]:
            color = "white" if self.current_tool == "eraser" else self.brush_color
            line = self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                width=self.brush_size,
                fill=color,
                capstyle=tk.ROUND,
                smooth=True
            )
            self.undo_stack.append({
                "type": "line",
                "id": line,
                "coords": [self.last_x, self.last_y, x, y],
                "color": color,
                "width": self.brush_size
            })
            self.redo_stack.clear()
        
        elif self.current_tool in ["rectangle", "circle", "line"]:
            self.canvas.delete("temp_shape")
            if self.current_tool == "rectangle":
                self.canvas.create_rectangle(
                    self.last_x, self.last_y, x, y,
                    outline=self.brush_color,
                    width=self.brush_size,
                    tags="temp_shape"
                )
            elif self.current_tool == "circle":
                self.canvas.create_oval(
                    self.last_x, self.last_y, x, y,
                    outline=self.brush_color,
                    width=self.brush_size,
                    tags="temp_shape"
                )
            elif self.current_tool == "line":
                self.canvas.create_line(
                    self.last_x, self.last_y, x, y,
                    fill=self.brush_color,
                    width=self.brush_size,
                    tags="temp_shape"
                )
        
        self.last_x = x
        self.last_y = y

    def stop_draw(self, event):
        if self.current_tool in ["rectangle", "circle", "line"]:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            shape = None
            
            if self.current_tool == "rectangle":
                shape = self.canvas.create_rectangle(
                    self.last_x, self.last_y, x, y,
                    outline=self.brush_color,
                    width=self.brush_size
                )
            elif self.current_tool == "circle":
                shape = self.canvas.create_oval(
                    self.last_x, self.last_y, x, y,
                    outline=self.brush_color,
                    width=self.brush_size
                )
            elif self.current_tool == "line":
                shape = self.canvas.create_line(
                    self.last_x, self.last_y, x, y,
                    fill=self.brush_color,
                    width=self.brush_size
                )
            
            if shape:
                self.undo_stack.append({
                    "type": self.current_tool,
                    "id": shape,
                    "coords": [self.last_x, self.last_y, x, y],
                    "color": self.brush_color,
                    "width": self.brush_size
                })
                self.redo_stack.clear()
            
            self.canvas.delete("temp_shape")

    def choose_color(self):
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color

    def update_brush_size(self, size):
        self.brush_size = int(float(size))

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        if self.grid_visible:
            self.draw_grid()
            self.grid_button.config(text="Grid Off")
        else:
            self.canvas.delete("grid")
            self.grid_button.config(text="Grid On")

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

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        bg_color = "#2d2d2d" if self.is_dark_mode else "white"
        self.canvas.configure(bg=bg_color)
        
        # Update button text based on current theme
        if self.is_dark_mode:
            self.theme_button.config(text="Light")
        else:
            self.theme_button.config(text="Dark")
            
        # Update all drawing colors on the canvas
        for item in self.canvas.find_all():
            # Skip grid lines
            if "grid" in self.canvas.gettags(item):
                continue
                
            # Handle fill color for shapes and lines
            fill = self.canvas.itemcget(item, "fill")
            if fill and fill != "":
                # Only convert black fill
                if fill.lower() in ["black", "#000000"]:
                    self.canvas.itemconfig(item, fill="white" if self.is_dark_mode else "black")

            # Handle outline color for shapes
            outline = self.canvas.itemcget(item, "outline")
            if outline and outline != "":
                # Only convert black outline
                if outline.lower() in ["black", "#000000"]:
                    self.canvas.itemconfig(item, outline="white" if self.is_dark_mode else "black")

    def zoom_canvas(self, event):
        if event.state == 4:  # Check if Ctrl key is pressed
            factor = 1.1 if event.delta > 0 else 0.9
            self.zoom_level *= factor
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

    def add_page(self):
        self.pages.append({"objects": [], "background": None})
        self.current_page = len(self.pages) - 1
        self.initialize_page()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.initialize_page()

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.initialize_page()

    def update_page_label(self):
        self.page_label.config(text=f"Page {self.current_page + 1}")

    def clear_canvas(self):
        self.canvas.delete("all")
        if self.grid_visible:
            self.draw_grid()
        self.undo_stack.clear()
        self.redo_stack.clear()

    def save_whiteboard(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wb",
            filetypes=[("Whiteboard files", "*.wb"), ("All files", "*.*")]
        )
        if file_path:
            data = {
                "pages": self.pages,
                "current_page": self.current_page,
                "is_dark_mode": self.is_dark_mode,
                "grid_visible": self.grid_visible
            }
            with open(file_path, "w") as f:
                json.dump(data, f)

    def load_whiteboard(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Whiteboard files", "*.wb"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.pages = data["pages"]
                self.current_page = data["current_page"]
                self.is_dark_mode = data["is_dark_mode"]
                self.grid_visible = data["grid_visible"]
                self.initialize_page()

    def export_as_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            # Create a temporary PostScript file
            ps_path = "temp.ps"
            self.canvas.postscript(file=ps_path)
            
            # Convert PostScript to PNG
            img = Image.open(ps_path)
            img.save(file_path, "png")
            
            # Clean up temporary file
            os.remove(ps_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalWhiteboard(root)
    root.mainloop()
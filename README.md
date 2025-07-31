# Digital WhiteBoard

A feature-rich Python desktop application built with Tkinter that provides an interactive, multi-page whiteboard for drawing, sketching, and note-taking.

## Features

### Drawing Tools
- **Brush Tool**: Free-hand drawing with customizable size and color
- **Eraser Tool**: Remove drawings while preserving grid lines
- **Shape Tools**: Rectangle, Circle, and Line drawing
- **Color Picker**: Choose from any color for your drawings
- **Brush Size Control**: Adjustable brush size from 1 to 20 pixels

### Canvas Features
- **Multi-page Support**: Create, navigate, and manage multiple whiteboard pages
- **Zoom Functionality**: Zoom in/out using Ctrl + Mouse Wheel
- **Scrollable Canvas**: Large drawing area with horizontal and vertical scrollbars
- **Grid Toggle**: Show/hide grid lines for precise drawing
- **Dark/Light Mode**: Switch between light and dark themes

### File Operations
- **Save Project**: Save your whiteboard pages as project files
- **Load Project**: Load previously saved whiteboard projects
- **Export Pages**: Export individual pages as image files (PNG, JPG, etc.)

### User Interface
- **Intuitive Toolbar**: Easy access to all tools and functions
- **Undo/Redo**: Full undo/redo support with 50-level history
- **Tooltips**: Helpful tooltips for all toolbar buttons
- **Responsive Design**: Adapts to different screen sizes

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)
- Pillow (PIL) library for image handling

## Installation

1. **Clone or download the repository**:
   ```bash
   git clone <repository-url>
   cd Digital-WhiteBoard
   ```

2. **Install required dependencies**:
   ```bash
   pip install Pillow
   ```

3. **Run the application**:
   ```bash
   python whiteboard.py
   ```

## Building Executable

To create a standalone executable file:

1. **Run the build script**:
   ```bash
   python build_exe.py
   ```

2. **Find the executable**:
   - The executable will be created in the `dist` folder
   - Named `Digital-Whiteboard.exe` on Windows

### Build Requirements
- PyInstaller (automatically installed by build script)
- All project dependencies

## Usage

### Basic Drawing
1. Select the **Brush** tool from the toolbar
2. Choose your desired color using the **Color** button
3. Adjust brush size with the size slider
4. Click and drag on the canvas to draw

### Shape Drawing
1. Select **Rectangle**, **Circle**, or **Line** tool
2. Click and drag to create the shape
3. Release to finalize the shape

### Page Management
- **New Page**: Click the "+" button to create a new page
- **Navigate**: Use left/right arrows to switch between pages
- **Page Counter**: Shows current page number and total pages

### File Operations
- **Save**: Ctrl+S or click Save button to save your project
- **Load**: Click Load button to open saved projects
- **Export**: Export current page as an image file

### Keyboard Shortcuts
- `Ctrl + Z`: Undo last action
- `Ctrl + Y`: Redo last undone action
- `Ctrl + Mouse Wheel`: Zoom in/out

## Project Structure

```
Digital-WhiteBoard/
├── whiteboard.py              # Main application entry point
├── build_exe.py              # Script to build executable
├── README.md                 # This file
├── Images/                   # Icon files for toolbar
│   ├── pencil.png
│   ├── eraser.png
│   ├── undo.png
│   └── ...
└── modules/                  # Application modules
    ├── whiteboard_app.py     # Main application class
    ├── canvas_manager.py     # Canvas and drawing functionality
    ├── toolbar_manager.py    # Toolbar creation and management
    ├── page_manager.py       # Multi-page functionality
    ├── file_manager.py       # File save/load operations
    └── tooltip.py            # Tooltip functionality
```

## Icon Requirements

The application requires icon files in the `Images/` directory:
- `pencil.png` - Brush tool
- `eraser.png` - Eraser tool
- `undo.png` - Undo action
- `redo.png` - Redo action
- `clear.png` - Clear canvas
- `paint-brush.png` - Color picker
- `left.png` - Previous page
- `right.png` - Next page
- `new page.png` - New page
- `grid-on.png` - Grid toggle
- `day-mode.png` - Theme toggle
- `save.png` - Save project
- `export.png` - Export page
- `open-folder.png` - Load project

## Troubleshooting

### Common Issues

1. **"PIL/Pillow is required" error**:
   ```bash
   pip install Pillow
   ```

2. **Icons not loading**:
   - Ensure all icon files are in the `Images/` directory
   - Check that icon filenames match exactly (case-sensitive)

3. **Build script fails**:
   - Install PyInstaller manually: `pip install pyinstaller`
   - Ensure all dependencies are installed

### Performance Tips
- Large drawings may affect performance - use Clear Canvas to reset
- Zoom out for better performance with complex drawings
- Regular saving is recommended for large projects

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source. Please check the license file for more details.

## Version History

- **v1.0**: Initial release with basic drawing tools
- **v1.1**: Added multi-page support
- **v1.2**: Added file save/load functionality
- **v1.3**: Added dark mode and grid toggle
- **v1.4**: Added export functionality and improved UI

## Support

For support, please open an issue in the project repository or contact the development team.

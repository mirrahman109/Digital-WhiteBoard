import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Images", "whiteboard_icon.ico")
    main_script = os.path.join(current_dir, "whiteboard.py")
    
    print("=== Digital Whiteboard Executable Builder ===")
    print(f"Building from: {current_dir}")
    
    # Check if main script exists
    if not os.path.exists(main_script):
        print(f"ERROR: Main script not found at {main_script}")
        return False
    
    # Check if Images directory exists
    images_dir = os.path.join(current_dir, "Images")
    if not os.path.exists(images_dir):
        print(f"ERROR: Images directory not found at {images_dir}")
        return False
    
    # List all icon files that should be included
    required_icons = [
        'pencil.png', 'eraser.png', 'shapes.png', 'square.png', 'circle.png', 'line.png',
        'undo.png', 'redo.png', 'clear.png', 'paint-brush.png', 'left.png', 'right.png',
        'new page.png', 'grid-on.png', 'day-mode.png', 'save.png', 'export.png', 'open-folder.png'
    ]
    
    print("\nChecking for required icon files:")
    missing_icons = []
    for icon in required_icons:
        icon_path_check = os.path.join(images_dir, icon)
        if os.path.exists(icon_path_check):
            print(f"  ✓ {icon}")
        else:
            print(f"  ✗ {icon} (MISSING)")
            missing_icons.append(icon)
    
    if missing_icons:
        print(f"\nWARNING: {len(missing_icons)} icon files are missing. The app will still work but some buttons may not have icons.")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"\nPyInstaller is already installed (version: {PyInstaller.__version__})")
    except ImportError:
        print("\nInstalling PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install PyInstaller: {e}")
            return False
    
    print("\nBuilding executable...")
    
    # Create a comprehensive build command
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # No console window (GUI app)
        "--name=Digital-Whiteboard",    # Name of the executable
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Working directory
        "--specpath=.",                 # Spec file location
        f"--add-data={images_dir};Images",  # Include entire Images folder
        "--hidden-import=PIL",          # Ensure PIL is included
        "--hidden-import=PIL.Image",    # Ensure PIL.Image is included
        "--hidden-import=PIL.ImageTk",  # Ensure PIL.ImageTk is included
        "--hidden-import=PIL.ImageGrab", # Ensure PIL.ImageGrab is included
        "--collect-all=PIL",            # Collect all PIL components
        main_script
    ]
    
    # Add icon if it exists
    if os.path.exists(os.path.join(current_dir, "Images", "whiteboard_icon.ico")):
        cmd.insert(-1, f"--icon={os.path.join(current_dir, 'Images', 'whiteboard_icon.ico')}")
        print(f"Using icon: whiteboard_icon.ico")
    else:
        print("Warning: whiteboard_icon.ico not found, building without custom icon")
    
    try:
        print("Running PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Executable built successfully!")
            
            # Check if the executable was created
            exe_path = os.path.join(current_dir, "dist", "Digital-Whiteboard.exe")
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
                print(f"✓ Executable created: {exe_path}")
                print(f"✓ File size: {file_size:.1f} MB")
                
                # Create a README for distribution
                create_distribution_readme(current_dir)
                
                print("\n=== Build Summary ===")
                print(f"Executable location: {exe_path}")
                print("The executable includes:")
                print("  • All Python dependencies")
                print("  • All icon files from Images folder")
                print("  • Complete whiteboard functionality")
                print("  • No external dependencies required")
                print("\nYou can now share this executable file!")
                
                return True
            else:
                print("ERROR: Executable was not created in expected location")
                return False
        else:
            print(f"ERROR: PyInstaller failed with return code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to build executable: {e}")
        return False
    except FileNotFoundError:
        print("ERROR: PyInstaller not found. Please install it manually with: pip install pyinstaller")
        return False

def create_distribution_readme(base_dir):
    """Create a README file for distribution"""
    readme_content = """# Digital Whiteboard - Standalone Executable

## About
This is a portable version of Digital Whiteboard - a feature-rich drawing and sketching application.

## Features
- Free-hand drawing with customizable brush size and colors
- Shape tools (Rectangle, Circle, Line)
- Multi-page support
- Undo/Redo functionality
- Grid overlay option
- Dark/Light theme toggle
- Save/Load projects
- Export pages as images
- Zoom functionality

## How to Use
1. Simply run `Digital-Whiteboard.exe`
2. No installation required - this is a portable application
3. All features work out of the box

## System Requirements
- Windows 7/8/10/11 (64-bit)
- No additional software required

## Controls
- **Drawing**: Select brush tool and click/drag to draw
- **Shapes**: Click the shapes button and select Rectangle, Circle, or Line
- **Undo/Redo**: Ctrl+Z / Ctrl+Y or use toolbar buttons
- **Zoom**: Ctrl + Mouse Wheel
- **Save**: Click Save button to save your project
- **Export**: Click Export button to save as image

## Troubleshooting
- If the app doesn't start, make sure you have Windows Defender or antivirus whitelist the executable
- The app creates temporary files in your system's temp directory
- Project files are saved with .wb extension

## Version
Built with Python and packaged as a standalone executable.
No Python installation required to run this application.

## License
Open source project. See GitHub repository for source code and license details.
"""
    
    readme_path = os.path.join(base_dir, "dist", "README.txt")
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✓ Distribution README created: {readme_path}")
    except Exception as e:
        print(f"Warning: Could not create README: {e}")

def create_github_release_info(base_dir):
    """Create information for GitHub release"""
    release_info = """# GitHub Release Information

## Files to include in GitHub release:
1. `Digital-Whiteboard.exe` - The main executable
2. `README.txt` - User instructions
3. Source code (automatically included by GitHub)

## Release Notes Template:
```
## Digital Whiteboard v1.0 - Standalone Executable

### Features
- Complete whiteboard application with drawing tools
- Multi-page support with navigation
- Shape tools (Rectangle, Circle, Line)
- Undo/Redo functionality
- Grid overlay and dark mode
- Save/Load projects and export as images
- Zoom functionality

### Download
- Download `Digital-Whiteboard.exe` for Windows
- No installation required - just run the executable
- All icons and features included

### System Requirements
- Windows 7/8/10/11 (64-bit)
- No additional dependencies

### File Size
- Approximately 25-35 MB (includes Python runtime and all dependencies)
```

## Upload Instructions:
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: v1.0
4. Upload the Digital-Whiteboard.exe file
5. Upload the README.txt file
6. Use the release notes template above
"""
    
    info_path = os.path.join(base_dir, "dist", "GitHub-Release-Info.txt")
    try:
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(release_info)
        print(f"✓ GitHub release info created: {info_path}")
    except Exception as e:
        print(f"Warning: Could not create GitHub info: {e}")

if __name__ == "__main__":
    print("Digital Whiteboard - Executable Builder")
    print("=======================================")
    
    success = build_executable()
    
    if success:
        # Create additional files for distribution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        create_github_release_info(current_dir)
        
        print("\n🎉 BUILD SUCCESSFUL! 🎉")
        print("\nNext steps:")
        print("1. Test the executable in the 'dist' folder")
        print("2. Check GitHub-Release-Info.txt for upload instructions")
        print("3. Create a release on GitHub and upload the .exe file")
        print("\nYour friends can now download and run the executable without installing Python!")
    else:
        print("\n❌ BUILD FAILED")
        print("Please check the error messages above and try again.")
    
    print("\nPress Enter to exit...")
    input()

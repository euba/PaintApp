# Paint App - Advanced Kivy Drawing Application

> **Note**: This repository was entirely created by AI using a test project by Kivy as a starting point. The AI developed all features, architecture, documentation, and code from the initial concept to the current advanced state.

A powerful and feature-rich painting application built with Kivy, featuring multiple drawing tools, export capabilities, and a clean modular architecture designed for easy maintenance and extensibility.

## 🎨 Features

### Drawing Tools
- **Freehand Drawing**: Natural brush-style drawing with touch/mouse support
- **Geometric Shapes**: Rectangle, Triangle, Circle, and Straight Line tools
- **Text Tool**: Add text with customizable font sizes based on line width
- **Multiple Brush Sizes**: Thin (3px), Normal (6px), Thick (12px)
- **Line Styles**: Solid and Dashed line support for all drawing modes

### User Interface
- **Color Palette**: 12 predefined colors with intuitive selection
- **Tool Selection**: Easy switching between drawing modes
- **Clear Canvas**: One-click canvas clearing with undo support
- **Responsive Design**: Automatic scaling and layout adjustment

### Advanced Features
- **Undo/Redo System**: Full undo/redo support for all drawing operations (50-level history)
- **High-Quality Export**: PNG export with 2x scaling and anti-aliasing
- **Smart Edge Rendering**: Dashed rectangles and triangles export with sharp edges, other shapes maintain smooth curves
- **Canvas Scaling**: Automatic drawing scaling when window is resized
- **Touch Optimization**: Optimized for both mouse and touch input

### Export Options
- **PNG Export**: High-resolution export with white background
- **Quality Scaling**: 2x resolution export for crisp output
- **Edge Control**: Smart edge rendering based on shape type and line style
- **Multiple Export Methods**: Standard export, simple export, and screenshot capture

## 📁 Project Structure

```
PaintApp/
├── src/
│   ├── main.py                     # Application entry point
│   └── paintapp/                   # Main package
│       ├── __init__.py            # Package initialization
│       ├── core/                  # Core application logic
│       │   ├── __init__.py
│       │   ├── app.py            # Main application class
│       │   ├── canvas.py         # Drawing canvas implementation
│       │   └── config.py         # Application configuration
│       ├── widgets/               # Custom UI widgets
│       │   ├── __init__.py
│       │   ├── buttons.py        # Custom button implementations
│       │   └── toolbar.py        # Toolbar widget
│       ├── ui/                    # UI layout management
│       │   ├── __init__.py
│       │   └── layout.py         # Main layout manager
│       ├── utils/                 # Utility functions and constants
│       │   ├── __init__.py
│       │   ├── constants.py      # Drawing modes, colors, and size constants
│       │   └── helpers.py        # Helper functions
│       └── assets/                # Application assets
│           └── kv/
│               └── paint.kv      # Kivy styling file
├── pyproject.toml                 # Project configuration
├── Makefile                       # Build automation
├── .flake8                        # Linting configuration
├── test_main.py                   # Comprehensive test suite
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Xcode Command Line Tools** (macOS only)
- **PIL/Pillow** (automatically installed for export functionality)

### Installation & Running

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd PaintApp
   ```

2. **Install dependencies:**
   ```bash
   make install
   ```

3. **Run the application:**
   ```bash
   make run
   ```

## 🎯 How to Use

### Drawing Modes

1. **Line Mode** (Default): Freehand drawing with natural brush strokes
2. **Rectangle Mode**: Click and drag to create rectangles
3. **Triangle Mode**: Click and drag to create triangles
4. **Circle Mode**: Click and drag to create circles from center point
5. **Straight Line Mode**: Click and drag to create straight lines
6. **Text Mode**: Click to place text input, type text, and press Enter to confirm

### Line Styles

- **Solid Lines**: Standard continuous lines (default)
- **Dashed Lines**: Dotted/dashed pattern for all drawing modes
- **Smart Export**: Dashed rectangles and triangles export with sharp corners, other shapes maintain smooth curves

### Controls

- **Color Selection**: Click any color button to change drawing color
- **Line Width**: Choose from Thin, Normal, or Thick brush sizes
- **Line Style**: Toggle between Solid and Dashed line styles
- **Drawing Mode**: Select your preferred drawing tool
- **Clear**: Clear the entire canvas (with undo support)
- **Undo/Redo**: Use keyboard shortcuts or menu options
- **Export**: Save your artwork as high-quality PNG

### Keyboard Shortcuts

- **Cmd+Z** (macOS) / **Ctrl+Z** (Windows/Linux): Undo
- **Cmd+Shift+Z** (macOS) / **Ctrl+Y** (Windows/Linux): Redo
- **Cmd+E** (macOS) / **Ctrl+E** (Windows/Linux): Export to PNG

## 🛠️ Development

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install runtime dependencies |
| `make install-dev` | Install development dependencies |
| `make install-build` | Install build dependencies |
| `make run` | Run the application |
| `make test` | Run the comprehensive test suite |
| `make lint` | Run code linting |
| `make format` | Format code with Black |
| `make build` | Build macOS app with PyInstaller |
| `make clean` | Clean build artifacts |

### Development Workflow

```bash
# Set up development environment
make install-dev

# Make your changes...

# Format and lint code
make format
make lint

# Run tests
make test

# Build the application
make build
```

## 🏗️ Architecture Overview

### Core Components

- **`paintapp.core.app.PaintApp`**: Main application class handling lifecycle and menu integration
- **`paintapp.core.canvas.MyCanvas`**: Advanced drawing canvas with multi-mode support, undo/redo, and export
- **`paintapp.core.config.AppConfig`**: Application configuration management

### UI Components

- **`paintapp.ui.layout.MainLayout`**: Responsive main layout organizing canvas and toolbar
- **`paintapp.widgets.toolbar.Toolbar`**: Comprehensive toolbar with all drawing controls
- **`paintapp.widgets.buttons`**: Custom button implementations for colors, tools, and modes

### Utilities

- **`paintapp.utils.constants`**: Drawing modes, line styles, color palettes, and line width definitions
- **`paintapp.utils.helpers`**: Resource path management and utility functions

### Key Design Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Dependency Injection**: Components receive dependencies rather than creating them
3. **Configuration Management**: Centralized configuration in `AppConfig`
4. **Resource Management**: Robust path handling for assets
5. **Extensibility**: Easy to add new tools, colors, or features
6. **State Management**: Comprehensive undo/redo system with clean state handling
7. **Export Quality**: High-resolution export with smart edge rendering

## 🧪 Testing

The project includes a comprehensive test suite covering:

- Module imports and structure
- Core functionality and drawing operations
- Widget behavior and interactions
- Configuration management
- Constants and utilities
- Canvas scaling and responsiveness
- Drawing modes and line styles
- Export functionality and edge rendering
- Undo/redo system

Run tests with:
```bash
make test
```

### Test Coverage

- ✅ **20 test cases** covering all major functionality
- ✅ **Drawing operations** for all modes and styles
- ✅ **Canvas scaling** and window resizing
- ✅ **Export quality** and edge rendering
- ✅ **Configuration** and constants validation
- ✅ **Widget behavior** and UI interactions

## 📦 Building

### PyInstaller Build (Recommended)

Creates a standalone macOS application:

```bash
make build
```

Output: `dist/PaintApp.app`

### Features of Built App

- ✅ **Standalone**: No Python installation required
- ✅ **Double-click launch**: Works from Finder
- ✅ **Resource bundling**: All assets included
- ✅ **Native performance**: Optimized for macOS
- ✅ **Full feature set**: All drawing tools and export functionality

## 🔧 Configuration

### Application Settings

Modify `src/paintapp/core/config.py` to customize:

- Default window size and behavior
- Default colors and line widths
- Default drawing mode and line style
- Input settings and touch behavior
- Export settings and quality

### Adding New Drawing Modes

1. Add mode constants to `src/paintapp/utils/constants.py`
2. Implement drawing logic in `src/paintapp/core/canvas.py`
3. Add UI controls in `src/paintapp/widgets/toolbar.py`
4. Update export handling for the new mode

### Adding New Colors

1. Add color constants to `src/paintapp/utils/constants.py`
2. Update the `get_palette()` method
3. Colors automatically appear in the toolbar

### Adding New Line Widths

1. Add width constants to `src/paintapp/utils/constants.py`
2. Update the `get_width_map()` method
3. Widths automatically appear in the toolbar

## 🎨 Advanced Features

### Dashed Line System

The application features a sophisticated dashed line system:

- **Continuous Path Dashing**: Maintains consistent dash patterns along curved paths
- **Shape-Specific Rendering**: Different algorithms for rectangles, circles, and freehand lines
- **Export Optimization**: Smart edge rendering for different shape types

### Export System

Multiple export methods for different use cases:

1. **High-Quality Export** (`export_to_png`): 2x resolution with anti-aliasing
2. **Simple Export** (`export_to_png_simple`): Basic Kivy widget export
3. **Screenshot Export** (`export_canvas_screenshot`): Direct framebuffer capture

### Undo/Redo System

Comprehensive state management:

- **50-level history**: Deep undo stack for complex drawings
- **Clean state copies**: Efficient memory usage without Kivy object references
- **Operation grouping**: Logical grouping of related drawing operations
- **Canvas redrawing**: Full canvas reconstruction from history

## 🐛 Troubleshooting

### Common Issues

**App won't launch from Finder:**
- Ensure you built with `make build` (not `make build-app`)
- Check Console.app for error messages

**Missing dependencies:**
- Run `make install` to ensure all dependencies are installed
- For build issues, try `make install-build`

**Import errors:**
- Ensure you're running from the project root
- Check that the `src/` directory structure is intact

**Export failures:**
- Ensure PIL/Pillow is installed: `uv add pillow`
- Check write permissions for export directory
- Try different export methods if one fails

**Performance issues:**
- Reduce canvas size for better performance
- Clear canvas periodically for long drawing sessions
- Use simpler shapes for complex drawings

### Debug Mode

Run with verbose logging:
```bash
KIVY_LOG_LEVEL=debug make run
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow the development workflow** (format, lint, test)
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Code Style

- **Python**: Follow PEP 8, enforced by Black and Flake8
- **Line length**: 88 characters (Black default)
- **Documentation**: Docstrings for all public methods
- **Type hints**: Encouraged for new code
- **Testing**: Add tests for new features

### Recent Contributions

- ✅ **Drawing Modes**: Rectangle, Triangle, Circle, Straight Line, and Text tools
- ✅ **Line Styles**: Solid and Dashed line support
- ✅ **Export System**: High-quality PNG export with smart edge rendering
- ✅ **Undo/Redo**: Comprehensive state management system
- ✅ **Canvas Scaling**: Automatic scaling when window is resized
- ✅ **Edge Rendering**: Sharp edges for dashed rectangles and triangles

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Kivy Team** for the excellent GUI framework
- **PyInstaller** for application packaging
- **uv** for fast Python package management
- **PIL/Pillow** for high-quality image export
- **Contributors** who have added features and improvements

---

**Happy Painting!** 🎨

*Create beautiful artwork with professional-grade drawing tools and export your masterpieces in high quality.*

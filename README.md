# Paint App - Modular Kivy Drawing Application

A simple yet powerful painting application built with Kivy, featuring a clean modular architecture designed for easy maintenance and extensibility.

## 🎨 Features

- **Drawing Tools**: Multiple brush sizes (Thin, Normal, Thick, Extra Thick)
- **Color Palette**: 12 predefined colors with easy selection
- **Clear Canvas**: One-click canvas clearing
- **Touch Support**: Full touch and mouse drawing support
- **Cross-Platform**: Runs on macOS, Windows, and Linux
- **Modular Architecture**: Clean, extensible codebase

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
│       │   ├── constants.py      # Color and size constants
│       │   └── helpers.py        # Helper functions
│       └── assets/                # Application assets
│           └── kv/
│               └── paint.kv      # Kivy styling file
├── pyproject.toml                 # Project configuration
├── Makefile                       # Build automation
├── .flake8                        # Linting configuration
├── test_main.py                   # Test suite
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Xcode Command Line Tools** (macOS only)

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

## 🛠️ Development

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install runtime dependencies |
| `make install-dev` | Install development dependencies |
| `make install-build` | Install build dependencies |
| `make run` | Run the application |
| `make test` | Run the test suite |
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

- **`paintapp.core.app.PaintApp`**: Main application class handling lifecycle
- **`paintapp.core.canvas.MyCanvas`**: Drawing canvas with touch event handling
- **`paintapp.core.config.AppConfig`**: Application configuration management

### UI Components

- **`paintapp.ui.layout.MainLayout`**: Main layout organizing canvas and toolbar
- **`paintapp.widgets.toolbar.Toolbar`**: Toolbar containing tools and controls
- **`paintapp.widgets.buttons`**: Custom button implementations

### Utilities

- **`paintapp.utils.constants`**: Color palettes and line width definitions
- **`paintapp.utils.helpers`**: Resource path management and utilities

### Key Design Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Dependency Injection**: Components receive dependencies rather than creating them
3. **Configuration Management**: Centralized configuration in `AppConfig`
4. **Resource Management**: Robust path handling for assets
5. **Extensibility**: Easy to add new tools, colors, or features

## 🧪 Testing

The project includes a comprehensive test suite covering:

- Module imports and structure
- Core functionality
- Widget behavior
- Configuration management
- Constants and utilities

Run tests with:
```bash
make test
```

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

## 🔧 Configuration

### Application Settings

Modify `src/paintapp/core/config.py` to customize:

- Default window size
- Default colors and line widths
- Window behavior
- Input settings

### Adding New Colors

1. Add color constants to `src/paintapp/utils/constants.py`
2. Update the `get_palette()` method
3. Colors automatically appear in the toolbar

### Adding New Line Widths

1. Add width constants to `src/paintapp/utils/constants.py`
2. Update the `get_width_map()` method
3. Widths automatically appear in the toolbar

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Kivy Team** for the excellent GUI framework
- **PyInstaller** for application packaging
- **uv** for fast Python package management

---

**Happy Painting!** 🎨

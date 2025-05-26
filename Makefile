# Paint App Makefile for macOS
# Requires uv package manager

.PHONY: help install install-dev clean build build-app build-dmg run test lint format check-deps create-icon

# Default target
help:
	@echo "Paint App - macOS Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install dependencies using uv"
	@echo "  install-dev  - Install development dependencies"
	@echo "  install-build- Install build dependencies"
	@echo "  clean        - Clean build artifacts"
	@echo "  run          - Run the application"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code with black"
	@echo "  build        - Build the application with PyInstaller"
	@echo "  build-app    - Build macOS .app bundle with py2app"
	@echo "  build-dmg    - Create DMG installer (ready for distribution)"
	@echo "  create-icon  - Create app icon (app_icon.icns)"
	@echo "  check-deps   - Check if required system dependencies are installed"

# Variables
APP_NAME = PaintApp
PYTHON_VERSION = 3.11
VENV_NAME = .venv
DIST_DIR = dist
BUILD_DIR = build

# Check if uv is installed
check-uv:
	@which uv > /dev/null || (echo "Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh" && exit 1)

# Check system dependencies
check-deps: check-uv
	@echo "Checking system dependencies..."
	@which python3 > /dev/null || (echo "Error: Python 3 is not installed" && exit 1)
	@python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" || (echo "Error: Python 3.9+ is required" && exit 1)
	@echo "✓ All system dependencies are available"

# Install main dependencies
install: check-deps
	@echo "Installing dependencies with uv..."
	uv sync
	@echo "✓ Dependencies installed"

# Install development dependencies
install-dev: install
	@echo "Installing development dependencies..."
	uv sync --extra dev
	@echo "✓ Development dependencies installed"

# Install build dependencies
install-build: install
	@echo "Installing build dependencies..."
	uv sync --extra build
	@echo "✓ Build dependencies installed"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf *.egg-info
	rm -rf __pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".DS_Store" -delete
	@echo "✓ Build artifacts cleaned"

# Run the application
run: install
	@echo "Running Paint App..."
	uv run python src/main.py

# Run tests
test: install-dev
	@echo "Running tests..."
	uv run pytest

# Run linting
lint: install-dev
	@echo "Running linting..."
	uv run flake8 src/

# Format code
format: install-dev
	@echo "Formatting code..."
	uv run black src/

# Create app icon
create-icon: install
	@echo "Creating app icon..."
	uv run python create_icon.py
	@echo "✓ App icon created"

# Build with PyInstaller (creates executable)
build: install-build clean
	@echo "Building application with PyInstaller..."
	uv run pyinstaller \
		--name "$(APP_NAME)" \
		--windowed \
		--onedir \
		--add-data "src/paintapp/assets/kv/paint.kv:paintapp/assets/kv" \
		--icon app_icon.icns \
		--osx-bundle-identifier "com.aniketthani.paintapp" \
		src/main.py
	@echo "✓ PyInstaller build complete. Check $(DIST_DIR)/$(APP_NAME)/"

# Create setup.py for py2app
setup-py2app:
	@echo "Creating setup.py for py2app..."
	@cp setup_template.py setup.py

# Build macOS .app bundle with py2app
build-app: install-build clean setup-py2app
	@echo "Building macOS .app bundle with py2app..."
	uv run python setup.py py2app
	@echo "✓ macOS .app bundle created in $(DIST_DIR)/"

# Create DMG installer using our simple build script
build-dmg: install-build
	@echo "Creating DMG installer..."
	python3 build_simple_dmg.py

# Full build pipeline
all: clean install-build create-icon build-app build-dmg
	@echo "✓ Complete build pipeline finished"
	@echo "📦 Outputs:"
	@echo "   - macOS App: $(DIST_DIR)/PaintApp.app"
	@echo "   - DMG Installer: $(DIST_DIR)/PaintApp.dmg"

# Development workflow
dev: install-dev format lint test
	@echo "✓ Development workflow complete" 
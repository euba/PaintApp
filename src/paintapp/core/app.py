"""
Main application module for PaintApp.

Contains the main Kivy application class and application lifecycle management.
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window

from ..ui.layout import MainLayout
from ..utils.helpers import get_kv_file_path
from .config import AppConfig


class PaintApp(App):
    """
    Main Paint Application class.

    This is the entry point for the Kivy application, handling
    initialization, configuration, and the main application lifecycle.
    """

    def __init__(self, **kwargs):
        """Initialize the Paint App."""
        super().__init__(**kwargs)

        # Application state
        self.main_layout = None

        # Load KV file if it exists
        self._load_kv_file()

    def _load_kv_file(self):
        """Load the KV file for UI styling if it exists."""
        try:
            kv_path = get_kv_file_path("paint.kv")
            Builder.load_file(kv_path)
        except FileNotFoundError:
            # KV file is optional - the app can work without it
            print("KV file not found, using programmatic UI")
        except Exception as e:
            print(f"Error loading KV file: {e}")

    def build(self):
        """
        Build and return the root widget.

        This method is called by Kivy to create the main application interface.

        Returns:
            Widget: The root widget of the application
        """
        # Set up application configuration
        AppConfig.setup_window()

        # Create the main layout
        self.main_layout = MainLayout()

        # Set the application title
        self.title = "Paint App"

        return self.main_layout

    def on_start(self):
        """Called when the application starts."""
        super().on_start()

        # Bind keyboard events
        Window.bind(on_key_down=self._on_keyboard_down)

        print("Paint App started successfully!")

    def on_stop(self):
        """Called when the application is about to stop."""
        super().on_stop()

        # Unbind keyboard events
        Window.unbind(on_key_down=self._on_keyboard_down)

        print("Paint App stopping...")

    def _on_keyboard_down(self, window, keycode, text, modifiers, *args, **kwargs):
        """
        Handle keyboard events for shortcuts.

        Args:
            window: The window instance
            keycode: The key code (scancode, key)
            text: The text representation of the key
            modifiers: List of modifier keys pressed
            *args: Additional positional arguments from Kivy
            **kwargs: Additional keyword arguments from Kivy

        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Get the key name - handle both tuple and integer formats
        if isinstance(keycode, (list, tuple)) and len(keycode) > 1:
            key = keycode[1]  # Use the string representation
        elif isinstance(keycode, (list, tuple)) and len(keycode) == 1:
            key = keycode[0]
        else:
            key = keycode  # keycode is already the key value

        # Check for CMD+Z (undo) on macOS or Ctrl+Z on other platforms
        if key == "z" and ("cmd" in modifiers or "ctrl" in modifiers):
            if "shift" in modifiers:
                # CMD+Shift+Z or Ctrl+Shift+Z (redo)
                self._handle_redo()
            else:
                # CMD+Z or Ctrl+Z (undo)
                self._handle_undo()
            return True

        # Check for CMD+Y (redo alternative) on Windows/Linux
        elif key == "y" and ("cmd" in modifiers or "ctrl" in modifiers):
            self._handle_redo()
            return True

        # Check for CMD+N or Ctrl+N (clear/new)
        elif key == "n" and ("cmd" in modifiers or "ctrl" in modifiers):
            self._handle_clear()
            return True

        # Check for CMD+S or Ctrl+S (export/save)
        elif key == "s" and ("cmd" in modifiers or "ctrl" in modifiers):
            self._handle_export()
            return True

        return False

    def _handle_undo(self):
        """Handle undo keyboard shortcut."""
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, "undo"):
            success = canvas.undo()
            if success:
                print("Undo performed")
            else:
                print("Nothing to undo")

    def _handle_redo(self):
        """Handle redo keyboard shortcut."""
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, "redo"):
            success = canvas.redo()
            if success:
                print("Redo performed")
            else:
                print("Nothing to redo")

    def _handle_clear(self):
        """Handle clear/new keyboard shortcut."""
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, "clear_screen"):
            canvas.clear_screen()
            print("Canvas cleared")

    def _handle_export(self):
        """Handle export/save keyboard shortcut."""
        toolbar = self.get_toolbar()
        if toolbar and hasattr(toolbar, "_show_export_dialog"):
            toolbar._show_export_dialog()
            print("Export dialog opened")

    def get_canvas(self):
        """
        Get the drawing canvas.

        Returns:
            MyCanvas: The drawing canvas widget or None if not available
        """
        return self.main_layout.get_canvas() if self.main_layout else None

    def get_toolbar(self):
        """
        Get the toolbar.

        Returns:
            Toolbar: The toolbar widget or None if not available
        """
        return self.main_layout.get_toolbar() if self.main_layout else None

    def clear_canvas(self):
        """Clear the drawing canvas."""
        if self.main_layout:
            self.main_layout.clear_canvas()

    def has_unsaved_changes(self):
        """
        Check if there are unsaved changes.

        Returns:
            bool: True if there are drawings that haven't been saved
        """
        return self.main_layout.has_drawings() if self.main_layout else False

    def get_app_info(self):
        """
        Get application information.

        Returns:
            dict: Dictionary containing app information
        """
        from .. import __version__, __author__

        return {
            "name": "Paint App",
            "version": __version__,
            "author": __author__,
            "description": "A simple painting application built with Kivy",
        }

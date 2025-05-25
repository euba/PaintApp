"""
Main application module for PaintApp.

Contains the main Kivy application class and application lifecycle management.
"""

from kivy.app import App
from kivy.lang import Builder

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
        print("Paint App started successfully!")

    def on_stop(self):
        """Called when the application is about to stop."""
        super().on_stop()
        print("Paint App stopping...")

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

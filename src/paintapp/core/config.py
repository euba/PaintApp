"""
Configuration module for PaintApp.

Handles application configuration, window settings, and user preferences.
"""

from kivy.config import Config
from kivy.core.window import Window


class AppConfig:
    """Application configuration manager."""

    # Default window settings
    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 800
    DEFAULT_BACKGROUND_COLOR = (1, 1, 1, 1)  # White

    # Default drawing settings
    DEFAULT_LINE_WIDTH = 6  # "Normal" width (updated to new thicker value)
    DEFAULT_COLOR = (0, 0, 0, 1)  # Black
    DEFAULT_LINE_STYLE = "solid"  # Default to solid lines

    @classmethod
    def setup_window(cls, width=None, height=None, resizable=True):
        """Configure the application window."""
        width = width or cls.DEFAULT_WIDTH
        height = height or cls.DEFAULT_HEIGHT

        Config.set("graphics", "width", str(width))
        Config.set("graphics", "height", str(height))

        if resizable:
            Config.set("graphics", "resizable", "1")
        else:
            Config.set("graphics", "resizable", "0")

        # Disable multitouch emulation with right-click
        Config.set("input", "mouse", "mouse,disable_multitouch")

        # Set background color
        Window.clearcolor = cls.DEFAULT_BACKGROUND_COLOR

    @classmethod
    def get_default_line_width(cls):
        """Get the default line width."""
        return cls.DEFAULT_LINE_WIDTH

    @classmethod
    def get_default_color(cls):
        """Get the default drawing color."""
        return cls.DEFAULT_COLOR

    @classmethod
    def get_default_line_style(cls):
        """Get the default line style."""
        return cls.DEFAULT_LINE_STYLE

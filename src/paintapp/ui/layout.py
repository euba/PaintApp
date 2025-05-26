"""
Layout module for PaintApp.

Contains the main layout manager that organizes the canvas and toolbar.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from ..core.canvas import MyCanvas
from ..widgets.toolbar import Toolbar


class MainLayout(BoxLayout):
    """
    Main layout widget that organizes the application interface.

    This layout contains the drawing canvas and the toolbar,
    arranged in a vertical layout with the toolbar at the bottom.
    """

    def __init__(self, **kwargs):
        """Initialize the main layout."""
        super().__init__(**kwargs)

        # Set up the layout orientation
        self.orientation = "vertical"

        # Create the main components
        self._setup_layout()

        # Bind keyboard events
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _setup_layout(self):
        """Set up the main layout with canvas and toolbar."""
        # Create the drawing canvas with proper scaling
        self.canvas_widget = MyCanvas()
        # Canvas should take up all available space except toolbar
        self.canvas_widget.size_hint = (1, 1)  # Full width, flexible height

        # Create the toolbar and link it to the canvas
        self.toolbar = Toolbar(canvas_widget=self.canvas_widget)
        # Toolbar has fixed height but scales width
        self.toolbar.size_hint = (1, None)  # Full width, fixed height

        # Add widgets to the layout
        # Canvas takes up most of the space
        self.add_widget(self.canvas_widget)

        # Toolbar is fixed at the bottom
        self.add_widget(self.toolbar)

    def get_canvas(self):
        """
        Get the canvas widget.

        Returns:
            MyCanvas: The drawing canvas widget
        """
        return self.canvas_widget

    def get_toolbar(self):
        """
        Get the toolbar widget.

        Returns:
            Toolbar: The toolbar widget
        """
        return self.toolbar

    def clear_canvas(self):
        """Clear the drawing canvas."""
        if self.canvas_widget:
            self.canvas_widget.clear_screen()

    def set_drawing_color(self, color):
        """
        Set the drawing color.

        Args:
            color (tuple): RGBA color tuple
        """
        if self.canvas_widget:
            self.canvas_widget.set_color(color)

    def set_line_width(self, width_name):
        """
        Set the line width.

        Args:
            width_name (str): Name of the width setting
        """
        if self.canvas_widget:
            self.canvas_widget.set_line_width(width_name)

    def has_drawings(self):
        """
        Check if there are any drawings on the canvas.

        Returns:
            bool: True if there are drawings, False otherwise
        """
        return self.canvas_widget.has_drawings() if self.canvas_widget else False

    def get_drawing_bounds(self):
        """
        Get the bounds of all drawings.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) or None if no drawings
        """
        return self.canvas_widget.get_drawing_bounds() if self.canvas_widget else None

    def _keyboard_closed(self):
        """Handle keyboard being closed."""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Handle keyboard key down events.

        Args:
            keyboard: The keyboard instance
            keycode: Tuple of (key_code, key_string)
            text: The text representation of the key
            modifiers: List of modifier keys pressed

        Returns:
            bool: True if the key was handled, False otherwise
        """
        key_code, key_string = keycode

        # Check for CMD+Shift+Z (redo) or CMD+Y (redo) on macOS, Ctrl+Shift+Z or Ctrl+Y on other platforms
        if "meta" in modifiers or "ctrl" in modifiers:
            if key_string == "z" and "shift" in modifiers:
                # CMD+Shift+Z or Ctrl+Shift+Z for redo
                if self.canvas_widget and hasattr(self.canvas_widget, "redo"):
                    self.canvas_widget.redo()
                    return True
            elif key_string == "y":
                # CMD+Y or Ctrl+Y for redo (alternative shortcut)
                if self.canvas_widget and hasattr(self.canvas_widget, "redo"):
                    self.canvas_widget.redo()
                    return True
            elif key_string == "z":
                # CMD+Z or Ctrl+Z for undo
                if self.canvas_widget and hasattr(self.canvas_widget, "undo"):
                    self.canvas_widget.undo()
                    return True

        return False

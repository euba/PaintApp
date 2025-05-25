"""
Layout module for PaintApp.

Contains the main layout manager that organizes the canvas and toolbar.
"""

from kivy.uix.boxlayout import BoxLayout

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

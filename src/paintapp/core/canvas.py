"""
Canvas module for PaintApp.

Contains the main drawing canvas with touch handling and drawing operations.
"""

from kivy.uix.widget import Widget
from kivy.graphics import Line, Color

from ..utils.constants import LineWidths
from .config import AppConfig


class MyCanvas(Widget):
    """
    Main drawing canvas widget.

    Handles touch events for drawing, manages drawing state,
    and provides methods for canvas operations.
    """

    def __init__(self, **kwargs):
        """Initialize the canvas with default settings."""
        super().__init__(**kwargs)

        # Drawing state
        self.line_width = AppConfig.get_default_line_width()
        self.current_color = AppConfig.get_default_color()

        # Drawing history for potential undo functionality
        self.drawing_history = []
        
        # Track canvas size for scaling calculations
        self.last_canvas_size = None
        self.is_resizing = False

        # Set initial drawing color
        with self.canvas:
            Color(*self.current_color)
        
        # Bind to size changes to handle window resizing
        self.bind(size=self.on_size_change)
        self.bind(pos=self.on_pos_change)

    def on_size_change(self, instance, size):
        """Handle canvas size changes when window is resized."""
        if self.last_canvas_size is None:
            # First time setting size, just store it
            self.last_canvas_size = size
            return
            
        # Calculate scaling factors
        old_width, old_height = self.last_canvas_size
        new_width, new_height = size
        
        if old_width <= 0 or old_height <= 0 or new_width <= 0 or new_height <= 0:
            return
            
        scale_x = new_width / old_width
        scale_y = new_height / old_height
        
        # Only scale if there's a significant change and we have drawings
        if (abs(scale_x - 1.0) > 0.01 or abs(scale_y - 1.0) > 0.01) and self.drawing_history:
            self.is_resizing = True
            self._scale_all_drawings(scale_x, scale_y)
            self.is_resizing = False
            
        # Update the stored canvas size
        self.last_canvas_size = size

    def on_pos_change(self, instance, pos):
        """Handle canvas position changes when window is resized."""
        # This method can be extended to handle any position-dependent operations
        pass

    def _scale_all_drawings(self, scale_x, scale_y):
        """Scale all drawings by the given factors."""
        # Clear the canvas
        self.canvas.clear()
        
        # Redraw all lines with scaled coordinates
        for entry in self.drawing_history:
            if entry["type"] in ["line_start", "line_complete"] and "points" in entry:
                # Scale the points
                scaled_points = []
                points = entry["points"]
                for i in range(0, len(points), 2):
                    if i + 1 < len(points):
                        x, y = points[i], points[i + 1]
                        scaled_x = x * scale_x
                        scaled_y = y * scale_y
                        scaled_points.extend([scaled_x, scaled_y])
                
                # Update the stored points
                entry["points"] = scaled_points
                
                # Redraw the line with scaled coordinates
                with self.canvas:
                    Color(*entry["color"])
                    # Scale line width proportionally (use average of scale factors)
                    scaled_width = entry["width"] * ((scale_x + scale_y) / 2)
                    new_line = Line(points=scaled_points, width=scaled_width)
                    entry["line"] = new_line
                    entry["width"] = scaled_width

    def on_touch_down(self, touch):
        """
        Handle touch down events to start drawing.

        Args:
            touch: Kivy touch event object

        Returns:
            bool: True if touch was handled, False otherwise
        """
        # Check if any child widgets handle the touch first
        for widget in self.children:
            if widget.on_touch_down(touch):
                return True

        # Only start drawing if the touch is within the canvas bounds
        if not self.collide_point(*touch.pos):
            return False

        # Initialize canvas size tracking if needed
        if self.last_canvas_size is None:
            self.last_canvas_size = self.size

        # Start a new line at the touch position
        with self.canvas:
            # Set the current color for this line
            Color(*self.current_color)

            # Create a new line starting at the touch position
            line = Line(points=[touch.x, touch.y], width=self.line_width)

            # Store the line in the touch user data for continuation
            touch.ud["line"] = line

            # Add to drawing history
            self.drawing_history.append(
                {
                    "type": "line_start",
                    "line": line,
                    "color": self.current_color,
                    "width": self.line_width,
                    "points": [touch.x, touch.y],
                }
            )

        return True

    def on_touch_move(self, touch):
        """
        Handle touch move events to continue drawing.

        Args:
            touch: Kivy touch event object

        Returns:
            bool: True if touch was handled, False otherwise
        """
        # Only draw if the touch is within the canvas bounds
        if self.collide_point(*touch.pos) and "line" in touch.ud:
            # Add the current touch position to the line
            touch.ud["line"].points += [touch.x, touch.y]

            # Update drawing history
            if self.drawing_history:
                last_entry = self.drawing_history[-1]
                if (
                    last_entry["type"] == "line_start"
                    and last_entry["line"] == touch.ud["line"]
                ):
                    last_entry["points"].extend([touch.x, touch.y])

        return True

    def on_touch_up(self, touch):
        """
        Handle touch up events to finish drawing.

        Args:
            touch: Kivy touch event object

        Returns:
            bool: True if touch was handled, False otherwise
        """
        # Clean up the touch user data
        if "line" in touch.ud:
            # Mark the line as complete in history
            if self.drawing_history:
                last_entry = self.drawing_history[-1]
                if (
                    last_entry["type"] == "line_start"
                    and last_entry["line"] == touch.ud["line"]
                ):
                    last_entry["type"] = "line_complete"

            del touch.ud["line"]

        return True

    def set_color(self, new_color):
        """
        Set the current drawing color.

        Args:
            new_color (tuple): RGBA color tuple (r, g, b, a)
        """
        self.current_color = new_color

        # Set the color for future drawing operations
        with self.canvas:
            Color(*new_color)

    def set_line_width(self, width_name):
        """
        Set the current line width.

        Args:
            width_name (str): Name of the width (e.g., "Thin", "Normal", "Thick")
        """
        width_map = LineWidths.get_width_map()
        if width_name in width_map:
            self.line_width = width_map[width_name]

    def clear_screen(self):
        """Clear the entire canvas while preserving child widgets."""
        # Save child widgets
        saved_widgets = self.children[:]

        # Remove all widgets temporarily
        self.clear_widgets()

        # Clear the canvas
        self.canvas.clear()

        # Reset drawing state
        with self.canvas:
            Color(*self.current_color)

        # Restore child widgets
        for widget in saved_widgets:
            self.add_widget(widget)

        # Clear drawing history and reset size tracking
        self.drawing_history.clear()
        self.last_canvas_size = self.size if self.size != [100, 100] else None

    def get_drawing_bounds(self):
        """
        Get the bounds of all drawings on the canvas.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) or None if no drawings
        """
        if not self.drawing_history:
            return None

        min_x = min_y = float("inf")
        max_x = max_y = float("-inf")

        for entry in self.drawing_history:
            if entry["type"] in ["line_start", "line_complete"] and "points" in entry:
                points = entry["points"]
                for i in range(0, len(points), 2):
                    if i + 1 < len(points):
                        x, y = points[i], points[i + 1]
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)

        if min_x == float("inf"):
            return None

        return (min_x, min_y, max_x, max_y)

    def has_drawings(self):
        """
        Check if the canvas has any drawings.

        Returns:
            bool: True if there are drawings, False otherwise
        """
        return len(self.drawing_history) > 0

    def get_current_color(self):
        """
        Get the current drawing color.

        Returns:
            tuple: RGBA color tuple
        """
        return self.current_color

    def get_current_line_width(self):
        """
        Get the current line width.

        Returns:
            int: Current line width in pixels
        """
        return self.line_width

"""
Canvas module for PaintApp.

Contains the main drawing canvas with touch handling and drawing operations.
"""

from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Line, Color, Ellipse, Triangle, Rectangle
from kivy.graphics.vertex_instructions import Rectangle as GraphicsRectangle
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
import math

from ..utils.constants import LineWidths, DrawingModes
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
        self.drawing_mode = DrawingModes.LINE  # Default to line drawing

        # Drawing history for potential undo functionality
        self.drawing_history = []
        
        # Track canvas size for scaling calculations
        self.last_canvas_size = None
        self.is_resizing = False
        
        # Text input state
        self.active_text_input = None
        self.text_input_pos = None

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
        
        # Redraw all drawings with scaled coordinates
        for entry in self.drawing_history:
            with self.canvas:
                Color(*entry["color"])
                scaled_width = entry["width"] * ((scale_x + scale_y) / 2)
                entry["width"] = scaled_width
                
                if entry["type"] in ["line_start", "line_complete"] and "points" in entry:
                    # Scale line points
                    scaled_points = []
                    points = entry["points"]
                    for i in range(0, len(points), 2):
                        if i + 1 < len(points):
                            x, y = points[i], points[i + 1]
                            scaled_x = x * scale_x
                            scaled_y = y * scale_y
                            scaled_points.extend([scaled_x, scaled_y])
                    
                    entry["points"] = scaled_points
                    new_line = Line(points=scaled_points, width=scaled_width)
                    entry["line"] = new_line
                    
                elif entry["type"] == "shape_complete":
                    # Scale shape coordinates
                    mode = entry["drawing_mode"]
                    start_x, start_y = entry["start_pos"]
                    end_x, end_y = entry["end_pos"]
                    
                    # Scale positions
                    scaled_start = (start_x * scale_x, start_y * scale_y)
                    scaled_end = (end_x * scale_x, end_y * scale_y)
                    entry["start_pos"] = scaled_start
                    entry["end_pos"] = scaled_end
                    
                    if mode == DrawingModes.CIRCLE:
                        radius = entry["radius"] * ((scale_x + scale_y) / 2)
                        entry["radius"] = radius
                        
                        # Recreate circle points with scaled radius and center
                        if radius > 0:
                            circle_points = []
                            num_segments = 64
                            for i in range(num_segments + 1):
                                angle = 2 * math.pi * i / num_segments
                                x = scaled_start[0] + radius * math.cos(angle)
                                y = scaled_start[1] + radius * math.sin(angle)
                                circle_points.extend([x, y])
                            
                            entry["circle_points"] = circle_points
                            new_shape = Line(points=circle_points, width=scaled_width)
                        else:
                            new_shape = Line(points=[scaled_start[0], scaled_start[1], scaled_start[0], scaled_start[1]], width=scaled_width)
                        
                    elif mode == DrawingModes.RECTANGLE:
                        min_x, min_y, width, height = entry["rect_bounds"]
                        scaled_bounds = (
                            min_x * scale_x,
                            min_y * scale_y,
                            width * scale_x,
                            height * scale_y
                        )
                        entry["rect_bounds"] = scaled_bounds
                        new_shape = Line(rectangle=scaled_bounds, width=scaled_width)
                        
                    elif mode == DrawingModes.TRIANGLE:
                        points = entry["points"]
                        scaled_points = []
                        for i in range(0, len(points), 2):
                            if i + 1 < len(points):
                                x, y = points[i], points[i + 1]
                                scaled_points.extend([x * scale_x, y * scale_y])
                        entry["points"] = scaled_points
                        new_shape = Line(points=scaled_points, width=scaled_width)
                        
                    elif mode == DrawingModes.STRAIGHT_LINE:
                        points = entry["points"]
                        scaled_points = []
                        for i in range(0, len(points), 2):
                            if i + 1 < len(points):
                                x, y = points[i], points[i + 1]
                                scaled_points.extend([x * scale_x, y * scale_y])
                        entry["points"] = scaled_points
                        new_shape = Line(points=scaled_points, width=scaled_width)
                    
                    entry["shape"] = new_shape
                    
                elif entry["type"] == "text_complete":
                    # Scale text position
                    old_x, old_y = entry["pos"]
                    scaled_pos = (old_x * scale_x, old_y * scale_y)
                    entry["pos"] = scaled_pos
                    
                    # Scale font size
                    old_font_size = entry["font_size"]
                    scaled_font_size = old_font_size * ((scale_x + scale_y) / 2)
                    entry["font_size"] = scaled_font_size
                    
                    # Recreate the text with new size and position
                    label = CoreLabel(
                        text=entry["text"],
                        font_size=scaled_font_size,
                        color=entry["color"]
                    )
                    label.refresh()
                    texture = label.texture
                    
                    new_text_rect = Rectangle(
                        texture=texture,
                        pos=scaled_pos,
                        size=texture.size
                    )
                    
                    entry["texture_rect"] = new_text_rect
                    entry["size"] = texture.size

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

        # If there's an active text input and we're not clicking on it, finalize it
        if self.active_text_input and not self.active_text_input.collide_point(*touch.pos):
            self._finalize_text_input()
            # Don't process this touch further if we're just finalizing text
            return True

        # Initialize canvas size tracking if needed
        if self.last_canvas_size is None:
            self.last_canvas_size = self.size

        # Store the starting position for shape drawing
        touch.ud["start_pos"] = (touch.x, touch.y)

        if self.drawing_mode == DrawingModes.LINE:
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
                        "drawing_mode": self.drawing_mode,
                    }
                )
        elif self.drawing_mode == DrawingModes.TEXT:
            # If there's already an active text input, finalize it first
            if self.active_text_input:
                self._finalize_text_input()
            # Create text input directly on canvas
            self._create_text_input(touch.x, touch.y)
            # Return True to indicate we handled this touch and prevent further processing
            return True
        else:
            # For shapes and straight lines, we'll create a temporary shape that gets updated during drag
            touch.ud["temp_shape"] = None
            touch.ud["drawing_mode"] = self.drawing_mode

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
        if not self.collide_point(*touch.pos):
            return True

        if "line" in touch.ud:
            # Line drawing mode
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

        elif "start_pos" in touch.ud and "drawing_mode" in touch.ud:
            # Shape drawing mode
            self._update_temp_shape(touch)

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

        elif "start_pos" in touch.ud and "drawing_mode" in touch.ud:
            # Finalize shape drawing
            self._finalize_shape(touch)

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
        # Finalize any active text input
        if self.active_text_input:
            self._finalize_text_input()
        
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

    def set_drawing_mode(self, mode):
        """
        Set the current drawing mode.

        Args:
            mode (str): Drawing mode (line, circle, triangle, rectangle)
        """
        if mode in DrawingModes.get_modes():
            self.drawing_mode = mode

    def get_drawing_mode(self):
        """
        Get the current drawing mode.

        Returns:
            str: Current drawing mode
        """
        return self.drawing_mode

    def _get_font_size_from_line_width(self):
        """
        Calculate font size based on current line width.
        
        Returns:
            int: Font size in pixels
        """
        # Base font sizes for each line width - increased for better visibility
        font_size_map = {
            2: 32,   # Thin -> 32pt (was 24pt)
            4: 48,   # Normal -> 48pt (was 36pt)
            8: 64,   # Thick -> 64pt (was 48pt)
        }
        return font_size_map.get(self.line_width, 48)

    def _update_temp_shape(self, touch):
        """Update the temporary shape during drag."""
        if "temp_shape" not in touch.ud:
            return

        start_x, start_y = touch.ud["start_pos"]
        current_x, current_y = touch.pos
        mode = touch.ud["drawing_mode"]

        # Remove the previous temporary shape
        if touch.ud["temp_shape"]:
            self.canvas.remove(touch.ud["temp_shape"])

        # Create new temporary shape
        with self.canvas:
            Color(*self.current_color)
            
            if mode == DrawingModes.STRAIGHT_LINE:
                # Create a straight line from start to current position
                touch.ud["temp_shape"] = Line(
                    points=[start_x, start_y, current_x, current_y],
                    width=self.line_width
                )
                
            elif mode == DrawingModes.CIRCLE:
                # Calculate radius from distance between start and current position
                radius = math.sqrt((current_x - start_x)**2 + (current_y - start_y)**2)
                # Create circle outline using Line with circle points
                if radius > 0:
                    # Generate points for a circle outline
                    circle_points = []
                    num_segments = 64  # Number of segments for smooth circle
                    for i in range(num_segments + 1):  # +1 to close the circle
                        angle = 2 * math.pi * i / num_segments
                        x = start_x + radius * math.cos(angle)
                        y = start_y + radius * math.sin(angle)
                        circle_points.extend([x, y])
                    
                    touch.ud["temp_shape"] = Line(points=circle_points, width=self.line_width)
                
            elif mode == DrawingModes.RECTANGLE:
                # Calculate rectangle bounds
                min_x = min(start_x, current_x)
                min_y = min(start_y, current_y)
                width = abs(current_x - start_x)
                height = abs(current_y - start_y)
                touch.ud["temp_shape"] = Line(
                    rectangle=(min_x, min_y, width, height),
                    width=self.line_width
                )
                
            elif mode == DrawingModes.TRIANGLE:
                # Create triangle with three points
                # Top point at start position, base between start and current
                mid_x = (start_x + current_x) / 2
                points = [
                    start_x, start_y,  # Top point
                    start_x - (current_x - start_x) / 2, current_y,  # Bottom left
                    start_x + (current_x - start_x) / 2, current_y,  # Bottom right
                    start_x, start_y   # Close the triangle
                ]
                touch.ud["temp_shape"] = Line(points=points, width=self.line_width)

    def _finalize_shape(self, touch):
        """Finalize the shape and add it to drawing history."""
        if "start_pos" not in touch.ud or "drawing_mode" not in touch.ud:
            return

        start_x, start_y = touch.ud["start_pos"]
        end_x, end_y = touch.pos
        mode = touch.ud["drawing_mode"]

        # Remove temporary shape
        if touch.ud.get("temp_shape"):
            self.canvas.remove(touch.ud["temp_shape"])

        # Create final shape
        with self.canvas:
            Color(*self.current_color)
            
            shape_data = {
                "type": "shape_complete",
                "color": self.current_color,
                "width": self.line_width,
                "drawing_mode": mode,
                "start_pos": (start_x, start_y),
                "end_pos": (end_x, end_y),
            }
            
            if mode == DrawingModes.STRAIGHT_LINE:
                # Create a straight line from start to end position
                final_shape = Line(
                    points=[start_x, start_y, end_x, end_y],
                    width=self.line_width
                )
                shape_data["points"] = [start_x, start_y, end_x, end_y]
                
            elif mode == DrawingModes.CIRCLE:
                radius = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                # Create circle outline using Line with circle points
                if radius > 0:
                    circle_points = []
                    num_segments = 64  # Number of segments for smooth circle
                    for i in range(num_segments + 1):  # +1 to close the circle
                        angle = 2 * math.pi * i / num_segments
                        x = start_x + radius * math.cos(angle)
                        y = start_y + radius * math.sin(angle)
                        circle_points.extend([x, y])
                    
                    final_shape = Line(points=circle_points, width=self.line_width)
                    shape_data["radius"] = radius
                    shape_data["circle_points"] = circle_points
                else:
                    # If radius is 0, create a small point
                    final_shape = Line(points=[start_x, start_y, start_x, start_y], width=self.line_width)
                    shape_data["radius"] = 0
                
            elif mode == DrawingModes.RECTANGLE:
                min_x = min(start_x, end_x)
                min_y = min(start_y, end_y)
                width = abs(end_x - start_x)
                height = abs(end_y - start_y)
                final_shape = Line(
                    rectangle=(min_x, min_y, width, height),
                    width=self.line_width
                )
                shape_data["rect_bounds"] = (min_x, min_y, width, height)
                
            elif mode == DrawingModes.TRIANGLE:
                points = [
                    start_x, start_y,
                    start_x - (end_x - start_x) / 2, end_y,
                    start_x + (end_x - start_x) / 2, end_y,
                    start_x, start_y
                ]
                final_shape = Line(points=points, width=self.line_width)
                shape_data["points"] = points

            shape_data["shape"] = final_shape
            self.drawing_history.append(shape_data)

    def _create_text_input(self, x, y):
        """Create a text input widget directly on the canvas."""
        # Remove any existing text input
        if self.active_text_input:
            self._finalize_text_input()
        
        # Get font size based on line width
        font_size = self._get_font_size_from_line_width()
        
        # Create text input widget
        self.active_text_input = TextInput(
            text='',
            multiline=False,  # Single line - Enter will finalize
            size_hint=(None, None),
            size=(300, font_size + 20),  # Wider and taller for larger text
            pos=(x, y - font_size - 10),  # Position slightly above click point
            font_size=font_size,
            background_color=(1, 1, 1, 0.9),  # More opaque white background
            foreground_color=self.current_color,  # Text color matches selected color
            cursor_color=self.current_color,
            border=(2, 2, 2, 2),
            write_tab=False  # Disable tab key to prevent focus issues
        )
        
        # Store position for later use
        self.text_input_pos = (x, y)
        
        # Bind events
        self.active_text_input.bind(on_text_validate=self._on_text_validate)
        self.active_text_input.bind(focus=self._on_text_focus_change)
        
        # Add to canvas first
        self.add_widget(self.active_text_input)
        # Schedule focus setting after the widget is fully added to the widget tree
        Clock.schedule_once(lambda dt: self._ensure_text_focus(), 0.1)

    def _ensure_text_focus(self):
        """Ensure the text input has focus and is ready for typing."""
        if self.active_text_input:
            # Make sure the text input is properly focused
            self.active_text_input.focus = True
            # Try to select all text to ensure cursor is active
            try:
                self.active_text_input.select_all()
                # Then deselect to just have cursor at end
                self.active_text_input.cursor = (0, 0)
            except:
                pass
            # Schedule another focus attempt if needed
            Clock.schedule_once(lambda dt: self._final_focus_attempt(), 0.1)

    def _final_focus_attempt(self):
        """Final attempt to ensure text input has focus."""
        if self.active_text_input and not self.active_text_input.focus:
            self.active_text_input.focus = True

    def _on_text_validate(self, text_input):
        """Handle when user presses Enter in text input."""
        # Finalize text input when Enter is pressed
        self._finalize_text_input()

    def _on_text_focus_change(self, text_input, focused):
        """Handle when text input loses focus."""
        # Don't auto-finalize on focus loss - only finalize on Enter or explicit click elsewhere
        pass



    def _finalize_text_input(self):
        """Finalize the text input and add text to canvas."""
        if not self.active_text_input:
            return
            
        text = self.active_text_input.text.strip()
        
        # Remove the text input widget
        self.remove_widget(self.active_text_input)
        
        # Add text to canvas if not empty
        if text and self.text_input_pos:
            self._add_text_to_canvas(text, self.text_input_pos[0], self.text_input_pos[1])
        
        # Clear references
        self.active_text_input = None
        self.text_input_pos = None

    def _add_text_to_canvas(self, text, x, y):
        """Add text to the canvas at the specified position."""
        if not text:
            return
            
        # Get font size based on line width
        font_size = self._get_font_size_from_line_width()
            
        # Create a label to render the text
        label = CoreLabel(
            text=text,
            font_size=font_size,
            color=self.current_color
        )
        label.refresh()
        
        # Get the texture from the label
        texture = label.texture
        
        # Add the text to the canvas
        with self.canvas:
            Color(*self.current_color)
            text_rect = Rectangle(
                texture=texture,
                pos=(x, y - texture.height),  # Adjust y to position text above click point
                size=texture.size
            )
        
        # Add to drawing history
        text_data = {
            "type": "text_complete",
            "text": text,
            "color": self.current_color,
            "pos": (x, y - texture.height),
            "size": texture.size,
            "font_size": font_size,
            "drawing_mode": DrawingModes.TEXT,
            "texture_rect": text_rect
        }
        
        self.drawing_history.append(text_data)

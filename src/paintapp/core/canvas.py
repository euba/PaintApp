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
from kivy.graphics.fbo import Fbo
from kivy.graphics.gl_instructions import ClearColor, ClearBuffers
import math

from ..utils.constants import LineWidths, DrawingModes, LineStyles
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
        self.line_style = AppConfig.get_default_line_style()  # Default to solid lines

        # Drawing history for potential undo functionality
        self.drawing_history = []

        # Undo/Redo functionality
        self.undo_stack = []  # Stack of states that can be undone
        self.redo_stack = []  # Stack of states that can be redone

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
        if (
            abs(scale_x - 1.0) > 0.01 or abs(scale_y - 1.0) > 0.01
        ) and self.drawing_history:
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

                if (
                    entry["type"] in ["line_start", "line_complete"]
                    and "points" in entry
                ):
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
                            new_shape = Line(
                                points=[
                                    scaled_start[0],
                                    scaled_start[1],
                                    scaled_start[0],
                                    scaled_start[1],
                                ],
                                width=scaled_width,
                            )

                    elif mode == DrawingModes.RECTANGLE:
                        min_x, min_y, width, height = entry["rect_bounds"]
                        scaled_bounds = (
                            min_x * scale_x,
                            min_y * scale_y,
                            width * scale_x,
                            height * scale_y,
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
                        color=entry["color"],
                    )
                    label.refresh()
                    texture = label.texture

                    new_text_rect = Rectangle(
                        texture=texture, pos=scaled_pos, size=texture.size
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
        if self.active_text_input and not self.active_text_input.collide_point(
            *touch.pos
        ):
            self._finalize_text_input()
            # Don't process this touch further if we're just finalizing text
            return True

        # Initialize canvas size tracking if needed
        if self.last_canvas_size is None:
            self.last_canvas_size = self.size

        # Store the starting position for shape drawing
        touch.ud["start_pos"] = (touch.x, touch.y)

        if self.drawing_mode == DrawingModes.LINE:
            # Save state before starting new drawing action
            self._save_state_for_undo()

            # Start a new line at the touch position
            with self.canvas:
                # Set the current color for this line
                Color(*self.current_color)

                # Create a new line starting at the touch position
                line = self._create_line(points=[touch.x, touch.y])

                # Store the line in the touch user data for continuation
                touch.ud["line"] = line

                # Add to drawing history
                self.drawing_history.append(
                    {
                        "type": "line_start",
                        "line": line,
                        "color": self.current_color,
                        "width": self.line_width,
                        "style": self.line_style,
                        "points": [touch.x, touch.y],
                        "drawing_mode": self.drawing_mode,
                    }
                )
        elif self.drawing_mode == DrawingModes.TEXT:
            # If there's already an active text input, finalize it first
            if self.active_text_input:
                self._finalize_text_input()
            # Save state before starting text input
            self._save_state_for_undo()
            # Create text input directly on canvas
            self._create_text_input(touch.x, touch.y)
            # Return True to indicate we handled this touch and prevent further processing
            return True
        else:
            # Save state before starting shape drawing
            self._save_state_for_undo()
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

                    # If this is a dashed line, replace it with dashed segments
                    if self.line_style == LineStyles.DASHED:
                        self._convert_to_dashed_line(last_entry)

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
        # Save state before clearing for undo functionality
        if self.drawing_history:  # Only save if there's something to clear
            self._save_state_for_undo()

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

    def set_line_style(self, style):
        """
        Set the current line style.

        Args:
            style (str): Line style ("solid" or "dashed")
        """
        if style in LineStyles.get_styles():
            self.line_style = style

    def get_line_style(self):
        """
        Get the current line style.

        Returns:
            str: Current line style
        """
        return self.line_style

    def _create_line(self, **kwargs):
        """
        Create a line with current style settings.

        Args:
            **kwargs: Arguments to pass to Line constructor

        Returns:
            Line: The created line object
        """
        line = Line(width=self.line_width, **kwargs)

        # For dashed lines, we'll handle the dashing in a different way
        # by creating multiple line segments when the line is finalized
        return line

    def _create_dashed_line(self, **kwargs):
        """
        Create a dashed line by drawing multiple short segments.

        Args:
            **kwargs: Arguments that would be passed to Line constructor

        Returns:
            list: List of Line objects representing the dashed pattern
        """
        dash_length = max(self.line_width * 3, 15)  # Length of each dash
        gap_length = (
            dash_length * 1.5
        )  # Length of each gap (consistent with other methods)

        lines = []

        if "points" in kwargs:
            points = kwargs["points"]
            if len(points) >= 4:
                lines.extend(
                    self._create_dashed_line_from_points(
                        points, dash_length, gap_length
                    )
                )
        elif "rectangle" in kwargs:
            rect = kwargs["rectangle"]
            lines.extend(self._create_dashed_rectangle(rect, dash_length, gap_length))

        return lines

    def _create_dashed_line_from_points(
        self, points, dash_length, gap_length, width=None
    ):
        """Create dashed line segments from a list of points."""
        lines = []

        # Use provided width or fall back to current line width
        line_width = width if width is not None else self.line_width

        if len(points) < 4:  # Need at least 2 points (4 coordinates)
            return lines

        # For free-drawn lines (many points), treat as continuous path
        if len(points) > 4:
            return self._create_dashed_continuous_path(
                points, dash_length, gap_length, width
            )

        # For simple lines (2 points), use the original method
        x1, y1 = points[0], points[1]
        x2, y2 = points[2], points[3]

        # Calculate line length and direction
        dx = x2 - x1
        dy = y2 - y1
        line_length = math.sqrt(dx * dx + dy * dy)

        if line_length > 0:
            # Normalize direction vector
            dx_norm = dx / line_length
            dy_norm = dy / line_length

            # Create dashed segments along this line
            current_pos = 0
            while current_pos < line_length:
                # Calculate dash start and end positions
                dash_start = current_pos
                dash_end = min(current_pos + dash_length, line_length)

                # Calculate actual coordinates
                start_x = x1 + dx_norm * dash_start
                start_y = y1 + dy_norm * dash_start
                end_x = x1 + dx_norm * dash_end
                end_y = y1 + dy_norm * dash_end

                # Create the dash segment
                dash_line = Line(
                    points=[start_x, start_y, end_x, end_y], width=line_width
                )
                lines.append(dash_line)

                # Move to next dash (skip the gap)
                current_pos += dash_length + gap_length

        return lines

    def _create_dashed_continuous_path(
        self, points, dash_length, gap_length, width=None
    ):
        """Create dashed line segments along a continuous path with even distribution."""
        lines = []

        # Use provided width or fall back to current line width
        line_width = width if width is not None else self.line_width

        # Calculate total path length and create distance markers
        path_segments = []
        total_length = 0

        for i in range(0, len(points) - 2, 2):
            x1, y1 = points[i], points[i + 1]
            x2, y2 = points[i + 2], points[i + 3]

            dx = x2 - x1
            dy = y2 - y1
            segment_length = math.sqrt(dx * dx + dy * dy)

            if segment_length > 0:
                path_segments.append(
                    {
                        "start": (x1, y1),
                        "end": (x2, y2),
                        "length": segment_length,
                        "start_distance": total_length,
                        "end_distance": total_length + segment_length,
                    }
                )
                total_length += segment_length

        if total_length == 0:
            return lines

        # Create dashes along the total path length
        current_distance = 0
        dash_cycle = dash_length + gap_length

        while current_distance < total_length:
            dash_start = current_distance
            dash_end = min(current_distance + dash_length, total_length)

            # Find the segments that contain this dash
            dash_points = []

            # Get start point
            start_point = self._get_point_at_distance(path_segments, dash_start)
            if start_point:
                dash_points.extend(start_point)

            # Get end point
            end_point = self._get_point_at_distance(path_segments, dash_end)
            if end_point:
                dash_points.extend(end_point)

            # Create the dash if we have valid points
            if len(dash_points) >= 4:
                dash_line = Line(points=dash_points, width=line_width)
                lines.append(dash_line)

            # Move to next dash
            current_distance += dash_cycle

        return lines

    def _get_point_at_distance(self, path_segments, target_distance):
        """Get the x,y coordinates at a specific distance along the path."""
        for segment in path_segments:
            if segment["start_distance"] <= target_distance <= segment["end_distance"]:
                # Calculate position within this segment
                segment_progress = (
                    target_distance - segment["start_distance"]
                ) / segment["length"]

                x1, y1 = segment["start"]
                x2, y2 = segment["end"]

                # Linear interpolation
                x = x1 + (x2 - x1) * segment_progress
                y = y1 + (y2 - y1) * segment_progress

                return [x, y]

        return None

    def _create_dashed_rectangle(self, rect, dash_length, gap_length, width=None):
        """Create dashed rectangle by creating dashed lines for each side."""
        x, y, rect_width, height = rect
        lines = []

        # Top side
        top_points = [x, y + height, x + rect_width, y + height]
        lines.extend(
            self._create_dashed_line_from_points(
                top_points, dash_length, gap_length, width
            )
        )

        # Right side
        right_points = [x + rect_width, y + height, x + rect_width, y]
        lines.extend(
            self._create_dashed_line_from_points(
                right_points, dash_length, gap_length, width
            )
        )

        # Bottom side
        bottom_points = [x + rect_width, y, x, y]
        lines.extend(
            self._create_dashed_line_from_points(
                bottom_points, dash_length, gap_length, width
            )
        )

        # Left side
        left_points = [x, y, x, y + height]
        lines.extend(
            self._create_dashed_line_from_points(
                left_points, dash_length, gap_length, width
            )
        )

        return lines

    def _convert_to_dashed_line(self, line_entry):
        """Convert a solid line entry to dashed line segments."""
        if "points" not in line_entry or "line" not in line_entry:
            return

        # Remove the original solid line from canvas
        original_line = line_entry["line"]
        try:
            if original_line in self.canvas.children:
                self.canvas.remove(original_line)
        except (ValueError, AttributeError):
            # Line might have already been removed or doesn't exist
            pass

        # Create dashed segments using the stored width
        points = line_entry["points"]
        width = line_entry.get("width", self.line_width)
        dash_length = max(width * 3, 15)  # Shorter dashes for better visibility
        gap_length = dash_length * 1.5  # Larger gaps for more spacing

        # Draw dashed segments
        with self.canvas:
            Color(*line_entry["color"])
            dash_segments = self._create_dashed_line_from_points(
                points, dash_length, gap_length, width
            )

            # Store the dash segments in the line entry
            line_entry["dash_segments"] = dash_segments

    def _convert_shape_to_dashed(self, shape_entry):
        """Convert a solid shape to dashed segments."""
        if "shape" not in shape_entry:
            return

        # Remove the original solid shape from canvas
        original_shape = shape_entry["shape"]
        try:
            if original_shape in self.canvas.children:
                self.canvas.remove(original_shape)
        except (ValueError, AttributeError):
            # Shape might have already been removed or doesn't exist
            pass

        # Create dashed segments based on shape type using the stored width
        mode = shape_entry.get("drawing_mode", "")
        width = shape_entry.get("width", self.line_width)
        dash_length = max(width * 3, 15)
        gap_length = dash_length * 1.5

        with self.canvas:
            Color(*shape_entry["color"])
            dash_segments = []

            if mode == DrawingModes.STRAIGHT_LINE and "points" in shape_entry:
                dash_segments = self._create_dashed_line_from_points(
                    shape_entry["points"], dash_length, gap_length, width
                )
            elif mode == DrawingModes.CIRCLE and "circle_points" in shape_entry:
                dash_segments = self._create_dashed_line_from_points(
                    shape_entry["circle_points"], dash_length, gap_length, width
                )
            elif mode == DrawingModes.RECTANGLE and "rect_bounds" in shape_entry:
                dash_segments = self._create_dashed_rectangle(
                    shape_entry["rect_bounds"], dash_length, gap_length, width
                )
            elif mode == DrawingModes.TRIANGLE and "points" in shape_entry:
                dash_segments = self._create_dashed_line_from_points(
                    shape_entry["points"], dash_length, gap_length, width
                )

            # Store the dash segments in the shape entry
            shape_entry["dash_segments"] = dash_segments

    def _get_font_size_from_line_width(self):
        """
        Calculate font size based on current line width.

        Returns:
            int: Font size in pixels
        """
        # Base font sizes for each line width - scaled to match current line width values
        font_size_map = {
            3: 32,  # Thin -> 32pt
            6: 48,  # Normal -> 48pt
            12: 64,  # Thick -> 64pt
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
            try:
                if touch.ud["temp_shape"] in self.canvas.children:
                    self.canvas.remove(touch.ud["temp_shape"])
            except (ValueError, AttributeError):
                # Shape might have already been removed or doesn't exist
                pass

        # Create new temporary shape
        with self.canvas:
            Color(*self.current_color)

            if mode == DrawingModes.STRAIGHT_LINE:
                # Create a straight line from start to current position
                touch.ud["temp_shape"] = self._create_line(
                    points=[start_x, start_y, current_x, current_y]
                )

            elif mode == DrawingModes.CIRCLE:
                # Calculate radius from distance between start and current position
                radius = math.sqrt(
                    (current_x - start_x) ** 2 + (current_y - start_y) ** 2
                )
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

                    touch.ud["temp_shape"] = self._create_line(points=circle_points)

            elif mode == DrawingModes.RECTANGLE:
                # Calculate rectangle bounds
                min_x = min(start_x, current_x)
                min_y = min(start_y, current_y)
                width = abs(current_x - start_x)
                height = abs(current_y - start_y)
                touch.ud["temp_shape"] = self._create_line(
                    rectangle=(min_x, min_y, width, height)
                )

            elif mode == DrawingModes.TRIANGLE:
                # Create triangle with three points
                # Top point at start position, base between start and current
                mid_x = (start_x + current_x) / 2
                points = [
                    start_x,
                    start_y,  # Top point
                    start_x - (current_x - start_x) / 2,
                    current_y,  # Bottom left
                    start_x + (current_x - start_x) / 2,
                    current_y,  # Bottom right
                    start_x,
                    start_y,  # Close the triangle
                ]
                touch.ud["temp_shape"] = self._create_line(points=points)

    def _finalize_shape(self, touch):
        """Finalize the shape and add it to drawing history."""
        if "start_pos" not in touch.ud or "drawing_mode" not in touch.ud:
            return

        start_x, start_y = touch.ud["start_pos"]
        end_x, end_y = touch.pos
        mode = touch.ud["drawing_mode"]

        # Remove temporary shape
        if touch.ud.get("temp_shape"):
            try:
                if touch.ud["temp_shape"] in self.canvas.children:
                    self.canvas.remove(touch.ud["temp_shape"])
            except (ValueError, AttributeError):
                # Shape might have already been removed or doesn't exist
                pass

        # Create final shape
        with self.canvas:
            Color(*self.current_color)

            shape_data = {
                "type": "shape_complete",
                "color": self.current_color,
                "width": self.line_width,
                "style": self.line_style,
                "drawing_mode": mode,
                "start_pos": (start_x, start_y),
                "end_pos": (end_x, end_y),
            }

            if mode == DrawingModes.STRAIGHT_LINE:
                # Create a straight line from start to end position
                final_shape = self._create_line(points=[start_x, start_y, end_x, end_y])
                shape_data["points"] = [start_x, start_y, end_x, end_y]

            elif mode == DrawingModes.CIRCLE:
                radius = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
                # Create circle outline using Line with circle points
                if radius > 0:
                    circle_points = []
                    num_segments = 64  # Number of segments for smooth circle
                    for i in range(num_segments + 1):  # +1 to close the circle
                        angle = 2 * math.pi * i / num_segments
                        x = start_x + radius * math.cos(angle)
                        y = start_y + radius * math.sin(angle)
                        circle_points.extend([x, y])

                    final_shape = self._create_line(points=circle_points)
                    shape_data["radius"] = radius
                    shape_data["circle_points"] = circle_points
                else:
                    # If radius is 0, create a small point
                    final_shape = self._create_line(
                        points=[start_x, start_y, start_x, start_y]
                    )
                    shape_data["radius"] = 0

            elif mode == DrawingModes.RECTANGLE:
                min_x = min(start_x, end_x)
                min_y = min(start_y, end_y)
                width = abs(end_x - start_x)
                height = abs(end_y - start_y)
                final_shape = self._create_line(rectangle=(min_x, min_y, width, height))
                shape_data["rect_bounds"] = (min_x, min_y, width, height)

            elif mode == DrawingModes.TRIANGLE:
                points = [
                    start_x,
                    start_y,
                    start_x - (end_x - start_x) / 2,
                    end_y,
                    start_x + (end_x - start_x) / 2,
                    end_y,
                    start_x,
                    start_y,
                ]
                final_shape = self._create_line(points=points)
                shape_data["points"] = points

            shape_data["shape"] = final_shape
            self.drawing_history.append(shape_data)

            # If this is a dashed shape, convert it to dashed segments
            if self.line_style == LineStyles.DASHED:
                self._convert_shape_to_dashed(shape_data)

    def _create_text_input(self, x, y):
        """Create a text input widget directly on the canvas."""
        # Remove any existing text input
        if self.active_text_input:
            self._finalize_text_input()

        # Get font size based on line width
        font_size = self._get_font_size_from_line_width()

        # Create text input widget
        self.active_text_input = TextInput(
            text="",
            multiline=False,  # Single line - Enter will finalize
            size_hint=(None, None),
            size=(300, font_size + 20),  # Wider and taller for larger text
            pos=(x, y - font_size - 10),  # Position slightly above click point
            font_size=font_size,
            background_color=(1, 1, 1, 0.9),  # More opaque white background
            foreground_color=self.current_color,  # Text color matches selected color
            cursor_color=self.current_color,
            border=(2, 2, 2, 2),
            write_tab=False,  # Disable tab key to prevent focus issues
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
        try:
            if self.active_text_input in self.children:
                self.remove_widget(self.active_text_input)
        except (ValueError, AttributeError):
            # Widget might have already been removed
            pass

        # Add text to canvas if not empty
        if text and self.text_input_pos:
            self._add_text_to_canvas(
                text, self.text_input_pos[0], self.text_input_pos[1]
            )

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
        label = CoreLabel(text=text, font_size=font_size, color=self.current_color)
        label.refresh()

        # Get the texture from the label
        texture = label.texture

        # Add the text to the canvas
        with self.canvas:
            Color(*self.current_color)
            text_rect = Rectangle(
                texture=texture,
                pos=(
                    x,
                    y - texture.height,
                ),  # Adjust y to position text above click point
                size=texture.size,
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
            "texture_rect": text_rect,
        }

        self.drawing_history.append(text_data)

    def _save_state_for_undo(self):
        """Save current state to undo stack."""
        # Create a simplified copy of the drawing history without Kivy objects
        current_state = []
        for entry in self.drawing_history:
            # Create a clean copy without Kivy graphics objects
            clean_entry = {
                "type": entry.get("type", "unknown"),
                "color": entry.get("color", (0, 0, 0, 1)),
                "width": entry.get("width", 2),
                "drawing_mode": entry.get("drawing_mode", "line"),
                "style": entry.get("style", "solid"),
            }

            # Copy specific data based on entry type
            if "points" in entry:
                clean_entry["points"] = entry["points"][:]
            if "start_pos" in entry:
                clean_entry["start_pos"] = entry["start_pos"]
            if "end_pos" in entry:
                clean_entry["end_pos"] = entry["end_pos"]
            if "radius" in entry:
                clean_entry["radius"] = entry["radius"]
            if "circle_points" in entry:
                clean_entry["circle_points"] = entry["circle_points"][:]
            if "rect_bounds" in entry:
                clean_entry["rect_bounds"] = entry["rect_bounds"]
            if "text" in entry:
                clean_entry["text"] = entry["text"]
            if "pos" in entry:
                clean_entry["pos"] = entry["pos"]
            if "size" in entry:
                clean_entry["size"] = entry["size"]
            if "font_size" in entry:
                clean_entry["font_size"] = entry["font_size"]

            current_state.append(clean_entry)

        self.undo_stack.append(current_state)

        # Limit undo stack size to prevent memory issues
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

        # Clear redo stack when new action is performed
        self.redo_stack.clear()

    def undo(self):
        """Undo the last action."""
        if not self.undo_stack:
            return False

        # Finalize any active text input first
        if self.active_text_input:
            self._finalize_text_input()

        # Save current state to redo stack (using our clean copy method)
        current_state = []
        for entry in self.drawing_history:
            clean_entry = {
                "type": entry.get("type", "unknown"),
                "color": entry.get("color", (0, 0, 0, 1)),
                "width": entry.get("width", 2),
                "drawing_mode": entry.get("drawing_mode", "line"),
                "style": entry.get("style", "solid"),
            }

            # Copy specific data based on entry type
            if "points" in entry:
                clean_entry["points"] = entry["points"][:]
            if "start_pos" in entry:
                clean_entry["start_pos"] = entry["start_pos"]
            if "end_pos" in entry:
                clean_entry["end_pos"] = entry["end_pos"]
            if "radius" in entry:
                clean_entry["radius"] = entry["radius"]
            if "circle_points" in entry:
                clean_entry["circle_points"] = entry["circle_points"][:]
            if "rect_bounds" in entry:
                clean_entry["rect_bounds"] = entry["rect_bounds"]
            if "text" in entry:
                clean_entry["text"] = entry["text"]
            if "pos" in entry:
                clean_entry["pos"] = entry["pos"]
            if "size" in entry:
                clean_entry["size"] = entry["size"]
            if "font_size" in entry:
                clean_entry["font_size"] = entry["font_size"]

            current_state.append(clean_entry)

        self.redo_stack.append(current_state)

        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.drawing_history = previous_state

        # Redraw canvas
        self._redraw_canvas()
        return True

    def redo(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            return False

        # Finalize any active text input first
        if self.active_text_input:
            self._finalize_text_input()

        # Save current state to undo stack (using our clean copy method)
        current_state = []
        for entry in self.drawing_history:
            clean_entry = {
                "type": entry.get("type", "unknown"),
                "color": entry.get("color", (0, 0, 0, 1)),
                "width": entry.get("width", 2),
                "drawing_mode": entry.get("drawing_mode", "line"),
                "style": entry.get("style", "solid"),
            }

            # Copy specific data based on entry type
            if "points" in entry:
                clean_entry["points"] = entry["points"][:]
            if "start_pos" in entry:
                clean_entry["start_pos"] = entry["start_pos"]
            if "end_pos" in entry:
                clean_entry["end_pos"] = entry["end_pos"]
            if "radius" in entry:
                clean_entry["radius"] = entry["radius"]
            if "circle_points" in entry:
                clean_entry["circle_points"] = entry["circle_points"][:]
            if "rect_bounds" in entry:
                clean_entry["rect_bounds"] = entry["rect_bounds"]
            if "text" in entry:
                clean_entry["text"] = entry["text"]
            if "pos" in entry:
                clean_entry["pos"] = entry["pos"]
            if "size" in entry:
                clean_entry["size"] = entry["size"]
            if "font_size" in entry:
                clean_entry["font_size"] = entry["font_size"]

            current_state.append(clean_entry)

        self.undo_stack.append(current_state)

        # Restore next state
        next_state = self.redo_stack.pop()
        self.drawing_history = next_state

        # Redraw canvas
        self._redraw_canvas()
        return True

    def _redraw_canvas(self):
        """Redraw the entire canvas from drawing history."""
        # Clear the canvas
        self.canvas.clear()

        # Reset drawing state
        with self.canvas:
            Color(*self.current_color)

        # Redraw all items from history
        for entry in self.drawing_history:
            try:
                with self.canvas:
                    Color(*entry.get("color", (0, 0, 0, 1)))

                    entry_type = entry.get("type", "unknown")
                    width = entry.get("width", 2)

                    if (
                        entry_type in ["line_start", "line_complete"]
                        and "points" in entry
                    ):
                        # Redraw line with style support
                        style = entry.get("style", "solid")
                        if style == LineStyles.DASHED:
                            # Redraw as dashed line
                            dash_length = max(width * 3, 15)
                            gap_length = dash_length * 1.5
                            self._create_dashed_line_from_points(
                                entry["points"], dash_length, gap_length, width
                            )
                        else:
                            # Draw solid line
                            Line(points=entry["points"], width=width)

                    elif entry_type == "shape_complete":
                        # Redraw shape
                        mode = entry.get("drawing_mode", "line")

                        style = entry.get("style", "solid")

                        if style == LineStyles.DASHED:
                            # Redraw as dashed shape
                            dash_length = max(width * 3, 15)
                            gap_length = dash_length * 1.5

                            if mode == DrawingModes.STRAIGHT_LINE and "points" in entry:
                                self._create_dashed_line_from_points(
                                    entry["points"], dash_length, gap_length, width
                                )
                            elif (
                                mode == DrawingModes.CIRCLE and "circle_points" in entry
                            ):
                                self._create_dashed_line_from_points(
                                    entry["circle_points"],
                                    dash_length,
                                    gap_length,
                                    width,
                                )
                            elif (
                                mode == DrawingModes.RECTANGLE
                                and "rect_bounds" in entry
                            ):
                                self._create_dashed_rectangle(
                                    entry["rect_bounds"], dash_length, gap_length, width
                                )
                            elif mode == DrawingModes.TRIANGLE and "points" in entry:
                                self._create_dashed_line_from_points(
                                    entry["points"], dash_length, gap_length, width
                                )
                        else:
                            # Draw solid shapes
                            if mode == DrawingModes.STRAIGHT_LINE and "points" in entry:
                                Line(points=entry["points"], width=width)
                            elif (
                                mode == DrawingModes.CIRCLE and "circle_points" in entry
                            ):
                                Line(points=entry["circle_points"], width=width)
                            elif (
                                mode == DrawingModes.RECTANGLE
                                and "rect_bounds" in entry
                            ):
                                Line(rectangle=entry["rect_bounds"], width=width)
                            elif mode == DrawingModes.TRIANGLE and "points" in entry:
                                Line(points=entry["points"], width=width)

                    elif entry_type == "text_complete":
                        # Redraw text
                        text = entry.get("text", "")
                        font_size = entry.get("font_size", 24)
                        pos = entry.get("pos", (0, 0))
                        color = entry.get("color", (0, 0, 0, 1))

                        if text:
                            label = CoreLabel(
                                text=text, font_size=font_size, color=color
                            )
                            label.refresh()
                            texture = label.texture

                            Rectangle(texture=texture, pos=pos, size=texture.size)
            except Exception as e:
                # Skip problematic entries to prevent crashes
                print(f"Warning: Skipping drawing entry due to error: {e}")
                continue

    def can_undo(self):
        """Check if undo is possible."""
        return len(self.undo_stack) > 0

    def can_redo(self):
        """Check if redo is possible."""
        return len(self.redo_stack) > 0

    def _export_dashed_line_segments(
        self,
        points,
        dash_length,
        gap_length,
        draw,
        rgb_color,
        width_px,
        canvas_height,
        use_rounded_edges=True,
    ):
        """Create high-quality dashed line segments for export with continuous path dashing."""
        # Use the same continuous path algorithm as drawing for consistency
        self._export_dashed_continuous_path(
            points,
            dash_length,
            gap_length,
            draw,
            rgb_color,
            width_px,
            canvas_height,
            use_rounded_edges,
        )

    def _export_dashed_continuous_path(
        self,
        points,
        dash_length,
        gap_length,
        draw,
        rgb_color,
        width_px,
        canvas_height,
        use_rounded_edges=True,
    ):
        """Create dashed line segments along a continuous path for export - matches drawing behavior."""
        # Calculate total path length and create distance markers
        path_segments = []
        total_length = 0

        for i in range(0, len(points) - 2, 2):
            x1, y1 = float(points[i]), float(
                canvas_height - points[i + 1]
            )  # Flip Y coordinate
            x2, y2 = float(points[i + 2]), float(
                canvas_height - points[i + 3]
            )  # Flip Y coordinate

            dx = x2 - x1
            dy = y2 - y1
            segment_length = math.sqrt(dx * dx + dy * dy)

            if segment_length > 0:
                path_segments.append(
                    {
                        "start": (x1, y1),
                        "end": (x2, y2),
                        "length": segment_length,
                        "start_distance": total_length,
                        "end_distance": total_length + segment_length,
                    }
                )
                total_length += segment_length

        if total_length == 0:
            return

        # Create dashes along the total path length (same as drawing method)
        current_distance = 0
        dash_cycle = dash_length + gap_length

        while current_distance < total_length:
            dash_start = current_distance
            dash_end = min(current_distance + dash_length, total_length)

            # Get start point
            start_point = self._get_export_point_at_distance(path_segments, dash_start)
            # Get end point
            end_point = self._get_export_point_at_distance(path_segments, dash_end)

            # Draw the dash with appropriate edge style
            if start_point and end_point:
                if use_rounded_edges:
                    draw.line(
                        [start_point, end_point],
                        fill=rgb_color,
                        width=max(1, int(round(width_px))),
                        joint="curve",
                    )
                else:
                    draw.line(
                        [start_point, end_point],
                        fill=rgb_color,
                        width=max(1, int(round(width_px))),
                    )

            # Move to next dash
            current_distance += dash_cycle

    def _get_export_point_at_distance(self, path_segments, target_distance):
        """Get the x,y coordinates at a specific distance along the path for export."""
        for segment in path_segments:
            if segment["start_distance"] <= target_distance <= segment["end_distance"]:
                # Calculate position within this segment
                segment_progress = (
                    target_distance - segment["start_distance"]
                ) / segment["length"]

                x1, y1 = segment["start"]
                x2, y2 = segment["end"]

                # Linear interpolation
                x = x1 + (x2 - x1) * segment_progress
                y = y1 + (y2 - y1) * segment_progress

                return (x, y)

        return None

    def _export_dashed_line_segments_direct(
        self,
        points,
        dash_length,
        gap_length,
        draw,
        rgb_color,
        width_px,
        use_rounded_edges=True,
    ):
        """Create high-quality dashed line segments for export with pre-flipped coordinates."""
        # Use the same continuous path algorithm as drawing for consistency
        self._export_dashed_continuous_path_direct(
            points,
            dash_length,
            gap_length,
            draw,
            rgb_color,
            width_px,
            use_rounded_edges,
        )

    def _export_dashed_continuous_path_direct(
        self,
        points,
        dash_length,
        gap_length,
        draw,
        rgb_color,
        width_px,
        use_rounded_edges=True,
    ):
        """Create dashed line segments along a continuous path for export with pre-flipped coordinates."""
        # Calculate total path length and create distance markers
        path_segments = []
        total_length = 0

        for i in range(0, len(points) - 2, 2):
            x1, y1 = float(points[i]), float(points[i + 1])
            x2, y2 = float(points[i + 2]), float(points[i + 3])

            dx = x2 - x1
            dy = y2 - y1
            segment_length = math.sqrt(dx * dx + dy * dy)

            if segment_length > 0:
                path_segments.append(
                    {
                        "start": (x1, y1),
                        "end": (x2, y2),
                        "length": segment_length,
                        "start_distance": total_length,
                        "end_distance": total_length + segment_length,
                    }
                )
                total_length += segment_length

        if total_length == 0:
            return

        # Create dashes along the total path length (same as drawing method)
        current_distance = 0
        dash_cycle = dash_length + gap_length

        while current_distance < total_length:
            dash_start = current_distance
            dash_end = min(current_distance + dash_length, total_length)

            # Get start point
            start_point = self._get_export_point_at_distance(path_segments, dash_start)
            # Get end point
            end_point = self._get_export_point_at_distance(path_segments, dash_end)

            # Draw the dash with appropriate edge style
            if start_point and end_point:
                if use_rounded_edges:
                    draw.line(
                        [start_point, end_point],
                        fill=rgb_color,
                        width=max(1, int(round(width_px))),
                        joint="curve",
                    )
                else:
                    draw.line(
                        [start_point, end_point],
                        fill=rgb_color,
                        width=max(1, int(round(width_px))),
                    )

            # Move to next dash
            current_distance += dash_cycle

    def _export_smooth_line_segments(
        self, points, draw, rgb_color, width_px, canvas_height, use_rounded_edges=True
    ):
        """Create high-quality smooth line segments for export."""
        min_segment_length = 1.0

        # Process points in pairs to create line segments
        for i in range(0, len(points) - 2, 2):
            x1, y1 = float(points[i]), float(canvas_height - points[i + 1])
            x2, y2 = float(points[i + 2]), float(canvas_height - points[i + 3])

            # Calculate line length
            dx = x2 - x1
            dy = y2 - y1
            line_length = math.sqrt(dx * dx + dy * dy)

            # Skip very short segments to avoid artifacts
            if line_length < min_segment_length:
                continue

            # Draw line segment with appropriate edge style
            if use_rounded_edges:
                draw.line(
                    [(x1, y1), (x2, y2)],
                    fill=rgb_color,
                    width=max(1, int(round(width_px))),
                    joint="curve",
                )
            else:
                draw.line(
                    [(x1, y1), (x2, y2)],
                    fill=rgb_color,
                    width=max(1, int(round(width_px))),
                )

    def _export_smooth_line_segments_direct(
        self, points, draw, rgb_color, width_px, use_rounded_edges=True
    ):
        """Create high-quality smooth line segments for export with pre-flipped coordinates."""
        min_segment_length = 1.0

        # Process points in pairs to create line segments
        for i in range(0, len(points) - 2, 2):
            x1, y1 = float(points[i]), float(points[i + 1])
            x2, y2 = float(points[i + 2]), float(points[i + 3])

            # Calculate line length
            dx = x2 - x1
            dy = y2 - y1
            line_length = math.sqrt(dx * dx + dy * dy)

            # Skip very short segments to avoid artifacts
            if line_length < min_segment_length:
                continue

            # Draw line segment with appropriate edge style
            if use_rounded_edges:
                draw.line(
                    [(x1, y1), (x2, y2)],
                    fill=rgb_color,
                    width=max(1, int(round(width_px))),
                    joint="curve",
                )
            else:
                draw.line(
                    [(x1, y1), (x2, y2)],
                    fill=rgb_color,
                    width=max(1, int(round(width_px))),
                )

    def _export_shape_outline(
        self,
        points,
        draw,
        rgb_color,
        width_px,
        canvas_height,
        is_dashed=False,
        dash_length=None,
        gap_length=None,
        use_rounded_edges=True,
    ):
        """Export shape outline with consistent quality."""
        if not points or len(points) < 4:
            return

        # Points are already scaled, just need to flip Y coordinates for export
        flipped_points = []
        for i in range(0, len(points), 2):
            if i + 1 < len(points):
                x = float(points[i])
                y = float(canvas_height - points[i + 1])
                flipped_points.extend([x, y])

        if is_dashed and dash_length and gap_length:
            # For dashed lines, pass the flipped points directly (no double flipping)
            self._export_dashed_line_segments_direct(
                flipped_points,
                dash_length,
                gap_length,
                draw,
                rgb_color,
                width_px,
                use_rounded_edges,
            )
        else:
            # For solid lines, pass the flipped points directly (no double flipping)
            self._export_smooth_line_segments_direct(
                flipped_points, draw, rgb_color, width_px, use_rounded_edges
            )

    def export_to_png(self, filename, scale_factor=2):
        """
        Export the canvas to a high-quality PNG file with white background.

        Args:
            filename (str): The path where to save the PNG file
            scale_factor (int): Scaling factor for higher resolution export (default: 2x)

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Calculate high-resolution dimensions
            base_width, base_height = int(self.size[0]), int(self.size[1])
            export_width = base_width * scale_factor
            export_height = base_height * scale_factor

            # Create a high-resolution white background image with anti-aliasing
            img = Image.new("RGBA", (export_width, export_height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Draw all entries from history
            for entry in self.drawing_history:
                try:
                    color = entry.get("color", (0, 0, 0, 1))
                    # Convert RGBA to RGB with proper alpha handling
                    alpha = int(color[3] * 255) if len(color) > 3 else 255
                    rgb_color = (
                        int(color[0] * 255),
                        int(color[1] * 255),
                        int(color[2] * 255),
                        alpha,
                    )

                    entry_type = entry.get("type", "unknown")
                    base_width_px = entry.get("width", 2)
                    # Scale line width for high-resolution export
                    width_px = max(1, int(round(base_width_px * scale_factor)))
                    style = entry.get("style", "solid")

                    if (
                        entry_type in ["line_start", "line_complete"]
                        and "points" in entry
                    ):
                        # Draw freehand line
                        points = entry["points"]
                        if len(points) >= 4:
                            # Scale points for high-resolution export
                            scaled_points = [p * scale_factor for p in points]

                            if style == LineStyles.DASHED:
                                # Draw dashed line with scaled parameters
                                dash_length = max(base_width_px * 3, 15) * scale_factor
                                gap_length = dash_length * 1.5
                                # Keep rounded edges for freehand lines (default behavior)
                                self._export_dashed_line_segments(
                                    scaled_points,
                                    dash_length,
                                    gap_length,
                                    draw,
                                    rgb_color,
                                    width_px,
                                    export_height,
                                    True,
                                )
                            else:
                                # Draw solid line with anti-aliasing (keep rounded edges for freehand lines)
                                self._export_smooth_line_segments(
                                    scaled_points,
                                    draw,
                                    rgb_color,
                                    width_px,
                                    export_height,
                                    True,
                                )

                    elif entry_type == "shape_complete":
                        # Draw shapes with consistent quality
                        mode = entry.get("drawing_mode", "line")
                        is_dashed = style == LineStyles.DASHED
                        dash_length = (
                            max(base_width_px * 3, 15) * scale_factor
                            if is_dashed
                            else None
                        )
                        gap_length = dash_length * 1.5 if is_dashed else None

                        if mode == "rectangle" and "rect_bounds" in entry:
                            # Draw rectangle outline
                            x, y, w, h = entry["rect_bounds"]
                            # Scale rectangle bounds
                            x, y, w, h = (
                                x * scale_factor,
                                y * scale_factor,
                                w * scale_factor,
                                h * scale_factor,
                            )

                            # Create points for rectangle outline (clockwise)
                            rect_points = [
                                x,
                                y + h,
                                x + w,
                                y + h,  # Top side
                                x + w,
                                y + h,
                                x + w,
                                y,  # Right side
                                x + w,
                                y,
                                x,
                                y,  # Bottom side
                                x,
                                y,
                                x,
                                y + h,  # Left side
                            ]
                            # For dashed rectangles, do not round the edges
                            use_rounded_edges = not is_dashed
                            self._export_shape_outline(
                                rect_points,
                                draw,
                                rgb_color,
                                width_px,
                                export_height,
                                is_dashed,
                                dash_length,
                                gap_length,
                                use_rounded_edges,
                            )

                        elif mode in ["line", "straight_line"] and "points" in entry:
                            # Draw straight line
                            points = entry["points"]
                            if len(points) >= 4:
                                scaled_points = [p * scale_factor for p in points]
                                # Keep rounded edges for lines (default behavior)
                                self._export_shape_outline(
                                    scaled_points,
                                    draw,
                                    rgb_color,
                                    width_px,
                                    export_height,
                                    is_dashed,
                                    dash_length,
                                    gap_length,
                                    True,
                                )

                        elif mode == "circle" and "circle_points" in entry:
                            # Draw circle outline
                            points = entry["circle_points"]
                            if len(points) >= 4:
                                scaled_points = [p * scale_factor for p in points]
                                # Keep rounded edges for circles (default behavior)
                                self._export_shape_outline(
                                    scaled_points,
                                    draw,
                                    rgb_color,
                                    width_px,
                                    export_height,
                                    is_dashed,
                                    dash_length,
                                    gap_length,
                                    True,
                                )

                        elif mode == "triangle" and "points" in entry:
                            # Draw triangle outline
                            points = entry["points"]
                            if len(points) >= 6:
                                scaled_points = [p * scale_factor for p in points]
                                # For dashed triangles, do not round the edges
                                use_rounded_edges = not is_dashed
                                self._export_shape_outline(
                                    scaled_points,
                                    draw,
                                    rgb_color,
                                    width_px,
                                    export_height,
                                    is_dashed,
                                    dash_length,
                                    gap_length,
                                    use_rounded_edges,
                                )

                    elif entry_type == "text_complete":
                        # Draw text with proper scaling and positioning
                        text = entry.get("text", "")
                        pos = entry.get("pos", (0, 0))
                        font_size = entry.get("font_size", 24)

                        if text and pos:
                            # Scale position and font size - fix Y coordinate flipping
                            x = pos[0] * scale_factor
                            y = (export_height - (pos[1] * scale_factor)) - (
                                font_size * scale_factor
                            )
                            scaled_font_size = max(12, int(font_size * scale_factor))

                            try:
                                # Try to use a system font for better text rendering
                                font = ImageFont.truetype("Arial.ttf", scaled_font_size)
                            except (OSError, IOError):
                                try:
                                    # Fallback to default font
                                    font = ImageFont.load_default()
                                except:
                                    # If all else fails, draw a text placeholder rectangle
                                    text_width = len(text) * (scaled_font_size // 2)
                                    text_height = scaled_font_size
                                    draw.rectangle(
                                        [x, y - text_height, x + text_width, y],
                                        outline=rgb_color,
                                        width=max(1, scale_factor),
                                    )
                                    continue

                            # Draw the actual text
                            draw.text((x, y), text, fill=rgb_color, font=font)

                except Exception as e:
                    print(f"Warning: Skipping drawing entry during export: {e}")
                    continue

            # Convert to RGB for final output (removes alpha channel)
            final_img = Image.new("RGB", (export_width, export_height), (255, 255, 255))
            final_img.paste(img, (0, 0), img)

            # Save with high quality settings
            final_img.save(filename, "PNG", optimize=True, compress_level=6)
            return True

        except Exception as e:
            print(f"Export failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _export_simple_white_background(self, filename):
        """Export with white background using simpler method."""
        try:
            # Create FBO for final composition
            final_fbo = Fbo(size=self.size)

            # Clear the FBO and set white background
            with final_fbo:
                ClearColor(1, 1, 1, 1)  # White background
                ClearBuffers()

                # Draw white background rectangle to ensure it's there
                Color(1, 1, 1, 1)
                Rectangle(pos=(0, 0), size=self.size)

                # Then draw all canvas content on top
                for instruction in self.canvas.children:
                    final_fbo.add(instruction)

            # Save the texture
            final_fbo.texture.save(filename)
            return True

        except Exception as e:
            print(f"Simple export failed: {e}")
            return False

    def export_to_png_simple(self, filename):
        """Simple fallback export method."""
        try:
            # Use widget's export_to_png method if available
            if hasattr(self, "export_to_png"):
                # This is Kivy's built-in widget export method
                super().export_to_png(filename)
            else:
                # Manual texture capture
                from kivy.graphics.texture import Texture

                texture = Texture.create(size=self.size)
                fbo = Fbo(size=self.size)
                with fbo:
                    Color(1, 1, 1, 1)  # White background
                    Rectangle(size=self.size)
                    # Copy current canvas
                    for instruction in self.canvas.children:
                        fbo.add(instruction)
                fbo.texture.save(filename)
        except Exception as e:
            print(f"Simple export failed: {e}")

    def export_canvas_screenshot(self, filename, scale_factor=1):
        """
        Export the canvas as a literal screenshot of the displayed pixels.

        This method captures the actual rendered pixels from the screen buffer,
        exactly like taking a system screenshot of just the canvas area.

        Args:
            filename (str): The path where to save the PNG file
            scale_factor (int): Scaling factor for higher resolution (default: 1x)

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            from kivy.graphics.opengl import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE
            from kivy.core.window import Window
            import numpy as np
            from PIL import Image

            # Get the canvas position and size in window coordinates
            canvas_x = int(self.x)
            canvas_y = int(self.y)
            canvas_width = int(self.width)
            canvas_height = int(self.height)

            # Convert to OpenGL coordinates (flip Y axis)
            window_height = int(Window.height)
            gl_y = window_height - canvas_y - canvas_height

            print(
                f"Capturing canvas area: x={canvas_x}, y={gl_y}, w={canvas_width}, h={canvas_height}"
            )

            # Read pixels directly from the OpenGL framebuffer
            pixels = glReadPixels(
                canvas_x, gl_y, canvas_width, canvas_height, GL_RGBA, GL_UNSIGNED_BYTE
            )

            # Convert to numpy array
            pixel_array = np.frombuffer(pixels, dtype=np.uint8)
            pixel_array = pixel_array.reshape((canvas_height, canvas_width, 4))

            # Flip vertically (OpenGL has origin at bottom-left, images at top-left)
            pixel_array = np.flipud(pixel_array)

            # Convert RGBA to RGB with white background
            rgb_array = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
            alpha = pixel_array[:, :, 3:4] / 255.0

            # Blend with white background
            rgb_array[:, :, 0] = pixel_array[:, :, 0] * alpha[:, :, 0] + 255 * (
                1 - alpha[:, :, 0]
            )
            rgb_array[:, :, 1] = pixel_array[:, :, 1] * alpha[:, :, 0] + 255 * (
                1 - alpha[:, :, 0]
            )
            rgb_array[:, :, 2] = pixel_array[:, :, 2] * alpha[:, :, 0] + 255 * (
                1 - alpha[:, :, 0]
            )

            # Create PIL image
            image = Image.fromarray(rgb_array, "RGB")

            # Apply scaling if requested
            if scale_factor != 1:
                new_width = canvas_width * scale_factor
                new_height = canvas_height * scale_factor
                image = image.resize((new_width, new_height), Image.LANCZOS)

            # Save the image
            image.save(filename, "PNG", optimize=True)

            print(f"Canvas screenshot exported successfully to: {filename}")
            return True

        except Exception as e:
            print(f"Screenshot export failed: {e}")
            import traceback

            traceback.print_exc()
            return False

"""
Custom button widgets for PaintApp.

Contains specialized button implementations for color selection,
line width selection, and other UI interactions.
"""

from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line


class RadioButton(ToggleButton):
    """
    A radio button that ensures only one button in a group is selected.

    This extends the standard ToggleButton to provide radio button behavior
    where selecting one button deselects others in the same group.
    """

    def _do_press(self):
        """Handle button press, ensuring radio button behavior."""
        if self.state == "normal":
            ToggleButtonBehavior._do_press(self)


class ColorButton(RadioButton):
    """
    A specialized radio button for color selection.

    This button is designed to display and select colors in the paint application.
    It shows the actual color as its background and displays a red border when selected.
    """

    # Kivy property to make color_value accessible in KV files
    color_value = ListProperty([0.8, 0.8, 0.8, 1])

    def __init__(self, color=None, **kwargs):
        """
        Initialize the color button.

        Args:
            color (tuple): RGBA color tuple (r, g, b, a)
            **kwargs: Additional keyword arguments for the parent class
        """
        super().__init__(**kwargs)
        
        # Remove default button styling
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)  # Transparent
        self.text = ''  # No text on color buttons
        
        # Set the color value if provided
        if color:
            self.color_value = list(color)
        
        # Initialize graphics
        self.color_rect = None
        self.border_color = None
        self.border_line = None
        
        # Bind to events
        self.bind(size=self._update_graphics)
        self.bind(pos=self._update_graphics)
        self.bind(state=self._update_graphics)
        
        # Schedule initial graphics setup
        Clock.schedule_once(self._setup_graphics, 0)

    def _setup_graphics(self, dt):
        """Set up the graphics for the color button."""
        with self.canvas.before:
            # Color rectangle
            self.color_instruction = Color(*self.color_value)
            self.color_rect = Rectangle(pos=self.pos, size=self.size)
            
            # Border - thinner lines
            border_color = (1, 0, 0, 1) if self.state == 'down' else (0.3, 0.3, 0.3, 1)
            self.border_color = Color(*border_color)
            border_width = 2 if self.state == 'down' else 1  # Reduced from 3/2 to 2/1
            self.border_line = Line(rectangle=(*self.pos, *self.size), width=border_width)

    def _update_graphics(self, *args):
        """Update the graphics when size, position, or state changes."""
        if self.color_rect and self.border_line:
            # Update color
            self.color_instruction.rgba = self.color_value
            
            # Update rectangle position and size
            self.color_rect.pos = self.pos
            self.color_rect.size = self.size
            
            # Update border - thinner lines
            border_color = (1, 0, 0, 1) if self.state == 'down' else (0.3, 0.3, 0.3, 1)
            self.border_color.rgba = border_color
            border_width = 2 if self.state == 'down' else 1  # Reduced from 3/2 to 2/1
            self.border_line.rectangle = (*self.pos, *self.size)
            self.border_line.width = border_width

    def on_color_value(self, instance, value):
        """Called when color_value property changes."""
        if hasattr(self, 'color_instruction') and self.color_instruction:
            self.color_instruction.rgba = value

    def get_color(self):
        """
        Get the color value associated with this button.

        Returns:
            tuple: RGBA color tuple
        """
        return tuple(self.color_value)

    def set_color(self, color):
        """
        Set the color value and update the button appearance.

        Args:
            color (tuple): RGBA color tuple (r, g, b, a)
        """
        self.color_value = list(color)


class LineWidthButton(RadioButton):
    """
    A specialized radio button for line width selection.

    This button represents different line widths and can display
    a visual representation of the width it represents.
    """

    def __init__(self, width_name=None, width_value=None, **kwargs):
        """
        Initialize the line width button.

        Args:
            width_name (str): Display name for the width (e.g., "Thin", "Normal")
            width_value (int): Actual width value in pixels
            **kwargs: Additional keyword arguments for the parent class
        """
        super().__init__(**kwargs)
        self.width_name = width_name or "Normal"
        self.width_value = width_value or 2

        # Set the button text to show line thickness using simple characters
        width_symbols = {
            "Thin": "-",     # Simple dash (thin)
            "Normal": "=",   # Equals sign (medium)
            "Thick": "#",    # Hash symbol (thick)
        }
        self.text = width_symbols.get(self.width_name, self.width_name)

    def get_width(self):
        """
        Get the width value associated with this button.

        Returns:
            int: Line width in pixels
        """
        return self.width_value

    def get_width_name(self):
        """
        Get the display name of the width.

        Returns:
            str: Width name
        """
        return self.width_name

    def set_width(self, width_name, width_value):
        """
        Set the width name and value.

        Args:
            width_name (str): Display name for the width
            width_value (int): Actual width value in pixels
        """
        self.width_name = width_name
        self.width_value = width_value
        
        # Update button text with appropriate symbol
        width_symbols = {
            "Thin": "-",     # Simple dash (thin)
            "Normal": "=",   # Equals sign (medium)
            "Thick": "#",    # Hash symbol (thick)
        }
        self.text = width_symbols.get(width_name, width_name)


class DrawingModeButton(RadioButton):
    """
    A specialized radio button for drawing mode selection.

    This button represents different drawing modes (line, circle, triangle, rectangle).
    """

    def __init__(self, mode=None, **kwargs):
        """
        Initialize the drawing mode button.

        Args:
            mode (str): Drawing mode (e.g., "line", "circle", "triangle", "rectangle")
            **kwargs: Additional keyword arguments for the parent class
        """
        super().__init__(**kwargs)
        self.drawing_mode = mode or "line"

        # Set the button text using simple, reliable characters
        mode_labels = {
            "line": "/",  # Simple slash for line
            "straight_line": "|",  # Vertical bar for straight line
            "circle": "O",  # Letter O for circle
            "triangle": "^",  # Caret for triangle
            "rectangle": "[]",  # Square brackets for rectangle
            "text": "T",  # Letter T for text
        }
        self.text = mode_labels.get(self.drawing_mode, self.drawing_mode.title())

    def get_mode(self):
        """
        Get the drawing mode associated with this button.

        Returns:
            str: Drawing mode
        """
        return self.drawing_mode

    def set_mode(self, mode):
        """
        Set the drawing mode.

        Args:
            mode (str): Drawing mode
        """
        self.drawing_mode = mode
        mode_labels = {
            "line": "/",  # Simple slash for line
            "straight_line": "|",  # Vertical bar for straight line
            "circle": "O",  # Letter O for circle
            "triangle": "^",  # Caret for triangle
            "rectangle": "[]",  # Square brackets for rectangle
            "text": "T",  # Letter T for text
        }
        self.text = mode_labels.get(mode, mode.title())


class LineStyleButton(RadioButton):
    """
    A specialized radio button for line style selection (solid/dashed).

    This button toggles between solid and dashed line styles.
    """

    def __init__(self, style=None, **kwargs):
        """
        Initialize the line style button.

        Args:
            style (str): Line style ("solid" or "dashed")
            **kwargs: Additional keyword arguments for the parent class
        """
        super().__init__(**kwargs)
        self.line_style = style or "solid"

        # Set the button text - use ":" for dashed lines as requested
        if self.line_style == "dashed":
            self.text = ":"
        else:
            self.text = "—"  # Em dash for solid lines

    def get_style(self):
        """
        Get the line style associated with this button.

        Returns:
            str: Line style ("solid" or "dashed")
        """
        return self.line_style

    def set_style(self, style):
        """
        Set the line style.

        Args:
            style (str): Line style ("solid" or "dashed")
        """
        self.line_style = style
        if style == "dashed":
            self.text = ":"
        else:
            self.text = "—"  # Em dash for solid lines

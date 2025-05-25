"""
Custom button widgets for PaintApp.

Contains specialized button implementations for color selection,
line width selection, and other UI interactions.
"""

from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton


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
    It can be styled to show the color it represents.
    """

    def __init__(self, color=None, **kwargs):
        """
        Initialize the color button.

        Args:
            color (tuple): RGBA color tuple (r, g, b, a)
            **kwargs: Additional keyword arguments for the parent class
        """
        super().__init__(**kwargs)
        self.color_value = color or (0, 0, 0, 1)

        # Set the button's background color to match the color it represents
        if color:
            self.background_color = color

    def get_color(self):
        """
        Get the color value associated with this button.

        Returns:
            tuple: RGBA color tuple
        """
        return self.color_value

    def set_color(self, color):
        """
        Set the color value and update the button appearance.

        Args:
            color (tuple): RGBA color tuple (r, g, b, a)
        """
        self.color_value = color
        self.background_color = color


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

        # Set the button text to the width name
        self.text = self.width_name

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
        self.text = width_name

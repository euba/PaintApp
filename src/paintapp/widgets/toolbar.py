"""
Toolbar widget for PaintApp.

Contains the main toolbar with color selection, line width controls,
and other painting tools.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from .buttons import ColorButton, LineWidthButton
from ..utils.constants import Colors, LineWidths


class Toolbar(BoxLayout):
    """
    Main toolbar widget containing painting tools and controls.

    This widget organizes color selection, line width controls,
    and action buttons in a convenient toolbar layout.
    """

    def __init__(self, canvas_widget=None, **kwargs):
        """
        Initialize the toolbar.

        Args:
            canvas_widget: Reference to the canvas widget for tool interactions
            **kwargs: Additional keyword arguments for BoxLayout
        """
        super().__init__(**kwargs)
        self.canvas_widget = canvas_widget
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 40

        self._setup_toolbar()

    def _setup_toolbar(self):
        """Set up the toolbar with all controls."""
        # Color selection section
        self._add_color_section()

        # Line width section
        self._add_line_width_section()

        # Action buttons section
        self._add_action_buttons()

    def _add_color_section(self):
        """Add color selection buttons to the toolbar."""
        # Color label
        color_label = Label(text="Colors:", size_hint_x=None, width=60, height=40)
        self.add_widget(color_label)

        # Color buttons
        colors = Colors.get_palette()
        self.color_buttons = []

        for i, color in enumerate(colors):
            color_btn = ColorButton(
                color=color, group="colors", size_hint_x=None, width=30, height=30
            )
            color_btn.bind(on_press=self._on_color_selected)

            # Set the first color as default
            if i == 0:
                color_btn.state = "down"

            self.color_buttons.append(color_btn)
            self.add_widget(color_btn)

    def _add_line_width_section(self):
        """Add line width selection buttons to the toolbar."""
        # Separator
        separator = Label(text="|", size_hint_x=None, width=20)
        self.add_widget(separator)

        # Line width label
        width_label = Label(text="Width:", size_hint_x=None, width=50, height=40)
        self.add_widget(width_label)

        # Line width buttons
        width_map = LineWidths.get_width_map()
        self.width_buttons = []

        for i, (name, value) in enumerate(width_map.items()):
            width_btn = LineWidthButton(
                width_name=name,
                width_value=value,
                group="widths",
                size_hint_x=None,
                width=80,
                height=30,
            )
            width_btn.bind(on_press=self._on_width_selected)

            # Set "Normal" as default
            if name == "Normal":
                width_btn.state = "down"

            self.width_buttons.append(width_btn)
            self.add_widget(width_btn)

    def _add_action_buttons(self):
        """Add action buttons to the toolbar."""
        # Separator
        separator = Label(text="|", size_hint_x=None, width=20)
        self.add_widget(separator)

        # Clear button
        clear_btn = Button(text="Clear", size_hint_x=None, width=80, height=30)
        clear_btn.bind(on_press=self._on_clear_pressed)
        self.add_widget(clear_btn)

        # Spacer to push everything to the left
        spacer = Label(text="")
        self.add_widget(spacer)

    def _on_color_selected(self, button):
        """
        Handle color selection.

        Args:
            button (ColorButton): The selected color button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "set_color"):
            color = button.get_color()
            self.canvas_widget.set_color(color)

    def _on_width_selected(self, button):
        """
        Handle line width selection.

        Args:
            button (LineWidthButton): The selected width button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "set_line_width"):
            width_name = button.get_width_name()
            self.canvas_widget.set_line_width(width_name)

    def _on_clear_pressed(self, button):
        """
        Handle clear button press.

        Args:
            button (Button): The clear button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "clear_screen"):
            self.canvas_widget.clear_screen()

    def set_canvas_widget(self, canvas_widget):
        """
        Set the canvas widget reference.

        Args:
            canvas_widget: The canvas widget to control
        """
        self.canvas_widget = canvas_widget

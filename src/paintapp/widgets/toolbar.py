"""
Toolbar widget for PaintApp.

Contains the main toolbar with color selection, line width controls,
and other painting tools.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import os
from datetime import datetime

from .buttons import ColorButton, LineWidthButton, DrawingModeButton, LineStyleButton
from ..utils.constants import Colors, LineWidths, DrawingModes, LineStyles


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
        self.height = 50  # Increased height for better visibility
        self.spacing = 5  # Add spacing between elements
        self.padding = [5, 5, 5, 5]  # Add padding around the toolbar

        self._setup_toolbar()

    def _setup_toolbar(self):
        """Set up the toolbar with all controls."""
        # Export button section (far left)
        self._add_export_section()

        # Drawing mode section
        self._add_drawing_mode_section()

        # Color selection section
        self._add_color_section()

        # Line width section
        self._add_line_width_section()

        # Action buttons section
        self._add_action_buttons()

    def _add_export_section(self):
        """Add export button to the toolbar."""
        # Export section container
        export_section = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.10,  # 10% of horizontal space for export button
            spacing=3,
        )

        # Export button with bold text
        export_btn = Button(
            text="[b]Export[/b]", markup=True, size_hint_x=1.0, size_hint_y=1.0
        )
        export_btn.bind(on_press=self._on_export_pressed)
        export_section.add_widget(export_btn)

        self.add_widget(export_section)

    def _add_drawing_mode_section(self):
        """Add drawing mode selection buttons to the toolbar."""
        # Drawing mode section container
        mode_section = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.22,  # Reduced from 25% to make room for export button
            spacing=3,
        )

        # Drawing mode buttons container (now takes full width)
        modes_container = BoxLayout(
            orientation="horizontal",
            size_hint_x=1.0,  # Full width of the mode section
            spacing=2,
        )

        # Drawing mode buttons
        modes = DrawingModes.get_modes()
        self.mode_buttons = []

        for i, mode in enumerate(modes):
            mode_btn = DrawingModeButton(
                mode=mode,
                group="drawing_modes",
                size_hint_x=1.0 / len(modes),  # Equal distribution
                size_hint_y=1.0,
            )
            mode_btn.bind(on_press=self._on_mode_selected)

            # Set "line" as default
            if mode == "line":
                mode_btn.state = "down"

            self.mode_buttons.append(mode_btn)
            modes_container.add_widget(mode_btn)

        mode_section.add_widget(modes_container)
        self.add_widget(mode_section)

    def _add_color_section(self):
        """Add color selection buttons to the toolbar."""
        # Color section container
        color_section = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.25,  # Reduced to accommodate new spacer
            spacing=3,
        )

        # Color buttons container (now takes more width)
        colors_container = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.8,  # Increased from 60% to 80%
            spacing=4,  # Increased spacing between buttons
        )

        # Color buttons
        colors = Colors.get_palette()
        self.color_buttons = []

        for i, color in enumerate(colors):
            color_btn = ColorButton(
                color=color,
                group="colors",
                size_hint_x=1.0
                / len(colors),  # Equal distribution within smaller container
                size_hint_y=1.0,
            )
            color_btn.bind(on_press=self._on_color_selected)

            # Set the first color as default
            if i == 0:
                color_btn.state = "down"

            self.color_buttons.append(color_btn)
            colors_container.add_widget(color_btn)

        color_section.add_widget(colors_container)

        # Add invisible spacer to center the color buttons
        spacer = Label(text="", size_hint_x=0.1, color=(0, 0, 0, 0))  # Transparent text
        color_section.add_widget(spacer)

        self.add_widget(color_section)

    def _add_line_width_section(self):
        """Add line width selection buttons and line style button to the toolbar."""
        # Line width section container
        width_section = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.20,  # Increased to accommodate line style button
            spacing=3,
        )

        # Line width buttons container (now takes more width)
        widths_container = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.75,  # Increased from 60% to 75%
            spacing=2,
        )

        # Line width buttons
        width_map = LineWidths.get_width_map()
        self.width_buttons = []

        for i, (name, value) in enumerate(width_map.items()):
            width_btn = LineWidthButton(
                width_name=name,
                width_value=value,
                group="widths",
                size_hint_x=1.0 / len(width_map),  # Equal distribution
                size_hint_y=1.0,
            )
            width_btn.bind(on_press=self._on_width_selected)

            # Set "Normal" as default (middle option)
            if name == "Normal":
                width_btn.state = "down"

            self.width_buttons.append(width_btn)
            widths_container.add_widget(width_btn)

        width_section.add_widget(widths_container)

        # Line style button (dashed/solid toggle)
        self.line_style_button = LineStyleButton(
            style="solid",  # Default to solid
            group="line_style",
            size_hint_x=0.25,  # 25% of the width section
            size_hint_y=1.0,
        )
        self.line_style_button.bind(on_press=self._on_line_style_selected)
        width_section.add_widget(self.line_style_button)

        self.add_widget(width_section)

        # Add invisible spacer between line width and undo/redo buttons
        spacer_width_to_undo = Label(
            text="", size_hint_x=0.08, color=(0, 0, 0, 0)  # Transparent text
        )
        self.add_widget(spacer_width_to_undo)

    def _add_action_buttons(self):
        """Add action buttons to the toolbar."""
        # Undo/Redo section
        undo_redo_section = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.15,  # Smaller section for undo/redo
            spacing=2,
        )

        # Undo button
        undo_btn = Button(
            text="<-",  # Back arrow
            size_hint_x=0.5,  # Half of undo/redo section
            size_hint_y=1.0,
        )
        undo_btn.bind(on_press=self._on_undo_pressed)
        undo_redo_section.add_widget(undo_btn)

        # Redo button
        redo_btn = Button(
            text="->",  # Forward arrow
            size_hint_x=0.5,  # Half of undo/redo section
            size_hint_y=1.0,
        )
        redo_btn.bind(on_press=self._on_redo_pressed)
        undo_redo_section.add_widget(redo_btn)

        self.add_widget(undo_redo_section)

        # Invisible spacer between undo/redo and clear button
        spacer = Label(
            text="", size_hint_x=0.05, color=(0, 0, 0, 0)  # Transparent text
        )
        self.add_widget(spacer)

        # Clear button section (same size as export)
        clear_section = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.10,  # Same size as export button
            spacing=3,
        )

        # Clear button with bold text (same size as export)
        clear_btn = Button(
            text="[b]Clear[/b]", markup=True, size_hint_x=1.0, size_hint_y=1.0
        )
        clear_btn.bind(on_press=self._on_clear_pressed)
        clear_section.add_widget(clear_btn)

        self.add_widget(clear_section)

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

    def _on_mode_selected(self, button):
        """
        Handle drawing mode selection.

        Args:
            button (DrawingModeButton): The selected mode button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "set_drawing_mode"):
            mode = button.get_mode()
            self.canvas_widget.set_drawing_mode(mode)

    def _on_line_style_selected(self, button):
        """
        Handle line style selection (toggle between solid and dashed).

        Args:
            button (LineStyleButton): The line style button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "set_line_style"):
            # Toggle between solid and dashed
            current_style = button.get_style()
            if current_style == "solid":
                new_style = "dashed"
            else:
                new_style = "solid"

            button.set_style(new_style)
            self.canvas_widget.set_line_style(new_style)

    def _on_undo_pressed(self, button):
        """
        Handle undo button press.

        Args:
            button (Button): The undo button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "undo"):
            self.canvas_widget.undo()

    def _on_redo_pressed(self, button):
        """
        Handle redo button press.

        Args:
            button (Button): The redo button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "redo"):
            self.canvas_widget.redo()

    def _on_clear_pressed(self, button):
        """
        Handle clear button press.

        Args:
            button (Button): The clear button
        """
        if self.canvas_widget and hasattr(self.canvas_widget, "clear_screen"):
            self.canvas_widget.clear_screen()

    def _on_export_pressed(self, button):
        """
        Handle export button press.

        Args:
            button (Button): The export button
        """
        self._show_export_dialog()

    def _show_export_dialog(self):
        """Show file dialog for exporting canvas to PNG."""
        # Create the file chooser content
        content = BoxLayout(orientation="vertical", spacing=15, padding=20)

        # File chooser with bigger font
        filechooser = FileChooserIconView(
            path=os.path.expanduser("~/Desktop"),  # Start at Desktop
            dirselect=False,
            filters=["*.png"],
        )
        content.add_widget(filechooser)

        # Filename input with much bigger font and better spacing
        filename_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=100, spacing=25
        )

        filename_label = Label(
            text="Filename:",
            size_hint_x=None,
            width=180,
            font_size=32,
            text_size=(180, None),
            halign="left",
            valign="middle",
        )
        filename_layout.add_widget(filename_label)

        # Generate default filename with current date
        current_date = datetime.now().strftime("%d-%m-%Y")
        default_filename = f"{current_date}_scratch.png"

        filename_input = TextInput(
            text=default_filename,
            multiline=False,
            size_hint_y=None,
            height=70,
            font_size=28,
            padding=[20, 20],
        )
        filename_layout.add_widget(filename_input)
        content.add_widget(filename_layout)

        # Quality selection with bigger font
        quality_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=80, spacing=25
        )

        quality_label = Label(
            text="Quality:",
            size_hint_x=None,
            width=180,
            font_size=28,
            text_size=(180, None),
            halign="left",
            valign="middle",
        )
        quality_layout.add_widget(quality_label)

        # Quality buttons
        quality_buttons_layout = BoxLayout(orientation="horizontal", spacing=10)

        standard_btn = ToggleButton(
            text="Standard (1x)",
            group="quality",
            state="down",  # Default selection
            font_size=24,
        )
        high_btn = ToggleButton(text="High (2x)", group="quality", font_size=24)
        ultra_btn = ToggleButton(text="Ultra (4x)", group="quality", font_size=24)

        quality_buttons_layout.add_widget(standard_btn)
        quality_buttons_layout.add_widget(high_btn)
        quality_buttons_layout.add_widget(ultra_btn)
        quality_layout.add_widget(quality_buttons_layout)
        content.add_widget(quality_layout)

        # Buttons with much bigger font
        button_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=100, spacing=25
        )

        cancel_btn = Button(text="Cancel", size_hint_x=0.5, font_size=32)
        save_btn = Button(text="Save", size_hint_x=0.5, font_size=32)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        content.add_widget(button_layout)

        # Create popup with much bigger title font
        popup = Popup(
            title="Export Canvas to PNG",
            content=content,
            size_hint=(0.95, 0.95),
            auto_dismiss=False,
            title_size=36,
        )

        # Button handlers
        def on_cancel(instance):
            popup.dismiss()

        def on_save(instance):
            # Get selected path and filename
            if filechooser.selection:
                folder_path = os.path.dirname(filechooser.selection[0])
            else:
                folder_path = filechooser.path

            filename = filename_input.text.strip()
            if not filename:
                # Fallback to date-based filename if empty
                current_date = datetime.now().strftime("%d-%m-%Y")
                filename = f"{current_date}_scratch.png"
            elif not filename.lower().endswith(".png"):
                filename += ".png"

            full_path = os.path.join(folder_path, filename)

            # Determine scale factor based on quality selection
            scale_factor = 1  # Default
            if high_btn.state == "down":
                scale_factor = 2
            elif ultra_btn.state == "down":
                scale_factor = 4

            # Export the canvas with selected quality
            if self.canvas_widget and hasattr(self.canvas_widget, "export_to_png"):
                success = self.canvas_widget.export_to_png(full_path, scale_factor)
                if success:
                    quality_text = (
                        f"{scale_factor}x" if scale_factor > 1 else "standard"
                    )
                    print(
                        f"Canvas exported successfully to: {full_path} (Quality: {quality_text})"
                    )
                else:
                    print(f"Failed to export canvas to: {full_path}")

            popup.dismiss()

        cancel_btn.bind(on_press=on_cancel)
        save_btn.bind(on_press=on_save)

        popup.open()

    def set_canvas_widget(self, canvas_widget):
        """
        Set the canvas widget reference.

        Args:
            canvas_widget: The canvas widget to control
        """
        self.canvas_widget = canvas_widget

"""
Text input widget for PaintApp.

Contains a popup text input dialog for entering text to be drawn on the canvas.
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label


class TextInputDialog(Popup):
    """
    A popup dialog for text input when using the text tool.
    
    This dialog appears when the user clicks on the canvas in text mode,
    allowing them to enter text that will be drawn at the clicked position.
    """

    def __init__(self, callback=None, **kwargs):
        """
        Initialize the text input dialog.
        
        Args:
            callback: Function to call when text is confirmed
            **kwargs: Additional keyword arguments for Popup
        """
        super().__init__(**kwargs)
        
        self.callback = callback
        self.title = "Enter Text"
        self.size_hint = (0.6, 0.4)
        self.auto_dismiss = False
        
        # Create the main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Add instruction label
        instruction = Label(
            text="Enter the text you want to add:",
            size_hint_y=None,
            height=30,
            text_size=(None, None)
        )
        main_layout.add_widget(instruction)
        
        # Create text input
        self.text_input = TextInput(
            multiline=True,
            size_hint_y=0.6,
            font_size=16,
            hint_text="Type your text here..."
        )
        main_layout.add_widget(self.text_input)
        
        # Create button layout
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10
        )
        
        # Cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5
        )
        cancel_btn.bind(on_press=self._on_cancel)
        button_layout.add_widget(cancel_btn)
        
        # OK button
        ok_btn = Button(
            text="OK",
            size_hint_x=0.5
        )
        ok_btn.bind(on_press=self._on_ok)
        button_layout.add_widget(ok_btn)
        
        main_layout.add_widget(button_layout)
        
        self.content = main_layout
        
        # Focus on text input when opened
        self.bind(on_open=self._on_open)

    def _on_open(self, instance):
        """Focus the text input when dialog opens."""
        self.text_input.focus = True

    def _on_cancel(self, button):
        """Handle cancel button press."""
        self.dismiss()

    def _on_ok(self, button):
        """Handle OK button press."""
        text = self.text_input.text.strip()
        if text and self.callback:
            self.callback(text)
        self.dismiss()

    def get_text(self):
        """
        Get the entered text.
        
        Returns:
            str: The text entered by the user
        """
        return self.text_input.text.strip() 
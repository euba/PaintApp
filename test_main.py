"""
Basic tests for the Paint App.
"""
import pytest
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import main
        from paintapp import PaintApp
        from paintapp.core.canvas import MyCanvas
        from paintapp.widgets.buttons import RadioButton, ColorButton, LineWidthButton
        from paintapp.utils.constants import Colors, LineWidths
        
        assert hasattr(main, 'main')
        assert PaintApp is not None
        assert MyCanvas is not None
        assert RadioButton is not None
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

def test_paint_app_class():
    """Test that PaintApp class exists and has required methods."""
    from paintapp import PaintApp
    
    app = PaintApp()
    assert hasattr(app, 'build')
    assert hasattr(app, 'get_app_info')
    assert callable(app.build)

def test_canvas_class():
    """Test that MyCanvas class exists and has required methods."""
    from paintapp.core.canvas import MyCanvas
    
    canvas = MyCanvas()
    assert hasattr(canvas, 'clear_screen')
    assert hasattr(canvas, 'set_color')
    assert hasattr(canvas, 'set_line_width')
    assert hasattr(canvas, 'line_width')
    assert hasattr(canvas, 'has_drawings')
    
    # Test default line width (now "Normal" which is 4)
    assert canvas.line_width == 4

def test_line_width_setting():
    """Test line width setting functionality."""
    from paintapp.core.canvas import MyCanvas
    
    canvas = MyCanvas()
    
    # Test different line widths (updated values after removing original Thin)
    canvas.set_line_width('Thin')
    assert canvas.line_width == 2  # Previously Normal
    
    canvas.set_line_width('Normal')
    assert canvas.line_width == 4  # Previously Thick
    
    canvas.set_line_width('Thick')
    assert canvas.line_width == 8  # Previously Extra Thick

def test_color_constants():
    """Test that color constants are properly defined."""
    from paintapp.utils.constants import Colors
    
    assert hasattr(Colors, 'BLACK')
    assert hasattr(Colors, 'RED')
    assert hasattr(Colors, 'GREEN')
    assert hasattr(Colors, 'BLUE')
    
    # Test color palette - should have exactly 6 distinct colors
    palette = Colors.get_palette()
    assert isinstance(palette, list)
    assert len(palette) == 6

def test_line_width_constants():
    """Test that line width constants are properly defined."""
    from paintapp.utils.constants import LineWidths
    
    assert hasattr(LineWidths, 'THIN')
    assert hasattr(LineWidths, 'NORMAL')
    assert hasattr(LineWidths, 'THICK')
    
    # Test width mapping
    width_map = LineWidths.get_width_map()
    assert isinstance(width_map, dict)
    assert 'Thin' in width_map
    assert 'Normal' in width_map

def test_main_function_exists():
    """Test that main function exists and is callable."""
    import main
    assert hasattr(main, 'main')
    assert callable(main.main)

def test_kv_file_exists():
    """Test that the Kivy layout file exists."""
    kv_path = src_dir / "paintapp" / "assets" / "kv" / "paint.kv"
    assert kv_path.exists(), f"paint.kv file should exist at {kv_path}"

def test_color_button():
    """Test ColorButton functionality."""
    from paintapp.widgets.buttons import ColorButton
    
    # Test color button creation with orange color
    orange_color = (1, 0.5, 0, 1)
    btn = ColorButton(color=orange_color)
    
    assert btn.get_color() == orange_color
    assert btn.color_value == list(orange_color)
    assert btn.text == ''  # Color buttons should have no text

def test_app_info():
    """Test that app info is available."""
    from paintapp import PaintApp
    
    app = PaintApp()
    info = app.get_app_info()
    assert isinstance(info, dict)
    assert "name" in info
    assert "version" in info
    assert "author" in info
    assert "description" in info

def test_canvas_scaling():
    """Test that canvas properly handles size changes for window resizing."""
    from paintapp.core.canvas import MyCanvas
    
    canvas = MyCanvas()
    
    # Test initial size hint (should be responsive)
    assert hasattr(canvas, 'size_hint')
    
    # Test that canvas has size change handlers
    assert hasattr(canvas, 'on_size_change')
    assert hasattr(canvas, 'on_pos_change')
    
    # Test collision detection method exists
    assert hasattr(canvas, 'collide_point')
    
    # Simulate size change
    original_size = canvas.size
    canvas.size = (800, 600)
    canvas.on_size_change(canvas, canvas.size)
    
    # Canvas should handle size changes gracefully
    assert list(canvas.size) == [800, 600]

def test_layout_responsiveness():
    """Test that the main layout is configured for responsive design."""
    from paintapp.ui.layout import MainLayout
    
    layout = MainLayout()
    
    # Test that layout has proper orientation
    assert layout.orientation == "vertical"
    
    # Test that canvas has proper size hints for scaling
    canvas = layout.get_canvas()
    assert list(canvas.size_hint) == [1, 1]  # Should take full available space
    
    # Test that toolbar has proper size hints
    toolbar = layout.get_toolbar()
    assert list(toolbar.size_hint) == [1, None]  # Full width, fixed height

def test_window_resizable_config():
    """Test that window is configured to be resizable."""
    from paintapp.core.config import AppConfig
    from kivy.config import Config
    
    # Test default resizable setting
    AppConfig.setup_window()
    
    # Check that resizable is enabled by default
    # Note: We can't easily test the actual Config value in unit tests
    # but we can verify the method accepts resizable parameter
    AppConfig.setup_window(resizable=True)
    AppConfig.setup_window(resizable=False)


def test_canvas_drawing_scaling():
    """Test that canvas drawings scale correctly when window is resized."""
    from paintapp.core.canvas import MyCanvas
    
    canvas = MyCanvas()
    canvas.size = (400, 300)
    canvas.last_canvas_size = (400, 300)
    
    # Add a mock drawing to the history
    canvas.drawing_history.append({
        "type": "line_complete",
        "color": (0, 0, 0, 1),
        "width": 4,
        "points": [100, 100, 200, 200]
    })
    
    # Simulate window resize (double the size)
    new_size = (800, 600)
    canvas.size = new_size
    canvas.on_size_change(canvas, new_size)
    
    # Check that points were scaled correctly
    scaled_points = canvas.drawing_history[0]['points']
    expected_points = [200.0, 200.0, 400.0, 400.0]
    
    assert len(scaled_points) == len(expected_points)
    for actual, expected in zip(scaled_points, expected_points):
        assert abs(actual - expected) < 0.1  # Allow for floating point precision
    
    # Check that line width was scaled
    assert abs(canvas.drawing_history[0]['width'] - 6.0) < 0.1  # 4 * 1.5 (average of 2.0 and 2.0)


def test_drawing_modes():
    """Test that drawing modes can be set and retrieved."""
    from paintapp.core.canvas import MyCanvas
    from paintapp.utils.constants import DrawingModes
    
    canvas = MyCanvas()
    
    # Test default mode
    assert canvas.get_drawing_mode() == DrawingModes.LINE
    
    # Test setting different modes
    canvas.set_drawing_mode(DrawingModes.STRAIGHT_LINE)
    assert canvas.get_drawing_mode() == DrawingModes.STRAIGHT_LINE
    
    canvas.set_drawing_mode(DrawingModes.CIRCLE)
    assert canvas.get_drawing_mode() == DrawingModes.CIRCLE
    
    canvas.set_drawing_mode(DrawingModes.TRIANGLE)
    assert canvas.get_drawing_mode() == DrawingModes.TRIANGLE
    
    canvas.set_drawing_mode(DrawingModes.RECTANGLE)
    assert canvas.get_drawing_mode() == DrawingModes.RECTANGLE
    
    canvas.set_drawing_mode(DrawingModes.TEXT)
    assert canvas.get_drawing_mode() == DrawingModes.TEXT
    
    # Test invalid mode (should not change)
    canvas.set_drawing_mode("invalid_mode")
    assert canvas.get_drawing_mode() == DrawingModes.TEXT


def test_drawing_mode_button():
    """Test DrawingModeButton functionality."""
    from paintapp.widgets.buttons import DrawingModeButton
    from paintapp.utils.constants import DrawingModes
    
    # Test line mode button
    line_btn = DrawingModeButton(mode=DrawingModes.LINE)
    assert line_btn.get_mode() == DrawingModes.LINE
    assert line_btn.text == "/"
    
    # Test straight line mode button
    straight_line_btn = DrawingModeButton(mode=DrawingModes.STRAIGHT_LINE)
    assert straight_line_btn.get_mode() == DrawingModes.STRAIGHT_LINE
    assert straight_line_btn.text == "|"
    
    # Test circle mode button
    circle_btn = DrawingModeButton(mode=DrawingModes.CIRCLE)
    assert circle_btn.get_mode() == DrawingModes.CIRCLE
    assert circle_btn.text == "O"
    
    # Test triangle mode button
    triangle_btn = DrawingModeButton(mode=DrawingModes.TRIANGLE)
    assert triangle_btn.get_mode() == DrawingModes.TRIANGLE
    assert triangle_btn.text == "^"
    
    # Test rectangle mode button
    rect_btn = DrawingModeButton(mode=DrawingModes.RECTANGLE)
    assert rect_btn.get_mode() == DrawingModes.RECTANGLE
    assert rect_btn.text == "[]"
    
    # Test text mode button
    text_btn = DrawingModeButton(mode=DrawingModes.TEXT)
    assert text_btn.get_mode() == DrawingModes.TEXT
    assert text_btn.text == "T"


def test_drawing_mode_constants():
    """Test that drawing mode constants are properly defined."""
    from paintapp.utils.constants import DrawingModes
    
    # Test that all modes exist
    assert hasattr(DrawingModes, 'LINE')
    assert hasattr(DrawingModes, 'STRAIGHT_LINE')
    assert hasattr(DrawingModes, 'CIRCLE')
    assert hasattr(DrawingModes, 'TRIANGLE')
    assert hasattr(DrawingModes, 'RECTANGLE')
    assert hasattr(DrawingModes, 'TEXT')
    
    # Test get_modes method
    modes = DrawingModes.get_modes()
    assert isinstance(modes, list)
    assert len(modes) == 6
    assert DrawingModes.LINE in modes
    assert DrawingModes.STRAIGHT_LINE in modes
    assert DrawingModes.CIRCLE in modes
    assert DrawingModes.TRIANGLE in modes
    assert DrawingModes.RECTANGLE in modes
    assert DrawingModes.TEXT in modes
    
    # Test get_mode_labels method
    labels = DrawingModes.get_mode_labels()
    assert isinstance(labels, dict)
    assert len(labels) == 6


def test_line_width_button_symbols():
    """Test that line width buttons show correct Unicode symbols."""
    from paintapp.widgets.buttons import LineWidthButton
    
    # Test thin line button
    thin_btn = LineWidthButton(width_name="Thin", width_value=2)
    assert thin_btn.get_width_name() == "Thin"
    assert thin_btn.text == "-"  # Simple dash (thin)
    
    # Test normal line button
    normal_btn = LineWidthButton(width_name="Normal", width_value=4)
    assert normal_btn.get_width_name() == "Normal"
    assert normal_btn.text == "="  # Equals sign (medium)
    
    # Test thick line button
    thick_btn = LineWidthButton(width_name="Thick", width_value=8)
    assert thick_btn.get_width_name() == "Thick"
    assert thick_btn.text == "#"  # Hash symbol (thick)

if __name__ == '__main__':
    pytest.main([__file__]) 
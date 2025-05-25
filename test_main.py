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
    
    # Test default line width
    assert canvas.line_width == 2

def test_line_width_setting():
    """Test line width setting functionality."""
    from paintapp.core.canvas import MyCanvas
    
    canvas = MyCanvas()
    
    # Test different line widths
    canvas.set_line_width('Thin')
    assert canvas.line_width == 1
    
    canvas.set_line_width('Normal')
    assert canvas.line_width == 2
    
    canvas.set_line_width('Thick')
    assert canvas.line_width == 4

def test_color_constants():
    """Test that color constants are properly defined."""
    from paintapp.utils.constants import Colors
    
    assert hasattr(Colors, 'BLACK')
    assert hasattr(Colors, 'RED')
    assert hasattr(Colors, 'GREEN')
    assert hasattr(Colors, 'BLUE')
    
    # Test color palette
    palette = Colors.get_palette()
    assert isinstance(palette, list)
    assert len(palette) > 0

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

def test_app_info():
    """Test that app info is properly configured."""
    from paintapp import PaintApp
    
    app = PaintApp()
    info = app.get_app_info()
    
    assert isinstance(info, dict)
    assert 'name' in info
    assert 'version' in info
    assert 'author' in info
    assert info['name'] == 'Paint App'

if __name__ == '__main__':
    pytest.main([__file__]) 
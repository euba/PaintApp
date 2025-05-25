"""
Constants for PaintApp.

Defines color palettes, line widths, and other application constants.
"""


class Colors:
    """Color constants for the paint application."""

    # Basic colors (R, G, B, A) - 6 very distinct colors
    BLACK = (0, 0, 0, 1)
    RED = (1, 0, 0, 1)
    GREEN = (0, 0.8, 0, 1)  # Slightly darker green for better visibility
    BLUE = (0, 0, 1, 1)
    ORANGE = (1, 0.5, 0, 1)  # Replaced yellow with orange
    WHITE = (1, 1, 1, 1)

    # Extended palette (kept for potential future use)
    CYAN = (0, 1, 1, 1)
    MAGENTA = (1, 0, 1, 1)
    PURPLE = (0.5, 0, 1, 1)
    PINK = (1, 0.75, 0.8, 1)
    BROWN = (0.6, 0.3, 0, 1)
    GRAY = (0.5, 0.5, 0.5, 1)
    LIGHT_GRAY = (0.8, 0.8, 0.8, 1)
    DARK_GRAY = (0.3, 0.3, 0.3, 1)

    @classmethod
    def get_palette(cls):
        """Get the default color palette - 6 distinct colors."""
        return [
            cls.BLACK,
            cls.RED,
            cls.GREEN,
            cls.BLUE,
            cls.ORANGE,
            cls.WHITE,
        ]


class LineWidths:
    """Line width constants."""

    # Updated width constants - made thicker
    THIN = 3      # Increased from 2
    NORMAL = 6    # Increased from 4  
    THICK = 12    # Increased from 8

    @classmethod
    def get_width_map(cls):
        """Get the line width mapping."""
        return {
            "Thin": cls.THIN,
            "Normal": cls.NORMAL,
            "Thick": cls.THICK,
        }

    @classmethod
    def get_available_widths(cls):
        """Get list of available width names."""
        return list(cls.get_width_map().keys())


class LineStyles:
    """Line style constants."""
    
    SOLID = "solid"
    DASHED = "dashed"
    
    @classmethod
    def get_styles(cls):
        """Get all available line styles."""
        return [cls.SOLID, cls.DASHED]
    
    @classmethod
    def get_style_labels(cls):
        """Get human-readable labels for line styles."""
        return {
            cls.SOLID: "Solid",
            cls.DASHED: "Dashed",
        }


class DrawingModes:
    """Drawing mode constants."""

    # Drawing modes
    LINE = "line"
    STRAIGHT_LINE = "straight_line"
    CIRCLE = "circle"
    TRIANGLE = "triangle"
    RECTANGLE = "rectangle"
    TEXT = "text"

    @classmethod
    def get_modes(cls):
        """Get all available drawing modes."""
        return [cls.LINE, cls.STRAIGHT_LINE, cls.CIRCLE, cls.TRIANGLE, cls.RECTANGLE, cls.TEXT]

    @classmethod
    def get_mode_labels(cls):
        """Get human-readable labels for drawing modes."""
        return {
            cls.LINE: "Line",
            cls.STRAIGHT_LINE: "Straight Line",
            cls.CIRCLE: "Circle", 
            cls.TRIANGLE: "Triangle",
            cls.RECTANGLE: "Rectangle",
            cls.TEXT: "Text",
        }

"""
Constants for PaintApp.

Defines color palettes, line widths, and other application constants.
"""


class Colors:
    """Color constants for the paint application."""

    # Basic colors (R, G, B, A)
    BLACK = (0, 0, 0, 1)
    WHITE = (1, 1, 1, 1)
    RED = (1, 0, 0, 1)
    GREEN = (0, 1, 0, 1)
    BLUE = (0, 0, 1, 1)
    YELLOW = (1, 1, 0, 1)
    CYAN = (0, 1, 1, 1)
    MAGENTA = (1, 0, 1, 1)

    # Extended palette
    ORANGE = (1, 0.5, 0, 1)
    PURPLE = (0.5, 0, 1, 1)
    PINK = (1, 0.75, 0.8, 1)
    BROWN = (0.6, 0.3, 0, 1)
    GRAY = (0.5, 0.5, 0.5, 1)
    LIGHT_GRAY = (0.8, 0.8, 0.8, 1)
    DARK_GRAY = (0.3, 0.3, 0.3, 1)

    @classmethod
    def get_palette(cls):
        """Get the default color palette."""
        return [
            cls.BLACK,
            cls.RED,
            cls.GREEN,
            cls.BLUE,
            cls.YELLOW,
            cls.CYAN,
            cls.MAGENTA,
            cls.ORANGE,
            cls.PURPLE,
            cls.PINK,
            cls.BROWN,
            cls.GRAY,
        ]


class LineWidths:
    """Line width constants."""

    # Renamed width constants (removed THIN, renamed others)
    THIN = 2      # Previously NORMAL
    NORMAL = 4    # Previously THICK
    THICK = 8     # Previously EXTRA_THICK

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

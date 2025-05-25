"""
Core module for PaintApp.

Contains the main application logic, canvas implementation, and core functionality.
"""

from .app import PaintApp
from .canvas import MyCanvas
from .config import AppConfig

__all__ = ["PaintApp", "MyCanvas", "AppConfig"]

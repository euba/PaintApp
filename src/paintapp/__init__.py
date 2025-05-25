"""
PaintApp - A simple painting application built with Kivy.

A modular, extensible paint application with drawing tools, color selection,
and various brush sizes.
"""

__version__ = "1.0.0"
__author__ = "Aniket Thani"

from .core.app import PaintApp
from .core.canvas import MyCanvas

__all__ = ["PaintApp", "MyCanvas"]

#!/usr/bin/env python3
"""
Main entry point for the Paint App.

This script initializes and runs the Paint App using the modular structure.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from paintapp import PaintApp  # noqa: E402


def main():
    """Main entry point for the Paint App."""
    try:
        # Create and run the application
        app = PaintApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Helper functions for PaintApp.

Utility functions for resource management, file operations, and common tasks.
"""

from pathlib import Path


def get_resource_path(relative_path):
    """
    Get the absolute path to a resource file.

    This function handles both development and packaged app scenarios,
    ensuring resources are found regardless of how the app is launched.

    Args:
        relative_path (str): Path relative to the assets directory

    Returns:
        str: Absolute path to the resource
    """
    # Get the directory where this module is located
    current_dir = Path(__file__).parent

    # Go up to the paintapp package root
    package_root = current_dir.parent

    # Construct path to assets
    assets_dir = package_root / "assets"
    resource_path = assets_dir / relative_path

    if resource_path.exists():
        return str(resource_path)

    # Fallback: try relative to the main script directory
    # This handles cases where the app is run from different locations
    try:
        import sys

        if hasattr(sys, "_MEIPASS"):
            # PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # Development mode
            base_path = Path(sys.argv[0]).parent if sys.argv else Path.cwd()

        fallback_path = base_path / relative_path
        if fallback_path.exists():
            return str(fallback_path)
    except (AttributeError, IndexError):
        pass

    # Last resort: return the original path and let the caller handle it
    return str(resource_path)


def get_kv_file_path(filename):
    """
    Get the path to a KV file in the assets/kv directory.

    Args:
        filename (str): Name of the KV file

    Returns:
        str: Absolute path to the KV file
    """
    return get_resource_path(f"kv/{filename}")


def get_icon_path(filename):
    """
    Get the path to an icon file in the assets/icons directory.

    Args:
        filename (str): Name of the icon file

    Returns:
        str: Absolute path to the icon file
    """
    return get_resource_path(f"icons/{filename}")


def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path (str or Path): Path to the directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

#!/usr/bin/env python3
"""
Helper script to create a basic app icon for the Paint App.
This creates a simple icon with a paintbrush design.
"""

import os
import sys

def create_basic_icon():
    """Create a basic app icon using PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL (Pillow) is required to create icons.")
        print("Install it with: uv add pillow")
        return False
    
    # Icon sizes for macOS
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    # Create iconset directory
    iconset_dir = "icon.iconset"
    if not os.path.exists(iconset_dir):
        os.makedirs(iconset_dir)
    
    for size in sizes:
        # Create image
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple paintbrush icon
        # Handle (brown)
        handle_width = max(2, size // 20)
        handle_start = size * 0.7
        handle_end = size * 0.9
        draw.rectangle([
            size * 0.45, handle_start,
            size * 0.55, handle_end
        ], fill=(139, 69, 19, 255))
        
        # Ferrule (silver)
        ferrule_start = size * 0.6
        ferrule_end = handle_start
        draw.rectangle([
            size * 0.43, ferrule_start,
            size * 0.57, ferrule_end
        ], fill=(192, 192, 192, 255))
        
        # Brush bristles (black to blue gradient effect)
        bristle_start = size * 0.2
        bristle_end = ferrule_start
        brush_width = size * 0.2
        
        # Create brush shape (triangle-like)
        points = [
            (size * 0.5, bristle_start),  # tip
            (size * 0.4, bristle_end),    # left base
            (size * 0.6, bristle_end),    # right base
        ]
        draw.polygon(points, fill=(0, 100, 200, 255))
        
        # Add some paint drops
        if size >= 64:
            # Red paint drop
            drop_size = max(2, size // 32)
            draw.ellipse([
                size * 0.3 - drop_size, size * 0.4 - drop_size,
                size * 0.3 + drop_size, size * 0.4 + drop_size
            ], fill=(255, 0, 0, 255))
            
            # Blue paint drop
            draw.ellipse([
                size * 0.7 - drop_size, size * 0.3 - drop_size,
                size * 0.7 + drop_size, size * 0.3 + drop_size
            ], fill=(0, 0, 255, 255))
        
        # Save icon files
        if size <= 32:
            img.save(f"{iconset_dir}/icon_{size}x{size}.png")
        else:
            img.save(f"{iconset_dir}/icon_{size}x{size}.png")
            # Also create @2x version for retina displays
            if size <= 512:
                img.save(f"{iconset_dir}/icon_{size//2}x{size//2}@2x.png")
    
    print(f"✓ Icon files created in {iconset_dir}/")
    return True

def create_icns():
    """Convert iconset to .icns file using macOS iconutil."""
    if not os.path.exists("icon.iconset"):
        print("Error: icon.iconset directory not found. Run create_basic_icon() first.")
        return False
    
    try:
        import subprocess
        result = subprocess.run([
            "iconutil", "-c", "icns", "icon.iconset", "-o", "app_icon.icns"
        ], check=True, capture_output=True, text=True)
        print("✓ app_icon.icns created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating .icns file: {e}")
        print("Make sure you're running on macOS with iconutil available")
        return False
    except FileNotFoundError:
        print("Error: iconutil not found. This tool requires macOS.")
        return False

def main():
    """Main function to create app icon."""
    print("Creating Paint App icon...")
    
    if create_basic_icon():
        print("\nConverting to .icns format...")
        if create_icns():
            print("\n✓ Icon creation complete!")
            print("The app_icon.icns file is ready for use in builds.")
        else:
            print("\n⚠️  Icon files created but .icns conversion failed.")
            print("You can manually convert using: iconutil -c icns icon.iconset")
    else:
        print("\n❌ Icon creation failed.")

if __name__ == "__main__":
    main() 
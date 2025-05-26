#!/usr/bin/env python3
"""
Simple DMG build script for Paint App on macOS.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main build process."""
    print("🎨 Building Paint App DMG (Simple)...")
    print("=" * 50)
    
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("❌ This script only works on macOS")
        sys.exit(1)
    
    # Check if uv is available
    if not shutil.which('uv'):
        print("❌ uv is not installed. Please install it first:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    
    try:
        # Step 1: Install build dependencies
        print("Installing build dependencies...")
        if not run_command(['uv', 'sync', '--extra', 'build']):
            print("❌ Failed to install build dependencies")
            sys.exit(1)
        
        # Step 2: Clean previous builds
        print("Cleaning previous builds...")
        for dir_name in ['build', 'dist']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
        
        # Step 3: Build with PyInstaller using simple command
        print("Building app with PyInstaller...")
        cmd = [
            'uv', 'run', 'pyinstaller',
            '--name', 'PaintApp',
            '--windowed',
            '--onedir',
            '--add-data', 'src/paintapp/assets:paintapp/assets',
            '--hidden-import', 'kivy.core.text',
            '--hidden-import', 'kivy.core.image', 
            '--hidden-import', 'kivy.core.window',
            '--hidden-import', 'PIL.Image',
            '--hidden-import', 'PIL.ImageDraw',
            '--hidden-import', 'PIL.ImageFont',
            '--hidden-import', 'numpy',
            '--hidden-import', 'paintapp',
            '--hidden-import', 'paintapp.core',
            '--hidden-import', 'paintapp.core.canvas',
            '--osx-bundle-identifier', 'com.paintapp.paintapp',
            'src/main.py'
        ]
        
        if not run_command(cmd):
            print("❌ Failed to build app")
            sys.exit(1)
        
        # Step 4: Check if app was created
        app_path = 'dist/PaintApp.app'
        if not os.path.exists(app_path):
            print(f"❌ App not found at {app_path}")
            sys.exit(1)
        
        # Step 5: Create DMG using hdiutil (built into macOS)
        print("Creating DMG file...")
        dmg_name = 'PaintApp-1.0.0.dmg'
        
        # Remove existing DMG
        if os.path.exists(dmg_name):
            os.remove(dmg_name)
        
        # Create temporary directory for DMG contents
        temp_dir = 'temp_dmg'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        # Copy app to temp directory
        shutil.copytree(app_path, f'{temp_dir}/PaintApp.app')
        
        # Create Applications symlink
        os.symlink('/Applications', f'{temp_dir}/Applications')
        
        # Create DMG
        cmd = [
            'hdiutil', 'create',
            '-volname', 'Paint App',
            '-srcfolder', temp_dir,
            '-ov',
            '-format', 'UDZO',
            dmg_name
        ]
        
        if not run_command(cmd):
            print("❌ Failed to create DMG")
            sys.exit(1)
        
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        
        print(f"\n🎉 Successfully created {dmg_name}!")
        print("You can now distribute this DMG file.")
        
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
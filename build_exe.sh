#!/bin/bash
# Clean previous builds
rm -rf build dist *.spec

# Run PyInstaller
# --onefile: Create a single executable file
# --name: Name of the executable
# --paths: Add src to python path so imports work
# --noconsole: Don't show the console window (optional, good for GUI games)
# src/main.py: The entry point script

pyinstaller --onefile \
            --name "TheBeaconOfHope" \
            --paths src \
            src/main.py

echo "Build complete. Executable is in dist/"

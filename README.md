# The Beacon of Hope

A 2D Cinematic Platformer / Puzzle-Adventure game.

**Genre:** 2D Platformer
**Mechanic:** Chrono-Light (Lantern reveals past/future forms of objects)

## How to Play

1.  **Move**: Left/Right Arrow Keys
2.  **Jump**: Spacebar
3.  **Toggle Lantern**: 'F' Key

## Installation & Running (Source)

1.  Install Python 3.10+.
2.  Install dependencies:
    ```bash
    pip install pygame
    ```
3.  Run the game:
    ```bash
    python src/main.py
    ```

## Creating the Executable (.exe)

If you want to create a standalone `.exe` file (Windows) or binary (Linux/Mac) so you can play without Python installed:

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

2.  **Windows**: Double-click `build_exe.bat`.
3.  **Linux/Mac**: Run `./build_exe.sh` in the terminal.

4.  The executable file will be created in the `dist/` folder.
    *   **Windows**: `dist\TheBeaconOfHope.exe`
    *   **Linux**: `dist/TheBeaconOfHope`

You can move this file anywhere and run it directly.

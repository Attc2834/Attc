@echo off
REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Run PyInstaller
REM --onefile: Create a single executable file
REM --name: Name of the executable
REM --paths: Add src to python path so imports work
REM --noconsole: Don't show the console window
REM src/main.py: The entry point script

echo Building The Beacon of Hope...
pyinstaller --onefile --noconsole --name "TheBeaconOfHope" --paths src src\main.py

echo.
echo Build complete.
echo You can find the executable in the 'dist' folder: dist\TheBeaconOfHope.exe
pause

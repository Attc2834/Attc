@echo off
chcp 65001 >nul 2>&1
title ATTC JARVIS - Kurulum
color 0A

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║                                           ║
echo  ║       ATTC JARVIS - KURULUM BASLIYOR      ║
echo  ║                                           ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Python kontrolü
echo  [1/3] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Python bulunamadi!
    echo  Python'u indirin: https://www.python.org/downloads/
    echo  Kurulumda "Add Python to PATH" kutusunu isaretleyin!
    echo.
    pause
    exit /b
)
python --version
echo  [OK] Python mevcut.
echo.

:: Python kütüphaneleri
echo  [2/3] Python kutuphaneleri kuruluyor...
echo  (Bu islem birkac dakika surebilir)
echo.
pip install customtkinter google-generativeai edge-tts SpeechRecognition PyAudio openwakeword playwright Pillow pydub aiohttp numpy
echo.
echo  [OK] Kutuphaneler kuruldu.
echo.

:: Playwright Chromium
echo  [3/3] Playwright tarayicisi indiriliyor...
playwright install chromium
echo.
echo  [OK] Tarayici kuruldu.
echo.

echo  ╔═══════════════════════════════════════════╗
echo  ║                                           ║
echo  ║        KURULUM TAMAMLANDI!                ║
echo  ║        Cift tikla: baslat.bat             ║
echo  ║                                           ║
echo  ╚═══════════════════════════════════════════╝
echo.
pause

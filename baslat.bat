@echo off
chcp 65001 >nul 2>&1
title ATTC JARVIS
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Uygulama baslatılamadı.
    echo  Önce kur.bat dosyasini calistirdiginizdan emin olun.
    echo.
    pause
)

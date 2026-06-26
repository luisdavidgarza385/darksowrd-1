@echo off
title SPECTRAL X PRO - Panel de Control
color 0A
cls
echo.
echo  ╔════════════════════════════════════════════════╗
echo  ║       SPECTRAL X PRO - Panel de Control        ║
echo  ╚════════════════════════════════════════════════╝
echo.
echo  Iniciando servidor...
echo.
python server.py
if errorlevel 1 (
    echo.
    echo  [!] Python no encontrado.
    echo  [!] Descarga: https://www.python.org/downloads/
    echo.
    pause
)

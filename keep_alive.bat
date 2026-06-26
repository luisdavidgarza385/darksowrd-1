@echo off
title SPECTRAL X PRO - Servidor Permanente
color 0A
cd /d "%~dp0"
:loop
echo [%date% %time%] Iniciando server...
python server.py
echo [%date% %time%] Server se cayo, reiniciando en 3 segundos...
timeout /t 3 /nobreak > nul
goto loop

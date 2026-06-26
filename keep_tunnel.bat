@echo off
title SPECTRAL X PRO - Tunnel Permanente
color 0B
cd /d "%~dp0"
:loop
echo [%date% %time%] Iniciando tunnel...
cloudflared tunnel --url http://localhost:8080
echo [%date% %time%] Tunnel se cayo, reiniciando en 3 segundos...
timeout /t 3 /nobreak > nul
goto loop

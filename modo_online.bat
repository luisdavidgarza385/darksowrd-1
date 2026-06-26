@echo off
title SPECTRAL X PRO - Modo Online
color 0B
cls
echo.
echo  ╔════════════════════════════════════════════════╗
echo  ║     SPECTRAL X PRO - Modo Online (GRATIS)      ║
echo  ╚════════════════════════════════════════════════╝
echo.

where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] cloudflared no encontrado.
    echo  Descarga GRATIS: https://github.com/cloudflare/cloudflared/releases/latest
    echo  Busca: cloudflared-windows-amd64.exe
    echo  Renombralo a: cloudflared.exe
    echo  Ponealo en esta carpeta o en C:\Windows\System32
    echo.
    pause
    exit /b
)

echo  [1/2] Iniciando servidor...
start "SpectralServer" /min python server.py
timeout /t 2 /nobreak > nul
echo  [OK] Servidor activo
echo.
echo  [2/2] Iniciando tunel Cloudflare...
echo.
echo  ══════════════════════════════════════════════════
echo   COPIA TU URL Y DALE A TUS CLIENTES:
echo  ══════════════════════════════════════════════════
echo.
cloudflared tunnel --url http://localhost:8080
echo.
echo  Tunel cerrado.
taskkill /f /im python.exe >nul 2>&1

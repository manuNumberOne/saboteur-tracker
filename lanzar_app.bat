@echo off
title Lanzador de Gold Tracker
:: Navega a la carpeta donde está este archivo
cd /d "%~dp0"
echo Iniciando Gold Tracker...
:: Ejecuta streamlit
python -m streamlit run streamlit_app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Ocurrio un error al iniciar la aplicacion. Asegurate de tener Python y Streamlit instalados.
    pause
)

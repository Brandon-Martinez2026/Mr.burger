@echo off
REM ============================================================
REM Iniciar_Mr_Burger.bat
REM ------------------------------------------------------------
REM Doble clic en este archivo para abrir Mr.Burger.
REM
REM Qué hace:
REM   1. Se ubica en la carpeta donde está este mismo archivo
REM      (para que funcione sin importar desde dónde lo abras).
REM   2. Revisa que Python esté instalado.
REM   3. Instala/actualiza las librerías necesarias
REM      (mysql-connector-python, pillow) si no están.
REM   4. Abre la pantalla de inicio de sesión.
REM
REM No crea la base de datos ni las tablas: eso se hace UNA sola
REM vez, a mano, con los scripts de la carpeta migraciones/ y
REM mr_burguer_db.sql (ver Como_funciona_la_app.md).
REM ============================================================

cd /d "%~dp0"

echo ============================================
echo   Mr.Burger - Iniciando...
echo ============================================
echo.

REM ------------------------------------------------------------
REM 1) Verificar que Python este instalado
REM ------------------------------------------------------------

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python instalado en esta computadora.
    echo Descargalo desde https://www.python.org/downloads/ e intenta de nuevo.
    echo Al instalarlo, marca la casilla "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM 2) Instalar dependencias (silencioso; no reinstala si ya
REM    estan, pip se encarga de eso solo)
REM ------------------------------------------------------------

echo Revisando dependencias necesarias...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se pudieron instalar las dependencias.
    echo Revisa tu conexion a internet e intenta de nuevo.
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM 3) Abrir el programa
REM ------------------------------------------------------------

echo Abriendo Mr.Burger...
echo.

python IniciarSesion.py

REM Si el programa se cerro por un error de Python (por ejemplo,
REM no se pudo conectar a la base de datos), deja la ventana
REM abierta para poder leer el mensaje.
if %errorlevel% neq 0 (
    echo.
    echo El programa se cerro con un error. Revisa el mensaje de arriba.
    echo (Un error comun es que MySQL no este encendido, o que la
    echo  contrasena en basedatos/config.py no sea la correcta.)
    echo.
    pause
)

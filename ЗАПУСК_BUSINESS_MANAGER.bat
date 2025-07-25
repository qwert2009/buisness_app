@echo off
chcp 65001 >nul
title Business Manager - Простой запуск

echo.
echo 🏢 Business Manager - Выберите способ запуска
echo =============================================
echo.

REM Переходим в папку "Новая папка"
cd /d "C:\Users\Windows 11\Desktop\qwe\Новая папка"

echo 📂 Рабочая папка: %CD%
echo.

echo 🎯 Доступные способы запуска:
echo.
echo 1️⃣ EXE файл (366 MB) - автономная версия
echo 2️⃣ Python скрипт - быстрый запуск  
echo 3️⃣ BAT файл - с отображением процесса
echo.

set /p choice="Выберите способ (1, 2 или 3): "

if "%choice%"=="1" goto run_exe
if "%choice%"=="2" goto run_python
if "%choice%"=="3" goto run_bat

echo ❌ Неверный выбор. Запускаем Python версию по умолчанию...
goto run_python

:run_exe
echo.
echo 🚀 Запуск EXE файла...
echo ⏳ Это может занять 30-60 секунд при первом запуске...
echo.

REM Принудительно запускаем exe файл
"BusinessManager.exe"

if %errorlevel% neq 0 (
    echo ❌ Exe файл не запустился (код ошибки: %errorlevel%)
    echo 🔄 Пробуем Python версию...
    goto run_python
)
goto end

:run_python
echo.
echo 🐍 Запуск Python версии...
echo ⚡ Быстро и надежно!
echo.

python BusinessManager.py

if %errorlevel% neq 0 (
    echo ❌ Python версия не запустилась
    echo 🔄 Пробуем BAT файл...
    goto run_bat
)
goto end

:run_bat
echo.
echo 🖥️ Запуск через BAT файл...
echo 📊 Показывает подробную информацию
echo.

BusinessManager.bat
goto end

:end
echo.
echo ✅ Завершение работы
pause

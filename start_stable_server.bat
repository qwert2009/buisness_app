@echo off
chcp 65001 >nul
title Business Manager - Автозапуск сервера

echo.
echo 🏢 Business Manager - Автоматический запуск сервера
echo ====================================================
echo.
echo 📍 Запуск из папки: %CD%
echo 🕐 Время запуска: %date% %time%
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не установлен!
    echo 📥 Скачайте Python с https://python.org
    pause
    exit /b 1
)

REM Проверяем наличие главного файла
if not exist business_manager.py (
    echo ❌ Файл business_manager.py не найден!
    echo 📂 Убедитесь, что вы запускаете скрипт из правильной папки
    pause
    exit /b 1
)

echo ✅ Python найден
echo ✅ Файл приложения найден
echo.

REM Запускаем автоматический менеджер сервера
echo 🚀 Запуск менеджера сервера...
python auto_start_server.py

REM Если мы здесь, значит сервер остановился
echo.
echo 🛑 Сервер остановлен
echo.
pause

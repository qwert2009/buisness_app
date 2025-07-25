@echo off
chcp 65001 >nul
title Business Manager - Создание EXE файла

echo.
echo 🏭 Business Manager - Создание исполняемого файла
echo ================================================================
echo.

REM Переходим в рабочую папку
cd /d "C:\Users\Windows 11\Desktop\qwe"
echo 📂 Рабочая папка: %CD%

REM Проверяем Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не установлен!
    pause
    exit /b 1
)
echo ✅ Python найден

REM Создаем папку для сборки если не существует
if not exist "Новая папка" mkdir "Новая папка"

REM Копируем файлы
echo.
echo 📋 Копирование файлов...
copy /Y "business_manager.py" "Новая папка\" >nul
if exist "smart_functions.py" copy /Y "smart_functions.py" "Новая папка\" >nul
if exist "notifications.py" copy /Y "notifications.py" "Новая папка\" >nul  
if exist "advanced_analytics.py" copy /Y "advanced_analytics.py" "Новая папка\" >nul
echo ✅ Файлы скопированы

REM Переходим в папку сборки
cd "Новая папка"

REM Проверяем и устанавливаем PyInstaller
echo.
echo 📦 Проверка PyInstaller...
pip show PyInstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 Установка PyInstaller...
    pip install PyInstaller
    if %errorlevel% neq 0 (
        echo ❌ Ошибка установки PyInstaller
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller готов

REM Проверяем основные зависимости
echo.
echo 📦 Проверка зависимостей...
python -c "import streamlit, pandas, plotly" 2>nul
if %errorlevel% neq 0 (
    echo 🔧 Установка зависимостей...
    pip install streamlit pandas plotly openpyxl numpy
)
echo ✅ Зависимости готовы

REM Создаем exe файл
echo.
echo 🔨 Создание исполняемого файла...
echo ⏳ Это может занять несколько минут...
echo.

REM Используем python -m для запуска PyInstaller
python -m PyInstaller --onefile --console --name "BusinessManager" --clean --distpath . business_manager_launcher.py

if %errorlevel% equ 0 (
    echo.
    echo 🎉 УСПЕШНО! Exe файл создан!
    echo.
    if exist "BusinessManager.exe" (
        echo ✅ Файл создан: BusinessManager.exe
        for %%I in ("BusinessManager.exe") do echo 📦 Размер: %%~zI байт
        echo.
        echo 📋 Инструкция по использованию:
        echo 1. Дважды кликните на BusinessManager.exe
        echo 2. Подождите запуска сервера
        echo 3. Браузер откроется автоматически
        echo 4. Используйте приложение!
        echo.
        echo 🎯 Готово! Файл находится в папке "Новая папка"
    ) else (
        echo ❌ Exe файл не найден после сборки
    )
) else (
    echo ❌ Ошибка при создании exe файла
)

echo.
pause

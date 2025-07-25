@echo off
chcp 65001 >nul
title Business Manager - Запуск EXE файла

echo.
echo 🚀 Business Manager - Запуск исполняемого файла
echo =====================================================
echo.

REM Переходим в папку "Новая папка"
cd /d "C:\Users\Windows 11\Desktop\qwe\Новая папка"

echo 📂 Рабочая папка: %CD%

REM Проверяем наличие exe файла
if not exist "BusinessManager.exe" (
    echo ❌ Файл BusinessManager.exe не найден!
    echo 📂 Убедитесь, что вы находитесь в правильной папке
    pause
    exit /b 1
)

REM Показываем информацию о файле
for %%I in ("BusinessManager.exe") do (
    echo ✅ Найден файл: BusinessManager.exe
    echo 📦 Размер: %%~zI байт (приблизительно 384 MB)
)

echo.
echo 🔧 Запуск exe файла принудительно...
echo ⏳ Подождите, это может занять 30-60 секунд...
echo.

REM Принудительный запуск exe файла
echo 🚀 Запускаем BusinessManager.exe...

REM При запуске exe файла, он должен распаковаться во временную папку
REM и запустить Streamlit сервер
start /wait "" "BusinessManager.exe"

echo.
echo 🔍 Если exe файл не запустился, попробуйте альтернативные способы:
echo.
echo 1️⃣ Запуск через Python скрипт:
echo    python BusinessManager.py
echo.
echo 2️⃣ Запуск через командную строку с правами администратора:
echo    Правый клик на BusinessManager.exe → Запуск от имени администратора
echo.
echo 3️⃣ Проверка антивируса:
echo    Добавьте BusinessManager.exe в исключения антивируса
echo.

pause

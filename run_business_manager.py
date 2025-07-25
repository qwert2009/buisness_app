#!/usr/bin/env python3
"""
Скрипт для запуска бизнес-менеджера
"""
import subprocess
import sys
import os

def install_requirements():
    """Установка зависимостей"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Все зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False

def run_app():
    """Запуск приложения"""
    try:
        # Проверяем, существует ли файл приложения
        if not os.path.exists("business_manager.py"):
            print("❌ Файл business_manager.py не найден!")
            return False
        
        print("🚀 Запуск бизнес-менеджера...")
        print("📍 Приложение будет доступно по адресу: http://localhost:8501")
        print("⏹️  Для остановки приложения нажмите Ctrl+C")
        
        # Запуск Streamlit приложения
        subprocess.run([sys.executable, "-m", "streamlit", "run", "business_manager.py", "--server.port", "8501"])
        
    except KeyboardInterrupt:
        print("\n✅ Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске приложения: {e}")

def main():
    print("🏢 Бизнес Менеджер - Система управления заказами")
    print("=" * 50)
    
    # Проверяем и устанавливаем зависимости
    print("📦 Проверка зависимостей...")
    
    try:
        import streamlit
        import pandas
        import plotly
        import openpyxl
        print("✅ Все необходимые библиотеки уже установлены!")
    except ImportError:
        print("📦 Установка недостающих зависимостей...")
        if not install_requirements():
            print("❌ Не удалось установить зависимости. Запустите вручную:")
            print("pip install -r requirements.txt")
            return
    
    # Запуск приложения
    run_app()

if __name__ == "__main__":
    main()

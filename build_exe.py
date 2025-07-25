#!/usr/bin/env python3
"""
Создание исполняемого файла Business Manager с помощью Python
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def main():
    """Основная функция создания exe"""
    print("🏭 Business Manager - Создание исполняемого файла")
    print("=" * 60)
    
    # Определяем пути
    source_dir = Path("C:/Users/Windows 11/Desktop/qwe")
    target_dir = source_dir / "Новая папка"
    
    print(f"📂 Исходная папка: {source_dir}")
    print(f"📦 Целевая папка: {target_dir}")
    
    # Создаем целевую папку
    target_dir.mkdir(exist_ok=True)
    
    # Меняем рабочую директорию
    os.chdir(target_dir)
    print(f"📂 Рабочая папка: {target_dir}")
    
    # Проверяем и устанавливаем PyInstaller
    print("\n📦 Проверка PyInstaller...")
    try:
        import PyInstaller
        print("✅ PyInstaller уже установлен")
    except ImportError:
        print("🔧 Установка PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
            print("✅ PyInstaller установлен")
        except Exception as e:
            print(f"❌ Ошибка установки PyInstaller: {e}")
            return False
    
    # Копируем необходимые файлы
    print("\n📋 Копирование файлов...")
    files_to_copy = [
        "business_manager.py",
        "smart_functions.py", 
        "notifications.py",
        "advanced_analytics.py"
    ]
    
    for file_name in files_to_copy:
        source_file = source_dir / file_name
        target_file = target_dir / file_name
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                print(f"✅ Скопирован: {file_name}")
            except Exception as e:
                print(f"❌ Ошибка копирования {file_name}: {e}")
        else:
            print(f"⚠️ Файл не найден: {file_name}")
    
    # Проверяем, что launcher уже создан
    launcher_file = target_dir / "business_manager_launcher.py"
    if not launcher_file.exists():
        print("❌ Файл business_manager_launcher.py не найден!")
        print("Создайте его сначала в папке 'Новая папка'")
        return False
    
    print("✅ Launcher файл найден")
    
    # Создаем exe файл
    print("\n🔨 Создание исполняемого файла...")
    print("⏳ Это может занять несколько минут...")
    
    try:
        # Команда для создания exe
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console", 
            "--name", "BusinessManager",
            "--clean",
            "--distpath", ".",  # Сохранить exe в текущей папке
            "business_manager_launcher.py"
        ]
        
        print(f"🔧 Команда: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Сборка завершена успешно!")
            
            # Проверяем наличие exe файла
            exe_file = target_dir / "BusinessManager.exe"
            if exe_file.exists():
                file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
                print(f"🎉 УСПЕШНО! Exe файл создан!")
                print(f"📦 Размер файла: {file_size:.1f} MB")
                print(f"📍 Путь к файлу: {exe_file}")
                
                print("\n📋 Инструкция по использованию:")
                print("1. Дважды кликните на BusinessManager.exe")
                print("2. Подождите запуска сервера")
                print("3. Браузер откроется автоматически")
                print("4. Используйте приложение!")
                
                return True
            else:
                print("❌ Exe файл не найден после сборки")
                return False
        else:
            print("❌ Ошибка при создании exe файла:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка при сборке: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nНажмите Enter для выхода...")

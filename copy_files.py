#!/usr/bin/env python3
"""
Копирование файлов для создания exe
"""
import shutil
import os
from pathlib import Path

def copy_files():
    """Копирование необходимых файлов"""
    source_dir = Path("C:/Users/Windows 11/Desktop/qwe")
    target_dir = Path("C:/Users/Windows 11/Desktop/qwe/Новая папка")
    
    # Файлы для копирования
    files_to_copy = [
        "business_manager.py",
        "smart_functions.py", 
        "notifications.py",
        "advanced_analytics.py"
    ]
    
    print("📋 Копирование файлов...")
    print(f"📂 Из: {source_dir}")
    print(f"📂 В: {target_dir}")
    print("=" * 50)
    
    for file_name in files_to_copy:
        source_file = source_dir / file_name
        target_file = target_dir / file_name
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                file_size = source_file.stat().st_size / 1024  # KB
                print(f"✅ {file_name} ({file_size:.1f} KB)")
            except Exception as e:
                print(f"❌ Ошибка копирования {file_name}: {e}")
        else:
            print(f"⚠️ Файл не найден: {file_name}")
    
    print("=" * 50)
    print("✅ Копирование завершено!")

if __name__ == "__main__":
    copy_files()

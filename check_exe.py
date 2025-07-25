#!/usr/bin/env python3
"""
Проверка статуса создания exe файла
"""
import os
from pathlib import Path

def check_exe_status():
    """Проверяем статус создания exe файла"""
    print("🔍 Проверка статуса создания exe файла")
    print("=" * 50)
    
    target_dir = Path("C:/Users/Windows 11/Desktop/qwe/Новая папка")
    exe_file = target_dir / "BusinessManager.exe"
    
    print(f"📂 Папка: {target_dir}")
    print(f"📄 Ожидаемый exe файл: {exe_file}")
    
    if target_dir.exists():
        print("✅ Папка существует")
        
        # Список всех файлов в папке
        files = list(target_dir.glob("*"))
        print(f"📋 Файлов в папке: {len(files)}")
        
        for file in files:
            size = file.stat().st_size if file.is_file() else 0
            size_mb = size / (1024 * 1024) if size > 0 else 0
            file_type = "📄" if file.is_file() else "📁"
            
            if size_mb > 1:
                print(f"  {file_type} {file.name} ({size_mb:.1f} MB)")
            else:
                print(f"  {file_type} {file.name}")
        
        # Проверяем exe файл
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"\n🎉 УСПЕШНО! BusinessManager.exe создан!")
            print(f"📦 Размер: {size_mb:.1f} MB")
            print(f"📍 Путь: {exe_file}")
            
            print(f"\n📋 Инструкция:")
            print(f"1. Перейдите в папку: {target_dir}")
            print(f"2. Дважды кликните на BusinessManager.exe")
            print(f"3. Подождите запуска сервера")
            print(f"4. Браузер откроется автоматически")
            
            return True
        else:
            print(f"\n❌ BusinessManager.exe не найден")
            
            # Ищем другие exe файлы
            exe_files = list(target_dir.glob("*.exe"))
            if exe_files:
                print(f"🔍 Найдены другие exe файлы:")
                for exe in exe_files:
                    size_mb = exe.stat().st_size / (1024 * 1024)
                    print(f"  📄 {exe.name} ({size_mb:.1f} MB)")
            
            return False
    else:
        print("❌ Папка не существует")
        return False

if __name__ == "__main__":
    check_exe_status()

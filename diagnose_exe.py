#!/usr/bin/env python3
"""
Диагностика exe файла Business Manager
"""
import os
import sys
import subprocess
from pathlib import Path

def diagnose_exe():
    """Диагностика exe файла"""
    print("🔍 Диагностика exe файла Business Manager")
    print("=" * 50)
    
    exe_path = Path("C:/Users/Windows 11/Desktop/qwe/Новая папка/BusinessManager.exe")
    
    print(f"📍 Путь к exe: {exe_path}")
    
    # Проверка существования файла
    if exe_path.exists():
        print("✅ Exe файл найден")
        
        # Информация о файле
        size_bytes = exe_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        print(f"📦 Размер файла: {size_mb:.1f} MB ({size_bytes:,} байт)")
        
        # Проверка, что это исполняемый файл
        if exe_path.suffix.lower() == '.exe':
            print("✅ Файл имеет расширение .exe")
        else:
            print("❌ Файл не имеет расширения .exe")
        
        # Попытка получить информацию о файле
        try:
            result = subprocess.run(['file', str(exe_path)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"📋 Тип файла: {result.stdout.strip()}")
        except:
            print("⚠️ Не удалось определить тип файла (команда 'file' недоступна)")
        
        # Попытка запуска exe файла
        print("\n🚀 Попытка запуска exe файла...")
        try:
            # Меняем рабочую директорию
            os.chdir(exe_path.parent)
            print(f"📂 Рабочая папка: {exe_path.parent}")
            
            # Запуск exe файла
            process = subprocess.Popen(
                [str(exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("⏳ Exe файл запущен, ждем вывода...")
            
            # Ждем немного и проверяем статус
            import time
            time.sleep(5)
            
            if process.poll() is None:
                print("✅ Процесс exe файла запущен и работает!")
                print("🌐 Проверьте браузер: http://localhost:8501")
                
                # Завершаем процесс для тестирования
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                return True
            else:
                # Процесс завершился
                stdout, stderr = process.communicate()
                print(f"❌ Exe файл завершился с кодом: {process.returncode}")
                if stdout:
                    print(f"📤 Вывод: {stdout}")
                if stderr:
                    print(f"❌ Ошибки: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при запуске exe файла: {e}")
            return False
            
    else:
        print("❌ Exe файл не найден!")
        
        # Ищем альтернативные файлы
        folder_path = exe_path.parent
        if folder_path.exists():
            print(f"\n📋 Файлы в папке {folder_path.name}:")
            for file in folder_path.iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  📄 {file.name} ({size_mb:.1f} MB)")
        
        return False

def suggest_solutions():
    """Предложения решений"""
    print("\n💡 Предложения решений:")
    print("=" * 30)
    
    print("1️⃣ Попробуйте альтернативные способы:")
    print("   • Дважды кликните на BusinessManager.py")
    print("   • Запустите BusinessManager.bat")
    print("   • Используйте start_server.bat в основной папке")
    
    print("\n2️⃣ Если exe файл не запускается:")
    print("   • Запустите от имени администратора")
    print("   • Проверьте антивирус (добавьте в исключения)")
    print("   • Временно отключите Windows Defender")
    
    print("\n3️⃣ Проверьте системные требования:")
    print("   • Windows 10/11 64-bit")
    print("   • Свободный порт 8501")
    print("   • Права на запуск exe файлов")
    
    print("\n4️⃣ Альтернатива - Python версия:")
    print("   • Запустите: python auto_start_server.py")
    print("   • Или: python -m streamlit run business_manager.py")

if __name__ == "__main__":
    success = diagnose_exe()
    suggest_solutions()
    
    if not success:
        print("\n🔄 Рекомендуется использовать Python версию для надежности")
    
    input("\nНажмите Enter для завершения...")

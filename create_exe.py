#!/usr/bin/env python3
"""
Скрипт для создания исполняемого файла Business Manager
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Установка PyInstaller если не установлен"""
    try:
        import PyInstaller
        print("✅ PyInstaller уже установлен")
        return True
    except ImportError:
        print("📦 Установка PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller установлен успешно")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки PyInstaller: {e}")
            return False

def create_launcher_script():
    """Создание основного скрипта запуска"""
    launcher_content = '''#!/usr/bin/env python3
"""
Главный launcher для Business Manager
"""
import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def main():
    """Основная функция запуска"""
    print("🏢 Business Manager - Запуск приложения")
    print("=" * 50)
    
    # Определяем папку с исполняемым файлом
    if getattr(sys, 'frozen', False):
        # Если запущен как exe файл
        app_dir = Path(sys.executable).parent
    else:
        # Если запущен как Python скрипт
        app_dir = Path(__file__).parent
    
    os.chdir(app_dir)
    print(f"📂 Рабочая папка: {app_dir}")
    
    # Проверяем наличие основного файла
    main_file = app_dir / "business_manager.py"
    if not main_file.exists():
        print("❌ Файл business_manager.py не найден!")
        input("Нажмите Enter для выхода...")
        return
    
    print("✅ Файл приложения найден")
    
    try:
        print("🚀 Запуск Streamlit сервера...")
        
        # Команда запуска
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(main_file),
            "--server.port", "8501",
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false"
        ]
        
        print("🌐 Приложение будет доступно по адресу: http://localhost:8501")
        print("⏳ Подождите несколько секунд для запуска...")
        
        # Открываем браузер через 5 секунд
        def open_browser():
            time.sleep(5)
            try:
                webbrowser.open('http://localhost:8501')
                print("🌐 Браузер открыт автоматически")
            except Exception as e:
                print(f"⚠️ Не удалось открыть браузер: {e}")
                print("🌐 Откройте браузер вручную: http://localhost:8501")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Запускаем сервер
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\\n⚠️ Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
'''
    
    with open("business_manager_launcher.py", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ Launcher скрипт создан")

def copy_required_files():
    """Копирование необходимых файлов"""
    source_dir = Path("C:/Users/Windows 11/Desktop/qwe")
    
    required_files = [
        "business_manager.py",
        "smart_functions.py", 
        "notifications.py",
        "advanced_analytics.py"
    ]
    
    print("📋 Копирование файлов...")
    for file_name in required_files:
        source_file = source_dir / file_name
        if source_file.exists():
            shutil.copy2(source_file, file_name)
            print(f"✅ Скопирован: {file_name}")
        else:
            print(f"⚠️ Файл не найден: {file_name}")

def create_spec_file():
    """Создание spec файла для PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['business_manager_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('business_manager.py', '.'),
        ('smart_functions.py', '.'),
        ('notifications.py', '.'),
        ('advanced_analytics.py', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'openpyxl',
        'numpy',
        'sqlite3',
        'email.mime.text',
        'email.mime.multipart',
        'smtplib',
        'ssl',
        'hashlib',
        'webbrowser',
        'threading',
        'datetime',
        'json',
        'os',
        'sys',
        'time',
        'pathlib',
        'subprocess',
        'shutil',
        'collections',
        're'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BusinessManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open("business_manager.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Spec файл создан")

def build_exe():
    """Сборка exe файла"""
    print("🔨 Начинаем сборку exe файла...")
    print("⏳ Это может занять несколько минут...")
    
    try:
        # Запускаем PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console",
            "--name", "BusinessManager",
            "--clean",
            "business_manager.spec"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Exe файл создан успешно!")
            
            # Проверяем наличие exe файла
            exe_path = Path("dist/BusinessManager.exe")
            if exe_path.exists():
                exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"📦 Размер файла: {exe_size:.1f} MB")
                print(f"📍 Путь к файлу: {exe_path.absolute()}")
                return True
            else:
                print("❌ Exe файл не найден в папке dist/")
                return False
        else:
            print("❌ Ошибка при создании exe файла:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка при сборке: {e}")
        return False

def move_to_target_directory():
    """Перемещение exe файла в целевую папку"""
    source_exe = Path("dist/BusinessManager.exe")
    target_dir = Path("C:/Users/Windows 11/Desktop/qwe/Новая папка")
    target_exe = target_dir / "BusinessManager.exe"
    
    if source_exe.exists():
        try:
            shutil.copy2(source_exe, target_exe)
            print(f"✅ Exe файл скопирован в: {target_exe}")
            
            # Также копируем необходимые файлы данных
            data_files = ["business_manager.py", "smart_functions.py", "notifications.py", "advanced_analytics.py"]
            for file_name in data_files:
                if Path(file_name).exists():
                    shutil.copy2(file_name, target_dir / file_name)
            
            print("✅ Все файлы скопированы в целевую папку")
            return True
        except Exception as e:
            print(f"❌ Ошибка копирования: {e}")
            return False
    else:
        print("❌ Исходный exe файл не найден")
        return False

def main():
    """Основная функция"""
    print("🏭 Business Manager - Создание исполняемого файла")
    print("=" * 60)
    
    # Переходим в рабочую папку
    work_dir = Path("C:/Users/Windows 11/Desktop/qwe/build_temp")
    work_dir.mkdir(exist_ok=True)
    os.chdir(work_dir)
    
    print(f"📂 Рабочая папка: {work_dir}")
    
    steps = [
        ("Установка PyInstaller", install_pyinstaller),
        ("Создание launcher скрипта", create_launcher_script),
        ("Копирование файлов", copy_required_files),
        ("Создание spec файла", create_spec_file),
        ("Сборка exe файла", build_exe),
        ("Перемещение в целевую папку", move_to_target_directory)
    ]
    
    for step_name, step_func in steps:
        print(f"\\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Ошибка на этапе: {step_name}")
            print("🛑 Сборка прервана")
            input("Нажмите Enter для выхода...")
            return
    
    print("\\n🎉 УСПЕШНО! Exe файл создан!")
    print("📍 Местоположение: C:/Users/Windows 11/Desktop/qwe/Новая папка/BusinessManager.exe")
    print("\\n📋 Инструкция по использованию:")
    print("1. Перейдите в папку 'Новая папка'")
    print("2. Дважды кликните на BusinessManager.exe")
    print("3. Подождите запуска (откроется браузер автоматически)")
    print("4. Используйте приложение!")
    
    input("\\nНажмите Enter для завершения...")

if __name__ == "__main__":
    main()

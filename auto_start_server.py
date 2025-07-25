#!/usr/bin/env python3
"""
Автоматический запуск и мониторинг Business Manager сервера
Перезапускает сервер при сбоях для обеспечения непрерывной работы
"""
import subprocess
import sys
import os
import time
import threading
import webbrowser
from datetime import datetime

class ServerManager:
    def __init__(self):
        self.server_process = None
        self.should_run = True
        self.restart_count = 0
        self.max_restarts = 10
        
    def log(self, message):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def check_dependencies(self):
        """Проверка и установка зависимостей"""
        self.log("📦 Проверка зависимостей...")
        
        required_packages = [
            'streamlit', 'pandas', 'plotly', 'openpyxl', 
            'numpy', 'sqlite3'  # sqlite3 встроен в Python
        ]
        
        missing_packages = []
        
        for package in required_packages:
            if package == 'sqlite3':
                continue  # Встроенный модуль
            try:
                __import__(package)
                self.log(f"✅ {package} установлен")
            except ImportError:
                missing_packages.append(package)
                self.log(f"❌ {package} не установлен")
        
        if missing_packages:
            self.log("🔧 Установка недостающих пакетов...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    *missing_packages
                ])
                self.log("✅ Все пакеты установлены")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Ошибка установки пакетов: {e}")
                return False
        
        return True
    
    def start_server(self):
        """Запуск Streamlit сервера"""
        try:
            self.log("🚀 Запуск Business Manager сервера...")
            
            # Команда запуска с улучшенными параметрами
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                "business_manager.py",
                "--server.port", "8501",
                "--server.address", "127.0.0.1",  # Изменено на localhost
                "--server.headless", "true",
                "--server.runOnSave", "false",  # Отключаем автоперезагрузку
                "--browser.gatherUsageStats", "false",
                "--global.developmentMode", "false"
            ]
            
            # Запуск процесса
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.log("✅ Сервер запущен!")
            self.log("🌐 Адреса для доступа:")
            self.log("   - Основной: http://localhost:8501")
            self.log("   - Альтернативный: http://127.0.0.1:8501")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска сервера: {e}")
            return False
    
    def monitor_server(self):
        """Мониторинг работы сервера"""
        while self.should_run and self.server_process:
            try:
                # Проверяем статус процесса
                return_code = self.server_process.poll()
                
                if return_code is not None:
                    self.log(f"⚠️ Сервер остановлен с кодом: {return_code}")
                    
                    if self.should_run and self.restart_count < self.max_restarts:
                        self.restart_count += 1
                        self.log(f"🔄 Перезапуск сервера ({self.restart_count}/{self.max_restarts})...")
                        time.sleep(5)  # Ждем 5 секунд перед перезапуском
                        
                        if self.start_server():
                            continue
                        else:
                            self.log("❌ Не удалось перезапустить сервер")
                            break
                    else:
                        self.log("❌ Превышено максимальное количество перезапусков")
                        break
                
                # Читаем вывод сервера
                if self.server_process and self.server_process.stdout:
                    line = self.server_process.stdout.readline()
                    if line:
                        print(line.strip())
                
                time.sleep(1)
                    
            except Exception as e:
                self.log(f"❌ Ошибка мониторинга: {e}")
                time.sleep(5)
    
    def open_browser(self):
        """Открытие браузера через 3 секунды"""
        def delayed_open():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:8501')
                self.log("🌐 Браузер открыт")
            except Exception as e:
                self.log(f"⚠️ Не удалось открыть браузер: {e}")
                self.log("🌐 Откройте браузер вручную: http://localhost:8501")
        
        threading.Thread(target=delayed_open, daemon=True).start()
    
    def stop_server(self):
        """Остановка сервера"""
        self.should_run = False
        if self.server_process:
            self.log("🛑 Остановка сервера...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.log("✅ Сервер остановлен")
    
    def run(self):
        """Основной цикл работы"""
        self.log("🏢 Business Manager - Автозапуск сервера")
        self.log("=" * 50)
        
        # Проверяем файл приложения
        if not os.path.exists("business_manager.py"):
            self.log("❌ Файл business_manager.py не найден!")
            return False
        
        # Проверяем зависимости
        if not self.check_dependencies():
            return False
        
        try:
            # Запускаем сервер
            if not self.start_server():
                return False
            
            # Открываем браузер
            self.open_browser()
            
            # Мониторим сервер
            self.monitor_server()
            
        except KeyboardInterrupt:
            self.log("⚠️ Получен сигнал остановки")
        except Exception as e:
            self.log(f"❌ Критическая ошибка: {e}")
        finally:
            self.stop_server()
        
        return True

def main():
    """Точка входа"""
    # Меняем рабочую директорию на папку скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Создаем и запускаем менеджер сервера
    server_manager = ServerManager()
    
    try:
        server_manager.run()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()

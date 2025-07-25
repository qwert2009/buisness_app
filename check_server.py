#!/usr/bin/env python3
"""
Простая проверка статуса сервера Business Manager
"""
import requests
import time
import webbrowser
from datetime import datetime

def check_server_status(url="http://localhost:8501", max_attempts=30):
    """Проверяет статус сервера"""
    print("🔍 Проверка статуса сервера Business Manager...")
    print(f"📡 URL: {url}")
    print("=" * 50)
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[{attempt:2d}/{max_attempts}] Проверка подключения...", end=" ")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print("✅ СЕРВЕР РАБОТАЕТ!")
                print(f"🌐 Приложение доступно: {url}")
                print("🎉 Открываю браузер...")
                
                # Открываем браузер
                webbrowser.open(url)
                return True
            else:
                print(f"⚠️ Код ответа: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Нет соединения")
        except requests.exceptions.Timeout:
            print("⏱️ Таймаут")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        if attempt < max_attempts:
            print("   ⏳ Ждем 2 секунды...")
            time.sleep(2)
    
    print("\n❌ СЕРВЕР НЕ ОТВЕЧАЕТ!")
    print("\n💡 Возможные решения:")
    print("1. Убедитесь, что сервер запущен: python -m streamlit run business_manager.py")
    print("2. Проверьте порт 8501 (возможно занят)")
    print("3. Проверьте настройки брандмауэра")
    print("4. Попробуйте другой порт: --server.port 8502")
    
    return False

def main():
    """Основная функция"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🏢 Business Manager - Проверка статуса сервера")
    print(f"🕐 Время: {timestamp}")
    print("=" * 50)
    
    # Проверяем стандартный порт
    if check_server_status("http://localhost:8501"):
        return
    
    # Если основной порт не работает, проверяем альтернативные
    print("\n🔍 Проверка альтернативных портов...")
    alternative_ports = [8502, 8503, 8504, 8080]
    
    for port in alternative_ports:
        url = f"http://localhost:{port}"
        print(f"\n📡 Проверка порта {port}...")
        if check_server_status(url, max_attempts=3):
            return
    
    print("\n❌ Сервер не найден ни на одном из портов")
    print("\n🛠️ ИНСТРУКЦИЯ ПО ЗАПУСКУ:")
    print("1. Откройте командную строку или PowerShell")
    print("2. Перейдите в папку проекта: cd \"C:\\Users\\Windows 11\\Desktop\\qwe\"")
    print("3. Запустите: python -m streamlit run business_manager.py")
    print("4. Или дважды кликните start_server.bat")

if __name__ == "__main__":
    main()

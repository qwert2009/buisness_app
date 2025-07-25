#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функции очистки склада
"""

import sqlite3
import sys
import os

# Добавляем путь к главному файлу
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_clear_inventory():
    """Тестирует функцию очистки склада"""
    
    # Импортируем функции из основного файла
    try:
        from business_manager import clear_inventory, add_to_inventory, get_inventory, init_db
        print("✅ Функции успешно импортированы")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return
    
    # Инициализируем базу данных
    try:
        init_db()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Создаем тестового пользователя
    test_user_id = 999  # Тестовый ID пользователя
    
    # Добавляем тестовые товары
    print("\n📦 Добавляем тестовые товары...")
    test_products = [
        ("Тест товар 1", 10, "http://test1.com"),
        ("Тест товар 2", 5, "http://test2.com"),
        ("Тест товар 3", 15, "http://test3.com")
    ]
    
    try:
        for name, qty, link in test_products:
            add_to_inventory(test_user_id, name, qty, link)
            print(f"  ✅ Добавлен: {name} (количество: {qty})")
    except Exception as e:
        print(f"❌ Ошибка добавления товаров: {e}")
        return
    
    # Проверяем, что товары добавились
    print("\n📋 Проверяем склад до очистки...")
    try:
        inventory_before = get_inventory(test_user_id)
        print(f"  📊 Товаров на складе: {len(inventory_before)}")
        for _, row in inventory_before.iterrows():
            print(f"    • {row['product_name']}: {row['quantity']} шт.")
    except Exception as e:
        print(f"❌ Ошибка получения склада: {e}")
        return
    
    # Очищаем склад
    print("\n🗑️ Очищаем склад...")
    try:
        deleted_count = clear_inventory(test_user_id)
        print(f"  ✅ Удалено товаров: {deleted_count}")
    except Exception as e:
        print(f"❌ Ошибка очистки склада: {e}")
        return
    
    # Проверяем, что склад пуст
    print("\n📋 Проверяем склад после очистки...")
    try:
        inventory_after = get_inventory(test_user_id)
        print(f"  📊 Товаров на складе: {len(inventory_after)}")
        
        if len(inventory_after) == 0:
            print("  ✅ Склад успешно очищен!")
        else:
            print("  ❌ Склад не полностью очищен")
            for _, row in inventory_after.iterrows():
                print(f"    • Остался: {row['product_name']}: {row['quantity']} шт.")
    except Exception as e:
        print(f"❌ Ошибка проверки склада: {e}")
        return
    
    print("\n🎉 Тест завершен успешно!")

if __name__ == "__main__":
    print("🧪 ТЕСТИРОВАНИЕ ФУНКЦИИ ОЧИСТКИ СКЛАДА")
    print("=" * 50)
    test_clear_inventory()

"""
Модуль умных функций и автозаполнения
"""
import sqlite3
import json
from datetime import datetime, timedelta
from collections import Counter
import re

class SmartFunctions:
    def __init__(self, db_path='business_manager.db'):
        self.db_path = db_path
        
    def get_product_suggestions(self, user_id, query="", limit=10):
        """Автозаполнение названий товаров"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if query:
            # Поиск по частичному совпадению
            cursor.execute('''
                SELECT DISTINCT product_name, COUNT(*) as frequency
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND product_name LIKE ?
                GROUP BY product_name
                ORDER BY frequency DESC, product_name ASC
                LIMIT ?
            ''', (user_id, f'%{query}%', limit))
        else:
            # Самые популярные товары
            cursor.execute('''
                SELECT product_name, COUNT(*) as frequency
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ?
                GROUP BY product_name
                ORDER BY frequency DESC
                LIMIT ?
            ''', (user_id, limit))
        
        suggestions = cursor.fetchall()
        conn.close()
        
        return [{'name': suggestion[0], 'frequency': suggestion[1]} for suggestion in suggestions]
    
    def get_price_suggestions(self, user_id, product_name):
        """Предложения цен на основе истории"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cost_price, weight, delivery_cost, total_cost
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ? AND oi.product_name = ?
            ORDER BY o.created_at DESC
            LIMIT 10
        ''', (user_id, product_name))
        
        history = cursor.fetchall()
        conn.close()
        
        if not history:
            return None
        
        # Анализ исторических данных
        cost_prices = [item[0] for item in history]
        weights = [item[1] for item in history]
        delivery_costs = [item[2] for item in history]
        total_costs = [item[3] for item in history]
        
        return {
            'avg_cost_price': sum(cost_prices) / len(cost_prices),
            'last_cost_price': cost_prices[0],
            'avg_weight': sum(weights) / len(weights),
            'last_weight': weights[0],
            'avg_delivery_cost': sum(delivery_costs) / len(delivery_costs),
            'avg_total_cost': sum(total_costs) / len(total_costs),
            'price_range': {
                'min': min(cost_prices),
                'max': max(cost_prices)
            }
        }
    
    def detect_duplicate_orders(self, user_id, product_name, quantity, cost_price, weight):
        """Обнаружение возможных дублирующих заказов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ищем похожие заказы за последние 24 часа
        yesterday = datetime.now() - timedelta(days=1)
        
        cursor.execute('''
            SELECT o.order_name, oi.quantity, oi.cost_price, oi.weight, o.created_at
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ? 
            AND oi.product_name = ?
            AND datetime(o.created_at) >= ?
            AND ABS(oi.quantity - ?) <= 1
            AND ABS(oi.cost_price - ?) <= 5.0
            AND ABS(oi.weight - ?) <= 1.0
        ''', (user_id, product_name, yesterday.strftime('%Y-%m-%d %H:%M:%S'), 
              quantity, cost_price, weight))
        
        similar_orders = cursor.fetchall()
        conn.close()
        
        return similar_orders
    
    def get_seasonal_insights(self, user_id):
        """Анализ сезонных трендов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%m', o.created_at) as month,
                oi.product_name,
                COUNT(*) as order_count,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.total_cost) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ?
            GROUP BY month, oi.product_name
            HAVING order_count > 1
            ORDER BY month, total_revenue DESC
        ''', (user_id,))
        
        data = cursor.fetchall()
        conn.close()
        
        # Группируем по месяцам
        seasonal_data = {}
        month_names = {
            '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
            '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
            '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
        }
        
        for month, product, count, quantity, revenue in data:
            month_name = month_names.get(month, month)
            if month_name not in seasonal_data:
                seasonal_data[month_name] = []
            
            seasonal_data[month_name].append({
                'product': product,
                'orders': count,
                'quantity': quantity,
                'revenue': revenue
            })
        
        return seasonal_data
    
    def get_reorder_recommendations(self, user_id):
        """Рекомендации для повторного заказа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Находим товары, которые заказывались регулярно, но давно не заказывались
        cursor.execute('''
            SELECT 
                oi.product_name,
                COUNT(*) as order_frequency,
                MAX(datetime(o.created_at)) as last_order,
                AVG(oi.quantity) as avg_quantity,
                AVG(oi.cost_price) as avg_cost_price,
                AVG(oi.weight) as avg_weight
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ?
            GROUP BY oi.product_name
            HAVING order_frequency >= 2
            ORDER BY last_order ASC
        ''', (user_id,))
        
        products = cursor.fetchall()
        conn.close()
        
        recommendations = []
        current_time = datetime.now()
        
        for product_data in products:
            product_name, frequency, last_order_str, avg_qty, avg_cost, avg_weight = product_data
            last_order = datetime.strptime(last_order_str, '%Y-%m-%d %H:%M:%S')
            days_since_last = (current_time - last_order).days
            
            # Рекомендуем если прошло больше 30 дней и товар заказывался часто
            if days_since_last > 30 and frequency >= 3:
                recommendations.append({
                    'product_name': product_name,
                    'days_since_last': days_since_last,
                    'frequency': frequency,
                    'suggested_quantity': round(avg_qty),
                    'suggested_cost_price': round(avg_cost, 2),
                    'suggested_weight': round(avg_weight, 2),
                    'priority': 'high' if days_since_last > 60 else 'medium'
                })
        
        # Сортируем по приоритету и давности
        recommendations.sort(key=lambda x: (x['priority'] == 'high', x['days_since_last']), reverse=True)
        
        return recommendations[:10]  # Топ-10 рекомендаций
    
    def analyze_supplier_performance(self, user_id):
        """Анализ эффективности поставщиков (на основе типов доставки)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                o.delivery_type,
                COUNT(DISTINCT o.id) as orders_count,
                AVG(oi.delivery_cost) as avg_delivery_cost,
                SUM(oi.total_cost) as total_revenue,
                AVG(julianday('now') - julianday(o.created_at)) as avg_order_age
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ?
            GROUP BY o.delivery_type
        ''', (user_id,))
        
        data = cursor.fetchall()
        conn.close()
        
        analysis = {}
        for delivery_type, orders, avg_delivery, revenue, avg_age in data:
            supplier_name = "Авиа-поставщик" if delivery_type == 'airplane' else "Авто-поставщик"
            
            analysis[supplier_name] = {
                'orders_count': orders,
                'avg_delivery_cost': round(avg_delivery, 2),
                'total_revenue': round(revenue, 2),
                'avg_order_age_days': round(avg_age, 1),
                'delivery_type': delivery_type,
                'performance_score': self._calculate_supplier_score(orders, avg_delivery, avg_age)
            }
        
        return analysis
    
    def _calculate_supplier_score(self, orders_count, avg_delivery_cost, avg_order_age):
        """Расчет балла эффективности поставщика"""
        # Простая формула: больше заказов = лучше, меньше стоимость доставки = лучше
        # Нормализуем значения
        orders_score = min(orders_count / 10, 1.0) * 40  # До 40 баллов за количество
        cost_score = max(0, (10 - avg_delivery_cost) / 10) * 30  # До 30 баллов за низкую стоимость
        age_score = max(0, (365 - avg_order_age) / 365) * 30  # До 30 баллов за свежесть заказов
        
        return round(orders_score + cost_score + age_score, 1)
    
    def generate_smart_insights(self, user_id):
        """Генерация умных инсайтов"""
        insights = []
        
        # Рекомендации для повторного заказа
        reorder_recs = self.get_reorder_recommendations(user_id)
        if reorder_recs:
            high_priority = [r for r in reorder_recs if r['priority'] == 'high']
            if high_priority:
                insights.append({
                    'type': 'reorder',
                    'title': '🔄 Рекомендации для повторного заказа',
                    'message': f"У вас есть {len(high_priority)} товаров для срочного повторного заказа",
                    'data': high_priority[:3]
                })
        
        # Анализ поставщиков
        supplier_analysis = self.analyze_supplier_performance(user_id)
        if supplier_analysis:
            best_supplier = max(supplier_analysis.items(), key=lambda x: x[1]['performance_score'])
            insights.append({
                'type': 'supplier',
                'title': '⭐ Лучший поставщик',
                'message': f"{best_supplier[0]} показывает лучшие результаты (рейтинг: {best_supplier[1]['performance_score']})",
                'data': best_supplier[1]
            })
        
        # Сезонные тренды
        seasonal_data = self.get_seasonal_insights(user_id)
        if seasonal_data:
            current_month = datetime.now().strftime('%B')
            if current_month in seasonal_data:
                top_product = max(seasonal_data[current_month], key=lambda x: x['revenue'])
                insights.append({
                    'type': 'seasonal',
                    'title': '📅 Сезонный тренд',
                    'message': f"В {current_month} лучше всего продается {top_product['product']}",
                    'data': top_product
                })
        
        return insights
    
    def smart_autocomplete(self, user_id, field_type, query):
        """Универсальное автозаполнение"""
        if field_type == 'product_name':
            return self.get_product_suggestions(user_id, query)
        elif field_type == 'order_name':
            return self._get_order_name_suggestions(user_id, query)
        else:
            return []
    
    def _get_order_name_suggestions(self, user_id, query):
        """Предложения названий заказов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT order_name, COUNT(*) as frequency
            FROM orders
            WHERE user_id = ? AND order_name LIKE ?
            GROUP BY order_name
            ORDER BY frequency DESC
            LIMIT 5
        ''', (user_id, f'%{query}%'))
        
        suggestions = cursor.fetchall()
        conn.close()
        
        return [{'name': suggestion[0], 'frequency': suggestion[1]} for suggestion in suggestions]

# Функция для создания единственного экземпляра
_smart_functions = None

def get_smart_functions():
    global _smart_functions
    if _smart_functions is None:
        _smart_functions = SmartFunctions()
    return _smart_functions

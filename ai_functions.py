import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter
import json

class BusinessAI:
    """Класс с ИИ функциями для бизнес-аналитики"""
    
    def __init__(self, db_path='business_manager.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def smart_price_recommendation(self, user_id, product_name, cost_price, weight, delivery_type='truck'):
        """ИИ рекомендация оптимальной цены продажи"""
        conn = self.get_connection()
        
        try:
            # Анализируем историю продаж похожих товаров
            query = '''
                SELECT oi.sale_price, oi.cost_price, oi.weight, oi.item_delivery_type,
                       o.created_at, oi.quantity
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND oi.product_name LIKE ?
                ORDER BY o.created_at DESC
                LIMIT 50
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id, f'%{product_name}%'))
            
            if df.empty:
                # Если нет истории, используем стандартную формулу
                delivery_rates = self._get_delivery_rates(user_id)
                delivery_cost = weight * delivery_rates[delivery_type]
                recommended_price = cost_price * 1.3  # 30% маржа
                
                return {
                    'recommended_price': round(recommended_price, 2),
                    'min_price': round(cost_price * 1.1, 2),
                    'max_price': round(cost_price * 2.0, 2),
                    'confidence': 0.5,
                    'reasoning': 'Базовая рекомендация (30% маржа) - нет исторических данных',
                    'market_trend': 'unknown',
                    'profit_margin': 30.0,
                    'delivery_cost': delivery_cost
                }
            
            # Анализируем тренды цен
            df['price_ratio'] = df['sale_price'] / df['cost_price']
            df['profit_margin'] = ((df['sale_price'] - df['cost_price']) / df['sale_price'] * 100)
            
            # Тренд по времени
            recent_data = df.head(10)
            old_data = df.tail(10)
            
            recent_avg_ratio = recent_data['price_ratio'].mean()
            old_avg_ratio = old_data['price_ratio'].mean()
            
            trend = 'stable'
            if recent_avg_ratio > old_avg_ratio * 1.05:
                trend = 'growing'
            elif recent_avg_ratio < old_avg_ratio * 0.95:
                trend = 'declining'
            
            # Рекомендуемая цена на основе медианы успешных продаж
            median_ratio = df['price_ratio'].median()
            recommended_price = cost_price * median_ratio
            
            # Доверительный интервал
            q25 = df['price_ratio'].quantile(0.25)
            q75 = df['price_ratio'].quantile(0.75)
            
            min_price = cost_price * q25
            max_price = cost_price * q75
            
            # Уверенность в рекомендации
            confidence = min(1.0, len(df) / 20.0)  # Максимум при 20+ записях
            
            # Объяснение
            avg_margin = df['profit_margin'].mean()
            reasoning = f"На основе {len(df)} похожих продаж. Средняя маржа: {avg_margin:.1f}%. Тренд: {trend}"
            
            delivery_rates = self._get_delivery_rates(user_id)
            delivery_cost = weight * delivery_rates[delivery_type]
            
            return {
                'recommended_price': round(recommended_price, 2),
                'min_price': round(max(min_price, cost_price * 1.05), 2),
                'max_price': round(max_price, 2),
                'confidence': round(confidence, 2),
                'reasoning': reasoning,
                'market_trend': trend,
                'profit_margin': round(avg_margin, 1),
                'delivery_cost': delivery_cost,
                'historical_sales': len(df)
            }
            
        finally:
            conn.close()
    
    def demand_forecasting(self, user_id, days_ahead=30):
        """Прогнозирование спроса на товары"""
        conn = self.get_connection()
        
        try:
            # Получаем данные за последние 90 дней
            query = '''
                SELECT oi.product_name, oi.quantity, o.created_at,
                       strftime('%w', o.created_at) as day_of_week,
                       strftime('%Y-%m', o.created_at) as month_year
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-90 days')
                ORDER BY o.created_at
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return {"error": "Недостаточно данных для прогнозирования"}
            
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            forecasts = {}
            
            for product in df['product_name'].unique():
                product_data = df[df['product_name'] == product]
                
                # Группируем по дням
                daily_sales = product_data.groupby(product_data['created_at'].dt.date)['quantity'].sum()
                
                if len(daily_sales) < 7:  # Минимум неделя данных
                    continue
                
                # Простой тренд анализ
                dates = pd.to_datetime(daily_sales.index)
                quantities = daily_sales.values
                
                # Линейная регрессия для тренда
                x = np.arange(len(quantities))
                if len(x) > 1:
                    trend = np.polyfit(x, quantities, 1)[0]
                else:
                    trend = 0
                
                # Сезонность по дням недели
                weekly_pattern = product_data.groupby('day_of_week')['quantity'].mean()
                
                # Прогноз
                avg_daily = quantities.mean()
                forecast_base = max(0, avg_daily + trend * days_ahead)
                
                # Учитываем сезонность
                today_dow = datetime.now().weekday()
                seasonal_multiplier = weekly_pattern.get(str(today_dow), 1.0) / weekly_pattern.mean()
                
                forecasted_demand = forecast_base * seasonal_multiplier * days_ahead
                
                forecasts[product] = {
                    'forecasted_demand': round(forecasted_demand, 1),
                    'daily_average': round(avg_daily, 2),
                    'trend': 'растущий' if trend > 0.1 else 'падающий' if trend < -0.1 else 'стабильный',
                    'trend_value': round(trend, 3),
                    'confidence': min(1.0, len(daily_sales) / 30.0),
                    'historical_days': len(daily_sales)
                }
            
            return forecasts
            
        finally:
            conn.close()
    
    def smart_inventory_alerts(self, user_id):
        """Умные уведомления о состоянии склада"""
        conn = self.get_connection()
        
        try:
            # Получаем данные склада и продаж
            inventory_query = '''
                SELECT product_name, quantity
                FROM inventory
                WHERE user_id = ?
            '''
            
            sales_query = '''
                SELECT oi.product_name, SUM(oi.quantity) as total_sold,
                       COUNT(*) as orders_count,
                       AVG(oi.quantity) as avg_per_order,
                       MAX(o.created_at) as last_order_date
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-30 days')
                GROUP BY oi.product_name
            '''
            
            inventory_df = pd.read_sql_query(inventory_query, conn, params=(user_id,))
            sales_df = pd.read_sql_query(sales_query, conn, params=(user_id,))
            
            alerts = []
            
            # Объединяем данные
            for _, inv_row in inventory_df.iterrows():
                product = inv_row['product_name']
                current_stock = inv_row['quantity']
                
                # Находим данные продаж для этого товара
                sales_data = sales_df[sales_df['product_name'] == product]
                
                if not sales_data.empty:
                    sales_row = sales_data.iloc[0]
                    total_sold = sales_row['total_sold']
                    avg_per_order = sales_row['avg_per_order']
                    orders_count = sales_row['orders_count']
                    
                    # Рассчитываем скорость продаж (товаров в день)
                    daily_rate = total_sold / 30.0
                    
                    # Дни до исчерпания запасов
                    days_until_empty = current_stock / daily_rate if daily_rate > 0 else float('inf')
                    
                    # Генерируем алерты
                    if days_until_empty <= 3:
                        alerts.append({
                            'product': product,
                            'type': 'critical',
                            'message': f'КРИТИЧНО: {product} закончится через {days_until_empty:.1f} дней',
                            'current_stock': current_stock,
                            'daily_rate': round(daily_rate, 2),
                            'recommended_action': f'Заказать минимум {int(daily_rate * 14)} единиц'
                        })
                    elif days_until_empty <= 7:
                        alerts.append({
                            'product': product,
                            'type': 'warning',
                            'message': f'ВНИМАНИЕ: {product} закончится через {days_until_empty:.1f} дней',
                            'current_stock': current_stock,
                            'daily_rate': round(daily_rate, 2),
                            'recommended_action': f'Рекомендуется заказать {int(daily_rate * 21)} единиц'
                        })
                    elif days_until_empty <= 14:
                        alerts.append({
                            'product': product,
                            'type': 'info',
                            'message': f'Планирование: {product} закончится через {days_until_empty:.1f} дней',
                            'current_stock': current_stock,
                            'daily_rate': round(daily_rate, 2),
                            'recommended_action': f'Запланировать заказ {int(daily_rate * 30)} единиц'
                        })
                
                # Проверяем товары без движения
                elif current_stock > 0:
                    alerts.append({
                        'product': product,
                        'type': 'stagnant',
                        'message': f'Застой: {product} не продавался 30+ дней',
                        'current_stock': current_stock,
                        'daily_rate': 0,
                        'recommended_action': 'Рассмотреть акцию или пересмотреть цену'
                    })
            
            return sorted(alerts, key=lambda x: {'critical': 0, 'warning': 1, 'info': 2, 'stagnant': 3}[x['type']])
            
        finally:
            conn.close()
    
    def profit_optimization_suggestions(self, user_id):
        """ИИ предложения по оптимизации прибыли"""
        conn = self.get_connection()
        
        try:
            # Анализируем все заказы и товары
            query = '''
                SELECT oi.product_name, oi.cost_price, oi.sale_price, oi.quantity,
                       oi.weight, oi.item_delivery_type, oi.delivery_cost,
                       o.created_at, o.order_type
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-60 days')
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return {"error": "Недостаточно данных для анализа"}
            
            suggestions = []
            
            # 1. Анализ прибыльности товаров
            df['profit_per_item'] = df['sale_price'] - df['cost_price']
            df['profit_margin'] = (df['profit_per_item'] / df['sale_price']) * 100
            df['total_profit'] = df['profit_per_item'] * df['quantity']
            
            product_analysis = df.groupby('product_name').agg({
                'total_profit': 'sum',
                'profit_margin': 'mean',
                'quantity': 'sum',
                'cost_price': 'mean',
                'sale_price': 'mean'
            }).sort_values('total_profit', ascending=False)
            
            # Топ прибыльные товары
            top_profitable = product_analysis.head(3)
            suggestions.append({
                'type': 'focus_profitable',
                'title': '🎯 Фокус на прибыльных товарах',
                'description': f"Ваши топ-3 товара приносят {top_profitable['total_profit'].sum():.2f}$ прибыли",
                'products': list(top_profitable.index),
                'action': 'Увеличьте закупки этих товаров'
            })
            
            # Товары с низкой маржей
            low_margin = product_analysis[product_analysis['profit_margin'] < 15]
            if not low_margin.empty:
                suggestions.append({
                    'type': 'improve_margin',
                    'title': '📈 Улучшить маржинальность',
                    'description': f"{len(low_margin)} товаров с маржей менее 15%",
                    'products': list(low_margin.index),
                    'action': 'Пересмотрите цены или найдите более дешевых поставщиков'
                })
            
            # 2. Анализ способов доставки
            delivery_analysis = df.groupby('item_delivery_type').agg({
                'delivery_cost': 'mean',
                'quantity': 'sum',
                'profit_per_item': 'mean'
            })
            
            if len(delivery_analysis) > 1:
                airplane_profit = delivery_analysis.loc['airplane', 'profit_per_item'] if 'airplane' in delivery_analysis.index else 0
                truck_profit = delivery_analysis.loc['truck', 'profit_per_item'] if 'truck' in delivery_analysis.index else 0
                
                if airplane_profit < truck_profit:
                    suggestions.append({
                        'type': 'optimize_delivery',
                        'title': '🚛 Оптимизация доставки',
                        'description': f"Доставка машиной прибыльнее на {truck_profit - airplane_profit:.2f}$ за товар",
                        'action': 'Рассмотрите перевод больше товаров на доставку машиной'
                    })
            
            # 3. Сезонный анализ
            df['month'] = pd.to_datetime(df['created_at']).dt.month
            monthly_profit = df.groupby('month')['total_profit'].sum()
            
            if len(monthly_profit) > 1:
                best_month = monthly_profit.idxmax()
                worst_month = monthly_profit.idxmin()
                
                month_names = {1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
                              5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
                              9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'}
                
                suggestions.append({
                    'type': 'seasonal_planning',
                    'title': '📅 Сезонное планирование',
                    'description': f"Лучший месяц: {month_names.get(best_month)}, худший: {month_names.get(worst_month)}",
                    'action': f'Подготовьтесь к пику продаж в {month_names.get(best_month)}'
                })
            
            # 4. Анализ размера заказов
            avg_order_value = df.groupby(['created_at'])['total_profit'].sum().mean()
            high_value_orders = df[df['sale_price'] * df['quantity'] > avg_order_value * 1.5]
            
            if not high_value_orders.empty:
                vip_products = high_value_orders['product_name'].value_counts().head(3)
                suggestions.append({
                    'type': 'premium_focus',
                    'title': '💎 Премиум товары',
                    'description': f"Товары для крупных заказов: {', '.join(vip_products.index)}",
                    'action': 'Создайте специальные предложения для премиум сегмента'
                })
            
            return suggestions
            
        finally:
            conn.close()
    
    def automated_reorder_suggestions(self, user_id):
        """Автоматические предложения по дозаказу товаров"""
        conn = self.get_connection()
        
        try:
            # Комплексный анализ для предложений дозаказа
            query = '''
                SELECT 
                    i.product_name,
                    i.quantity as current_stock,
                    COALESCE(sales.total_sold_30d, 0) as sold_30d,
                    COALESCE(sales.total_sold_7d, 0) as sold_7d,
                    COALESCE(sales.avg_order_size, 0) as avg_order_size,
                    COALESCE(sales.last_sale_date, i.created_at) as last_activity,
                    COALESCE(profits.avg_profit_margin, 0) as avg_profit_margin,
                    COALESCE(profits.total_profit, 0) as total_profit_30d
                FROM inventory i
                LEFT JOIN (
                    SELECT 
                        oi.product_name,
                        SUM(CASE WHEN o.created_at >= date('now', '-30 days') THEN oi.quantity ELSE 0 END) as total_sold_30d,
                        SUM(CASE WHEN o.created_at >= date('now', '-7 days') THEN oi.quantity ELSE 0 END) as total_sold_7d,
                        AVG(oi.quantity) as avg_order_size,
                        MAX(o.created_at) as last_sale_date
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.id
                    WHERE o.user_id = ?
                    GROUP BY oi.product_name
                ) sales ON i.product_name = sales.product_name
                LEFT JOIN (
                    SELECT 
                        oi.product_name,
                        AVG((oi.sale_price - oi.cost_price) / oi.sale_price * 100) as avg_profit_margin,
                        SUM((oi.sale_price - oi.cost_price) * oi.quantity) as total_profit
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.id
                    WHERE o.user_id = ? AND o.created_at >= date('now', '-30 days')
                    GROUP BY oi.product_name
                ) profits ON i.product_name = profits.product_name
                WHERE i.user_id = ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id, user_id, user_id))
            
            if df.empty:
                return []
            
            recommendations = []
            
            for _, row in df.iterrows():
                product = row['product_name']
                current_stock = row['current_stock']
                sold_30d = row['sold_30d']
                sold_7d = row['sold_7d']
                avg_order_size = row['avg_order_size']
                profit_margin = row['avg_profit_margin']
                total_profit = row['total_profit_30d']
                
                # Рассчитываем скорость продаж
                daily_rate_30d = sold_30d / 30.0
                daily_rate_7d = sold_7d / 7.0
                
                # Используем более актуальную скорость
                daily_rate = max(daily_rate_30d, daily_rate_7d * 0.8)  # Взвешиваем недавние продажи
                
                if daily_rate > 0:
                    days_until_empty = current_stock / daily_rate
                    
                    # Определяем приоритет дозаказа
                    priority = 0
                    reason = []
                    
                    # Критичность по времени
                    if days_until_empty <= 5:
                        priority += 100
                        reason.append("КРИТИЧНО: товар закончится через 5 дней")
                    elif days_until_empty <= 10:
                        priority += 80
                        reason.append("товар закончится через 10 дней")
                    elif days_until_empty <= 20:
                        priority += 50
                        reason.append("планирование на 3 недели")
                    
                    # Бонус за прибыльность
                    if profit_margin > 25:
                        priority += 30
                        reason.append("высокая маржа")
                    elif profit_margin > 15:
                        priority += 20
                        reason.append("хорошая маржа")
                    
                    # Бонус за объем продаж
                    if sold_7d > sold_30d * 0.4:  # Более 40% месячных продаж за неделю
                        priority += 25
                        reason.append("растущие продажи")
                    
                    # Бонус за общую прибыль
                    if total_profit > 100:
                        priority += 15
                        reason.append("высокая общая прибыль")
                    
                    # Рассчитываем рекомендуемое количество
                    # Базируемся на покрытии на 30-45 дней + буфер
                    recommended_order = max(
                        int(daily_rate * 35),  # 35 дней покрытия
                        int(avg_order_size * 2),  # Минимум 2 средних заказа
                        10  # Абсолютный минимум
                    )
                    
                    if priority > 30:  # Только значимые рекомендации
                        recommendations.append({
                            'product': product,
                            'priority': priority,
                            'current_stock': current_stock,
                            'recommended_quantity': recommended_order,
                            'days_until_empty': round(days_until_empty, 1),
                            'daily_sales_rate': round(daily_rate, 2),
                            'profit_margin': round(profit_margin, 1),
                            'total_profit_30d': round(total_profit, 2),
                            'urgency_level': 'КРИТИЧНО' if priority >= 100 else 'ВЫСОКАЯ' if priority >= 80 else 'СРЕДНЯЯ',
                            'reasons': reason,
                            'estimated_profit': round(recommended_order * daily_rate * (profit_margin / 100) * 10, 2)  # Прибыль за 10 дней
                        })
            
            # Сортируем по приоритету
            recommendations.sort(key=lambda x: x['priority'], reverse=True)
            
            return recommendations[:10]  # Топ 10 рекомендаций
            
        finally:
            conn.close()
    
    def market_trend_analysis(self, user_id):
        """Анализ трендов рынка на базе ваших данных"""
        conn = self.get_connection()
        
        try:
            query = '''
                SELECT oi.product_name, oi.cost_price, oi.sale_price, oi.quantity,
                       o.created_at, oi.item_delivery_type,
                       strftime('%Y-%m', o.created_at) as month_year,
                       strftime('%Y-%W', o.created_at) as week_year
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-90 days')
                ORDER BY o.created_at
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return {"error": "Недостаточно данных для анализа трендов"}
            
            trends = {}
            
            # 1. Тренд цен по товарам
            price_trends = {}
            for product in df['product_name'].unique():
                product_data = df[df['product_name'] == product].sort_values('created_at')
                if len(product_data) >= 3:
                    # Анализируем тренд цены
                    prices = product_data['sale_price'].values
                    x = np.arange(len(prices))
                    if len(x) > 1:
                        slope, intercept = np.polyfit(x, prices, 1)
                        price_change = slope * len(x)
                        
                        price_trends[product] = {
                            'trend': 'растет' if slope > 0.1 else 'падает' if slope < -0.1 else 'стабильна',
                            'change_amount': round(price_change, 2),
                            'current_price': round(prices[-1], 2),
                            'price_stability': round(np.std(prices), 2)
                        }
            
            trends['price_trends'] = price_trends
            
            # 2. Тренд объемов продаж
            weekly_volumes = df.groupby('week_year')['quantity'].sum().sort_index()
            if len(weekly_volumes) >= 4:
                volumes = weekly_volumes.values
                x = np.arange(len(volumes))
                slope, _ = np.polyfit(x, volumes, 1)
                
                trends['volume_trend'] = {
                    'direction': 'растет' if slope > 0.5 else 'падает' if slope < -0.5 else 'стабилен',
                    'weekly_change': round(slope, 2),
                    'current_weekly_avg': round(volumes[-4:].mean(), 1),
                    'trend_strength': 'сильный' if abs(slope) > 2 else 'умеренный' if abs(slope) > 0.5 else 'слабый'
                }
            
            # 3. Тренд способов доставки
            delivery_trends = df.groupby(['month_year', 'item_delivery_type'])['quantity'].sum().unstack(fill_value=0)
            if not delivery_trends.empty and len(delivery_trends.columns) > 1:
                if 'airplane' in delivery_trends.columns and 'truck' in delivery_trends.columns:
                    airplane_trend = delivery_trends['airplane'].values
                    truck_trend = delivery_trends['truck'].values
                    
                    if len(airplane_trend) >= 2:
                        airplane_change = airplane_trend[-1] - airplane_trend[0]
                        truck_change = truck_trend[-1] - truck_trend[0]
                        
                        trends['delivery_trend'] = {
                            'airplane_change': airplane_change,
                            'truck_change': truck_change,
                            'preferred_method': 'самолет' if airplane_change > truck_change else 'машина',
                            'recommendation': 'Клиенты предпочитают быструю доставку' if airplane_change > truck_change else 'Клиенты выбирают экономию'
                        }
            
            # 4. Сезонные паттерны
            df['month'] = pd.to_datetime(df['created_at']).dt.month
            monthly_patterns = df.groupby('month').agg({
                'quantity': 'sum',
                'sale_price': 'mean'
            })
            
            if not monthly_patterns.empty:
                peak_month = monthly_patterns['quantity'].idxmax()
                low_month = monthly_patterns['quantity'].idxmin()
                
                month_names = {1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
                              5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
                              9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'}
                
                trends['seasonal_pattern'] = {
                    'peak_month': month_names.get(peak_month, 'неизвестно'),
                    'low_month': month_names.get(low_month, 'неизвестно'),
                    'seasonality_strength': round(monthly_patterns['quantity'].std() / monthly_patterns['quantity'].mean(), 2)
                }
            
            return trends
            
        finally:
            conn.close()
    
    def _get_delivery_rates(self, user_id):
        """Вспомогательная функция для получения тарифов доставки"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT airplane_rate, truck_rate FROM settings WHERE user_id = ?', (user_id,))
        rates = cursor.fetchone()
        conn.close()
        
        if rates and rates[0] is not None and rates[1] is not None:
            return {'airplane': rates[0], 'truck': rates[1]}
        else:
            return {'airplane': 7.0, 'truck': 0.68}
    
    def smart_competitor_analysis(self, user_id, product_name, your_price):
        """ИИ анализ конкурентоспособности цены"""
        # Симуляция анализа конкурентов на основе ваших исторических данных
        conn = self.get_connection()
        
        try:
            # Анализируем похожие товары в вашей базе
            query = '''
                SELECT oi.sale_price, oi.cost_price, oi.quantity, o.created_at
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND oi.product_name LIKE ?
                ORDER BY o.created_at DESC
                LIMIT 20
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id, f'%{product_name}%'))
            
            if df.empty:
                return {
                    'competitive_score': 5,  # Нейтральная оценка
                    'recommendation': 'Недостаточно данных для анализа',
                    'price_position': 'unknown',
                    'suggested_action': 'Соберите больше данных о продажах'
                }
            
            # Анализ на основе ваших исторических цен
            prices = df['sale_price'].values
            avg_historical_price = np.mean(prices)
            price_std = np.std(prices)
            
            # Оценка конкурентоспособности
            if your_price < avg_historical_price - price_std:
                competitive_score = 9
                price_position = 'очень конкурентная'
                recommendation = 'Отличная цена! Можете немного поднять для увеличения прибыли'
            elif your_price < avg_historical_price - price_std * 0.5:
                competitive_score = 8
                price_position = 'конкурентная'
                recommendation = 'Хорошая цена, привлекательная для покупателей'
            elif your_price < avg_historical_price + price_std * 0.5:
                competitive_score = 6
                price_position = 'рыночная'
                recommendation = 'Цена соответствует рынку'
            elif your_price < avg_historical_price + price_std:
                competitive_score = 4
                price_position = 'выше рынка'
                recommendation = 'Цена выше среднего, убедитесь в дополнительной ценности'
            else:
                competitive_score = 2
                price_position = 'значительно выше рынка'
                recommendation = 'Рассмотрите снижение цены для повышения конкурентоспособности'
            
            return {
                'competitive_score': competitive_score,
                'recommendation': recommendation,
                'price_position': price_position,
                'market_average': round(avg_historical_price, 2),
                'your_price': your_price,
                'price_difference': round(your_price - avg_historical_price, 2),
                'suggested_action': recommendation
            }
            
        finally:
            conn.close()

# Создаем экземпляр класса
business_ai = BusinessAI()

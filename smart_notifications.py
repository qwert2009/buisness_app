import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

class SmartNotificationSystem:
    """Система умных уведомлений для бизнеса"""
    
    def __init__(self, db_path='business_manager.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_low_stock_alerts(self, user_id, threshold=5):
        """Уведомления о низких остатках"""
        conn = self.get_connection()
        try:
            query = '''
                SELECT product_name, quantity, 
                       CASE 
                           WHEN quantity = 0 THEN '🔴 Товар закончился!'
                           WHEN quantity <= ? THEN '🟡 Критически мало!'
                           ELSE '🟢 В наличии'
                       END as status
                FROM inventory 
                WHERE user_id = ? AND quantity <= ?
                ORDER BY quantity ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(threshold, user_id, threshold))
            
            alerts = []
            for _, row in df.iterrows():
                if row['quantity'] == 0:
                    alerts.append({
                        'type': 'critical',
                        'icon': '🚨',
                        'title': f"Товар '{row['product_name']}' закончился!",
                        'message': "Необходимо срочно пополнить склад",
                        'priority': 'high'
                    })
                else:
                    alerts.append({
                        'type': 'warning',
                        'icon': '⚠️',
                        'title': f"Мало товара '{row['product_name']}'",
                        'message': f"Осталось всего {row['quantity']} шт",
                        'priority': 'medium'
                    })
            
            return alerts
            
        finally:
            conn.close()
    
    def get_profit_alerts(self, user_id):
        """Уведомления об изменениях прибыли"""
        conn = self.get_connection()
        try:
            # Сравниваем прибыль за последние 7 дней с предыдущими 7 днями
            query = '''
                SELECT 
                    SUM(CASE WHEN o.created_at >= date('now', '-7 days') 
                        THEN (oi.sale_price - oi.cost_price) * oi.quantity 
                        ELSE 0 END) as current_week_profit,
                    SUM(CASE WHEN o.created_at >= date('now', '-14 days') 
                             AND o.created_at < date('now', '-7 days')
                        THEN (oi.sale_price - oi.cost_price) * oi.quantity 
                        ELSE 0 END) as previous_week_profit
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-14 days')
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if not df.empty:
                current = float(df.iloc[0]['current_week_profit'] or 0)
                previous = float(df.iloc[0]['previous_week_profit'] or 0)
                
                alerts = []
                
                if previous > 0:
                    change_percent = ((current - previous) / previous) * 100
                    
                    if change_percent > 20:
                        alerts.append({
                            'type': 'success',
                            'icon': '📈',
                            'title': 'Отличный рост прибыли!',
                            'message': f"Прибыль выросла на {change_percent:.1f}% за неделю",
                            'priority': 'high'
                        })
                    elif change_percent < -20:
                        alerts.append({
                            'type': 'warning',
                            'icon': '📉',
                            'title': 'Снижение прибыли',
                            'message': f"Прибыль упала на {abs(change_percent):.1f}% за неделю",
                            'priority': 'high'
                        })
                
                return alerts
            
            return []
            
        finally:
            conn.close()
    
    def get_sales_trend_alerts(self, user_id):
        """Уведомления о трендах продаж"""
        conn = self.get_connection()
        try:
            query = '''
                SELECT 
                    COUNT(*) as orders_count,
                    AVG(oi.total_cost) as avg_order_value,
                    date(o.created_at) as order_date
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = ? AND o.created_at >= datetime('now', '-30 days')
                GROUP BY date(o.created_at)
                ORDER BY order_date DESC
                LIMIT 7
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            alerts = []
            
            if len(df) >= 3:
                recent_orders = df.head(3)['orders_count'].mean()
                older_orders = df.tail(3)['orders_count'].mean()
                
                if recent_orders > older_orders * 1.5:
                    alerts.append({
                        'type': 'success',
                        'icon': '🚀',
                        'title': 'Рост продаж!',
                        'message': f"Среднее количество заказов увеличилось с {older_orders:.1f} до {recent_orders:.1f}",
                        'priority': 'medium'
                    })
                elif recent_orders < older_orders * 0.7:
                    alerts.append({
                        'type': 'warning',
                        'icon': '📊',
                        'title': 'Снижение активности',
                        'message': f"Количество заказов снизилось с {older_orders:.1f} до {recent_orders:.1f}",
                        'priority': 'medium'
                    })
            
            return alerts
            
        finally:
            conn.close()
    
    def get_seasonal_alerts(self, user_id):
        """Сезонные уведомления и советы"""
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        seasonal_alerts = []
        
        # Новогодние праздники
        if current_month == 12 and current_day >= 15:
            seasonal_alerts.append({
                'type': 'info',
                'icon': '🎄',
                'title': 'Новогодний сезон!',
                'message': 'Время увеличить запасы подарочных товаров',
                'priority': 'medium'
            })
        
        # День Святого Валентина
        elif current_month == 2 and current_day <= 14:
            seasonal_alerts.append({
                'type': 'info',
                'icon': '💝',
                'title': 'День Святого Валентина близко!',
                'message': 'Подготовьте романтические товары и подарки',
                'priority': 'medium'
            })
        
        # Школьный сезон
        elif current_month == 8:
            seasonal_alerts.append({
                'type': 'info',
                'icon': '🎒',
                'title': 'Школьный сезон!',
                'message': 'Канцелярские товары пользуются повышенным спросом',
                'priority': 'medium'
            })
        
        return seasonal_alerts
    
    def get_performance_insights(self, user_id):
        """Инсайты о производительности"""
        conn = self.get_connection()
        try:
            # Топ товары по прибыли
            query = '''
                SELECT 
                    oi.product_name,
                    SUM((oi.sale_price - oi.cost_price) * oi.quantity) as profit,
                    SUM(oi.quantity) as total_sold
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-30 days')
                GROUP BY oi.product_name
                ORDER BY profit DESC
                LIMIT 3
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            insights = []
            
            if not df.empty:
                top_product = df.iloc[0]
                insights.append({
                    'type': 'success',
                    'icon': '🏆',
                    'title': 'Ваш ТОП товар!',
                    'message': f"'{top_product['product_name']}' принес {top_product['profit']:.2f} ТМ прибыли",
                    'priority': 'low'
                })
                
                if len(df) >= 2:
                    insights.append({
                        'type': 'info',
                        'icon': '📊',
                        'title': 'Ваши лидеры продаж',
                        'message': f"ТОП-3: {', '.join(df['product_name'].tolist())}",
                        'priority': 'low'
                    })
            
            return insights
            
        finally:
            conn.close()
    
    def get_all_notifications(self, user_id):
        """Получает все уведомления"""
        all_notifications = []
        
        # Собираем все типы уведомлений (убираем уведомления о малом количестве товара)
        all_notifications.extend(self.get_profit_alerts(user_id))
        all_notifications.extend(self.get_sales_trend_alerts(user_id))
        all_notifications.extend(self.get_seasonal_alerts(user_id))
        all_notifications.extend(self.get_performance_insights(user_id))
        
        # Сортируем по приоритету
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        all_notifications.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return all_notifications
    
    def format_notification_html(self, notification):
        """Форматирует уведомление в HTML"""
        type_colors = {
            'critical': '#ff4444',
            'warning': '#ff8800',
            'success': '#00aa44',
            'info': '#0088ff'
        }
        
        color = type_colors.get(notification['type'], '#888888')
        
        return f"""
        <div style="
            background: linear-gradient(90deg, {color}22 0%, {color}11 100%);
            border-left: 4px solid {color};
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4 style="margin: 0 0 8px 0; color: {color};">
                {notification['icon']} {notification['title']}
            </h4>
            <p style="margin: 0; color: #333;">
                {notification['message']}
            </p>
        </div>
        """

# Создаем экземпляр системы уведомлений
smart_notifications = SmartNotificationSystem()

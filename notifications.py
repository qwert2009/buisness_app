"""
Модуль уведомлений для бизнес-менеджера
"""
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import threading
import time
import schedule

class NotificationManager:
    def __init__(self, db_path='business_manager.db'):
        self.db_path = db_path
        
    def get_user_settings(self, user_id):
        """Получение настроек уведомлений пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email_notifications, smtp_server, smtp_port, email_username, email_password
            FROM settings WHERE user_id = ?
        ''', (user_id,))
        
        settings = cursor.fetchone()
        conn.close()
        
        if settings:
            return {
                'enabled': bool(settings[0]),
                'smtp_server': settings[1],
                'smtp_port': settings[2],
                'username': settings[3],
                'password': settings[4]
            }
        return None
    
    def send_email(self, user_id, subject, body, recipient_email):
        """Отправка email уведомления"""
        settings = self.get_user_settings(user_id)
        
        if not settings or not settings['enabled']:
            return False, "Уведомления отключены"
        
        try:
            # Создание сообщения
            msg = MIMEMultipart()
            msg['From'] = settings['username']
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Отправка через SMTP
            server = smtplib.SMTP(settings['smtp_server'], settings['smtp_port'])
            server.starttls()
            server.login(settings['username'], settings['password'])
            
            text = msg.as_string()
            server.sendmail(settings['username'], recipient_email, text)
            server.quit()
            
            return True, "Уведомление отправлено"
            
        except Exception as e:
            return False, f"Ошибка отправки: {str(e)}"
    
    def check_airplane_deliveries(self):
        """Проверка заказов с доставкой самолетом (еженедельные напоминания)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Находим заказы с доставкой самолетом, созданные более недели назад
        one_week_ago = datetime.now() - timedelta(days=7)
        
        cursor.execute('''
            SELECT DISTINCT o.id, o.order_name, o.created_at, u.email, o.user_id
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.delivery_type = 'airplane' 
            AND datetime(o.created_at) <= ?
            AND o.notification_sent = 0
        ''', (one_week_ago.strftime('%Y-%m-%d %H:%M:%S'),))
        
        orders = cursor.fetchall()
        
        for order in orders:
            order_id, order_name, created_at, email, user_id = order
            
            # Создаем уведомление
            subject = f"Напоминание о доставке: {order_name}"
            body = f"""
            <html>
            <body>
                <h2>Напоминание о прибытии товара</h2>
                <p>Здравствуйте!</p>
                <p>Напоминаем вам о заказе: <strong>{order_name}</strong></p>
                <p>Дата заказа: {created_at}</p>
                <p>Тип доставки: Самолет</p>
                <p>Пожалуйста, проверьте статус доставки вашего заказа.</p>
                <br>
                <p>С уважением,<br>Команда Бизнес Менеджера</p>
            </body>
            </html>
            """
            
            success, message = self.send_email(user_id, subject, body, email)
            
            if success:
                # Отмечаем, что уведомление отправлено
                cursor.execute('UPDATE orders SET notification_sent = 1 WHERE id = ?', (order_id,))
        
        conn.commit()
        conn.close()
    
    def check_truck_deliveries(self):
        """Проверка заказов с доставкой машиной (месячные напоминания)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Находим заказы с доставкой машиной, созданные более месяца назад
        one_month_ago = datetime.now() - timedelta(days=30)
        
        cursor.execute('''
            SELECT DISTINCT o.id, o.order_name, o.created_at, u.email, o.user_id
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.delivery_type = 'truck' 
            AND datetime(o.created_at) <= ?
            AND o.notification_sent = 0
        ''', (one_month_ago.strftime('%Y-%m-%d %H:%M:%S'),))
        
        orders = cursor.fetchall()
        
        for order in orders:
            order_id, order_name, created_at, email, user_id = order
            
            # Создаем уведомление
            subject = f"Напоминание о доставке: {order_name}"
            body = f"""
            <html>
            <body>
                <h2>Напоминание о прибытии товара</h2>
                <p>Здравствуйте!</p>
                <p>Напоминаем вам о заказе: <strong>{order_name}</strong></p>
                <p>Дата заказа: {created_at}</p>
                <p>Тип доставки: Автомобиль</p>
                <p>Прошел месяц с момента заказа. Пожалуйста, проверьте статус доставки.</p>
                <br>
                <p>С уважением,<br>Команда Бизнес Менеджера</p>
            </body>
            </html>
            """
            
            success, message = self.send_email(user_id, subject, body, email)
            
            if success:
                # Отмечаем, что уведомление отправлено
                cursor.execute('UPDATE orders SET notification_sent = 1 WHERE id = ?', (order_id,))
        
        conn.commit()
        conn.close()
    
    def check_low_stock(self):
        """Проверка низких остатков на складе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем настройки пользователей и их склады
        cursor.execute('''
            SELECT DISTINCT i.user_id, u.email
            FROM inventory i
            JOIN users u ON i.user_id = u.id
            WHERE i.quantity <= 5
        ''')
        
        users_with_low_stock = cursor.fetchall()
        
        for user_id, email in users_with_low_stock:
            # Получаем товары с низкими остатками для этого пользователя
            cursor.execute('''
                SELECT product_name, quantity
                FROM inventory
                WHERE user_id = ? AND quantity <= 5
                ORDER BY quantity ASC
            ''', (user_id,))
            
            low_stock_items = cursor.fetchall()
            
            if low_stock_items:
                # Создаем список товаров для уведомления
                items_html = ""
                for product_name, quantity in low_stock_items:
                    items_html += f"<li>{product_name}: <strong>{quantity} шт.</strong></li>"
                
                subject = "⚠️ Предупреждение о низких остатках на складе"
                body = f"""
                <html>
                <body>
                    <h2>Низкие остатки на складе</h2>
                    <p>Здравствуйте!</p>
                    <p>Обнаружены товары с низкими остатками на вашем складе:</p>
                    <ul>
                        {items_html}
                    </ul>
                    <p>Рекомендуем пополнить запасы данных товаров.</p>
                    <br>
                    <p>С уважением,<br>Команда Бизнес Менеджера</p>
                </body>
                </html>
                """
                
                self.send_email(user_id, subject, body, email)
        
        conn.close()
    
    def start_notification_scheduler(self):
        """Запуск планировщика уведомлений"""
        # Планируем проверки
        schedule.every().tuesday.at("10:00").do(self.check_airplane_deliveries)
        schedule.every().day.at("09:00").do(self.check_truck_deliveries)
        schedule.every().monday.at("08:00").do(self.check_low_stock)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Проверяем каждый час
        
        # Запускаем в отдельном потоке
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        return "Планировщик уведомлений запущен"

# Функция для создания единственного экземпляра
_notification_manager = None

def get_notification_manager():
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager

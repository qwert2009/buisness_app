import random
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

class BusinessChatBot:
    """ИИ чат-бот для бизнес консультаций"""
    
    def __init__(self, db_path='business_manager.db'):
        self.db_path = db_path
        self.responses = {
            'greeting': [
                "Привет! 👋 Я ваш ИИ помощник по бизнесу. Как дела с продажами?",
                "Добро пожаловать! 🚀 Готов помочь оптимизировать ваш бизнес!",
                "Здравствуйте! 💼 Давайте увеличим вашу прибыль вместе!"
            ],
            'profit_question': [
                "Отличный вопрос о прибыли! 💰 Давайте проанализируем ваши данные...",
                "Прибыль - это ключ к успеху! 📈 Сейчас посмотрю ваши показатели...",
                "Вопрос на миллион! 💎 Анализирую ваш бизнес..."
            ],
            'inventory_question': [
                "Управление складом - важная тема! 📦 Проверяю ваши запасы...",
                "Хороший склад = хорошие продажи! 🏪 Анализирую ситуацию...",
                "Оптимизация склада поможет сэкономить! 💡 Изучаю данные..."
            ],
            'sales_question': [
                "Продажи - это сердце бизнеса! ❤️ Смотрю ваши показатели...",
                "Отличная тема! 🎯 Анализирую ваши продажи...",
                "Продажи растут? 📊 Давайте разберемся вместе!"
            ]
        }
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def classify_question(self, question):
        """Классифицирует вопрос пользователя"""
        question_lower = question.lower()
        
        profit_keywords = ['прибыль', 'доход', 'заработок', 'деньги', 'выручка', 'маржа']
        inventory_keywords = ['склад', 'товар', 'запас', 'остаток', 'инвентарь']
        sales_keywords = ['продажи', 'заказ', 'клиент', 'покупатель', 'объем']
        greeting_keywords = ['привет', 'здравствуй', 'добро пожаловать', 'начало']
        
        if any(word in question_lower for word in profit_keywords):
            return 'profit_question'
        elif any(word in question_lower for word in inventory_keywords):
            return 'inventory_question'
        elif any(word in question_lower for word in sales_keywords):
            return 'sales_question'
        elif any(word in question_lower for word in greeting_keywords):
            return 'greeting'
        else:
            return 'general'
    
    def get_business_insights(self, user_id):
        """Получает основные инсайты о бизнесе"""
        conn = self.get_connection()
        
        try:
            # Основная статистика
            query = '''
                SELECT 
                    COUNT(DISTINCT o.id) as total_orders,
                    SUM(oi.sale_price * oi.quantity) as total_revenue,
                    SUM((oi.sale_price - oi.cost_price) * oi.quantity) as total_profit,
                    AVG(oi.sale_price * oi.quantity) as avg_order_value,
                    COUNT(DISTINCT oi.product_name) as unique_products
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = ? AND o.created_at >= date('now', '-30 days')
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty or df.iloc[0]['total_orders'] == 0:
                return {
                    'total_orders': 0,
                    'total_revenue': 0,
                    'total_profit': 0,
                    'avg_order_value': 0,
                    'unique_products': 0,
                    'profit_margin': 0
                }
            
            row = df.iloc[0]
            profit_margin = (row['total_profit'] / row['total_revenue'] * 100) if row['total_revenue'] > 0 else 0
            
            return {
                'total_orders': int(row['total_orders']),
                'total_revenue': float(row['total_revenue']),
                'total_profit': float(row['total_profit']),
                'avg_order_value': float(row['avg_order_value']),
                'unique_products': int(row['unique_products']),
                'profit_margin': round(profit_margin, 1)
            }
            
        finally:
            conn.close()
    
    def get_inventory_status(self, user_id):
        """Получает статус склада"""
        conn = self.get_connection()
        
        try:
            query = '''
                SELECT 
                    COUNT(*) as total_products,
                    SUM(quantity) as total_items,
                    AVG(quantity) as avg_stock_per_product
                FROM inventory
                WHERE user_id = ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return {'total_products': 0, 'total_items': 0, 'avg_stock_per_product': 0}
            
            row = df.iloc[0]
            return {
                'total_products': int(row['total_products']),
                'total_items': int(row['total_items']),
                'avg_stock_per_product': round(float(row['avg_stock_per_product']), 1)
            }
            
        finally:
            conn.close()
    
    def generate_smart_response(self, user_id, question):
        """Генерирует умный ответ на основе данных пользователя"""
        question_type = self.classify_question(question)
        
        # Получаем данные для анализа
        insights = self.get_business_insights(user_id)
        inventory = self.get_inventory_status(user_id)
        
        # Базовый ответ
        base_response = random.choice(self.responses.get(question_type, ["Интересный вопрос! 🤔 Давайте разберемся..."]))
        
        # Генерируем персонализированный совет
        if question_type == 'profit_question':
            if insights['total_profit'] > 0:
                advice = f"""
📊 **Ваша статистика за 30 дней:**
• Общая прибыль: ${insights['total_profit']:.2f}
• Маржинальность: {insights['profit_margin']:.1f}%
• Заказов: {insights['total_orders']}

💡 **Мой совет:**
"""
                if insights['profit_margin'] < 15:
                    advice += "Ваша маржа ниже 15% - стоит пересмотреть цены или найти более дешевых поставщиков! 📈"
                elif insights['profit_margin'] > 30:
                    advice += "Отличная маржа! Можно увеличить объемы или инвестировать в маркетинг! 🚀"
                else:
                    advice += "Хорошая маржа! Попробуйте оптимизировать самые прибыльные товары! 🎯"
            else:
                advice = "Пока данных мало, но не переживайте! Каждый успешный бизнес начинался с нуля. Сосредоточьтесь на качестве товаров и клиентском сервисе! 💪"
        
        elif question_type == 'inventory_question':
            advice = f"""
📦 **Ваш склад:**
• Товаров в ассортименте: {inventory['total_products']}
• Общее количество: {inventory['total_items']} шт
• В среднем на товар: {inventory['avg_stock_per_product']} шт

💡 **Рекомендация:**
"""
            if inventory['total_products'] > 50:
                advice += "Большой ассортимент! Проанализируйте, какие товары продаются лучше всего! 📊"
            elif inventory['total_products'] < 10:
                advice += "Стоит расширить ассортимент - больше товаров = больше возможностей! 🛒"
            else:
                advice += "Оптимальный размер! Следите за оборачиваемостью каждого товара! ⚡"
        
        elif question_type == 'sales_question':
            if insights['total_orders'] > 0:
                advice = f"""
🎯 **Ваши продажи:**
• Заказов за месяц: {insights['total_orders']}
• Средний чек: ${insights['avg_order_value']:.2f}
• Уникальных товаров: {insights['unique_products']}

💡 **Стратегия:**
"""
                if insights['avg_order_value'] < 20:
                    advice += "Средний чек низкий - попробуйте кросс-продажи и бонусы за объем! 💰"
                elif insights['avg_order_value'] > 100:
                    advice += "Высокий средний чек! Фокусируйтесь на VIP-клиентах и премиум сегменте! 💎"
                else:
                    advice += "Хороший средний чек! Работайте над увеличением частоты покупок! 🔄"
            else:
                advice = "Продажи только начинаются! Сосредоточьтесь на первых клиентах - они самые важные! 🌟"
        
        else:
            advice = self._generate_general_advice(insights, inventory)
        
        return f"{base_response}\n\n{advice}"
    
    def _generate_general_advice(self, insights, inventory):
        """Генерирует общий совет"""
        tips = []
        
        if insights['total_orders'] == 0:
            tips.append("🚀 Начните с малого - добавьте первые товары и создайте первый заказ!")
        
        if inventory['total_products'] > 0 and insights['total_orders'] == 0:
            tips.append("📦 У вас есть товары на складе - время продавать!")
        
        if insights['profit_margin'] > 0:
            tips.append(f"💰 Ваша маржа {insights['profit_margin']:.1f}% - это {'отлично' if insights['profit_margin'] > 25 else 'хорошо' if insights['profit_margin'] > 15 else 'можно улучшить'}!")
        
        if not tips:
            tips = [
                "📈 Анализируйте данные регулярно - это ключ к росту!",
                "🎯 Фокусируйтесь на самых прибыльных товарах!",
                "💡 Экспериментируйте с ценами и следите за результатом!",
                "🤝 Довольные клиенты - лучшая реклама!"
            ]
        
        return "💡 **Мои рекомендации:**\n" + "\n".join(f"• {tip}" for tip in random.sample(tips, min(3, len(tips))))
    
    def get_quick_business_summary(self, user_id):
        """Получает быструю сводку бизнеса"""
        insights = self.get_business_insights(user_id)
        inventory = self.get_inventory_status(user_id)
        
        if insights['total_orders'] == 0:
            return "🚀 **Ваш бизнес только начинается!** Время создать первый заказ и покорить рынок!"
        
        summary = f"""
🏢 **Быстрая сводка вашего бизнеса:**

📊 **За последние 30 дней:**
• Заказов: {insights['total_orders']}
• Выручка: ${insights['total_revenue']:.2f}
• Прибыль: ${insights['total_profit']:.2f}
• Маржинальность: {insights['profit_margin']:.1f}%

📦 **Склад:**
• Товаров: {inventory['total_products']}
• Общий остаток: {inventory['total_items']} шт

🎯 **Статус:** {'🔥 Отлично!' if insights['profit_margin'] > 25 else '📈 Хорошо!' if insights['profit_margin'] > 15 else '⚡ Есть потенциал!'}
        """
        
        return summary
    
    def get_business_tips(self):
        """Возвращает случайные бизнес-советы"""
        tips = [
            "� **Золотое правило:** 80% прибыли приносят 20% товаров. Найдите свои 20%!",
            "🎯 **Фокус на клиенте:** Удержать клиента в 5 раз дешевле, чем привлечь нового!",
            "📊 **Анализируйте данные:** Принимайте решения на основе фактов, а не интуиции!",
            "🚀 **Автоматизация:** Автоматизируйте рутинные процессы и фокусируйтесь на росте!",
            "💰 **Управление деньгами:** Следите за денежным потоком - это артерия бизнеса!",
            "🏆 **Качество превыше всего:** Лучше продать меньше, но качественно!",
            "📈 **Постоянное улучшение:** Каждый день делайте что-то для роста бизнеса!",
            "🤝 **Партнерства:** Стройте долгосрочные отношения с поставщиками и клиентами!",
            "🎨 **Инновации:** Не бойтесь экспериментировать с новыми товарами и услугами!",
            "� **Цифровизация:** Используйте технологии для масштабирования бизнеса!"
        ]
        return random.choice(tips)
    
    def get_market_advice(self, user_id):
        """Дает рыночные советы на основе данных"""
        insights = self.get_business_insights(user_id)
        
        advices = []
        
        if insights['avg_order_value'] < 25:
            advices.append("💰 **Увеличьте средний чек:** Предлагайте дополнительные товары или создавайте наборы!")
        
        if insights['profit_margin'] < 20:
            advices.append("📊 **Оптимизируйте маржу:** Пересмотрите закупочные цены или увеличьте розничные!")
        
        if insights['total_orders'] < 10:
            advices.append("🚀 **Увеличьте продажи:** Расширьте каналы продаж и улучшите маркетинг!")
        
        if not advices:
            advices = [
                "🏆 **Отлично работаете!** Продолжайте в том же духе и масштабируйте успешные практики!",
                "📈 **Время роста:** Ваши показатели хороши - пора думать о расширении ассортимента!",
                "💎 **VIP-клиенты:** Создайте программу лояльности для постоянных покупателей!"
            ]
        
        return "🎯 **Рыночные рекомендации:**\n\n" + "\n\n".join(f"• {advice}" for advice in advices[:3])
    
    def get_seasonal_advice(self):
        """Дает сезонные советы"""
        current_month = datetime.now().month
        
        seasonal_tips = {
            1: "❄️ **Январь:** Время планирования! Проанализируйте результаты года и поставьте цели.",
            2: "� **Февраль:** День Святого Валентина - отличная возможность для тематических акций!",
            3: "🌸 **Март:** Весенние товары входят в тренд. Обновите ассортимент!",
            4: "🐰 **Апрель:** Пасхальный сезон - время для сладких продаж!",
            5: "🌞 **Май:** Майские праздники - увеличьте запасы популярных товаров!",
            6: "👶 **Июнь:** День защиты детей - детские товары на пике спроса!",
            7: "�️ **Июль:** Летний сезон - время для товаров для отдыха и путешествий!",
            8: "☀️ **Август:** Подготовка к школе - канцелярия и учебные принадлежности!",
            9: "🎒 **Сентябрь:** Начало учебного года - пик продаж школьных товаров!",
            10: "🍂 **Октябрь:** Хэллоуин и осенние товары набирают популярность!",
            11: "🦃 **Ноябрь:** Подготовка к зиме и праздничному сезону!",
            12: "🎄 **Декабрь:** Новогодние продажи - самое горячее время года!"
        }
        
        return seasonal_tips.get(current_month, "📅 **Каждый месяц** - это новые возможности для роста!")
    
    def analyze_user_question_advanced(self, question, user_id):
        """Продвинутый анализ вопроса с учетом данных пользователя"""
        question_lower = question.lower()
        insights = self.get_business_insights(user_id)
        
        # Определяем интент более точно
        if any(word in question_lower for word in ['помощь', 'что делать', 'как', 'совет']):
            if insights['total_orders'] == 0:
                return self._get_startup_advice()
            elif insights['profit_margin'] < 10:
                return self._get_profit_improvement_advice()
            else:
                return self._get_growth_advice()
        
        return None
    
    def _get_startup_advice(self):
        """Советы for начинающих"""
        return """
🚀 **Советы для начала:**

1. **📦 Добавьте товары:** Начните с 5-10 товаров, которые вы хорошо знаете
2. **💰 Установите правильные цены:** Себестоимость + 30-50% = розничная цена
3. **📊 Создайте первый заказ:** Даже тестовый - чтобы понять процесс
4. **📈 Анализируйте:** Каждую неделю смотрите на цифры и корректируйте

💡 **Помните:** Каждый великий бизнес начинался с первого товара!
        """
    
    def _get_profit_improvement_advice(self):
        """Советы по улучшению прибыли"""
        return """
📈 **Как увеличить прибыль:**

1. **🔍 Анализ затрат:** Найдите где можно сэкономить на закупках
2. **💲 Пересмотр цен:** Возможно, ваши цены слишком низкие
3. **📦 ABC-анализ:** Сосредоточьтесь на самых прибыльных товарах
4. **⚡ Быстрая оборачиваемость:** Лучше продать быстро с меньшей маржой

🎯 **Цель:** Маржа 20%+ это здоровый бизнес!
        """
    
    def _get_growth_advice(self):
        """Советы по росту"""
        return """
🚀 **Стратегии роста:**

1. **📊 Масштабирование:** Увеличивайте объемы по успешным товарам
2. **🆕 Новые товары:** Добавляйте смежные категории
3. **👥 Клиентская база:** Работайте с повторными покупками
4. **🤖 Автоматизация:** Используйте ИИ функции нашего приложения

💎 **Вы на правильном пути - продолжайте развиваться!**
        """
    
    def get_motivational_quote(self):
        """Возвращает мотивационную цитату"""
        quotes = [
            "💪 \"Успех - это не конечная точка, неудача - не смертельная, важна смелость продолжать!\" - Уинстон Черчилль",
            "🚀 \"Лучшее время для посадки дерева было 20 лет назад. Второе лучшее время - сейчас!\" - Китайская пословица",
            "💎 \"Качество важнее количества. Один домашний забег лучше, чем дюжина промахов!\" - Стив Джобс",
            "🎯 \"Не ждите возможностей - создавайте их!\" - Джордж Бернард Шоу",
            "⚡ \"Инновации отличают лидера от последователя!\" - Стив Джобс",
            "🌟 \"Единственный способ делать великую работу - любить то, что вы делаете!\" - Стив Джобс",
            "🏆 \"Твой единственный ограничитель - это ты сам. Убери его!\" - Мотивационный коуч",
            "💰 \"Деньги - это только инструмент. Цель - это свобода!\" - Роберт Кийосаки",
            "📊 \"Измеряй дважды, режь один раз. В бизнесе - анализируй, потом действуй!\" - Бизнес мудрость"
        ]
        return random.choice(quotes)

# Создаем экземпляр чат-бота
business_chatbot = BusinessChatBot()

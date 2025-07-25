"""
Модуль расширенной аналитики и прогнозирования
"""
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    def __init__(self, db_path='business_manager.db'):
        self.db_path = db_path
    
    def get_sales_trends(self, user_id, days=30, delivery_method=None, start_date=None, end_date=None):
        """Анализ трендов продаж с расширенными фильтрами"""
        conn = sqlite3.connect(self.db_path)
        
        # Определяем временной диапазон
        if start_date and end_date:
            # Используем заданные даты
            pass
        else:
            # Используем количество дней назад
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
        
        # Строим базовый запрос
        base_query = '''
            SELECT 
                DATE(o.created_at) as date,
                SUM(oi.total_cost) as revenue,
                SUM(oi.cost_price + oi.delivery_cost) as costs,
                COUNT(DISTINCT o.id) as orders_count,
                SUM(oi.quantity) as items_sold,
                AVG(oi.total_cost) as avg_order_value,
                o.delivery_type
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ? 
            AND DATE(o.created_at) BETWEEN ? AND ?
        '''
        
        # Добавляем фильтр по типу доставки
        params = [user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if delivery_method and delivery_method != 'all':
            base_query += ' AND o.delivery_type = ?'
            params.append(delivery_method)
        
        base_query += '''
            GROUP BY DATE(o.created_at), o.delivery_type
            ORDER BY date
        '''
        
        df = pd.read_sql_query(base_query, conn, params=params)
        
        conn.close()
        
        if df.empty:
            return None
        
        # Группируем по дате если не нужно разделение по типу доставки
        if delivery_method == 'all' or delivery_method is None:
            df = df.groupby('date').agg({
                'revenue': 'sum',
                'costs': 'sum',
                'orders_count': 'sum',
                'items_sold': 'sum',
                'avg_order_value': 'mean'
            }).reset_index()
        
        # Добавляем расчетные поля
        df['profit'] = df['revenue'] - df['costs']
        df['profit_margin'] = (df['profit'] / df['revenue'] * 100).round(2)
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def predict_sales(self, user_id, days_ahead=30):
        """Простое прогнозирование продаж на основе линейной регрессии"""
        trends_df = self.get_sales_trends(user_id, days=90)  # Берем данные за 3 месяца
        
        if trends_df is None or len(trends_df) < 7:
            return None
        
        # Подготавливаем данные для прогноза
        trends_df['day_number'] = range(len(trends_df))
        
        # Простая линейная регрессия
        coeffs_revenue = np.polyfit(trends_df['day_number'], trends_df['revenue'], 1)
        coeffs_orders = np.polyfit(trends_df['day_number'], trends_df['orders_count'], 1)
        
        # Создаем прогноз
        last_day = len(trends_df)
        future_days = range(last_day, last_day + days_ahead)
        
        predicted_revenue = [coeffs_revenue[0] * day + coeffs_revenue[1] for day in future_days]
        predicted_orders = [max(0, coeffs_orders[0] * day + coeffs_orders[1]) for day in future_days]
        
        # Создаем даты для прогноза
        last_date = trends_df['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_revenue': predicted_revenue,
            'predicted_orders': predicted_orders
        })
        
        return {
            'historical': trends_df,
            'forecast': forecast_df,
            'revenue_trend': 'рост' if coeffs_revenue[0] > 0 else 'снижение',
            'orders_trend': 'рост' if coeffs_orders[0] > 0 else 'снижение'
        }
    
    def get_product_analytics(self, user_id):
        """Аналитика по товарам"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                oi.product_name,
                COUNT(*) as order_frequency,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.total_cost) as total_revenue,
                SUM(oi.cost_price) as total_cost,
                SUM(oi.total_cost - oi.cost_price - oi.delivery_cost) as total_profit,
                AVG(oi.total_cost) as avg_price,
                MAX(o.created_at) as last_order_date
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ?
            GROUP BY oi.product_name
            ORDER BY total_revenue DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        if df.empty:
            return None
        
        # Добавляем расчетные поля
        df['profit_margin'] = ((df['total_profit'] / df['total_revenue']) * 100).round(2)
        df['avg_profit_per_item'] = (df['total_profit'] / df['total_quantity']).round(2)
        
        return df
    
    def get_delivery_analytics(self, user_id):
        """Аналитика по типам доставки"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                o.delivery_type,
                COUNT(DISTINCT o.id) as orders_count,
                SUM(oi.total_cost) as total_revenue,
                SUM(oi.delivery_cost) as total_delivery_cost,
                SUM(oi.weight) as total_weight,
                AVG(oi.delivery_cost) as avg_delivery_cost
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ?
            GROUP BY o.delivery_type
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        if df.empty:
            return None
        
        # Добавляем расчеты
        df['delivery_cost_percentage'] = ((df['total_delivery_cost'] / df['total_revenue']) * 100).round(2)
        df['avg_weight_per_order'] = (df['total_weight'] / df['orders_count']).round(2)
        
        return df
    
    def get_profitability_analysis(self, user_id):
        """Анализ рентабельности по месяцам"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                strftime('%Y-%m', o.created_at) as month,
                SUM(oi.total_cost) as revenue,
                SUM(oi.cost_price) as cost_price,
                SUM(oi.delivery_cost) as delivery_cost,
                COUNT(DISTINCT o.id) as orders_count
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ?
            GROUP BY strftime('%Y-%m', o.created_at)
            ORDER BY month
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        if df.empty:
            return None
        
        # Расчеты
        df['total_costs'] = df['cost_price'] + df['delivery_cost']
        df['profit'] = df['revenue'] - df['total_costs']
        df['profit_margin'] = ((df['profit'] / df['revenue']) * 100).round(2)
        df['roi'] = ((df['profit'] / df['total_costs']) * 100).round(2)
        
        return df
    
    def create_dashboard_charts(self, user_id):
        """Создание графиков для дашборда"""
        charts = {}
        
        # 1. Тренд продаж
        sales_data = self.get_sales_trends(user_id, days=30)
        if sales_data is not None:
            fig_sales = go.Figure()
            fig_sales.add_trace(go.Scatter(
                x=sales_data['date'], 
                y=sales_data['revenue'],
                mode='lines+markers',
                name='Выручка',
                line=dict(color='#000080')
            ))
            fig_sales.add_trace(go.Scatter(
                x=sales_data['date'], 
                y=sales_data['profit'],
                mode='lines+markers',
                name='Прибыль',
                line=dict(color='#006400')
            ))
            fig_sales.update_layout(
                title='Динамика продаж за последний месяц',
                xaxis_title='Дата',
                yaxis_title='Сумма ($)',
                hovermode='x unified'
            )
            charts['sales_trend'] = fig_sales
        
        # 2. Аналитика товаров
        product_data = self.get_product_analytics(user_id)
        if product_data is not None:
            top_products = product_data.head(10)
            fig_products = px.bar(
                top_products, 
                x='product_name', 
                y='total_revenue',
                title='Топ-10 товаров по выручке',
                color='profit_margin',
                color_continuous_scale=[[0, '#000080'], [1, '#003366']]
            )
            fig_products.update_xaxes(tickangle=45)
            charts['top_products'] = fig_products
        
        # 3. Аналитика доставки
        delivery_data = self.get_delivery_analytics(user_id)
        if delivery_data is not None:
            fig_delivery = px.pie(
                delivery_data, 
                values='orders_count', 
                names='delivery_type',
                title='Распределение заказов по типу доставки',
                color_discrete_sequence=['#000080', '#003366', '#004d00', '#333333']
            )
            charts['delivery_distribution'] = fig_delivery
        
        # 4. Помесячная рентабельность
        profitability_data = self.get_profitability_analysis(user_id)
        if profitability_data is not None:
            fig_prof = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_prof.add_trace(
                go.Bar(x=profitability_data['month'], y=profitability_data['profit'], 
                       name='Прибыль', marker_color='#000080'),
                secondary_y=False,
            )
            
            fig_prof.add_trace(
                go.Scatter(x=profitability_data['month'], y=profitability_data['profit_margin'], 
                          mode='lines+markers', name='Маржа %', line=dict(color='#003366')),
                secondary_y=True,
            )
            
            fig_prof.update_xaxes(title_text="Месяц")
            fig_prof.update_yaxes(title_text="Прибыль ($)", secondary_y=False)
            fig_prof.update_yaxes(title_text="Маржа (%)", secondary_y=True)
            fig_prof.update_layout(title_text="Помесячная рентабельность")
            
            charts['monthly_profitability'] = fig_prof
        
        return charts
    
    def get_business_insights(self, user_id):
        """Генерация бизнес-инсайтов"""
        insights = []
        
        # Анализ товаров
        product_data = self.get_product_analytics(user_id)
        if product_data is not None:
            # Самый прибыльный товар
            most_profitable = product_data.loc[product_data['total_profit'].idxmax()]
            insights.append(f"💰 Самый прибыльный товар: {most_profitable['product_name']} (${most_profitable['total_profit']:.2f})")
            
            # Товар с лучшей маржей
            best_margin = product_data.loc[product_data['profit_margin'].idxmax()]
            insights.append(f"📈 Лучшая маржа: {best_margin['product_name']} ({best_margin['profit_margin']:.1f}%)")
            
            # Самый популярный товар
            most_popular = product_data.loc[product_data['order_frequency'].idxmax()]
            insights.append(f"🔥 Самый заказываемый: {most_popular['product_name']} ({most_popular['order_frequency']} заказов)")
        
        # Анализ доставки
        delivery_data = self.get_delivery_analytics(user_id)
        if delivery_data is not None:
            for _, row in delivery_data.iterrows():
                delivery_type = "Самолет" if row['delivery_type'] == 'airplane' else "Автомобиль"
                insights.append(f"🚚 {delivery_type}: {row['orders_count']} заказов, {row['delivery_cost_percentage']:.1f}% от выручки")
        
        # Прогноз
        prediction = self.predict_sales(user_id, days_ahead=7)
        if prediction:
            total_predicted = sum(prediction['forecast']['predicted_revenue'])
            insights.append(f"🔮 Прогноз на неделю: ${total_predicted:.2f} (тренд: {prediction['revenue_trend']})")
        
        return insights
    
    def get_advanced_predictions(self, user_id, days_ahead=30):
        """Продвинутые AI предсказания с машинным обучением"""
        conn = sqlite3.connect(self.db_path)
        
        # Получаем исторические данные
        query = '''
            SELECT 
                DATE(o.created_at) as date,
                o.delivery_type,
                SUM(oi.total_cost) as revenue,
                COUNT(DISTINCT o.id) as orders,
                SUM(oi.quantity) as items_sold,
                SUM(oi.weight) as total_weight
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ?
            GROUP BY DATE(o.created_at), o.delivery_type
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        if df.empty or len(df) < 7:
            return None
        
        # Подготовка данных для ML
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Создаем агрегированные данные по дням
        daily_data = df.groupby('date').agg({
            'revenue': 'sum',
            'orders': 'sum',
            'items_sold': 'sum',
            'total_weight': 'sum'
        })
        
        # Добавляем временные признаки
        daily_data['day_of_week'] = daily_data.index.dayofweek
        daily_data['day_of_month'] = daily_data.index.day
        daily_data['month'] = daily_data.index.month
        
        # Скользящие средние
        daily_data['revenue_ma_7'] = daily_data['revenue'].rolling(window=7).mean()
        daily_data['orders_ma_7'] = daily_data['orders'].rolling(window=7).mean()
        
        # Удаляем NaN значения
        daily_data = daily_data.dropna()
        
        if len(daily_data) < 5:
            return None
        
        predictions = {}
        
        # Предсказание выручки
        X_revenue = daily_data[['day_of_week', 'day_of_month', 'month', 'revenue_ma_7']].values
        y_revenue = daily_data['revenue'].values
        
        poly_features = PolynomialFeatures(degree=2)
        X_revenue_poly = poly_features.fit_transform(X_revenue)
        
        model_revenue = LinearRegression()
        model_revenue.fit(X_revenue_poly, y_revenue)
        
        # Предсказание заказов
        X_orders = daily_data[['day_of_week', 'day_of_month', 'month', 'orders_ma_7']].values
        y_orders = daily_data['orders'].values
        
        X_orders_poly = poly_features.fit_transform(X_orders)
        model_orders = LinearRegression()
        model_orders.fit(X_orders_poly, y_orders)
        
        # Создаем прогноз на будущее
        last_date = daily_data.index.max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead)
        
        future_predictions = []
        last_revenue_ma = daily_data['revenue_ma_7'].iloc[-1]
        last_orders_ma = daily_data['orders_ma_7'].iloc[-1]
        
        for date in future_dates:
            features = [
                date.dayofweek,
                date.day,
                date.month,
                last_revenue_ma  # Используем последнее скользящее среднее
            ]
            
            features_poly = poly_features.transform([features])
            pred_revenue = model_revenue.predict(features_poly)[0]
            
            features_orders = [date.dayofweek, date.day, date.month, last_orders_ma]
            features_orders_poly = poly_features.transform([features_orders])
            pred_orders = model_orders.predict(features_orders_poly)[0]
            
            future_predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_revenue': max(0, pred_revenue),
                'predicted_orders': max(0, int(pred_orders)),
                'confidence': 'high' if len(daily_data) > 30 else 'medium'
            })
            
            # Обновляем скользящие средние
            last_revenue_ma = (last_revenue_ma * 6 + pred_revenue) / 7
            last_orders_ma = (last_orders_ma * 6 + pred_orders) / 7
        
        return {
            'predictions': future_predictions,
            'model_accuracy': {
                'revenue_r2': model_revenue.score(X_revenue_poly, y_revenue),
                'orders_r2': model_orders.score(X_orders_poly, y_orders)
            },
            'total_predicted_revenue': sum([p['predicted_revenue'] for p in future_predictions]),
            'total_predicted_orders': sum([p['predicted_orders'] for p in future_predictions])
        }
    
    def get_delivery_comparison(self, user_id, start_date=None, end_date=None):
        """Сравнительный анализ методов доставки"""
        conn = sqlite3.connect(self.db_path)
        
        date_filter = ""
        params = [user_id]
        
        if start_date and end_date:
            date_filter = "AND DATE(o.created_at) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query = f'''
            SELECT 
                o.delivery_type,
                COUNT(DISTINCT o.id) as orders_count,
                SUM(oi.total_cost) as total_revenue,
                SUM(oi.cost_price) as total_cost_price,
                SUM(oi.delivery_cost) as total_delivery_cost,
                SUM(oi.weight) as total_weight,
                AVG(oi.delivery_cost) as avg_delivery_cost,
                7.0 as avg_delivery_days
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ? {date_filter}
            GROUP BY o.delivery_type
        '''
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return None
        
        # Расчеты для сравнения
        df['profit'] = df['total_revenue'] - df['total_cost_price'] - df['total_delivery_cost']
        df['profit_margin'] = ((df['profit'] / df['total_revenue']) * 100).round(2)
        df['delivery_cost_per_kg'] = (df['total_delivery_cost'] / df['total_weight']).round(2)
        df['revenue_per_order'] = (df['total_revenue'] / df['orders_count']).round(2)
        df['efficiency_score'] = (df['profit'] / (df['avg_delivery_days'] * df['total_delivery_cost'])).round(2)
        
        # Добавляем рекомендации
        if len(df) == 2:  # Если есть оба типа доставки
            airplane_data = df[df['delivery_type'] == 'airplane'].iloc[0] if len(df[df['delivery_type'] == 'airplane']) > 0 else None
            truck_data = df[df['delivery_type'] == 'truck'].iloc[0] if len(df[df['delivery_type'] == 'truck']) > 0 else None
            
            recommendations = []
            
            if airplane_data is not None and truck_data is not None:
                if airplane_data['profit_margin'] > truck_data['profit_margin']:
                    recommendations.append("Самолет более рентабелен по марже прибыли")
                else:
                    recommendations.append("Автомобиль более рентабелен по марже прибыли")
                
                if airplane_data['avg_delivery_days'] < truck_data['avg_delivery_days']:
                    recommendations.append("Самолет быстрее в доставке")
                else:
                    recommendations.append("Автомобиль быстрее в доставке")
                
                if airplane_data['delivery_cost_per_kg'] < truck_data['delivery_cost_per_kg']:
                    recommendations.append("Самолет дешевле за килограмм")
                else:
                    recommendations.append("Автомобиль дешевле за килограмм")
            
            df = df.copy()
            # Создаем новую строку с рекомендациями
            new_row = pd.DataFrame([{
                'delivery_type': 'recommendations',
                'orders_count': 0,
                'total_revenue': 0,
                'total_cost_price': 0,
                'total_delivery_cost': 0,
                'total_weight': 0,
                'avg_delivery_cost': 0,
                'avg_delivery_days': 0,
                'profit': 0,
                'profit_margin': 0,
                'delivery_cost_per_kg': 0,
                'revenue_per_order': 0,
                'efficiency_score': 0,
                'recommendations': recommendations
            }])
            df = pd.concat([df, new_row], ignore_index=True)
        
        return df
    
    def get_ai_insights(self, user_id, period_days=30):
        """AI-анализ и умные инсайты"""
        insights = {
            'performance': [],
            'opportunities': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Получаем данные за период
        conn = sqlite3.connect(self.db_path)
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        
        # Анализ трендов
        sales_trends = self.get_sales_trends(user_id, days=period_days)
        if sales_trends is not None and len(sales_trends) > 7:
            # Анализ роста
            recent_revenue = sales_trends.tail(7)['revenue'].mean()
            previous_revenue = sales_trends.head(7)['revenue'].mean()
            growth_rate = ((recent_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            if growth_rate > 10:
                insights['performance'].append(f"📈 Отличный рост продаж: +{growth_rate:.1f}% за период")
            elif growth_rate > 0:
                insights['performance'].append(f"📊 Умеренный рост продаж: +{growth_rate:.1f}%")
            else:
                insights['warnings'].append(f"📉 Снижение продаж: {growth_rate:.1f}%")
                insights['recommendations'].append("Рекомендуется пересмотреть маркетинговую стратегию")
        
        # Анализ доставки
        delivery_comparison = self.get_delivery_comparison(user_id, start_date, end_date)
        if delivery_comparison is not None and len(delivery_comparison) > 0:
            best_margin = delivery_comparison.loc[delivery_comparison['profit_margin'].idxmax()]
            delivery_name = "Самолет" if best_margin['delivery_type'] == 'airplane' else "Автомобиль"
            
            insights['opportunities'].append(f"🚚 Лучшая рентабельность у доставки: {delivery_name} ({best_margin['profit_margin']:.1f}%)")
            
            # Анализ эффективности доставки
            if len(delivery_comparison) > 1:
                efficiency_diff = delivery_comparison['efficiency_score'].max() - delivery_comparison['efficiency_score'].min()
                if efficiency_diff > 0.1:
                    best_delivery = delivery_comparison.loc[delivery_comparison['efficiency_score'].idxmax(), 'delivery_type']
                    insights['recommendations'].append(f"Используйте больше доставку {best_delivery} для повышения эффективности")
        
        # Анализ товаров
        product_analytics = self.get_product_analytics(user_id)
        if product_analytics is not None:
            # Топ товар
            top_product = product_analytics.iloc[0]
            insights['performance'].append(f"🏆 Топ товар: {top_product['product_name']} (${top_product['total_revenue']:.2f} выручки)")
            
            # Товары с низкой маржой
            low_margin_products = product_analytics[product_analytics['profit_margin'] < 10]
            if len(low_margin_products) > 0:
                insights['warnings'].append(f"⚠️ {len(low_margin_products)} товаров с маржой < 10%")
                insights['recommendations'].append("Пересмотрите ценообразование для товаров с низкой маржой")
            
            # Возможности роста
            high_frequency = product_analytics[product_analytics['order_frequency'] > product_analytics['order_frequency'].median()]
            if len(high_frequency) > 0:
                insights['opportunities'].append(f"📈 {len(high_frequency)} товаров показывают высокий спрос")
        
        # Предсказания
        predictions = self.get_advanced_predictions(user_id, days_ahead=7)
        if predictions:
            next_week_revenue = predictions['total_predicted_revenue']
            current_week_avg = sales_trends.tail(7)['revenue'].sum() if sales_trends is not None else 0
            
            if next_week_revenue > current_week_avg * 1.1:
                insights['opportunities'].append(f"🔮 Прогноз роста на следующую неделю: ${next_week_revenue:.2f}")
            elif next_week_revenue < current_week_avg * 0.9:
                insights['warnings'].append(f"🔮 Прогноз снижения на следующую неделю: ${next_week_revenue:.2f}")
                insights['recommendations'].append("Подготовьте маркетинговые активности для поддержки продаж")
        
        conn.close()
        return insights

# Функция для создания единственного экземпляра
_analytics_manager = None

def get_analytics_manager():
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AdvancedAnalytics()
    return _analytics_manager

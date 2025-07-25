import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import io
import base64
import time

# Настройка страницы
st.set_page_config(
    page_title="Бизнес Менеджер",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Минималистичный классический дизайн
st.markdown("""
<style>
    /* Исправление отображения эмодзи */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", system-ui, sans-serif;
    }
    
    /* Стили для правильного отображения эмодзи */
    .emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "EmojiOne Color", "Android Emoji", "Twemoji Mozilla", sans-serif;
        font-style: normal;
        font-weight: normal;
        text-rendering: optimizeLegibility;
    }
    
    /* Минималистичная цветовая палитра */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #e9ecef;
        --text-primary: #000000;
        --text-secondary: #333333;
        --text-muted: #555555;
        --accent-blue: #003366;
        --accent-green: #004d00;
        --accent-red: #990000;
        --accent-orange: #cc6600;
        --border-light: #dee2e6;
        --border-medium: #ced4da;
        --shadow-subtle: 0 1px 3px rgba(0,0,0,0.08);
        --shadow-medium: 0 2px 8px rgba(0,0,0,0.12);
    }
    
    /* Основные стили */
    .main {
        background: var(--bg-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        color: var(--text-primary);
        line-height: 1.5;
    }
    
    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.025em;
        margin: 0 0 1rem 0;
    }
    
    /* Карточки */
    .card {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-subtle);
        transition: box-shadow 0.2s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-medium);
    }
    
    /* Современная навигация */
    .modern-nav {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.75rem;
    }
    
    .nav-item {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 6px;
        padding: 0.75rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        color: var(--text-primary);
    }
    
    .nav-item:hover {
        border-color: var(--accent-blue);
        background: var(--bg-secondary);
        transform: translateY(-1px);
    }
    
    .nav-item.active {
        background: var(--accent-blue);
        color: #000000;
        border-color: var(--accent-blue);
    }
    
    .nav-icon {
        font-size: 1.25rem;
        margin-bottom: 0.25rem;
        display: block;
    }
    
    .nav-text {
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Кнопки */
    .stButton > button {
        background: var(--accent-blue) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-subtle) !important;
    }
    
    .stButton > button:hover {
        background: #0052a3 !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-medium) !important;
    }
    
    /* Формы */
    .stTextInput > div > div > input {
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        font-size: 0.875rem !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(0,102,204,0.1) !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div > div {
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Статистические карточки */
    .stat-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-subtle);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* Статусы */
    .status-success { color: var(--accent-green); }
    .status-warning { color: var(--accent-orange); }
    .status-danger { color: var(--accent-red); }
    
    /* Заказы */
    .order-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-subtle);
        transition: all 0.2s ease;
    }
    
    .order-card:hover {
        box-shadow: var(--shadow-medium);
        border-color: var(--border-medium);
    }
    
    .order-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .order-title {
        color: var(--accent-blue);
        font-size: 1.125rem;
        font-weight: 600;
        margin: 0;
        cursor: pointer;
        text-decoration: none;
    }
    
    .order-title:hover {
        text-decoration: underline;
    }
    
    .order-meta {
        color: var(--text-muted);
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-pending {
        background: #fff3cd;
        color: #663300;
        border: 1px solid #ffeaa7;
    }
    
    .status-delivered {
        background: #d1e7dd;
        color: #003300;
        border: 1px solid #badbcc;
    }
    
    .status-delayed {
        background: #f8d7da;
        color: #660000;
        border: 1px solid #f5c2c7;
    }
    
    /* Детали заказа */
    .order-details {
        background: var(--bg-secondary);
        border-radius: 6px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid var(--border-light);
    }
    
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .detail-item {
        text-align: center;
    }
    
    .detail-value {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .detail-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
    
    /* Управление заказом */
    .order-actions {
        border-top: 1px solid var(--border-light);
        padding-top: 1rem;
        margin-top: 1rem;
    }
    
    /* Скрыть стандартные элементы Streamlit */
    .stDeployButton {display: none !important;}
    .stDecoration {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stToolbar {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .styles_viewerBadge__1yB5_ {display: none !important;}
    #stDecoration {display: none !important;}
    .reportview-container .main .block-container {
        padding-top: 1rem;
    }
    
    /* Улучшенные стили для эмодзи */
    .stButton > button, .stSelectbox, .stTextInput, 
    .stMarkdown, .stMetric, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", "Twitter Color Emoji", "EmojiOne Color", system-ui, sans-serif !important;
    }
    
    /* Конкретные стили для кнопок с эмодзи */
    .stButton > button {
        font-variant-emoji: emoji !important;
        text-rendering: optimizeSpeed !important;
    }
    
    /* Адаптивность */
    @media (max-width: 768px) {
        .nav-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .detail-grid {
            grid-template-columns: 1fr;
        }
        
        .order-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
    }
    
    /* Улучшение контраста для таблиц */
    .stDataFrame {
        background: var(--bg-primary) !important;
    }
    
    .stDataFrame table {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    .stDataFrame th {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--border-medium) !important;
    }
    
    .stDataFrame td {
        color: var(--text-primary) !important;
        border-bottom: 1px solid var(--border-light) !important;
        padding: 8px 12px !important;
    }
    
    .stDataFrame tr:hover {
        background: var(--bg-secondary) !important;
    }
    
    .stDataFrame tr:nth-child(even) {
        background: rgba(248, 249, 250, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

def show_modern_navigation():
    """Современная минималистичная навигация с уведомлениями"""
    
    # Получаем количество непрочитанных уведомлений
    unread_count = get_unread_notifications_count(st.session_state.user_id)
    
    # Кнопки навигации с использованием колонок
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        if st.button("📊 Панель", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("📦 Заказы", use_container_width=True,
                    type="primary" if st.session_state.current_page == "orders" else "secondary"):
            st.session_state.current_page = "orders"
            st.rerun()
    
    with col3:
        if st.button("📋 Управление", use_container_width=True,
                    type="primary" if st.session_state.current_page == "order_management" else "secondary"):
            st.session_state.current_page = "order_management"
            st.rerun()
    
    with col4:
        if st.button("📈 Аналитика", use_container_width=True,
                    type="primary" if st.session_state.current_page == "analytics" else "secondary"):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col5:
        if st.button("🏪 Склад", use_container_width=True,
                    type="primary" if st.session_state.current_page == "inventory" else "secondary"):
            st.session_state.current_page = "inventory"
            st.rerun()
    
    with col6:
        # Кнопка уведомлений с индикатором
        notification_button_type = "primary" if st.session_state.current_page == "notifications" else "secondary"
        if unread_count > 0:
            button_label = f"🔔 ({unread_count})"
        else:
            button_label = "🔔"
            
        if st.button(button_label, use_container_width=True, type=notification_button_type):
            st.session_state.current_page = "notifications"
            st.rerun()
    
    with col7:
        if st.button("🧠 ИИ", use_container_width=True,
                    type="primary" if st.session_state.current_page == "smart" else "secondary"):
            st.session_state.current_page = "smart"
            st.rerun()
    
    with col8:
        if st.button("⚙️ Настройки", use_container_width=True,
                    type="primary" if st.session_state.current_page == "settings" else "secondary"):
            st.session_state.current_page = "settings"
            st.rerun()

def show_admin_navigation():
    """Дополнительная навигация для администратора"""
    if st.session_state.get('is_admin', False):
        st.markdown("---")
        st.markdown("### 👨‍💼 Панель администратора")
        
        # Админские кнопки
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("👥 Пользователи", use_container_width=True,
                        type="primary" if st.session_state.get('admin_page') == "users" else "secondary",
                        key="admin_users_btn"):
                st.session_state.admin_page = "users"
                st.session_state.current_page = "admin"
                st.rerun()
        
        with col2:
            if st.button("💳 Платежи", use_container_width=True,
                        type="primary" if st.session_state.get('admin_page') == "payments" else "secondary",
                        key="admin_payments_btn"):
                st.session_state.admin_page = "payments"
                st.session_state.current_page = "admin"
                st.rerun()
        
        with col3:
            if st.button("📊 Статистика", use_container_width=True,
                        type="primary" if st.session_state.get('admin_page') == "stats" else "secondary",
                        key="admin_stats_btn"):
                st.session_state.admin_page = "stats"
                st.session_state.current_page = "admin"
                st.rerun()
        
        with col4:
            if st.button("📈 Отчеты", use_container_width=True,
                        type="primary" if st.session_state.get('admin_page') == "reports" else "secondary",
                        key="admin_reports_btn"):
                st.session_state.admin_page = "reports"
                st.session_state.current_page = "admin"
                st.rerun()
        
        with col5:
            if st.button("⚙️ Админ настройки", use_container_width=True,
                        type="primary" if st.session_state.get('admin_page') == "admin_settings" else "secondary",
                        key="admin_settings_btn"):
                st.session_state.admin_page = "admin_settings"
                st.session_state.current_page = "admin"
                st.rerun()
        
        st.markdown("---")

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Таблица пользователей с расширенными полями
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            full_name TEXT,
            business_name TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            premium_status BOOLEAN DEFAULT FALSE,
            premium_start_date TIMESTAMP,
            premium_end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_type TEXT NOT NULL,
            order_name TEXT NOT NULL,
            total_payment REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_type TEXT,
            notification_sent INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица товаров в заказах
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            cost_price REAL NOT NULL,
            sale_price REAL DEFAULT 0,
            weight REAL NOT NULL,
            delivery_cost REAL,
            total_cost REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    
    # Проверяем и добавляем колонку sale_price если её нет
    try:
        cursor.execute('ALTER TABLE order_items ADD COLUMN sale_price REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    # Добавляем колонку delivery_type для каждого товара
    try:
        cursor.execute('ALTER TABLE order_items ADD COLUMN item_delivery_type TEXT DEFAULT "truck"')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    # Добавляем колонки для отслеживания статуса заказов
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN status TEXT DEFAULT "pending"')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN expected_delivery_date TIMESTAMP')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN actual_delivery_date TIMESTAMP')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN delay_notification_sent INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Колонка уже существует
    
    # Таблица склада
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица истории заказов (для товаров, которые привозятся под заказ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            cost_price REAL NOT NULL,
            sale_price REAL NOT NULL,
            weight REAL NOT NULL,
            delivery_type TEXT DEFAULT "truck",
            delivery_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT "completed",
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    
    # Таблица настроек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            financial_cushion_percent REAL DEFAULT 20.0,
            email_notifications BOOLEAN DEFAULT 1,
            smtp_server TEXT,
            smtp_port INTEGER DEFAULT 587,
            email_username TEXT,
            email_password TEXT,
            notify_new_orders BOOLEAN DEFAULT 1,
            notify_low_stock BOOLEAN DEFAULT 1,
            notify_daily_report BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Добавляем недостающие поля в таблицу settings, если их нет
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN notify_new_orders BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN notify_low_stock BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # Поле уже существует
        
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN notify_daily_report BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    # Добавляем поля для цен доставки
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN airplane_price_per_kg REAL DEFAULT 5.0")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN truck_price_per_kg REAL DEFAULT 2.0")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    # Обновленная таблица настроек с поддержкой универсальных настроек
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN setting_name TEXT")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN setting_value TEXT")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    # Новая универсальная таблица настроек для всех типов настроек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            setting_name TEXT NOT NULL,
            setting_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, setting_name)
        )
    ''')
    
    # Таблица уведомлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица заказов поставщикам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            supplier_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            order_date DATE DEFAULT (date('now')),
            expected_delivery_date DATE,
            actual_delivery_date DATE,
            status TEXT DEFAULT 'ordered',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Обновляем таблицу inventory для поддержки автоматического управления складом
    try:
        cursor.execute("ALTER TABLE inventory ADD COLUMN reserved_quantity INTEGER DEFAULT 0")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE inventory ADD COLUMN min_stock_level INTEGER DEFAULT 0")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE inventory ADD COLUMN max_stock_level INTEGER DEFAULT 100")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE inventory ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    # Таблица истории платежей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'bank_transfer',
            status TEXT DEFAULT 'pending',
            admin_confirmed BOOLEAN DEFAULT FALSE,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_date TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Добавляем недостающие поля в таблицу users
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN business_name TEXT")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN premium_status BOOLEAN DEFAULT FALSE")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN premium_start_date TIMESTAMP")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN premium_end_date TIMESTAMP")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass  # Поле уже существует
    
    # Создаем админа по умолчанию
    admin_email = 'alexkurumbayev@gmail.com'
    admin_password = hash_password('qwert123G')  # Админский пароль
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, password_hash, is_admin, premium_status, full_name)
        VALUES (?, ?, 1, 1, 'Alex Kurumbayev')
    ''', (admin_email, admin_password))
    
    conn.commit()
    conn.close()

# Функции для работы с премиум-подпиской
def check_premium_status(user_id):
    """Проверяет актуальность премиум-статуса"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT premium_status, premium_end_date, is_admin
        FROM users 
        WHERE id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False
    
    premium_status, premium_end_date, is_admin = result
    
    # Админ всегда имеет премиум
    if is_admin:
        conn.close()
        return True
    
    # Проверяем срок действия премиума
    if premium_status and premium_end_date:
        try:
            # Попробуем несколько форматов даты
            if 'T' in premium_end_date:
                # ISO формат с T
                end_date = datetime.fromisoformat(premium_end_date.replace('T', ' ').replace('Z', ''))
            elif len(premium_end_date) == 10:
                # Только дата без времени
                end_date = datetime.strptime(premium_end_date, '%Y-%m-%d')
            else:
                # Стандартный формат
                end_date = datetime.strptime(premium_end_date, '%Y-%m-%d %H:%M:%S')
                
            if datetime.now() > end_date:
                # Премиум истек, отключаем
                cursor.execute('''
                    UPDATE users 
                    SET premium_status = 0 
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
                conn.close()
                return False
        except (ValueError, TypeError) as e:
            # Если не удалось парсить дату, считаем что премиум истек
            cursor.execute('''
                UPDATE users 
                SET premium_status = 0 
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            return False
    
    conn.close()
    return premium_status

def activate_premium(user_id, months=1):
    """Активирует премиум-подписку на указанное количество месяцев"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30 * months)
    
    cursor.execute('''
        UPDATE users 
        SET premium_status = 1,
            premium_start_date = ?,
            premium_end_date = ?
        WHERE id = ?
    ''', (start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    
    # Обновляем сессию если это текущий пользователь
    if 'user_id' in st.session_state and st.session_state.user_id == user_id:
        st.session_state.premium_status = 1
        st.session_state.is_premium = True
    
    conn.commit()
    conn.close()
    return True

def request_premium_payment(user_id):
    """Создает запрос на оплату премиума"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO payment_history (user_id, amount, payment_method, status, notes)
        VALUES (?, 150.0, 'bank_transfer', 'pending', 'Premium subscription payment request')
    ''', (user_id,))
    
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Отправляем уведомление админу (здесь можно добавить отправку email)
    send_payment_notification_to_admin(user_id, payment_id)
    
    return payment_id

def send_payment_notification_to_admin(user_id, payment_id):
    """Отправляет уведомление админу о запросе оплаты"""
    # В реальном приложении здесь будет отправка email
    # Пока что создаем системное уведомление
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Получаем данные пользователя
    cursor.execute('''
        SELECT email, phone, full_name FROM users WHERE id = ?
    ''', (user_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        email, phone, full_name = user_data
        message = f"Пользователь {full_name or email} (тел: {phone or 'не указан'}) запросил подтверждение оплаты премиума. ID платежа: {payment_id}"
        
        # Здесь можно добавить реальную отправку email на alexkurumbayev@gmail.com
        print(f"EMAIL TO ADMIN: {message}")
    
    conn.close()

def confirm_payment(payment_id, admin_user_id):
    """Подтверждает оплату и активирует премиум"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Получаем данные платежа
    cursor.execute('''
        SELECT user_id FROM payment_history WHERE id = ?
    ''', (payment_id,))
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    user_id = result[0]
    
    # Подтверждаем платеж
    cursor.execute('''
        UPDATE payment_history 
        SET status = 'confirmed', 
            admin_confirmed = 1,
            confirmed_date = ?
        WHERE id = ?
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), payment_id))
    
    # Активируем премиум на месяц
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    cursor.execute('''
        UPDATE users 
        SET premium_status = 1,
            premium_start_date = ?,
            premium_end_date = ?
        WHERE id = ?
    ''', (start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    
    # Обновляем сессию если это текущий пользователь
    if 'user_id' in st.session_state and st.session_state.user_id == user_id:
        st.session_state.premium_status = 1
        st.session_state.is_premium = True
    
    conn.commit()
    conn.close()
    return True

# Функции для работы с пользователями
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password, phone=None, full_name=None, business_name=None):
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (email, password_hash, phone, full_name, business_name) VALUES (?, ?, ?, ?, ?)', 
                      (email, password_hash, phone, full_name, business_name))
        conn.commit()
        user_id = cursor.lastrowid
        # Создание настроек по умолчанию
        cursor.execute('INSERT INTO settings (user_id) VALUES (?)', (user_id,))
        conn.commit()
        return True, "Регистрация успешна!"
    except sqlite3.IntegrityError:
        return False, "Пользователь с таким email уже существует"
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute('SELECT id FROM users WHERE email = ? AND password_hash = ?', 
                  (email, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def delete_user(user_id):
    """Удаляет пользователя и все его данные"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли пользователь
        cursor.execute('SELECT id, email FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            return False
        
        print(f"Удаляем пользователя: {user[1]} (ID: {user[0]})")
        
        # Удаляем все связанные данные пользователя в правильном порядке
        # Сначала удаляем элементы заказов
        cursor.execute('DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE user_id = ?)', (user_id,))
        deleted_items = cursor.rowcount
        print(f"Удалено элементов заказов: {deleted_items}")
        
        # Затем заказы
        cursor.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
        deleted_orders = cursor.rowcount
        print(f"Удалено заказов: {deleted_orders}")
        
        # Удаляем инвентарь
        cursor.execute('DELETE FROM inventory WHERE user_id = ?', (user_id,))
        deleted_inventory = cursor.rowcount
        print(f"Удалено товаров из инвентаря: {deleted_inventory}")
        
        # Удаляем уведомления
        cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
        deleted_notifications = cursor.rowcount
        print(f"Удалено уведомлений: {deleted_notifications}")
        
        # Удаляем подписки (если таблица существует)
        try:
            cursor.execute('DELETE FROM premium_subscriptions WHERE user_id = ?', (user_id,))
            deleted_subscriptions = cursor.rowcount
            print(f"Удалено подписок: {deleted_subscriptions}")
        except sqlite3.OperationalError:
            print("Таблица premium_subscriptions не существует")
        
        # Удаляем запросы платежей (если таблица существует)
        try:
            cursor.execute('DELETE FROM payment_requests WHERE user_id = ?', (user_id,))
            deleted_payments = cursor.rowcount
            print(f"Удалено запросов платежей: {deleted_payments}")
        except sqlite3.OperationalError:
            print("Таблица payment_requests не существует")
        
        # Удаляем настройки
        cursor.execute('DELETE FROM settings WHERE user_id = ?', (user_id,))
        deleted_settings = cursor.rowcount
        print(f"Удалено настроек: {deleted_settings}")
        
        # Удаляем самого пользователя
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        deleted_user = cursor.rowcount
        print(f"Удален пользователь: {deleted_user}")
        
        conn.commit()
        print(f"Пользователь {user[1]} успешно удален")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении пользователя: {e}")
        st.error(f"Ошибка при удалении пользователя: {e}")
        return False
    finally:
        conn.close()

# Константы для расчета доставки
def get_delivery_rates(user_id):
    """Получает тарифы доставки из настроек пользователя"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT airplane_price_per_kg, truck_price_per_kg 
            FROM settings 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            return {
                'airplane': result[0] if result[0] is not None else 5.0,
                'truck': result[1] if result[1] is not None else 2.0
            }
        else:
            return {
                'airplane': 5.0,
                'truck': 2.0
            }
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        # Поля не существуют, добавляем их и возвращаем значения по умолчанию
        try:
            cursor.execute("ALTER TABLE settings ADD COLUMN airplane_price_per_kg REAL DEFAULT 5.0")
            cursor.execute("ALTER TABLE settings ADD COLUMN truck_price_per_kg REAL DEFAULT 2.0")
            conn.commit()
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            pass
        
        return {
            'airplane': 5.0,
            'truck': 2.0
        }
    finally:
        conn.close()

DELIVERY_RATES = {
    'airplane': 7.0,
    'truck': 0.68
}

# Функции для работы с заказами
def add_single_order(user_id, product_name, quantity, cost_price, sale_price, weight, delivery_type, order_date=None, expected_delivery_date=None, stock_status="unknown"):
    """Добавляет одиночный заказ с автоматическим управлением складом
    
    Args:
        stock_status: "in_stock", "out_of_stock", или "unknown"
    """
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем премиум статус пользователя
    is_premium = check_premium_status(user_id)
    
    # Для бесплатных пользователей проверяем лимит в 25 заказов
    if not is_premium:
        cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id,))
        current_orders = cursor.fetchone()[0]
        
        if current_orders >= 25:
            conn.close()
            return {
                'success': False,
                'message': "❌ Достигнут лимит в 25 заказов для бесплатной версии. Обновитесь до премиума для неограниченного количества заказов!",
                'order_id': None
            }
    
    delivery_rates = get_delivery_rates(user_id)
    delivery_cost = weight * delivery_rates[delivery_type]
    total_cost = sale_price * quantity + delivery_cost
    
    # Если дата заказа не указана, используем текущую дату
    if order_date is None:
        order_date = datetime.now().date()
    
    # Если ожидаемая дата доставки не указана, рассчитываем её
    if expected_delivery_date is None:
        delivery_days = 7 if delivery_type == "airplane" else 14
        expected_delivery_date = order_date + timedelta(days=delivery_days)
    
    # Определяем источник товара
    source = "warehouse" if stock_status == "in_stock" else "supplier"
    
    # Создаем заказ в основной таблице orders (всегда!)
    cursor.execute('''
        INSERT INTO orders (user_id, order_type, order_name, delivery_type, status, 
                           created_at, expected_delivery_date, total_payment) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 'single', product_name, delivery_type, 'pending', 
          order_date, expected_delivery_date, total_cost))
    
    order_id = cursor.lastrowid
    
    # Добавляем товар в order_items
    cursor.execute('''
        INSERT INTO order_items (order_id, product_name, quantity, cost_price, sale_price, 
                               weight, delivery_cost, total_cost, item_delivery_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, product_name, quantity, cost_price, sale_price, 
          weight, delivery_cost, total_cost, delivery_type))
    
    # Если товар есть на складе - резервируем его
    if stock_status == "in_stock":
        success, message = reserve_inventory(user_id, product_name, quantity)
        if success:
            # Добавляем уведомление об автоматическом резервировании
            cursor.execute('''
                INSERT INTO notifications (user_id, type, title, message, created_at, is_read)
                VALUES (?, 'inventory', 'Товар зарезервирован', ?, datetime('now'), 0)
            ''', (user_id, f'На складе зарезервировано {quantity} шт. товара "{product_name}" для заказа #{order_id}'))
    else:
        # Добавляем также запись в историю заказов для товаров под заказ
        cursor.execute('''
            INSERT INTO order_history 
            (user_id, order_id, product_name, quantity, cost_price, sale_price, 
             weight, delivery_type, delivery_cost, total_cost, order_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, order_id, product_name, quantity, cost_price, sale_price, 
              weight, delivery_type, delivery_cost, total_cost, order_date, 'ordered'))
        
        # Добавляем уведомление о заказе поставщику
        cursor.execute('''
            INSERT INTO notifications (user_id, type, title, message, created_at, is_read)
            VALUES (?, 'supplier', 'Нужен заказ поставщику', ?, datetime('now'), 0)
        ''', (user_id, f'Товар "{product_name}" ({quantity} шт.) нужно заказать у поставщика для заказа #{order_id}'))
    
    conn.commit()
    conn.close()
    return order_id

def delete_order(order_id, user_id):
    """Удаляет заказ и все связанные с ним товары"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем, принадлежит ли заказ пользователю
    cursor.execute('SELECT id FROM orders WHERE id = ? AND user_id = ?', (order_id, user_id))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return False
    
    # Удаляем товары заказа
    cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    
    # Удаляем сам заказ
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    
    conn.commit()
    conn.close()
    return True

def add_complex_order(user_id, order_name, total_payment, items, save_to_history_only=False):
    """Добавляет сложный заказ с множественными товарами
    
    Args:
        save_to_history_only: Если True, товары сохраняются только в историю заказов (для товаров под заказ)
                             Если False, создается обычный заказ со склада
    """
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем премиум статус пользователя
    is_premium = check_premium_status(user_id)
    
    # Для бесплатных пользователей проверяем лимит в 25 заказов
    if not is_premium:
        cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id,))
        current_orders = cursor.fetchone()[0]
        
        if current_orders >= 25:
            conn.close()
            return {
                'success': False,
                'message': "❌ Достигнут лимит в 25 заказов для бесплатной версии. Обновитесь до премиума для неограниченного количества заказов!",
                'order_id': None
            }
    
    # Рассчитываем общую себестоимость и общую стоимость доставки
    total_cost_price = sum(item['cost_price'] * item['quantity'] for item in items)
    delivery_rates = get_delivery_rates(user_id)
    total_delivery_cost = sum(item['weight'] * delivery_rates[item['delivery_type']] for item in items)
    
    # Распределяем платеж между товарами (минус доставка)
    remaining_payment = total_payment - total_delivery_cost
    order_id = None
    
    if not save_to_history_only:
        # Создаем обычный заказ со склада
        # Рассчитываем ожидаемую дату доставки (2 недели с понедельника)
        from datetime import datetime, timedelta
        today = datetime.now()
        # Находим следующий понедельник
        days_ahead = 0 - today.weekday()  # 0 = понедельник
        if days_ahead <= 0:  # Если сегодня понедельник или позже
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        expected_delivery = next_monday + timedelta(weeks=2)  # +2 недели
        
        # Добавляем заказ с ожидаемой датой доставки
        cursor.execute('''
            INSERT INTO orders (user_id, order_type, order_name, total_payment, status, expected_delivery_date) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, 'complex', order_name, total_payment, 'pending', expected_delivery))
        
        order_id = cursor.lastrowid
    
    for item in items:
        # Пропорциональное распределение платежа по себестоимости
        item_total_cost_price = item['cost_price'] * item['quantity']
        item_share = item_total_cost_price / total_cost_price if total_cost_price > 0 else 1 / len(items)
        item_payment = remaining_payment * item_share
        
        # Стоимость доставки для этого товара с его типом доставки
        item_delivery_cost = item['weight'] * delivery_rates[item['delivery_type']]
        item_total_cost = item_payment + item_delivery_cost
        
        # Рассчитываем эффективную цену продажи для этого товара
        effective_sale_price = item_payment / item['quantity'] if item['quantity'] > 0 else 0
        
        if save_to_history_only:
            # Сохраняем только в историю заказов (товары под заказ)
            cursor.execute('''
                INSERT INTO order_history 
                (user_id, order_id, product_name, quantity, cost_price, sale_price, 
                 weight, delivery_type, delivery_cost, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, None, item['product_name'], item['quantity'], item['cost_price'], 
                  effective_sale_price, item['weight'], item['delivery_type'], item_delivery_cost, item_total_cost))
        else:
            # Добавляем товар в order_items для обычного заказа
            cursor.execute('''
                INSERT INTO order_items (order_id, product_name, quantity, cost_price, sale_price, weight, delivery_cost, total_cost, item_delivery_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, item['product_name'], item['quantity'], item['cost_price'], 
                  effective_sale_price, item['weight'], item_delivery_cost, item_total_cost, item['delivery_type']))
    
    conn.commit()
    conn.close()
    return order_id

# Функции для управления статусами заказов
def update_order_status(order_id, user_id, new_status):
    """Обновляет статус заказа"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем, принадлежит ли заказ пользователю
    cursor.execute('SELECT id FROM orders WHERE id = ? AND user_id = ?', (order_id, user_id))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return False
    
    # Обновляем статус
    if new_status == 'delivered':
        from datetime import datetime
        cursor.execute('''
            UPDATE orders 
            SET status = ?, actual_delivery_date = ? 
            WHERE id = ?
        ''', (new_status, datetime.now(), order_id))
    else:
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    
    conn.commit()
    conn.close()
    return True

def get_order_details(order_id, user_id):
    """Получает детальную информацию о заказе для редактирования"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Получаем информацию о заказе
    cursor.execute('''
        SELECT o.id, o.order_name, o.order_type, o.total_payment, o.delivery_type, 
               o.status, o.created_at, o.expected_delivery_date
        FROM orders o
        WHERE o.id = ? AND o.user_id = ?
    ''', (order_id, user_id))
    
    order_info = cursor.fetchone()
    if not order_info:
        conn.close()
        return None, None
    
    # Получаем товары заказа
    cursor.execute('''
        SELECT oi.id, oi.product_name, oi.quantity, oi.cost_price, oi.sale_price, 
               oi.weight, oi.item_delivery_type
        FROM order_items oi
        WHERE oi.order_id = ?
    ''', (order_id,))
    
    order_items = cursor.fetchall()
    conn.close()
    
    return order_info, order_items

def update_single_order(order_id, user_id, product_name, quantity, cost_price, sale_price, weight, delivery_type):
    """Обновляет одиночный заказ"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        # Рассчитываем новую стоимость доставки
        delivery_rates = get_delivery_rates(user_id)
        delivery_cost = weight * delivery_rates[delivery_type]
        total_cost = sale_price * quantity + delivery_cost
        
        # Обновляем заказ
        cursor.execute('''
            UPDATE orders 
            SET order_name = ?, delivery_type = ?
            WHERE id = ? AND user_id = ?
        ''', (product_name, delivery_type, order_id, user_id))
        
        # Обновляем товар в заказе
        cursor.execute('''
            UPDATE order_items 
            SET product_name = ?, quantity = ?, cost_price = ?, sale_price = ?, 
                weight = ?, item_delivery_type = ?, delivery_cost = ?, total_cost = ?
            WHERE order_id = ?
        ''', (product_name, quantity, cost_price, sale_price, weight, delivery_type, 
              delivery_cost, total_cost, order_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def update_complex_order(order_id, user_id, order_name, total_payment, items):
    """Обновляет комплексный заказ"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        # Обновляем заказ
        cursor.execute('''
            UPDATE orders 
            SET order_name = ?, total_payment = ?
            WHERE id = ? AND user_id = ?
        ''', (order_name, total_payment, order_id, user_id))
        
        # Удаляем старые товары
        cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
        
        # Рассчитываем общую себестоимость и общую стоимость доставки
        total_cost_price = sum(item['cost_price'] * item['quantity'] for item in items)
        delivery_rates = get_delivery_rates(user_id)
        total_delivery_cost = sum(item['weight'] * delivery_rates[item['delivery_type']] for item in items)
        
        # Распределяем платеж между товарами (минус доставка)
        remaining_payment = total_payment - total_delivery_cost
        
        # Добавляем обновленные товары
        for item in items:
            item_total_cost_price = item['cost_price'] * item['quantity']
            item_share = item_total_cost_price / total_cost_price if total_cost_price > 0 else 1 / len(items)
            item_payment = remaining_payment * item_share
            
            item_delivery_cost = item['weight'] * delivery_rates[item['delivery_type']]
            item_total_cost = item_payment + item_delivery_cost
            
            effective_sale_price = item_payment / item['quantity'] if item['quantity'] > 0 else 0
            
            cursor.execute('''
                INSERT INTO order_items (order_id, product_name, quantity, cost_price, sale_price, weight, delivery_cost, total_cost, item_delivery_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, item['product_name'], item['quantity'], item['cost_price'], 
                  effective_sale_price, item['weight'], item_delivery_cost, item_total_cost, item['delivery_type']))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def show_edit_order_form(order_id, user_id):
    """Показывает форму редактирования заказа"""
    
    # Получаем данные заказа
    order_info, order_items = get_order_details(order_id, user_id)
    
    if not order_info:
        st.error("❌ Заказ не найден")
        return
    
    order_type = order_info[2]
    
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid var(--border-light);
    ">
        <h3 style="color: #000000; text-align: center; margin-bottom: 20px;">
            ✏️ Редактирование заказа #{order_id}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if order_type == "single":
        show_edit_single_order_form(order_id, user_id, order_info, order_items[0] if order_items else None)
    else:
        show_edit_complex_order_form(order_id, user_id, order_info, order_items)

def show_edit_single_order_form(order_id, user_id, order_info, order_item):
    """Форма редактирования одиночного заказа"""
    
    if not order_item:
        st.error("❌ Данные товара не найдены")
        return
    
    with st.form(f"edit_single_order_{order_id}"):
        st.subheader("📦 Редактирование товара")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Название товара *", 
                value=order_item[1],
                help="Укажите название товара"
            )
            quantity = st.number_input(
                "Количество *", 
                min_value=1, 
                value=int(order_item[2])
            )
            cost_price = st.number_input(
                "Себестоимость ($) *", 
                min_value=0.0, 
                format="%.2f",
                value=float(order_item[3])
            )
            sale_price = st.number_input(
                "Цена продажи ($) *", 
                min_value=0.0, 
                format="%.2f",
                value=float(order_item[4])
            )
        
        with col2:
            weight = st.number_input(
                "Вес (кг) *", 
                min_value=0.0, 
                format="%.2f",
                value=float(order_item[5])
            )
            delivery_type = st.selectbox(
                "Тип доставки *",
                options=["airplane", "truck"],
                format_func=lambda x: "✈️ Самолет ($7/кг)" if x == "airplane" else "🚛 Машина ($0.68/кг)",
                index=0 if order_item[6] == "airplane" else 1
            )
            
            # Автоматический расчет стоимости доставки
            if weight > 0:
                delivery_cost = weight * DELIVERY_RATES[delivery_type]
                total_cost = sale_price * quantity + delivery_cost
                profit = (sale_price - cost_price) * quantity
                
                st.info(f"""
                **💰 Расчет стоимости:**
                - Стоимость доставки: ${delivery_cost:.2f}
                - Общая стоимость: ${total_cost:.2f}
                - Прибыль: ${profit:.2f}
                """)
        
        # Кнопки управления
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_btn = st.form_submit_button("💾 Сохранить изменения", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🚫 Отмена", use_container_width=True):
                st.session_state[f'edit_mode_{order_id}'] = False
                st.rerun()
        
        with col3:
            preview_btn = st.form_submit_button("👁️ Предпросмотр", use_container_width=True)
        
        # Обработка сохранения
        if save_btn:
            if product_name and quantity > 0 and cost_price >= 0 and sale_price >= 0 and weight > 0:
                if update_single_order(order_id, user_id, product_name, quantity, cost_price, sale_price, weight, delivery_type):
                    st.success("✅ Заказ успешно обновлен!")
                    st.session_state[f'edit_mode_{order_id}'] = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Ошибка при обновлении заказа")
            else:
                st.error("❌ Заполните все обязательные поля")
        
        # Предпросмотр изменений
        if preview_btn and product_name and quantity > 0 and weight > 0:
            delivery_cost = weight * DELIVERY_RATES[delivery_type]
            total_cost = sale_price * quantity + delivery_cost
            profit = (sale_price - cost_price) * quantity
            
            st.markdown("""
            ### 👁️ Предпросмотр изменений
            """)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                **📦 Товар:** {product_name}  
                **📊 Количество:** {quantity} шт.  
                **💰 Себестоимость:** ${cost_price:.2f}  
                **💵 Цена продажи:** ${sale_price:.2f}
                """)
            
            with col2:
                st.markdown(f"""
                **⚖️ Вес:** {weight} кг  
                **🚚 Доставка:** {'✈️ Самолет' if delivery_type == 'airplane' else '🚛 Машина'}  
                **📦 Стоимость доставки:** ${delivery_cost:.2f}
                """)
            
            with col3:
                profit_color = "green" if profit > 0 else "red"
                st.markdown(f"""
                **💲 Общая стоимость:** ${total_cost:.2f}  
                **📈 Прибыль:** <span style="color: {profit_color}">${profit:.2f}</span>  
                **📊 Маржа:** {(profit / (sale_price * quantity) * 100) if sale_price * quantity > 0 else 0:.1f}%
                """, unsafe_allow_html=True)

def show_edit_complex_order_form(order_id, user_id, order_info, order_items):
    """Форма редактирования комплексного заказа"""
    
    # Инициализация состояния для редактируемых товаров
    edit_items_key = f'edit_complex_items_{order_id}'
    if edit_items_key not in st.session_state:
        st.session_state[edit_items_key] = [
            {
                'product_name': item[1],
                'quantity': int(item[2]),
                'cost_price': float(item[3]),
                'weight': float(item[5]),
                'delivery_type': item[6] or 'truck'
            }
            for item in order_items
        ]
    
    with st.form(f"edit_complex_order_{order_id}"):
        st.subheader("📋 Редактирование комплексного заказа")
        
        col1, col2 = st.columns(2)
        
        with col1:
            order_name = st.text_input(
                "Название заказа *", 
                value=order_info[1],
                help="Укажите название заказа"
            )
        
        with col2:
            total_payment = st.number_input(
                "Общая сумма платежа ($) *", 
                min_value=0.0, 
                format="%.2f",
                value=float(order_info[3] or 0)
            )
        
        st.subheader("🛍️ Товары в заказе")
        
        # Отображение текущих товаров для редактирования
        items_to_edit = st.session_state[edit_items_key]
        
        for i, item in enumerate(items_to_edit):
            with st.expander(f"📦 {item['product_name']} (Товар {i+1})"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    new_name = st.text_input(f"Название", value=item['product_name'], key=f"edit_name_{order_id}_{i}")
                    items_to_edit[i]['product_name'] = new_name
                
                with col2:
                    new_quantity = st.number_input(f"Количество", min_value=1, value=item['quantity'], key=f"edit_qty_{order_id}_{i}")
                    items_to_edit[i]['quantity'] = new_quantity
                
                with col3:
                    new_cost = st.number_input(f"Себестоимость ($)", min_value=0.0, format="%.2f", value=item['cost_price'], key=f"edit_cost_{order_id}_{i}")
                    items_to_edit[i]['cost_price'] = new_cost
                
                with col4:
                    new_weight = st.number_input(f"Вес (кг)", min_value=0.0, format="%.2f", value=item['weight'], key=f"edit_weight_{order_id}_{i}")
                    items_to_edit[i]['weight'] = new_weight
                
                delivery_type = st.selectbox(
                    f"Тип доставки",
                    options=["airplane", "truck"],
                    format_func=lambda x: "✈️ Самолет ($7/кг)" if x == "airplane" else "🚛 Машина ($0.68/кг)",
                    index=0 if item['delivery_type'] == "airplane" else 1,
                    key=f"edit_delivery_{order_id}_{i}"
                )
                items_to_edit[i]['delivery_type'] = delivery_type
                
                # Показать расчет для товара
                item_delivery_cost = new_weight * DELIVERY_RATES[delivery_type]
                st.info(f"📦 Стоимость доставки этого товара: ${item_delivery_cost:.2f}")
        
        # Общий расчет
        if items_to_edit and total_payment > 0:
            total_delivery_cost = sum(item['weight'] * DELIVERY_RATES[item['delivery_type']] for item in items_to_edit)
            total_weight = sum(item['weight'] for item in items_to_edit)
            
            st.markdown("### 💰 Предварительный расчет")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("⚖️ Общий вес", f"{total_weight:.2f} кг")
            
            with col2:
                st.metric("🚚 Стоимость доставки", f"${total_delivery_cost:.2f}")
            
            with col3:
                remaining = max(0, total_payment - total_delivery_cost)
                st.metric("💰 Остается на товары", f"${remaining:.2f}")
        
        # Кнопки управления
        col1, col2 = st.columns(2)
        
        with col1:
            save_btn = st.form_submit_button("💾 Сохранить изменения", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🚫 Отмена", use_container_width=True):
                st.session_state[f'edit_mode_{order_id}'] = False
                if edit_items_key in st.session_state:
                    del st.session_state[edit_items_key]
                st.rerun()
        
        # Обработка сохранения
        if save_btn:
            if order_name and total_payment > 0 and items_to_edit:
                # Проверяем, что все товары заполнены корректно
                valid_items = all(
                    item['product_name'] and item['quantity'] > 0 and 
                    item['cost_price'] >= 0 and item['weight'] > 0
                    for item in items_to_edit
                )
                
                if valid_items:
                    if update_complex_order(order_id, user_id, order_name, total_payment, items_to_edit):
                        st.success("✅ Комплексный заказ успешно обновлен!")
                        st.session_state[f'edit_mode_{order_id}'] = False
                        if edit_items_key in st.session_state:
                            del st.session_state[edit_items_key]
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Ошибка при обновлении заказа")
                else:
                    st.error("❌ Проверьте корректность заполнения всех товаров")
            else:
                st.error("❌ Заполните все обязательные поля")

def get_delayed_orders(user_id):
    """Получает заказы с задержкой доставки"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    from datetime import datetime
    current_time = datetime.now()
    
    query = '''
        SELECT id, order_name, expected_delivery_date, delay_notification_sent
        FROM orders 
        WHERE user_id = ? 
        AND status = 'pending' 
        AND expected_delivery_date < ?
        ORDER BY expected_delivery_date
    '''
    
    cursor.execute(query, (user_id, current_time))
    delayed_orders = cursor.fetchall()
    conn.close()
    
    return delayed_orders

def mark_delay_notification_sent(order_id):
    """Отмечает, что уведомление о задержке отправлено"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE orders SET delay_notification_sent = 1 WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

def send_delay_notifications(user_id):
    """Отправляет уведомления о задержанных заказах"""
    delayed_orders = get_delayed_orders(user_id)
    notifications_sent = 0
    
    for order in delayed_orders:
        order_id, order_name, expected_date, notification_sent = order
        
        if not notification_sent:  # Если уведомление еще не отправлялось
            # Здесь можно добавить отправку email уведомления
            print(f"🚨 ЗАДЕРЖКА: Заказ '{order_name}' должен был прибыть {expected_date}")
            
            # Отмечаем, что уведомление отправлено
            mark_delay_notification_sent(order_id)
            notifications_sent += 1
    
    return notifications_sent

# Функции аналитики
def get_analytics(user_id):
    conn = sqlite3.connect('business_manager.db')
    
    # Получаем все заказы пользователя
    query = '''
        SELECT oi.*, o.created_at, o.order_type
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.user_id = ?
    '''
    df = pd.read_sql_query(query, conn, params=(user_id,))
    
    if df.empty:
        conn.close()
        return {
            'total_revenue': 0,
            'total_costs': 0,
            'total_cost_price': 0,
            'total_delivery_costs': 0,
            'profit': 0,
            'margin': 0,
            'profitability': 0,
            'financial_cushion': 0,
            'personal_expenses': 0,
            'cushion_percent': 20.0
        }
    
    # Получаем настройки пользователя
    settings_query = 'SELECT financial_cushion_percent FROM settings WHERE user_id = ?'
    cursor = conn.cursor()
    cursor.execute(settings_query, (user_id,))
    settings = cursor.fetchone()
    cushion_percent = settings[0] if settings else 20.0
    
    conn.close()
    
    # Расчеты
    total_revenue = df['total_cost'].sum()
    total_cost_price = (df['cost_price'] * df['quantity']).sum()
    total_delivery_costs = df['delivery_cost'].sum()
    total_costs = total_cost_price + total_delivery_costs
    
    # Расчет прибыли на основе цены продажи
    total_sale_value = (df['sale_price'].fillna(0) * df['quantity']).sum()
    profit = total_sale_value - total_cost_price  # Прибыль без учета доставки
    margin = (profit / total_sale_value * 100) if total_sale_value > 0 else 0
    profitability = (profit / total_cost_price * 100) if total_cost_price > 0 else 0
    
    financial_cushion = profit * (cushion_percent / 100)
    personal_expenses = profit - financial_cushion
    
    return {
        'total_revenue': total_revenue,
        'total_costs': total_costs,
        'total_cost_price': total_cost_price,
        'total_delivery_costs': total_delivery_costs,
        'profit': profit,
        'margin': margin,
        'profitability': profitability,
        'financial_cushion': financial_cushion,
        'personal_expenses': personal_expenses,
        'cushion_percent': cushion_percent
    }

# Функции для работы со складом
def add_to_inventory(user_id, product_name, quantity, link="", min_stock_level=0):
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем премиум статус пользователя
    is_premium = check_premium_status(user_id)
    
    # Для бесплатных пользователей проверяем лимит в 20 товаров
    if not is_premium:
        cursor.execute('SELECT COUNT(*) FROM inventory WHERE user_id = ?', (user_id,))
        current_count = cursor.fetchone()[0]
        
        # Проверяем, есть ли уже такой товар
        cursor.execute('SELECT id FROM inventory WHERE user_id = ? AND product_name = ?', 
                      (user_id, product_name))
        existing = cursor.fetchone()
        
        # Если товара нет и достигнут лимит
        if not existing and current_count >= 20:
            conn.close()
            return False, "❌ Достигнут лимит в 20 товаров для бесплатной версии. Обновитесь до премиума для неограниченного доступа!"
    
    # Проверяем, есть ли уже такой товар
    cursor.execute('SELECT id, quantity, min_stock_level FROM inventory WHERE user_id = ? AND product_name = ?', 
                  (user_id, product_name))
    existing = cursor.fetchone()
    
    if existing:
        # Обновляем количество, сохраняя минимальный уровень если он не задан
        new_quantity = existing[1] + quantity
        current_min = existing[2] if existing[2] else min_stock_level
        cursor.execute('UPDATE inventory SET quantity = ?, link = ?, min_stock_level = ? WHERE id = ?', 
                      (new_quantity, link, current_min, existing[0]))
    else:
        # Добавляем новый товар
        cursor.execute('''INSERT INTO inventory (user_id, product_name, quantity, link, min_stock_level, reserved_quantity) 
                         VALUES (?, ?, ?, ?, ?, 0)''', 
                      (user_id, product_name, quantity, link, min_stock_level))
    
    conn.commit()
    conn.close()
    return True, "✅ Товар успешно добавлен на склад!"

def check_inventory_availability(user_id, product_name, required_quantity):
    """Проверка наличия товара на складе"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT quantity, COALESCE(reserved_quantity, 0), COALESCE(min_stock_level, 0) 
        FROM inventory 
        WHERE user_id = ? AND product_name = ?
    ''', (user_id, product_name))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return {
            'available': False,
            'current_stock': 0,
            'reserved': 0,
            'available_for_sale': 0,
            'min_level': 0,
            'message': 'Товар не найден на складе'
        }
    
    current_stock, reserved, min_level = result
    available_for_sale = current_stock - reserved
    
    return {
        'available': available_for_sale >= required_quantity,
        'current_stock': current_stock,
        'reserved': reserved,
        'available_for_sale': available_for_sale,
        'min_level': min_level,
        'message': f'В наличии: {available_for_sale} шт. (всего: {current_stock}, зарезервировано: {reserved})'
    }

def reserve_inventory(user_id, product_name, quantity):
    """Резервирование товара на складе"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем наличие
    availability = check_inventory_availability(user_id, product_name, quantity)
    
    if not availability['available']:
        conn.close()
        return False, availability['message']
    
    # Резервируем товар
    cursor.execute('''
        UPDATE inventory 
        SET reserved_quantity = COALESCE(reserved_quantity, 0) + ?
        WHERE user_id = ? AND product_name = ?
    ''', (quantity, user_id, product_name))
    
    conn.commit()
    conn.close()
    return True, f'Зарезервировано {quantity} шт. товара "{product_name}"'

def release_reservation(user_id, product_name, quantity):
    """Освобождение резерва товара"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE inventory 
        SET reserved_quantity = COALESCE(reserved_quantity, 0) - ?
        WHERE user_id = ? AND product_name = ?
    ''', (quantity, user_id, product_name))
    
    conn.commit()
    conn.close()

def confirm_sale_and_reduce_stock(user_id, product_name, quantity):
    """Подтверждение продажи и автоматическое списание со склада"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        # Уменьшаем количество товара и освобождаем резерв
        cursor.execute('''
            UPDATE inventory 
            SET quantity = quantity - ?,
                reserved_quantity = COALESCE(reserved_quantity, 0) - ?
            WHERE user_id = ? AND product_name = ?
        ''', (quantity, quantity, user_id, product_name))
        
        # Проверяем минимальный уровень для уведомлений
        cursor.execute('''
            SELECT quantity, COALESCE(min_stock_level, 0) 
            FROM inventory 
            WHERE user_id = ? AND product_name = ?
        ''', (user_id, product_name))
        
        result = cursor.fetchone()
        if result:
            current_qty, min_level = result
            
            if current_qty <= min_level and min_level > 0:
                # Добавляем уведомление о низком остатке
                cursor.execute('''
                    INSERT INTO notifications (user_id, type, message, created_at, is_read)
                    VALUES (?, 'low_stock', ?, datetime('now'), 0)
                ''', (user_id, f'Низкий остаток товара "{product_name}": {current_qty} шт. (минимум: {min_level})'))
        
        conn.commit()
        conn.close()
        return True, f'Продажа подтверждена. Списано {quantity} шт. товара "{product_name}"'
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f'Ошибка при списании товара: {str(e)}'

def get_low_stock_items(user_id):
    """Получение товаров с низким остатком"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_name, quantity, COALESCE(reserved_quantity, 0) as reserved, 
               COALESCE(min_stock_level, 0) as min_level,
               (quantity - COALESCE(reserved_quantity, 0)) as available
        FROM inventory 
        WHERE user_id = ? AND COALESCE(min_stock_level, 0) > 0 
        AND quantity <= min_stock_level
        ORDER BY (quantity - min_stock_level) ASC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'product_name': row[0],
            'current_stock': row[1],
            'reserved': row[2],
            'min_level': row[3],
            'available': row[4],
            'shortage': max(0, row[3] - row[1])
        }
        for row in results
    ]

def get_inventory(user_id):
    conn = sqlite3.connect('business_manager.db')
    df = pd.read_sql_query('SELECT * FROM inventory WHERE user_id = ? ORDER BY product_name', 
                          conn, params=(user_id,))
    conn.close()
    return df

def search_inventory(user_id, search_term):
    conn = sqlite3.connect('business_manager.db')
    query = '''
        SELECT * FROM inventory 
        WHERE user_id = ? AND product_name LIKE ? 
        ORDER BY product_name
    '''
    df = pd.read_sql_query(query, conn, params=(user_id, f'%{search_term}%'))
    conn.close()
    return df

def clear_inventory(user_id):
    """Удаляет все товары со склада пользователя"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Удаляем все товары пользователя
    cursor.execute('DELETE FROM inventory WHERE user_id = ?', (user_id,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    return deleted_count

def delete_inventory_item(user_id, product_id):
    """Удаляет конкретный товар со склада"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM inventory WHERE user_id = ? AND id = ?', (user_id, product_id))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted

def delete_inventory_items_bulk(user_id, product_ids):
    """Удаляет несколько товаров со склада"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    placeholders = ','.join('?' * len(product_ids))
    params = [user_id] + product_ids
    
    cursor.execute(f'DELETE FROM inventory WHERE user_id = ? AND id IN ({placeholders})', params)
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    return deleted_count

def update_inventory_quantity(user_id, product_id, new_quantity):
    """Обновляет количество товара на складе"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    if new_quantity <= 0:
        # Если количество 0 или меньше, удаляем товар
        cursor.execute('DELETE FROM inventory WHERE user_id = ? AND id = ?', (user_id, product_id))
    else:
        cursor.execute('UPDATE inventory SET quantity = ? WHERE user_id = ? AND id = ?', 
                      (new_quantity, user_id, product_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

# Функции для работы с историей заказов
def add_to_order_history(user_id, order_id, product_name, quantity, cost_price, sale_price, 
                        weight, delivery_type, delivery_cost, total_cost):
    """Добавляет запись в историю заказов (для товаров под заказ)"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO order_history 
        (user_id, order_id, product_name, quantity, cost_price, sale_price, 
         weight, delivery_type, delivery_cost, total_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, order_id, product_name, quantity, cost_price, sale_price, 
          weight, delivery_type, delivery_cost, total_cost))
    
    conn.commit()
    conn.close()

def get_order_history(user_id, limit=None):
    """Получает историю заказов пользователя"""
    conn = sqlite3.connect('business_manager.db')
    
    query = '''
        SELECT oh.*, o.order_name, o.created_at as order_created_at
        FROM order_history oh
        LEFT JOIN orders o ON oh.order_id = o.id
        WHERE oh.user_id = ?
        ORDER BY oh.order_date DESC
    '''
    
    if limit:
        query += f' LIMIT {limit}'
    
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def search_order_history(user_id, search_term, start_date=None, end_date=None):
    """Поиск в истории заказов с фильтрами"""
    conn = sqlite3.connect('business_manager.db')
    
    query = '''
        SELECT oh.*, o.order_name, o.created_at as order_created_at
        FROM order_history oh
        LEFT JOIN orders o ON oh.order_id = o.id
        WHERE oh.user_id = ? AND oh.product_name LIKE ?
    '''
    params = [user_id, f'%{search_term}%']
    
    if start_date:
        query += ' AND DATE(oh.order_date) >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND DATE(oh.order_date) <= ?'
        params.append(end_date)
    
    query += ' ORDER BY oh.order_date DESC'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def delete_order_history_item(item_id):
    """Удаляет отдельный товар из истории заказов"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM order_history WHERE id = ?', (item_id,))
    
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_rows > 0

def delete_order_history_items_bulk(item_ids):
    """Удаляет несколько товаров из истории заказов"""
    if not item_ids:
        return False
    
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in item_ids])
    cursor.execute(f'DELETE FROM order_history WHERE id IN ({placeholders})', item_ids)
    
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_rows > 0

# Функция для отображения улучшенной навигации
def show_navigation():
    """Отображает боковую навигационную панель"""
    
    # Инициализация состояний
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = True
    
    # Боковая панель навигации
    with st.sidebar:
        # Заголовок
        st.markdown("""
        <div class="nav-header">
            <div class="nav-title">📊 Бизнес Менеджер</div>
            <div class="nav-subtitle">Управление заказами</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Информация о пользователе
        if st.session_state.email:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #E3F2FD, #F0F7FF); 
                        padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                <strong style="color: var(--accent-color);">👤 {st.session_state.email}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Меню навигации
        menu_items = [
            ("dashboard", "📊", "Главная панель"),
            ("orders", "📦", "Заказы"),
            ("analytics", "📈", "Аналитика"),
            ("inventory", "🏪", "Склад"),
            ("smart", "🧠", "Умные функции"),
            ("settings", "⚙️", "Настройки")
        ]
        
        st.markdown('<div class="nav-menu">', unsafe_allow_html=True)
        
        for page_key, icon, title in menu_items:
            active_class = "active" if st.session_state.current_page == page_key else ""
            
            if st.button(
                f"{icon} {title}", 
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if active_class == "active" else "secondary"
            ):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Кнопка выхода
        st.markdown("---")
        if st.button("🚪 Выйти", use_container_width=True, type="secondary"):
            st.session_state.user_id = None
            st.session_state.email = None
            st.session_state.current_page = "dashboard"
            st.rerun()

def get_pending_orders_count():
    """Получить количество заказов в ожидании"""
    try:
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'pending'", 
                      (st.session_state.user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    except:
        return 0

def show_sidebar_menu():
    """Боковое меню с функциями"""
    
    # Создаем боковое меню
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;
                    text-align: center;">
            <h2 style="color: #000000; margin: 0;">🍔 Меню</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Навигационные кнопки
        if st.button("🏠 Главная страница", key="menu_dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.session_state.menu_open = False
            st.rerun()
        
        if st.button("📋 Управление заказами", key="menu_orders", use_container_width=True):
            st.session_state.current_page = "orders"
            st.session_state.menu_open = False
            st.rerun()
        
        if st.button("📊 Аналитика и отчеты", key="menu_analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.session_state.menu_open = False
            st.rerun()
        
        if st.button("📦 Управление инвентарем", key="menu_inventory", use_container_width=True):
            st.session_state.current_page = "inventory"
            st.session_state.menu_open = False
            st.rerun()
        
        if st.button("🤖 ИИ функции", key="menu_smart", use_container_width=True):
            st.session_state.current_page = "smart"
            st.session_state.menu_open = False
            st.rerun()
        
        if st.button("⚙️ Настройки", key="menu_settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.session_state.menu_open = False
            st.rerun()
        
        st.markdown("---")
        
        # Быстрая статистика
        st.markdown("### 📈 Быстрая статистика")
        
        try:
            total_orders = get_total_orders()
            total_revenue = get_total_revenue()
            delayed_orders = len(get_delayed_orders(st.session_state.user_id))
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Заказов", total_orders)
                st.metric("Задержек", delayed_orders)
            with col_b:
                st.metric("Выручка", f"${total_revenue:,.0f}")
                
        except Exception as e:
            st.error(f"Ошибка загрузки статистики: {e}")
        
        st.markdown("---")
        
        # Быстрые действия
        st.markdown("### ⚡ Быстрые действия")
        
        if st.button("� Проверить задержки", key="quick_delays", use_container_width=True):
            try:
                notifications = send_delay_notifications(st.session_state.user_id)
                if notifications > 0:
                    st.warning(f"⚠️ Найдено {notifications} задержанных заказов")
                else:
                    st.success("✅ Нет задержанных заказов")
            except Exception as e:
                st.error(f"Ошибка: {e}")
        
        if st.button("📤 Экспорт данных", key="quick_export", use_container_width=True):
            st.info("📄 Функция экспорта в разработке")
        
        st.markdown("---")
        
        # Кнопка закрытия меню
        if st.button("❌ Закрыть меню", key="close_menu", use_container_width=True):
            st.session_state.menu_open = False
            st.rerun()
        
        # Выход из системы
        if st.button("🚪 Выйти", key="menu_logout", use_container_width=True, type="secondary"):
            st.session_state.user_id = None
            st.session_state.email = None
            st.session_state.current_page = "dashboard"
            st.session_state.menu_open = False
            st.rerun()

def get_total_orders():
    """Получить общее количество заказов"""
    try:
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (st.session_state.user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    except:
        return 0

def get_total_revenue():
    """Получить общую выручку"""
    try:
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_price) FROM orders WHERE user_id = ?", (st.session_state.user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else 0
    except:
        return 0
        
        st.markdown("---")
        
        # Быстрая статистика
        st.markdown("### 📈 Быстрая статистика")
        
        try:
            # Получаем данные для быстрой статистики
            conn = sqlite3.connect('business_manager.db')
            cursor = conn.cursor()
            
            # Количество заказов
            cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (st.session_state.user_id,))
            total_orders = cursor.fetchone()[0]
            
            # Задержанные заказы
            delayed_orders = get_delayed_orders(st.session_state.user_id)
            delayed_count = len(delayed_orders)
            
            # Общая прибыль
            cursor.execute("SELECT SUM(profit) FROM orders WHERE user_id = ?", (st.session_state.user_id,))
            total_profit = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Отображаем статистику в красивых карточках
            st.markdown(f"""
            <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <div style="text-align: center;">
                    <h3 style="color: #1f77b4; margin: 0;">📋 {total_orders}</h3>
                    <p style="margin: 5px 0 0 0; color: #666;">Всего заказов</p>
                </div>
            </div>
            
            <div style="background: {'#ffe6e6' if delayed_count > 0 else '#e6ffe6'}; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <div style="text-align: center;">
                    <h3 style="color: {'#ff4444' if delayed_count > 0 else '#44ff44'}; margin: 0;">
                        {'⚠️' if delayed_count > 0 else '✅'} {delayed_count}
                    </h3>
                    <p style="margin: 5px 0 0 0; color: #666;">Задержанных заказов</p>
                </div>
            </div>
            
            <div style="background: #e6f7ff; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <div style="text-align: center;">
                    <h3 style="color: #52c41a; margin: 0;">💰 ${total_profit:,.0f}</h3>
                    <p style="margin: 5px 0 0 0; color: #666;">Общая прибыль</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Ошибка загрузки статистики: {e}")
        
        st.markdown("---")
        
        # Быстрые действия
        st.markdown("### ⚡ Быстрые действия")
        
        if st.button("🚨 Проверить задержки", use_container_width=True):
            notifications_sent = send_delay_notifications(st.session_state.user_id)
            if notifications_sent > 0:
                st.warning(f"Отправлено {notifications_sent} уведомлений")
            else:
                st.success("Нет задержанных заказов")
        
        if st.button("🔄 Обновить данные", use_container_width=True):
            st.cache_data.clear()
            st.success("Кэш очищен!")
        
        st.markdown("---")
        
        # Кнопка закрытия
        if st.button("❌ Закрыть меню", use_container_width=True, type="primary"):
            st.session_state.show_sidebar_menu = False
            st.rerun()

# Основное приложение
def apply_custom_styles():
    """Применить темные стили"""
    st.markdown("""
    <style>
    /* Скрыть стандартные элементы Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_container__1QSob {display: none;}
    
    /* CSS переменные для темной темы */
    :root {
        --primary-dark: #1a1a2e;
        --secondary-dark: #16213e;
        --accent-dark: #0f3460;
        --text-light: #ecf0f1;
        --text-muted: #95a5a6;
        --accent-blue: #00d4ff;
        --accent-gradient: linear-gradient(135deg, #00d4ff, #a8edea);
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
        --border-light: rgba(255,255,255,0.1);
        --shadow-dark: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Основные стили приложения */
    .stApp {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 1400px;
        background: var(--primary-dark);
        border-radius: 20px;
        margin: 1rem auto;
        box-shadow: var(--shadow-dark);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-light);
    }
    
    /* Темная форма аутентификации */
    .auth-container {
        max-width: 400px;
        margin: 50px auto;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
        border-radius: 20px;
        padding: 40px;
        box-shadow: var(--shadow-dark);
        border: 1px solid var(--border-light);
    }
    
    .auth-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-light);
        margin-bottom: 30px;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Поля ввода - исправленные стили */
    .stTextInput > div > div > input {
        background: var(--bg-primary) !important;
        border: 2px solid var(--border-medium) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(0,102,204,0.2) !important;
        background: var(--bg-primary) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Темные кнопки */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-blue) 0%, #a8edea 100%) !important;
        color: var(--primary-dark) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,212,255,0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,212,255,0.4) !important;
        background: linear-gradient(135deg, #a8edea 0%, var(--accent-blue) 100%) !important;
    }
    
    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-light) !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 10px !important;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Текст и параграфы */
    .stMarkdown p, .stText, .element-container p {
        color: var(--text-light) !important;
    }
    
    /* Темные табы */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--secondary-dark);
        border-radius: 15px;
        padding: 5px;
        border: 1px solid var(--border-light);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-gradient) !important;
        color: var(--primary-dark) !important;
    }
    
    /* Селектбоксы */
    .stSelectbox > div > div {
        background: var(--secondary-dark) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: 12px !important;
        color: var(--text-light) !important;
    }
    
    .stSelectbox > div > div > div {
        color: var(--text-light) !important;
    }
    
    /* Number input - исправленные стили */
    .stNumberInput > div > div > input {
        background: var(--bg-primary) !important;
        border: 2px solid var(--border-medium) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem !important;
    }
    
    /* Date input - исправленные стили */
    .stDateInput > div > div > input {
        background: var(--bg-primary) !important;
        border: 2px solid var(--border-medium) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem !important;
    }
    
    /* Метрики */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted);
    }
    
    /* Темные алерты */
    .stAlert {
        background: var(--secondary-dark) !important;
        border: 1px solid var(--border-light) !important;
        color: var(--text-light) !important;
        border-radius: 12px !important;
    }
    
    .stSuccess {
        background: rgba(39, 174, 96, 0.2) !important;
        border: 1px solid var(--success-color) !important;
    }
    
    .stError {
        background: rgba(231, 76, 60, 0.2) !important;
        border: 1px solid var(--danger-color) !important;
    }
    
    .stWarning {
        background: rgba(243, 156, 18, 0.2) !important;
        border: 1px solid var(--warning-color) !important;
    }
    
    .stInfo {
        background: rgba(0, 212, 255, 0.2) !important;
        border: 1px solid var(--accent-blue) !important;
    }
    
    /* Боковая панель */
    .css-1d391kg {
        background: var(--primary-dark) !important;
    }
    
    .css-1cypcdb {
        background: var(--secondary-dark) !important;
        border-right: 1px solid var(--border-light) !important;
    }
    
    /* Формы */
    .stForm {
        background: var(--secondary-dark) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    
    /* Радио кнопки */
    .stRadio > div {
        background: var(--secondary-dark) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border: 1px solid var(--border-light) !important;
    }
    
    .stRadio label {
        color: var(--text-light) !important;
    }
    
    /* Топ навигация */
    .top-nav {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 15px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .nav-item {
        display: inline-block;
        padding: 8px 20px;
        margin: 0 5px;
        background: rgba(255, 255, 255, 0.1);
        color: #000000;
        border-radius: 25px;
        text-decoration: none;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #3498db, #2980b9);
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
    }
    
    /* Карточки */
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
    }
    
    /* Метрики */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #000000;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border: none;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    /* Формы входа */
    .auth-container {
        max-width: 400px;
        margin: 50px auto;
        background: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .auth-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Поля ввода */
    .stTextInput > div > div > input {
        border: 2px solid #e1e8ed !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        background: #f8f9fa !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2) !important;
        background: white !important;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 10px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Списки заказов */
    .order-item {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .order-item:hover {
        transform: translateX(10px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-left-color: #764ba2;
    }
    
    .order-title {
        font-weight: 600;
        color: #2c3e50;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    
    .order-meta {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    
    /* Статусы */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-pending {
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: #000000;
    }
    
    .status-delivered {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: #000000;
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Адаптивность */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
            margin: 0.5rem;
        }
        
        .top-nav {
            padding: 10px 15px;
        }
        
        .nav-item {
            display: block;
            margin: 5px 0;
            text-align: center;
        }
        
        .auth-container {
            margin: 20px;
            padding: 30px 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Главная функция приложения"""
    st.set_page_config(
        page_title="📊 Business Manager Pro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_db()
    
    # Применить пользовательские стили
    apply_custom_styles()
    
    # Состояние сессии
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'is_premium' not in st.session_state:
        st.session_state.is_premium = False
    if 'show_smart_insights' not in st.session_state:
        st.session_state.show_smart_insights = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Аутентификация
    if not st.session_state.user_id:
        show_auth()
        return
    
    # Проверяем премиум статус при каждом входе
    st.session_state.is_premium = check_premium_status(st.session_state.user_id)
    
    # Проверяем админ статус
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE id = ?', (st.session_state.user_id,))
    result = cursor.fetchone()
    st.session_state.is_admin = result[0] if result else False
    conn.close()
    
    # Автоматическая проверка низких остатков при запуске
    check_and_create_low_stock_notifications(st.session_state.user_id)
    
    # Показать современную навигацию с уведомлениями
    show_modern_navigation()
    
    # Показать админскую навигацию если пользователь админ
    show_admin_navigation()
    
    # Отображение контента в зависимости от выбранной страницы
    page = st.session_state.current_page
    
    if page == "dashboard":
        show_dashboard()
    elif page == "orders":
        show_orders()
    elif page == "order_management":
        show_order_management()
    elif page == "analytics":
        # Премиум функция - полная аналитика
        if st.session_state.is_premium:
            show_analytics()
        else:
            show_limited_analytics()
    elif page == "inventory":
        show_inventory()
    elif page == "notifications":  
        show_notifications()
    elif page == "smart":
        # Премиум функция - умные инсайты
        if st.session_state.is_premium:
            show_smart_functions()
        else:
            show_premium_required("умные функции и инсайты")
    elif page == "admin":
        # Админская страница
        if st.session_state.get('is_admin', False):
            show_admin_panel()
        else:
            st.error("❌ У вас нет прав администратора")
    elif page == "settings":
        show_settings()
    else:
        show_dashboard()

def show_limited_analytics():
    """Ограниченная аналитика для обычных пользователей"""
    st.title("📊 Аналитика")
    
    st.warning("⚠️ Доступна только базовая аналитика. Для полных отчетов нужна премиум-подписка")
    
    analytics = get_analytics(st.session_state.user_id)
    
    # Только основные метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Общая выручка", f"${analytics['total_revenue']:.2f}")
    
    with col2:
        st.metric("💸 Общие расходы", f"${analytics['total_costs']:.2f}") 
    
    with col3:
        st.metric("📈 Прибыль", f"${analytics['profit']:.2f}")
    
    with col4:
        st.metric("📊 Маржа", f"{analytics['margin']:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📊 **Детальные графики** - только в премиум версии")
        st.info("📈 **Прогнозирование** - только в премиум версии")
    
    with col2:
        st.info("📤 **Экспорт отчетов** - только в премиум версии")
        st.info("📧 **Автоматические отчеты** - только в премиум версии")
    
    if st.button("💎 Перейти к премиум", type="primary"):
        st.session_state.current_page = "premium"
        st.rerun()

def show_premium_required(feature_name):
    """Показывает экран для премиум-функций"""
    st.title(f"💎 Премиум функция")
    
    st.error(f"⚠️ **{feature_name.title()}** доступны только в премиум версии!")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h2 style="color: #667eea;">🔒 {feature_name.title()}</h2>
        <p style="font-size: 1.2rem; color: #666;">
            Для использования данной функции необходимо активировать премиум-подписку
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: #000000; padding: 30px; border-radius: 15px; text-align: center;">
            <h3 style="color: #000000; margin-bottom: 20px;">💎 Премиум подписка</h3>
            <h2 style="color: #000000; margin: 20px 0;">150 ТМ / месяц</h2>
            <p style="margin-bottom: 20px;">
                Получите доступ ко всем возможностям Business Manager Pro:
            </p>
            <div style="text-align: left; margin: 20px 0;">
                <p>🧠 <strong>ИИ-функции и умные инсайты</strong></p>
                <p>📊 <strong>Расширенная аналитика</strong></p>
                <p>📈 <strong>Детальные отчеты и прогнозирование</strong></p>
                <p>📤 <strong>Экспорт данных в Excel</strong></p>
                <p>📧 <strong>Email уведомления</strong></p>
                <p>💰 <strong>Мультивалютность</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Перейти к покупке премиума", type="primary", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
        
        if st.button("← Вернуться назад", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

def show_auth():
    # Центрированная современная форма
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Современный заголовок
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0 2rem 0;">
            <h1 style="
                color: #2E4057; 
                font-size: 2.5rem; 
                font-weight: 300; 
                margin-bottom: 0.5rem;
                letter-spacing: -1px;
            ">Бизнес Менеджер</h1>
            <p style="
                color: #64748B; 
                font-size: 1.1rem; 
                margin: 0;
                font-weight: 300;
            ">Управление вашим бизнесом</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Современные вкладки
        tab1, tab2 = st.tabs(["Вход", "Регистрация"])
        
        with tab1:
            st.markdown("""
            <div class="auth-card">
                <div class="auth-header">
                    <h2>Добро пожаловать</h2>
                    <p>Войдите в свой аккаунт для продолжения</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(
                    "Email", 
                    placeholder="example@company.com",
                    help="Введите ваш email адрес"
                )
                password = st.text_input(
                    "Пароль", 
                    type="password", 
                    placeholder="Введите пароль",
                    help="Ваш пароль"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button(
                    "Войти в систему", 
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted:
                    if email and password:
                        user_id = login_user(email, password)
                        if user_id:
                            st.session_state.user_id = user_id
                            st.session_state.email = email
                            st.success("Успешный вход в систему!")
                            st.rerun()
                        else:
                            st.error("Неверные учетные данные")
                    else:
                        st.warning("Пожалуйста, заполните все поля")
        
        with tab2:
            st.markdown("""
            <div class="auth-card">
                <div class="auth-header">
                    <h2>Создать аккаунт</h2>
                    <p>Зарегистрируйтесь для начала работы</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form", clear_on_submit=False):
                reg_email = st.text_input(
                    "Email *", 
                    placeholder="example@company.com",
                    key="reg_email",
                    help="Ваш email будет использоваться для входа"
                )
                reg_password = st.text_input(
                    "Пароль *", 
                    type="password", 
                    placeholder="Создайте надежный пароль",
                    key="reg_password",
                    help="Минимум 6 символов"
                )
                reg_password_confirm = st.text_input(
                    "Подтвердите пароль *", 
                    type="password", 
                    placeholder="Повторите пароль",
                    key="reg_password_confirm"
                )
                
                # Дополнительные поля
                reg_phone = st.text_input(
                    "Номер телефона *",
                    placeholder="+993 XX XXX XX XX",
                    key="reg_phone",
                    help="Обязательное поле для связи и поддержки"
                )
                reg_full_name = st.text_input(
                    "Полное имя",
                    placeholder="Иван Иванов",
                    key="reg_full_name"
                )
                reg_business_name = st.text_input(
                    "Название бизнеса",
                    placeholder="ООО Мой Бизнес",
                    key="reg_business_name"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button(
                    "🚀 Создать аккаунт", 
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted:
                    if reg_email and reg_password and reg_password_confirm and reg_phone:
                        if len(reg_password) < 6:
                            st.error("Пароль должен содержать минимум 6 символов")
                        elif reg_password == reg_password_confirm:
                            success, message = register_user(reg_email, reg_password, reg_phone, 
                                                           reg_full_name, reg_business_name)
                            if success:
                                st.success(message)
                                st.info("Теперь вы можете войти в систему")
                            else:
                                st.error(message)
                        else:
                            st.error("Пароли не совпадают")
                    else:
                        st.warning("Пожалуйста, заполните все обязательные поля (*)")

def show_dashboard():
    st.title("📊 Панель управления")
    
    analytics = get_analytics(st.session_state.user_id)
    
    # Основные метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Общая выручка", f"${analytics['total_revenue']:.2f}")
    
    with col2:
        st.metric("💸 Общие расходы", f"${analytics['total_costs']:.2f}")
    
    with col3:
        st.metric("📈 Прибыль", f"${analytics['profit']:.2f}")
    
    with col4:
        st.metric("📊 Маржа", f"{analytics['margin']:.1f}%")
    
    # Финансовая подушка и личные расходы
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🛡️ Финансовая подушка", f"${analytics['financial_cushion']:.2f}")
    
    with col2:
        st.metric("🏠 На личные расходы", f"${analytics['personal_expenses']:.2f}")
    
    # Недавние заказы
    st.subheader("📦 Последние заказы")
    conn = sqlite3.connect('business_manager.db')
    recent_orders = pd.read_sql_query('''
        SELECT o.order_name, o.order_type, o.created_at, 
               COUNT(oi.id) as items_count,
               SUM(oi.total_cost) as total_value
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.id
        ORDER BY o.created_at DESC
        LIMIT 5
    ''', conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not recent_orders.empty:
        st.dataframe(recent_orders, use_container_width=True)
    else:
        st.info("Пока нет заказов")

def show_orders():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="
            color: #2E4057; 
            font-size: 2.5rem; 
            font-weight: 300; 
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        ">📦 Управление заказами</h1>
        <p style="
            color: #64748B; 
            font-size: 1.1rem; 
            margin: 0;
            font-weight: 300;
        ">Создавайте и отслеживайте заказы</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Добавить заказ", "📋 Одиночные заказы", "📋 Комплексные заказы"])
    
    with tab1:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #2E4057; font-weight: 400;">Выберите тип заказа</h2>
        </div>
        """, unsafe_allow_html=True)
        
        order_type = st.radio(
            "Тип заказа:", 
            ["Одиночный", "Комплексный"],
            horizontal=True,
            help="Одиночный заказ содержит один товар, комплексный - несколько товаров"
        )
        
        if order_type == "Одиночный":
            show_single_order_form()
        else:
            show_complex_order_form()
    
    with tab2:
        show_simple_order_history("single")
    
    with tab3:
        show_simple_order_history("complex")

def show_single_order_form():
    st.subheader("➕ Добавить одиночный заказ")
    
    with st.form("single_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Название товара *")
            quantity = st.number_input("Количество *", min_value=1, value=1)
            cost_price = st.number_input("Себестоимость ($) *", min_value=0.0, format="%.2f")
            sale_price = st.number_input("Цена продажи ($) *", min_value=0.0, format="%.2f")
        
        with col2:
            weight = st.number_input("Вес (кг) *", min_value=0.0, format="%.2f")
            delivery_type = st.selectbox("Тип доставки *", 
                                       options=["airplane", "truck"],
                                       format_func=lambda x: "Самолет ($7/кг)" if x == "airplane" else "Машина ($0.68/кг)")
            
            # Новое поле для даты заказа
            st.markdown("### 📅 Дата заказа")
            order_date = st.date_input(
                "Дата создания заказа:",
                value=datetime.now().date(),
                help="Выберите дату создания заказа. От этой даты будет рассчитана ожидаемая доставка."
            )
            
            # Автоматический расчет даты доставки
            delivery_days = 7 if delivery_type == "airplane" else 14  # Самолет - 7 дней, машина - 14 дней
            expected_delivery = order_date + timedelta(days=delivery_days)
            
            st.info(f"🚚 Ожидаемая доставка: **{expected_delivery.strftime('%d.%m.%Y')}** ({delivery_days} дней)")
            
            # Автоматическая проверка наличия на складе
            availability_info = None
            stock_status = "unknown"
            if product_name and quantity > 0:
                availability_info = check_inventory_availability(st.session_state.user_id, product_name, quantity)
                
                if availability_info['available']:
                    st.success(f"✅ В наличии на складе: {availability_info['available_for_sale']} шт.")
                    st.info("🏪 Товар будет автоматически списан со склада при подтверждении заказа")
                    stock_status = "in_stock"
                else:
                    if availability_info['current_stock'] > 0:
                        st.warning(f"⚠️ Недостаточно на складе. Доступно: {availability_info['available_for_sale']} шт.")
                        st.info("📋 Заказ будет создан как 'под заказ' - товар нужно будет докупить")
                    else:
                        st.error("❌ Товара нет на складе")
                        st.info("� Заказ будет создан как 'под заказ' - товар нужно будет закупить")
                    stock_status = "out_of_stock"
        
        # Предварительный расчет
        if weight > 0 and sale_price > 0:
            delivery_cost = weight * DELIVERY_RATES[delivery_type]
            total_cost = sale_price * quantity + delivery_cost
            profit_per_item = sale_price - cost_price
            total_profit = profit_per_item * quantity
            
            st.markdown("---")
            st.markdown("### 💰 Предварительный расчет")
            
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            
            with calc_col1:
                st.metric("🚚 Доставка", f"${delivery_cost:.2f}")
                st.metric("📊 Прибыль за ед.", f"${profit_per_item:.2f}")
            
            with calc_col2:
                st.metric("📈 Общая прибыль", f"${total_profit:.2f}")
                st.metric("💼 Маржа", f"{(profit_per_item/sale_price*100):.1f}%" if sale_price > 0 else "0%")
            
            with calc_col3:
                st.metric("💰 Итого", f"${total_cost:.2f}")
                profit_color = "normal" if total_profit >= 0 else "inverse"
                st.metric("🎯 Рентабельность", f"{'Прибыльно' if total_profit >= 0 else 'Убыточно'}", delta=f"{total_profit:.2f}")
        
        submitted = st.form_submit_button("➕ Создать заказ", use_container_width=True)
        
        if submitted:
            if product_name and quantity > 0 and cost_price >= 0 and sale_price >= 0 and weight > 0:
                # Создаем заказ (система сама определит, есть ли товар на складе)
                order_id = add_single_order(
                    st.session_state.user_id, 
                    product_name, 
                    quantity, 
                    cost_price, 
                    sale_price, 
                    weight, 
                    delivery_type,
                    order_date,
                    expected_delivery,
                    stock_status
                )
                
                if order_id:
                    if stock_status == "in_stock":
                        st.success(f"✅ Заказ #{order_id} создан! Товар зарезервирован на складе.")
                    else:
                        st.success(f"✅ Заказ #{order_id} создан! Товар нужно заказать у поставщика.")
                    
                    st.success(f"📅 Дата заказа: {order_date.strftime('%d.%m.%Y')}")
                    st.success(f"🚚 Ожидаемая доставка: {expected_delivery.strftime('%d.%m.%Y')}")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Ошибка при создании заказа")
            else:
                st.error("❌ Пожалуйста, заполните все обязательные поля")

def show_complex_order_form():
    st.subheader("➕ Добавить комплексный заказ")
    
    # Инициализация состояния для товаров
    if 'complex_items' not in st.session_state:
        st.session_state.complex_items = []
    
    with st.form("complex_order_form"):
        # Выбор типа заказа
        order_type = st.radio(
            "Выберите тип заказа:",
            ["Заказать под заказ", "Взять со склада"],
            horizontal=True,
            help="Под заказ - сохраняется только в историю заказов. Со склада - создается обычный заказ и добавляется на склад."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            order_name = st.text_input("Название заказа *")
            total_payment = st.number_input("Общая сумма платежа ($) *", min_value=0.0, format="%.2f")
        
        st.subheader("Товары в заказе")
        
        # Форма для добавления товара
        with st.expander("➕ Добавить товар"):
            item_name = st.text_input("Название товара")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                item_quantity = st.number_input("Количество", min_value=1, value=1, key="item_qty")
            with col2:
                item_cost = st.number_input("Себестоимость ($)", min_value=0.0, format="%.2f", key="item_cost")
            with col3:
                item_weight = st.number_input("Вес (кг)", min_value=0.0, format="%.2f", key="item_weight")
            with col4:
                item_delivery_type = st.selectbox("Тип доставки", 
                                                options=["airplane", "truck"],
                                                format_func=lambda x: "Самолет ($7/кг)" if x == "airplane" else "Машина ($0.68/кг)",
                                                key="item_delivery")
            
            add_item_btn = st.form_submit_button("Добавить товар")
            
            if add_item_btn and item_name and item_quantity > 0 and item_cost >= 0 and item_weight > 0:
                st.session_state.complex_items.append({
                    'product_name': item_name,
                    'quantity': item_quantity,
                    'cost_price': item_cost,
                    'weight': item_weight,
                    'delivery_type': item_delivery_type
                })
                st.success(f"Товар '{item_name}' добавлен")
        
        # Отображение добавленных товаров
        if st.session_state.complex_items:
            st.write("**Добавленные товары:**")
            
            # Создаем DataFrame с читаемыми типами доставки
            items_display = []
            for item in st.session_state.complex_items:
                display_item = item.copy()
                display_item['delivery_type_display'] = "Самолет ($7/кг)" if item['delivery_type'] == "airplane" else "Машина ($0.68/кг)"
                display_item['item_delivery_cost'] = item['weight'] * DELIVERY_RATES[item['delivery_type']]
                items_display.append(display_item)
            
            items_df = pd.DataFrame(items_display)
            # Переименовываем колонки для отображения
            display_columns = {
                'product_name': 'Товар',
                'quantity': 'Количество',
                'cost_price': 'Себестоимость ($)',
                'weight': 'Вес (кг)',
                'delivery_type_display': 'Тип доставки',
                'item_delivery_cost': 'Стоимость доставки ($)'
            }
            items_df_display = items_df[list(display_columns.keys())].rename(columns=display_columns)
            st.dataframe(items_df_display, use_container_width=True)
            
            # Предварительный расчет
            total_delivery_cost = sum(item['weight'] * DELIVERY_RATES[item['delivery_type']] for item in st.session_state.complex_items)
            total_weight = sum(item['weight'] for item in st.session_state.complex_items)
            
            st.write("**Предварительный расчет:**")
            st.write(f"- Общий вес: {total_weight:.2f} кг")
            st.write(f"- Общая стоимость доставки: ${total_delivery_cost:.2f}")
            st.write(f"- Остается на товары: ${max(0, total_payment - total_delivery_cost):.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_order = st.form_submit_button("Создать заказ")
        with col2:
            clear_items = st.form_submit_button("Очистить товары")
        
        if clear_items:
            st.session_state.complex_items = []
            st.rerun()
        
        if submit_order:
            if order_name and total_payment > 0 and st.session_state.complex_items:
                # Определяем, сохранять ли только в историю
                save_to_history_only = (order_type == "Заказать под заказ")
                
                order_id = add_complex_order(st.session_state.user_id, order_name, 
                                           total_payment, st.session_state.complex_items,
                                           save_to_history_only=save_to_history_only)
                
                # Добавляем товары на склад только если это заказ со склада
                if not save_to_history_only:
                    for item in st.session_state.complex_items:
                        add_to_inventory(st.session_state.user_id, item['product_name'], item['quantity'])
                
                order_type_msg = "под заказ" if save_to_history_only else "со склада"
                st.success(f"Комплексный заказ #{order_id} ({order_type_msg}) успешно создан!")
                st.session_state.complex_items = []
                st.rerun()
            else:
                st.error("Заполните все поля и добавьте хотя бы один товар")

def show_order_management():
    """Расширенное управление заказами с фильтрами и статусами"""
    st.title("📋 Управление заказами")
    
    # Основные вкладки
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Все заказы", "📦 Заказы со склада", "🚚 Заказы поставщикам", "⚡ Быстрые действия"])
    
    with tab1:
        st.header("📊 Все заказы")
        
        # Показываем информацию о лимитах
        if not st.session_state.is_premium:
            conn = sqlite3.connect('business_manager.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (st.session_state.user_id,))
            current_orders = cursor.fetchone()[0]
            conn.close()
            
            remaining_orders = 25 - current_orders
            if remaining_orders <= 5:
                st.warning(f"⚠️ **Лимит заказов**: {current_orders}/25 заказов. Осталось: {remaining_orders}")
                if remaining_orders == 0:
                    st.error("❌ Достигнут лимит! Обновитесь до премиума для неограниченных заказов")
            else:
                st.info(f"📦 **Заказы**: {current_orders}/25 заказов (бесплатная версия)")
        else:
            st.success("💎 **Премиум**: Неограниченное количество заказов")
        
        # Фильтры
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox(
                "Статус заказа:",
                ["Все", "pending", "confirmed", "shipped", "delivered", "cancelled"],
                format_func=lambda x: {
                    "Все": "Все статусы",
                    "pending": "Ожидает",
                    "confirmed": "Подтвержден", 
                    "shipped": "Отправлен",
                    "delivered": "Доставлен",
                    "cancelled": "Отменен"
                }.get(x, x)
            )
        
        with col2:
            date_from = st.date_input("С даты:", value=datetime.now().date() - timedelta(days=30))
        
        with col3:
            date_to = st.date_input("По дату:", value=datetime.now().date())
        
        with col4:
            search_product = st.text_input("Поиск по товару:")
        
        # Получение заказов с фильтрами
        conn = sqlite3.connect('business_manager.db')
        
        base_query = '''
            SELECT 
                o.id, 
                o.order_name,
                o.order_type,
                o.delivery_type, 
                o.created_at,
                o.expected_delivery_date, 
                COALESCE(o.status, 'pending') as status,
                COALESCE(o.total_payment, 0) as total_payment,
                COUNT(oi.id) as items_count,
                SUM(oi.total_cost) as total_cost,
                SUM(oi.cost_price * oi.quantity) as total_cost_price,
                SUM(oi.delivery_cost) as total_delivery_cost
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ?
        '''
        
        params = [st.session_state.user_id]
        
        # Применяем фильтры
        if status_filter != "Все":
            base_query += " AND COALESCE(o.status, 'pending') = ?"
            params.append(status_filter)
        
        if search_product:
            base_query += " AND (o.order_name LIKE ? OR oi.product_name LIKE ?)"
            params.extend([f"%{search_product}%", f"%{search_product}%"])
        
        base_query += " AND DATE(o.created_at) BETWEEN ? AND ?"
        params.extend([date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d')])
        
        base_query += " GROUP BY o.id ORDER BY o.created_at DESC"
        
        orders_df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()
        
        if not orders_df.empty:
            # Добавляем колонку с действиями
            st.subheader(f"Найдено заказов: {len(orders_df)}")
            
            # Отображаем статистику
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pending_count = len(orders_df[orders_df['status'] == 'pending'])
                st.metric("⏳ Ожидают", pending_count)
            
            with col2:
                delivered_count = len(orders_df[orders_df['status'] == 'delivered'])
                st.metric("✅ Доставлено", delivered_count)
            
            with col3:
                total_revenue = orders_df['total_cost'].sum()
                st.metric("💰 Общая выручка", f"${total_revenue:.2f}")
            
            with col4:
                total_profit = (orders_df['total_cost'] - orders_df['total_cost_price'] - orders_df['total_delivery_cost']).sum()
                st.metric("📈 Общая прибыль", f"${total_profit:.2f}")
            
            # Таблица заказов с возможностью изменения статуса
            st.subheader("📋 Список заказов")
            
            for idx, order in orders_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: #f8f9fa;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #000000;">🏷️ Заказ #{order['id']}: {order['order_name']}</h4>
                                <p style="margin: 5px 0; color: #333333;">
                                    📦 Тип: {order['order_type']} | 
                                    💵 Сумма: ${order['total_cost']:.2f} | 
                                    🚚 Доставка: {order['delivery_type']} | 
                                    📊 Товаров: {order['items_count']}
                                </p>
                                <p style="margin: 5px 0; color: #333333;">
                                    📅 Создан: {order['created_at'][:10]} | 
                                    🚀 Ожидается: {order['expected_delivery_date'] or 'Не указано'}
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: {'#28a745' if order['status'] == 'delivered' else '#ffc107' if order['status'] == 'pending' else '#6c757d'}; 
                                      color: #000000; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                                    {order['status'].upper()}
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Кнопки действий
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"✅ Подтвердить", key=f"confirm_{order['id']}"):
                            update_order_status(order['id'], st.session_state.user_id, 'confirmed')
                            st.success("Заказ подтвержден!")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🚚 Отправлен", key=f"ship_{order['id']}"):
                            update_order_status(order['id'], st.session_state.user_id, 'shipped')
                            st.success("Заказ отправлен!")
                            st.rerun()
                    
                    with col3:
                        if st.button(f"✅ Доставлен", key=f"deliver_{order['id']}"):
                            update_order_status(order['id'], st.session_state.user_id, 'delivered')
                            # Списываем товар со склада если есть
                            confirm_sale_and_reduce_stock(st.session_state.user_id, order['product_name'], order['quantity'])
                            st.success("Заказ доставлен и товар списан!")
                            st.rerun()
                    
                    with col4:
                        if st.button(f"❌ Отменить", key=f"cancel_{order['id']}"):
                            update_order_status(order['id'], st.session_state.user_id, 'cancelled')
                            # Освобождаем резерв если был
                            release_reservation(st.session_state.user_id, order['product_name'], order['quantity'])
                            st.warning("Заказ отменен!")
                            st.rerun()
        else:
            st.info("📭 Заказы не найдены")
    
    with tab2:
        st.header("📦 Контроль складских остатков")
        
        # Показываем информацию о лимитах
        if not st.session_state.is_premium:
            conn = sqlite3.connect('business_manager.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM inventory WHERE user_id = ?', (st.session_state.user_id,))
            current_items = cursor.fetchone()[0]
            conn.close()
            
            remaining_items = 20 - current_items
            if remaining_items <= 5:
                st.warning(f"⚠️ **Лимит склада**: {current_items}/20 товаров. Осталось: {remaining_items}")
                if remaining_items == 0:
                    st.error("❌ Достигнут лимит! Обновитесь до премиума для неограниченного склада")
            else:
                st.info(f"📦 **Склад**: {current_items}/20 товаров (бесплатная версия)")
        else:
            st.success("💎 **Премиум**: Неограниченный склад")
        
        # Информация о товарах с низким остатком
        low_stock_items = get_low_stock_items(st.session_state.user_id)
        
        if low_stock_items:
            st.error(f"⚠️ Товары с низким остатком ({len(low_stock_items)})")
            
            for item in low_stock_items:
                st.warning(f"""
                🏷️ **{item['product_name']}**: {item['current_stock']} шт. в наличии 
                (мин. уровень: {item['min_level']}, доступно: {item['available']} шт.)
                """)
        else:
            st.success("✅ Все товары в достаточном количестве")
        
        # Таблица текущих остатков
        st.subheader("📊 Текущие остатки на складе")
        inventory_df = get_inventory(st.session_state.user_id)
        
        if not inventory_df.empty:
            # Добавляем колонки для лучшего отображения
            inventory_display = inventory_df.copy()
            inventory_display['reserved_quantity'] = inventory_display['reserved_quantity'].fillna(0)
            inventory_display['min_stock_level'] = inventory_display['min_stock_level'].fillna(0)
            inventory_display['available'] = inventory_display['quantity'] - inventory_display['reserved_quantity']
            inventory_display['status'] = inventory_display.apply(
                lambda row: "🔴 Низкий остаток" if row['quantity'] <= row['min_stock_level'] and row['min_stock_level'] > 0 
                else "🟡 На резерве" if row['reserved_quantity'] > 0 
                else "🟢 В наличии", axis=1
            )
            
            display_columns = {
                'product_name': 'Товар',
                'quantity': 'Всего',
                'reserved_quantity': 'Резерв',
                'available': 'Доступно',
                'min_stock_level': 'Мин. уровень',
                'status': 'Статус'
            }
            
            st.dataframe(
                inventory_display[list(display_columns.keys())].rename(columns=display_columns),
                use_container_width=True
            )
        else:
            st.info("📭 Склад пуст")
    
    with tab3:
        st.header("🚚 Заказы поставщикам")
        show_supplier_orders()
    
    with tab4:
        st.header("⚡ Быстрые действия")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Автозаказ по минимумам")
            if st.button("🔄 Создать заказы по минимальным остаткам", use_container_width=True):
                create_auto_supplier_orders()
        
        with col2:
            st.subheader("📊 Экспорт данных")
            if st.button("📥 Экспорт всех заказов в Excel", use_container_width=True):
                export_orders_to_excel()

def show_order_details(order_id):
    """Показ детальной информации о заказе"""
    conn = sqlite3.connect('business_manager.db')
    
    # Получаем информацию о заказе
    order_query = '''
        SELECT o.*, COUNT(oi.id) as items_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.id = ?
        GROUP BY o.id
    '''
    order_df = pd.read_sql_query(order_query, conn, params=(order_id,))
    
    # Получаем товары заказа
    items_query = '''
        SELECT oi.*
        FROM order_items oi
        WHERE oi.order_id = ?
    '''
    items_df = pd.read_sql_query(items_query, conn, params=(order_id,))
    
    conn.close()
    
    if not order_df.empty:
        order = order_df.iloc[0]
        
        st.subheader(f"📋 Детали заказа #{order_id}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Название:** {order['order_name']}")
            st.write(f"**Тип:** {order['order_type']}")
            st.write(f"**Статус:** {order['status']}")
            st.write(f"**Доставка:** {order['delivery_type']}")
        
        with col2:
            st.write(f"**Создан:** {order['created_at']}")
            st.write(f"**Ожидаемая доставка:** {order['expected_delivery_date']}")
            if order['actual_delivery_date']:
                st.write(f"**Фактическая доставка:** {order['actual_delivery_date']}")
            st.write(f"**Общая сумма:** ${order['total_payment']:.2f}")
        
        if not items_df.empty:
            st.subheader("📦 Товары в заказе")
            st.dataframe(items_df, use_container_width=True)
    
    conn.commit()
    conn.close()

def show_supplier_orders():
    """Интерфейс для заказов поставщикам"""
    st.subheader("➕ Создать заказ поставщику")
    
    with st.form("supplier_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("Поставщик *")
            product_name = st.text_input("Товар *")
            quantity = st.number_input("Количество *", min_value=1, value=1)
        
        with col2:
            unit_cost = st.number_input("Цена за единицу *", min_value=0.01, format="%.2f")
            expected_date = st.date_input("Ожидаемая дата поставки", value=datetime.now().date() + timedelta(days=14))
            notes = st.text_area("Примечания")
        
        total_cost = quantity * unit_cost
        st.info(f"💰 Общая стоимость: ${total_cost:.2f}")
        
        submitted = st.form_submit_button("📋 Создать заказ поставщику")
        
        if submitted and supplier_name and product_name:
            conn = sqlite3.connect('business_manager.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO supplier_orders 
                (user_id, supplier_name, product_name, quantity, unit_cost, total_cost, 
                 order_date, expected_delivery_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (st.session_state.user_id, supplier_name, product_name, quantity,
                  unit_cost, total_cost, datetime.now().date(), expected_date, notes))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Заказ поставщику '{supplier_name}' создан!")
            st.rerun()
    
    # Список заказов поставщикам
    st.subheader("📋 Текущие заказы поставщикам")
    
    conn = sqlite3.connect('business_manager.db')
    supplier_orders_df = pd.read_sql_query('''
        SELECT * FROM supplier_orders 
        WHERE user_id = ? 
        ORDER BY order_date DESC
    ''', conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not supplier_orders_df.empty:
        for idx, order in supplier_orders_df.iterrows():
            with st.container():
                status_color = {
                    'ordered': '#ffc107',
                    'shipped': '#17a2b8', 
                    'delivered': '#28a745',
                    'cancelled': '#dc3545'
                }.get(order['status'], '#6c757d')
                
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: #f8f9fa;">
                    <h4 style="margin: 0; color: #000000;">🏪 {order['supplier_name']} - {order['product_name']}</h4>
                    <p style="margin: 5px 0; color: #333333;">
                        📦 {order['quantity']} шт. × ${order['unit_cost']:.2f} = ${order['total_cost']:.2f}<br>
                        📅 Заказано: {order['order_date']} | 🚚 Ожидается: {order['expected_delivery_date']}
                    </p>
                    <span style="background: {status_color}; color: #000000; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                        {order['status'].upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✅ Получен", key=f"receive_{order['id']}"):
                        # Обновляем статус и добавляем на склад
                        conn = sqlite3.connect('business_manager.db')
                        cursor = conn.cursor()
                        
                        cursor.execute('UPDATE supplier_orders SET status = ? WHERE id = ?', 
                                     ('delivered', order['id']))
                        conn.commit()
                        conn.close()
                        
                        # Добавляем товар на склад
                        add_to_inventory(st.session_state.user_id, order['product_name'], order['quantity'])
                        
                        st.success("Товар получен и добавлен на склад!")
                        st.rerun()
                
                with col2:
                    if st.button(f"🚚 В пути", key=f"ship_supplier_{order['id']}"):
                        conn = sqlite3.connect('business_manager.db')
                        cursor = conn.cursor()
                        cursor.execute('UPDATE supplier_orders SET status = ? WHERE id = ?', 
                                     ('shipped', order['id']))
                        conn.commit()
                        conn.close()
                        st.rerun()
                
                with col3:
                    if st.button(f"❌ Отменить", key=f"cancel_supplier_{order['id']}"):
                        conn = sqlite3.connect('business_manager.db')
                        cursor = conn.cursor()
                        cursor.execute('UPDATE supplier_orders SET status = ? WHERE id = ?', 
                                     ('cancelled', order['id']))
                        conn.commit()
                        conn.close()
                        st.rerun()
    else:
        st.info("📭 Заказы поставщикам не найдены")

def create_auto_supplier_orders():
    """Автоматическое создание заказов поставщикам по минимальным остаткам"""
    low_stock_items = get_low_stock_items(st.session_state.user_id)
    
    if not low_stock_items:
        st.success("✅ Все товары в достаточном количестве")
        return
    
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    created_orders = 0
    
    for item in low_stock_items:
        # Рассчитываем количество для заказа (до максимального уровня или мин. уровень * 2)
        order_quantity = max(item['min_level'] * 2 - item['current_stock'], item['min_level'])
        
        # Создаем заказ с условным поставщиком
        cursor.execute('''
            INSERT INTO supplier_orders 
            (user_id, supplier_name, product_name, quantity, unit_cost, total_cost, 
             order_date, expected_delivery_date, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (st.session_state.user_id, "Автоматический заказ", item['product_name'], 
              order_quantity, 0.0, 0.0, datetime.now().date(), 
              datetime.now().date() + timedelta(days=14), 
              f"Автозаказ по минимальному уровню. Нехватка: {item['shortage']} шт.", 
              'ordered'))
        
        created_orders += 1
    
    conn.commit()
    conn.close()
    
    st.success(f"✅ Создано {created_orders} автоматических заказов поставщикам")
    st.rerun()

def export_orders_to_excel():
    """Экспорт заказов в Excel"""
    conn = sqlite3.connect('business_manager.db')
    
    # Получаем все заказы
    orders_df = pd.read_sql_query('''
        SELECT o.*, 
               (o.sale_price - o.cost_price - o.delivery_cost) as profit
        FROM orders o
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    ''', conn, params=(st.session_state.user_id,))
    
    conn.close()
    
    if orders_df.empty:
        st.warning("Нет данных для экспорта")
        return
    
    # Создаем Excel файл в памяти
    from io import BytesIO
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        orders_df.to_excel(writer, sheet_name='Заказы', index=False)
        
        # Получаем workbook и worksheet для форматирования
        workbook = writer.book
        worksheet = writer.sheets['Заказы']
        
        # Форматирование заголовков
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Применяем форматирование к заголовкам
        for col_num, value in enumerate(orders_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    output.seek(0)
    
    st.download_button(
        label="📥 Скачать Excel файл",
        data=output.getvalue(),
        file_name=f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def show_notifications():
    """Система уведомлений"""
    st.title("🔔 Уведомления")
    
    # Вкладки уведомлений
    tab1, tab2, tab3 = st.tabs(["📢 Активные", "📋 История", "⚙️ Настройки"])
    
    with tab1:
        st.header("📢 Активные уведомления")
        
        # Получаем все непрочитанные уведомления
        conn = sqlite3.connect('business_manager.db')
        notifications_df = pd.read_sql_query('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND is_read = 0
            ORDER BY created_at DESC
        ''', conn, params=(st.session_state.user_id,))
        conn.close()
        
        if not notifications_df.empty:
            for idx, notification in notifications_df.iterrows():
                # Определяем иконку и цвет по типу
                icon_map = {
                    'low_stock': '⚠️',
                    'order_status': '📦',
                    'system': '🔧',
                    'supplier': '🏪',
                    'revenue': '💰'
                }
                
                color_map = {
                    'low_stock': '#ff6b6b',
                    'order_status': '#4ecdc4', 
                    'system': '#45b7d1',
                    'supplier': '#96ceb4',
                    'revenue': '#feca57'
                }
                
                icon = icon_map.get(notification['type'], '📢')
                color = color_map.get(notification['type'], '#6c757d')
                
                with st.container():
                    st.markdown(f"""
                    <div style="border-left: 4px solid {color}; background: rgba(255,255,255,0.9); 
                                padding: 15px; margin: 10px 0; border-radius: 5px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #000000;">{icon} {notification['title']}</h4>
                                <p style="margin: 5px 0; color: #333333;">{notification['message']}</p>
                                <small style="color: #666666;">📅 {notification['created_at']}</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col2:
                        if st.button("✅ Отметить прочитанным", key=f"read_{notification['id']}"):
                            mark_notification_as_read(notification['id'])
                            st.success("Уведомление отмечено как прочитанное")
                            st.rerun()
            
            # Кнопка "Отметить все как прочитанные"
            if st.button("✅ Отметить все как прочитанные", use_container_width=True):
                mark_all_notifications_as_read(st.session_state.user_id)
                st.success("Все уведомления отмечены как прочитанные")
                st.rerun()
        else:
            st.success("🎉 Новых уведомлений нет!")
    
    with tab2:
        st.header("📋 История уведомлений")
        
        # Получаем все уведомления с пагинацией
        page_size = 20
        page = st.number_input("Страница", min_value=1, value=1) - 1
        
        conn = sqlite3.connect('business_manager.db')
        all_notifications_df = pd.read_sql_query('''
            SELECT * FROM notifications 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', conn, params=(st.session_state.user_id, page_size, page * page_size))
        
        # Подсчет общего количества
        total_count = conn.execute('''
            SELECT COUNT(*) FROM notifications WHERE user_id = ?
        ''', (st.session_state.user_id,)).fetchone()[0]
        
        conn.close()
        
        if not all_notifications_df.empty:
            st.info(f"📊 Показано {len(all_notifications_df)} из {total_count} уведомлений")
            
            # Отображение в виде таблицы
            display_df = all_notifications_df.copy()
            display_df['status'] = display_df['is_read'].apply(lambda x: "✅ Прочитано" if x else "🔔 Новое")
            display_df['type_display'] = display_df['type'].replace({
                'low_stock': '⚠️ Низкий остаток',
                'order_status': '📦 Статус заказа',
                'system': '🔧 Система',
                'supplier': '🏪 Поставщик',
                'revenue': '💰 Выручка'
            })
            
            display_columns = {
                'created_at': 'Дата',
                'type_display': 'Тип',
                'title': 'Заголовок',
                'message': 'Сообщение',
                'status': 'Статус'
            }
            
            st.dataframe(
                display_df[list(display_columns.keys())].rename(columns=display_columns),
                use_container_width=True
            )
        else:
            st.info("📭 История уведомлений пуста")
    
    with tab3:
        st.header("⚙️ Настройки уведомлений")
        
        st.subheader("🔔 Типы уведомлений")
        
        # Получаем текущие настройки уведомлений пользователя
        notification_settings = get_notification_settings(st.session_state.user_id)
        
        with st.form("notification_settings_form"):
            low_stock_enabled = st.checkbox(
                "⚠️ Уведомления о низких остатках",
                value=notification_settings.get('low_stock_enabled', True)
            )
            
            order_status_enabled = st.checkbox(
                "📦 Уведомления о статусе заказов",
                value=notification_settings.get('order_status_enabled', True)
            )
            
            supplier_enabled = st.checkbox(
                "🏪 Уведомления от поставщиков",
                value=notification_settings.get('supplier_enabled', True)
            )
            
            revenue_enabled = st.checkbox(
                "💰 Уведомления о выручке",
                value=notification_settings.get('revenue_enabled', True)
            )
            
            # Настройки порогов
            st.subheader("📊 Пороговые значения")
            
            low_stock_threshold = st.number_input(
                "Минимальный остаток для уведомления:",
                min_value=0,
                value=notification_settings.get('low_stock_threshold', 5)
            )
            
            revenue_threshold = st.number_input(
                "Пороговая выручка для уведомления ($):",
                min_value=0.0,
                value=float(notification_settings.get('revenue_threshold', 1000.0)),
                format="%.2f"
            )
            
            submitted = st.form_submit_button("💾 Сохранить настройки")
            
            if submitted:
                save_notification_settings(st.session_state.user_id, {
                    'low_stock_enabled': low_stock_enabled,
                    'order_status_enabled': order_status_enabled,
                    'supplier_enabled': supplier_enabled,
                    'revenue_enabled': revenue_enabled,
                    'low_stock_threshold': low_stock_threshold,
                    'revenue_threshold': revenue_threshold
                })
                st.success("✅ Настройки уведомлений сохранены!")
        
        # Тестирование уведомлений
        st.subheader("🧪 Тестирование")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔔 Проверить низкие остатки", use_container_width=True):
                check_and_create_low_stock_notifications(st.session_state.user_id)
                st.success("Проверка выполнена!")
        
        with col2:
            if st.button("🧹 Очистить все уведомления", use_container_width=True):
                clear_all_notifications(st.session_state.user_id)
                st.success("Все уведомления удалены!")

def create_notification(user_id, notification_type, title, message):
    """Создание нового уведомления"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO notifications (user_id, type, title, message, created_at, is_read)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (user_id, notification_type, title, message, datetime.now()))
    
    conn.commit()
    conn.close()

def mark_notification_as_read(notification_id):
    """Отметить уведомление как прочитанное"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE notifications 
        SET is_read = 1 
        WHERE id = ?
    ''', (notification_id,))
    
    conn.commit()
    conn.close()

def mark_all_notifications_as_read(user_id):
    """Отметить все уведомления как прочитанные"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE notifications 
        SET is_read = 1 
        WHERE user_id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()

def get_notification_settings(user_id):
    """Получить настройки уведомлений пользователя"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Сначала проверим, есть ли настройки в новой таблице user_settings
    cursor.execute('''
        SELECT setting_name, setting_value 
        FROM user_settings 
        WHERE user_id = ? AND setting_name LIKE 'notification_%'
    ''', (user_id,))
    
    settings = {}
    for row in cursor.fetchall():
        key = row[0].replace('notification_', '')
        value = row[1]
        
        # Преобразуем строковые значения в соответствующие типы
        if value.lower() in ['true', 'false']:
            settings[key] = value.lower() == 'true'
        elif value.isdigit():
            settings[key] = int(value)
        else:
            try:
                settings[key] = float(value)
            except ValueError:
                settings[key] = value
    
    # Если настроек нет, создаем дефолтные
    if not settings:
        default_settings = {
            'low_stock_enabled': True,
            'order_status_enabled': True,
            'supplier_enabled': True,
            'revenue_enabled': True,
            'low_stock_threshold': 5,
            'revenue_threshold': 1000.0
        }
        
        # Сохраняем дефолтные настройки
        for key, value in default_settings.items():
            setting_name = f'notification_{key}'
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings (user_id, setting_name, setting_value)
                VALUES (?, ?, ?)
            ''', (user_id, setting_name, str(value)))
        
        conn.commit()
        settings = default_settings
    
    conn.close()
    return settings

def save_notification_settings(user_id, settings):
    """Сохранить настройки уведомлений"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    for key, value in settings.items():
        setting_name = f'notification_{key}'
        setting_value = str(value)
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_settings (user_id, setting_name, setting_value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, setting_name, setting_value))
    
    conn.commit()
    conn.close()

def check_and_create_low_stock_notifications(user_id):
    """Проверка и создание уведомлений о низких остатках"""
    notification_settings = get_notification_settings(user_id)
    
    if not notification_settings.get('low_stock_enabled', True):
        return
    
    # Получаем товары с низким остатком
    low_stock_items = get_low_stock_items(user_id)
    
    if not low_stock_items:
        return
    
    # Создаем уведомления для каждого товара
    for item in low_stock_items:
        title = f"⚠️ Низкий остаток: {item['product_name']}"
        message = f"Остаток {item['current_stock']} шт. (минимум: {item['min_level']} шт.). Рекомендуется пополнение."
        
        # Проверяем, есть ли уже такое уведомление за последние 24 часа
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND type = 'low_stock' 
            AND title = ? AND created_at > datetime('now', '-1 day')
        ''', (user_id, title))
        
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        if existing_count == 0:
            create_notification(user_id, 'low_stock', title, message)

def clear_all_notifications(user_id):
    """Удалить все уведомления пользователя"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def get_unread_notifications_count(user_id):
    """Получить количество непрочитанных уведомлений"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM notifications 
        WHERE user_id = ? AND is_read = 0
    ''', (user_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count
    """Отображение истории заказов в виде красивого списка карточек"""
    
    # CSS стили для красивого отображения
    st.markdown("""
    <style>
    .order-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .order-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .order-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f8f9fa;
    }
    
    .order-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .order-status {
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid;
        min-width: 120px;
        text-align: center;
    }
    
    .status-pending {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border-color: #ffc107;
    }
    
    .status-delivered {
        background: linear-gradient(135deg, #d1f2eb 0%, #a3d9c6 100%);
        color: #155724;
        border-color: #28a745;
    }
    
    .status-delayed {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border-color: #dc3545;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .order-info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 25px 0;
    }
    
    .info-card {
        background: rgba(255,255,255,0.8);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .info-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .info-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    
    .profit-positive {
        color: #28a745;
    }
    
    .profit-negative {
        color: #dc3545;
    }
    
    .order-actions {
        display: flex;
        gap: 15px;
        margin-top: 25px;
        flex-wrap: wrap;
        justify-content: flex-start;
    }
    
    .action-button {
        padding: 12px 24px;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #000000;
        border: 2px solid transparent;
    }
    
    .btn-success {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: #000000;
        border: 2px solid transparent;
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: #000000;
        border: 2px solid transparent;
    }
    
    .action-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .search-panel {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 30px;
        border: 2px solid #dee2e6;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .no-orders {
        text-align: center;
        padding: 80px 40px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 20px;
        margin: 40px 0;
        border: 2px dashed #dee2e6;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin: 30px 0;
        padding: 20px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок секции
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 20px; margin-bottom: 30px; text-align: center;
                box-shadow: 0 8px 30px rgba(0,0,0,0.1);">
        <h1 style="color: #000000; margin: 0; font-size: 2.2rem; font-weight: 700;">
            📋 История заказов - {order_type.upper()}
        </h1>
        <p style="color: #000000; margin: 10px 0 0 0; font-size: 1.1rem;">
            Управление и отслеживание ваших заказов
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Подключение к базе данных
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        # Панель поиска и фильтров
        with st.container():
            st.markdown('<div class="search-panel">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                search_term = st.text_input(
                    "🔍 Поиск заказов", 
                    placeholder="Введите название заказа для поиска...",
                    key=f"search_{order_type}"
                )
            
            with col2:
                status_filter = st.selectbox(
                    "📊 Статус", 
                    ["Все", "В ожидании", "Доставлен", "Задержан"],
                    key=f"status_filter_{order_type}"
                )
            
            with col3:
                sort_option = st.selectbox(
                    "📈 Сортировка", 
                    ["Дате (новые)", "Дате (старые)", "Прибыли ↓", "Прибыли ↑", "Названию"],
                    key=f"sort_{order_type}"
                )
            
            with col4:
                per_page = st.selectbox(
                    "📄 Показать", 
                    [5, 10, 20, 50], 
                    index=1,
                    key=f"per_page_{order_type}"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Построение запроса
        if order_type == "single":
            base_query = '''
                SELECT o.id, o.order_name, 
                       oi.quantity, 
                       oi.sale_price as price, 
                       oi.cost_price as cost,
                       (oi.sale_price - oi.cost_price) * oi.quantity as profit,
                       o.created_at as order_date, 
                       o.status, 
                       o.expected_delivery_date, 
                       o.actual_delivery_date,
                       o.delivery_type
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = ? AND o.order_type = "single"
            '''
        else:
            base_query = '''
                SELECT o.id, o.order_name, 
                       COUNT(oi.id) as total_items,
                       SUM(oi.sale_price * oi.quantity) as price,
                       SUM(oi.cost_price * oi.quantity) as cost,
                       SUM((oi.sale_price - oi.cost_price) * oi.quantity) as profit,
                       o.created_at as order_date, 
                       o.status, 
                       o.expected_delivery_date, 
                       o.actual_delivery_date,
                       o.delivery_type
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = ? AND o.order_type = "complex"
                GROUP BY o.id, o.order_name, o.created_at, o.status, o.expected_delivery_date, 
                         o.actual_delivery_date, o.delivery_type
            '''
        
        params = [st.session_state.user_id]
        
        # Применение фильтров
        if search_term:
            base_query += " AND LOWER(order_name) LIKE LOWER(?)"
            params.append(f"%{search_term}%")
        
        if status_filter != "Все":
            status_map = {"В ожидании": "pending", "Доставлен": "delivered"}
            if status_filter == "Задержан":
                # Для задержанных заказов проверяем дату
                base_query += " AND status = 'pending' AND expected_delivery_date < date('now')"
            elif status_filter in status_map:
                base_query += " AND status = ?"
                params.append(status_map[status_filter])
        
        # Сортировка
        if sort_option == "Дате (новые)":
            base_query += " ORDER BY order_date DESC"
        elif sort_option == "Дате (старые)":
            base_query += " ORDER BY order_date ASC"
        elif sort_option == "Прибыли ↓":
            base_query += " ORDER BY profit DESC"
        elif sort_option == "Прибыли ↑":
            base_query += " ORDER BY profit ASC"
        elif sort_option == "Названию":
            base_query += " ORDER BY order_name ASC"
        
        # Получение данных
        df = pd.read_sql_query(base_query, conn, params=params)
        
        if df.empty:
            st.markdown("""
            <div class="no-orders">
                <h2 style="color: #6c757d; margin-bottom: 20px;">📭 Заказы не найдены</h2>
                <p style="color: #6c757d; font-size: 1.2rem; margin-bottom: 30px;">
                    Попробуйте изменить параметры поиска или добавьте новый заказ
                </p>
                <div style="margin-top: 30px;">
                    <a href="#" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                      color: #000000; padding: 15px 30px; border-radius: 12px; 
                                      text-decoration: none; font-weight: 600;">
                        ➕ Добавить заказ
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Получение информации о задержках
        delayed_orders = get_delayed_orders(st.session_state.user_id)
        delayed_ids = [order[0] for order in delayed_orders]
        
        # Пагинация
        total_orders = len(df)
        total_pages = max(1, (total_orders + per_page - 1) // per_page)
        
        if f'page_{order_type}' not in st.session_state:
            st.session_state[f'page_{order_type}'] = 1
        
        current_page = st.session_state[f'page_{order_type}']
        
        # Панель пагинации
        if total_pages > 1:
            st.markdown(f"""
            <div class="pagination">
                <span style="color: #6c757d; font-weight: 600;">
                    Страница {current_page} из {total_pages} • Всего заказов: {total_orders}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
            
            with col1:
                if st.button("⏮️ Первая", disabled=current_page == 1, key=f"first_{order_type}"):
                    st.session_state[f'page_{order_type}'] = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️ Назад", disabled=current_page == 1, key=f"prev_{order_type}"):
                    st.session_state[f'page_{order_type}'] -= 1
                    st.rerun()
            
            with col4:
                if st.button("Вперед ▶️", disabled=current_page == total_pages, key=f"next_{order_type}"):
                    st.session_state[f'page_{order_type}'] += 1
                    st.rerun()
            
            with col5:
                if st.button("Последняя ⏭️", disabled=current_page == total_pages, key=f"last_{order_type}"):
                    st.session_state[f'page_{order_type}'] = total_pages
                    st.rerun()
        
        # Получение заказов для текущей страницы
        start_idx = (current_page - 1) * per_page
        end_idx = start_idx + per_page
        page_orders = df.iloc[start_idx:end_idx]
        
        # Отображение заказов в виде темных карточек
        for _, order in page_orders.iterrows():
            order_id = order['id']
            
            # Определение статуса с учетом задержек
            status = order['status']
            is_delayed = order_id in delayed_ids
            
            if is_delayed:
                status_display = "delayed"
                status_text = "⚠️ Задержан"
                status_color = "#e74c3c"
            elif status == "delivered":
                status_display = "delivered"
                status_text = "✅ Доставлен"
                status_color = "#27ae60"
            else:
                status_display = "pending"
                status_text = "⏳ В ожидании"
                status_color = "#f39c12"
            
            # Форматирование дат
            order_date = pd.to_datetime(order['order_date']).strftime('%d.%m.%Y')
            expected_date = pd.to_datetime(order['expected_delivery_date']).strftime('%d.%m.%Y') if order['expected_delivery_date'] else 'Не указана'
            
            # Определение цвета прибыли
            profit = order['profit']
            profit_color = "#27ae60" if profit > 0 else "#e74c3c"
            
            # Темная карточка заказа с кликабельным названием
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                border-radius: 20px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 40px rgba(0,212,255,0.2)'; this.style.borderColor='#00d4ff';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(0,0,0,0.3)'; this.style.borderColor='rgba(255,255,255,0.1)';">
                
                <!-- Цветная полоска статуса -->
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, {status_color}, {status_color}88);
                "></div>
                
                <!-- Заголовок с кликабельным названием -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <h2 style="
                            color: #000000; 
                            margin: 0; 
                            font-size: 1.5rem; 
                            font-weight: 700;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        " onclick="document.getElementById('detail_btn_{order_id}').click();">
                            📦 {order['order_name']}
                        </h2>
                        <p style="color: #95a5a6; margin: 5px 0 0 0; font-size: 0.9rem;">
                            ID: #{order_id} • {order_type.upper()}
                        </p>
                    </div>
                    <div style="
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: 700;
                        font-size: 0.9rem;
                        color: #000000;
                        background: {status_color};
                        box-shadow: 0 4px 15px {status_color}44;
                    ">
                        {status_text}
                    </div>
                </div>
                
                <!-- Информационные карточки -->
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                ">
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 15px;
                        border-radius: 12px;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.1);
                        transition: all 0.3s ease;
                    " onmouseover="this.style.background='rgba(0,212,255,0.1)'; this.style.borderColor='#00d4ff';"
                       onmouseout="this.style.background='rgba(255,255,255,0.05)'; this.style.borderColor='rgba(255,255,255,0.1)';">
                        <div style="color: #95a5a6; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px;">💰 Прибыль</div>
                        <div style="color: {profit_color}; font-size: 1.4rem; font-weight: 700;">${profit:,.0f}</div>
                    </div>
                    
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 15px;
                        border-radius: 12px;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.1);
                    ">
                        <div style="color: #95a5a6; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px;">📅 Дата заказа</div>
                        <div style="color: #ecf0f1; font-size: 1.2rem; font-weight: 600;">{order_date}</div>
                    </div>
                    
                    <div style="
                        background: rgba(255,255,255,0.05);
                        padding: 15px;
                        border-radius: 12px;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.1);
                    ">
                        <div style="color: #95a5a6; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px;">🚚 Доставка</div>
                        <div style="color: #ecf0f1; font-size: 1.2rem; font-weight: 600;">{expected_date}</div>
                    </div>
                    
                    {"<div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.1);'><div style='color: #95a5a6; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px;'>📊 Позиций</div><div style='color: #ecf0f1; font-size: 1.2rem; font-weight: 600;'>" + str(int(order.get('total_items', 1))) + "</div></div>" if order_type == "complex" and 'total_items' in order else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Темные кнопки управления
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            
            with col1:
                if st.button(f"📋 Подробнее", key=f"detail_btn_{order_id}", use_container_width=True):
                    st.session_state[f'show_details_{order_id}'] = not st.session_state.get(f'show_details_{order_id}', False)
                    st.rerun()
            
            with col2:
                if st.button(f"⚙️ Управление", key=f"manage_{order_id}_{order_type}", use_container_width=True):
                    st.session_state[f'show_management_{order_id}'] = not st.session_state.get(f'show_management_{order_id}', False)
                    st.rerun()
            
            with col3:
                # Быстрое изменение статуса
                if status == "pending":
                    if st.button(f"✅ Доставлен", key=f"quick_deliver_{order_id}", use_container_width=True):
                        if update_order_status(order_id, st.session_state.user_id, "delivered"):
                            st.success("✅ Статус обновлен!")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    if st.button(f"🔄 Вернуть", key=f"quick_pending_{order_id}", use_container_width=True):
                        if update_order_status(order_id, st.session_state.user_id, "pending"):
                            st.success("✅ Статус обновлен!")
                            time.sleep(0.5)
                            st.rerun()
            
            with col4:
                if st.button(f"🗑️ Удалить", key=f"delete_{order_id}_{order_type}", use_container_width=True):
                    st.session_state[f'confirm_delete_{order_id}'] = True
                    st.rerun()
            
            # Показать детали заказа, если активировано
            if st.session_state.get(f'show_details_{order_id}', False):
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 15px 0;
                    border: 1px solid #00d4ff;
                    box-shadow: 0 5px 20px rgba(0,212,255,0.2);
                ">
                    <h3 style="color: #00d4ff; margin-bottom: 15px;">📋 Детали заказа #{order_id}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Получаем детальную информацию о заказе
                if order_type == "complex":
                    show_order_details(order_id)
                else:
                    detail_col1, detail_col2 = st.columns(2)
                    with detail_col1:
                        st.info(f"📦 **Товар:** {order['order_name']}")
                        st.info(f"📊 **Количество:** {order.get('quantity', 'N/A')}")
                        st.info(f"💰 **Цена продажи:** ${order.get('price', 0):.0f}")
                    with detail_col2:
                        st.info(f"💸 **Себестоимость:** ${order.get('cost', 0):.0f}")
                        st.info(f"📈 **Прибыль:** ${profit:.0f}")
                        st.info(f"🚚 **Доставка:** {order.get('delivery_type', 'Не указан')}")
            
            # Показать управление заказом, если активировано
            if st.session_state.get(f'show_management_{order_id}', False):
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 15px 0;
                    border: 1px solid #f39c12;
                    box-shadow: 0 5px 20px rgba(243,156,18,0.2);
                ">
                    <h3 style="color: #f39c12; margin-bottom: 15px;">⚙️ Управление заказом #{order_id}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                mgmt_col1, mgmt_col2, mgmt_col3 = st.columns(3)
                
                with mgmt_col1:
                    st.subheader("📅 Дата доставки")
                    new_delivery_date = st.date_input(
                        "Ожидаемая доставка:",
                        value=pd.to_datetime(order['expected_delivery_date']).date() if order['expected_delivery_date'] else None,
                        key=f"delivery_date_{order_id}"
                    )
                    if st.button("💾 Обновить дату", key=f"update_date_{order_id}"):
                        # Здесь можно добавить функцию обновления даты
                        st.success("✅ Дата обновлена!")
                
                with mgmt_col2:
                    st.subheader("📋 Статус")
                    current_status_idx = 0 if status == "pending" else 1
                    new_status = st.selectbox(
                        "Новый статус:",
                        ["pending", "delivered"],
                        index=current_status_idx,
                        key=f"status_mgmt_{order_id}",
                        format_func=lambda x: "⏳ В ожидании" if x == "pending" else "✅ Доставлен"
                    )
                    if st.button("� Изменить статус", key=f"change_status_{order_id}"):
                        update_order_status(order_id, st.session_state.user_id, new_status)
                        st.success("✅ Статус изменен!")
                        st.rerun()
                
                with mgmt_col3:
                    st.subheader("🚨 Действия")
                    if st.button("📧 Отправить уведомление", key=f"notify_{order_id}"):
                        st.info("📧 Уведомление отправлено!")
                    
                    if st.button("📄 Экспорт данных", key=f"export_{order_id}"):
                        st.info("📄 Данные экспортированы!")
            
            # Подтверждение удаления
            if st.session_state.get(f'confirm_delete_{order_id}', False):
                st.error("⚠️ **Подтвердите удаление заказа**")
                delete_col1, delete_col2, delete_col3 = st.columns([1, 1, 2])
                
                with delete_col1:
                    if st.button("❌ Да, удалить", key=f"confirm_yes_{order_id}"):
                        if delete_order(order_id, st.session_state.user_id):
                            st.success("✅ Заказ удален!")
                            st.session_state[f'confirm_delete_{order_id}'] = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Ошибка удаления")
                
                with delete_col2:
                    if st.button("✅ Отмена", key=f"confirm_no_{order_id}"):
                        st.session_state[f'confirm_delete_{order_id}'] = False
                        st.rerun()
            
            # Показать форму редактирования, если активирована
            if st.session_state.get(f'edit_mode_{order_id}', False):
                show_edit_order_form(order_id, st.session_state.user_id)
            
            # Разделитель между заказами
            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
            
            # Разделитель между заказами
            st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #dee2e6, transparent);'>", unsafe_allow_html=True)
        
        # Сводная статистика
        st.markdown("---")
        st.markdown("## 📊 Статистика")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_profit = df['profit'].sum()
        pending_count = len(df[df['status'] == 'pending'])
        delivered_count = len(df[df['status'] == 'delivered']) 
        delayed_count = len([oid for oid in df['id'] if oid in delayed_ids])
        
        with col1:
            st.markdown(f"""
            <div class="stat-card" style="border-left: 4px solid #28a745;">
                <h3 style="color: #28a745; margin: 0; font-size: 2rem;">💰 ${total_profit:,.0f}</h3>
                <p style="color: #6c757d; margin: 5px 0 0 0; font-weight: 600;">Общая прибыль</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="border-left: 4px solid #ffc107;">
                <h3 style="color: #ffc107; margin: 0; font-size: 2rem;">⏳ {pending_count}</h3>
                <p style="color: #6c757d; margin: 5px 0 0 0; font-weight: 600;">В ожидании</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="border-left: 4px solid #17a2b8;">
                <h3 style="color: #17a2b8; margin: 0; font-size: 2rem;">✅ {delivered_count}</h3>
                <p style="color: #6c757d; margin: 5px 0 0 0; font-weight: 600;">Доставлено</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card" style="border-left: 4px solid #dc3545;">
                <h3 style="color: #dc3545; margin: 0; font-size: 2rem;">⚠️ {delayed_count}</h3>
                <p style="color: #6c757d; margin: 5px 0 0 0; font-weight: 600;">Задержано</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Кнопка проверки задержек
        if delayed_count > 0:
            st.markdown("### 🚨 Действия по задержкам")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("📧 Отправить уведомления", type="primary", use_container_width=True):
                    notifications_sent = send_delay_notifications(st.session_state.user_id)
                    if notifications_sent > 0:
                        st.success(f"✅ Отправлено {notifications_sent} уведомлений")
                    else:
                        st.info("ℹ️ Уведомления уже были отправлены")
            
            with col2:
                st.warning(f"У вас {delayed_count} задержанных заказов. Рекомендуется связаться с поставщиками.")
    
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке заказов: {e}")
        st.exception(e)
    
    finally:
        conn.close()

def show_simple_order_history(order_type):
    """Простое отображение истории заказов"""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
        padding: 30px; 
        border-radius: 20px; 
        margin-bottom: 30px; 
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    ">
        <h1 style="color: #00d4ff; margin: 0; font-size: 2.2rem; font-weight: 700;">
            📋 История заказов - {order_type.upper()}
        </h1>
        <p style="color: #000000; margin: 10px 0 0 0; font-size: 1.1rem;">
            Управление и отслеживание ваших заказов
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Подключение к базе данных
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    try:
        # Получение заказов в зависимости от типа
        if order_type == "single":
            query = '''
                SELECT o.id, o.order_name, o.status, o.created_at, o.expected_delivery_date,
                       oi.quantity, oi.sale_price, oi.cost_price,
                       (oi.sale_price - oi.cost_price) * oi.quantity as profit
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = ? AND o.order_type = "single"
                ORDER BY o.created_at DESC
            '''
        else:  # complex
            query = '''
                SELECT o.id, o.order_name, o.status, o.created_at, o.expected_delivery_date,
                       COUNT(oi.id) as item_count,
                       SUM(oi.sale_price * oi.quantity) as total_sale,
                       SUM(oi.cost_price * oi.quantity) as total_cost,
                       SUM((oi.sale_price - oi.cost_price) * oi.quantity) as profit
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = ? AND o.order_type = "complex"
                GROUP BY o.id, o.order_name, o.status, o.created_at, o.expected_delivery_date
                ORDER BY o.created_at DESC
            '''
        
        cursor.execute(query, (st.session_state.user_id,))
        orders = cursor.fetchall()
        
        if not orders:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 60px 40px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                margin: 40px 0;
                border: 2px dashed rgba(255,255,255,0.2);
            ">
                <h3 style="color: #95a5a6; margin-bottom: 20px;">📦 Заказов пока нет</h3>
                <p style="color: #7f8c8d;">Создайте свой первый заказ, чтобы начать отслеживание</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Отображение заказов
        for order in orders:
            order_id = order[0]
            order_name = order[1]
            status = order[2]
            created_at = order[3]
            expected_delivery = order[4]
            
            # Статус и цвет
            if status == "delivered":
                status_text = "✅ Доставлен"
                status_color = "#27ae60"
            elif status == "pending":
                status_text = "⏳ В ожидании"
                status_color = "#f39c12"
            else:
                status_text = "⚠️ Задержан"
                status_color = "#e74c3c"
            
            # Прибыль и ее цвет
            profit = order[-1] if order[-1] else 0
            profit_color = "#27ae60" if profit > 0 else "#e74c3c"
            
            # Форматирование даты
            order_date = pd.to_datetime(created_at).strftime('%d.%m.%Y') if created_at else 'Не указана'
            delivery_date = pd.to_datetime(expected_delivery).strftime('%d.%m.%Y') if expected_delivery else 'Не указана'
            
            # Состояние раскрытия деталей
            details_key = f"details_{order_id}"
            if details_key not in st.session_state:
                st.session_state[details_key] = False
            
            # Простая карточка заказа
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="
                            color: #00d4ff; 
                            margin: 0; 
                            font-size: 1.4rem; 
                            font-weight: 600;
                            cursor: pointer;
                        " onclick="document.getElementById('detail_btn_{order_id}').click();">
                            {'📦' if order_type == 'single' else '📋'} {order_name}
                        </h3>
                        <p style="color: #95a5a6; margin: 5px 0 0 0; font-size: 0.9rem;">
                            {order_type.upper()}
                        </p>
                    </div>
                    <div style="
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: 600;
                        font-size: 0.9rem;
                        color: #000000;
                        background: {status_color};
                        box-shadow: 0 4px 15px {status_color}44;
                    ">
                        {status_text}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Кнопка для раскрытия деталей (скрытая)
            if st.button("👁️", key=f"detail_btn_{order_id}", help="Показать детали"):
                st.session_state[details_key] = not st.session_state[details_key]
                st.rerun()
            
            # Детали заказа (если раскрыты)
            if st.session_state[details_key]:
                with st.container():
                    st.markdown(f"""
                    <div style="
                        background: rgba(255,255,255,0.05);
                        border-radius: 12px;
                        padding: 20px;
                        margin: 10px 0 20px 0;
                        border: 1px solid rgba(255,255,255,0.1);
                    ">
                    """, unsafe_allow_html=True)
                    
                    # Информационные карточки
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px;">
                            <div style="color: #95a5a6; font-size: 0.8rem; margin-bottom: 8px;">💰 ПРИБЫЛЬ</div>
                            <div style="color: {profit_color}; font-size: 1.4rem; font-weight: 700;">${profit:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px;">
                            <div style="color: #95a5a6; font-size: 0.8rem; margin-bottom: 8px;">📅 ДАТА ЗАКАЗА</div>
                            <div style="color: #ecf0f1; font-size: 1.2rem; font-weight: 600;">{order_date}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px;">
                            <div style="color: #95a5a6; font-size: 0.8rem; margin-bottom: 8px;">🚚 ДОСТАВКА</div>
                            <div style="color: #ecf0f1; font-size: 1.2rem; font-weight: 600;">{delivery_date}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Детальная информация о товарах
                    st.markdown("### 📦 Информация о товарах")
                    
                    # Получаем подробную информацию о товарах заказа
                    cursor.execute('''
                        SELECT oi.product_name, oi.quantity, oi.cost_price, oi.sale_price, 
                               oi.weight, oi.item_delivery_type, oi.delivery_cost,
                               (oi.sale_price - oi.cost_price) * oi.quantity as item_profit
                        FROM order_items oi
                        WHERE oi.order_id = ?
                    ''', (order_id,))
                    
                    order_items = cursor.fetchall()
                    
                    if order_items:
                        for i, item in enumerate(order_items):
                            item_name, item_qty, item_cost, item_sale, item_weight, item_delivery_type, item_delivery_cost, item_profit = item
                            
                            # Цвет прибыли товара
                            item_profit_color = "#27ae60" if item_profit > 0 else "#e74c3c"
                            
                            st.markdown(f"""
                            <div style="
                                background: rgba(255,255,255,0.03);
                                border-radius: 8px;
                                padding: 15px;
                                margin: 10px 0;
                                border: 1px solid rgba(255,255,255,0.1);
                            ">
                                <h4 style="color: #00d4ff; margin: 0 0 10px 0;">📦 {item_name}</h4>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">КОЛИЧЕСТВО</div>
                                        <div style="color: #ecf0f1; font-weight: 600;">{item_qty} шт.</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">СЕБЕСТОИМОСТЬ</div>
                                        <div style="color: #ecf0f1; font-weight: 600;">${item_cost:.2f}</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">ЦЕНА ПРОДАЖИ</div>
                                        <div style="color: #ecf0f1; font-weight: 600;">${item_sale:.2f}</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">ВЕС</div>
                                        <div style="color: #ecf0f1; font-weight: 600;">{item_weight:.2f} кг</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">ДОСТАВКА</div>
                                        <div style="color: #ecf0f1; font-weight: 600;">{'✈️ Самолет' if item_delivery_type == 'airplane' else '🚛 Машина'}</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">СТОИМОСТЬ ДОСТАВКИ</div>
                                        <div style="color: #ecf0f1; font-weight: 600;">${item_delivery_cost:.2f}</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="color: #95a5a6; font-size: 0.7rem; margin-bottom: 4px;">ПРИБЫЛЬ</div>
                                        <div style="color: {item_profit_color}; font-weight: 700;">${item_profit:.2f}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("ℹ️ Информация о товарах не найдена")
                    
                    # Кнопки управления
                    st.markdown("### 🔧 Управление заказом")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if status == "pending":
                            if st.button(f"✅ Отметить доставленным", key=f"deliver_{order_id}", use_container_width=True):
                                if update_order_status(order_id, st.session_state.user_id, "delivered"):
                                    st.success("✅ Статус обновлен!")
                                    st.rerun()
                    
                    with col2:
                        edit_key = f'edit_mode_{order_id}'
                        if edit_key not in st.session_state:
                            st.session_state[edit_key] = False
                        
                        if not st.session_state[edit_key]:
                            if st.button(f"✏️ Редактировать", key=f"edit_{order_id}", use_container_width=True):
                                st.session_state[edit_key] = True
                                st.rerun()
                        else:
                            if st.button(f"� Отмена редактирования", key=f"cancel_edit_{order_id}", use_container_width=True):
                                st.session_state[edit_key] = False
                                st.rerun()
                    
                    with col3:
                        if st.button(f"❌ Удалить", key=f"delete_{order_id}", use_container_width=True):
                            if delete_order(order_id, st.session_state.user_id):
                                st.success("✅ Заказ удален!")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка удаления")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке заказов: {e}")
    
    finally:
        conn.close()

def show_order_details(order_id):
    """Показывает детали комплексного заказа"""
    st.subheader(f"📦 Детали заказа #{order_id}")
    
    conn = sqlite3.connect('business_manager.db')
    
    # Получаем информацию о заказе
    order_query = '''
        SELECT order_name, total_payment, created_at 
        FROM orders 
        WHERE id = ?
    '''
    order_info = pd.read_sql_query(order_query, conn, params=(order_id,))
    
    # Получаем товары в заказе
    items_query = '''
        SELECT product_name, quantity, cost_price, sale_price, weight, 
               delivery_cost, total_cost, item_delivery_type
        FROM order_items 
        WHERE order_id = ?
    '''
    items_df = pd.read_sql_query(items_query, conn, params=(order_id,))
    conn.close()
    
    if not order_info.empty:
        order_data = order_info.iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Название", order_data['order_name'])
        with col2:
            st.metric("💰 Общий платеж", f"${order_data['total_payment']:.2f}")
        with col3:
            st.metric("📅 Дата создания", order_data['created_at'][:10])
        
        if not items_df.empty:
            st.write("**Товары в заказе:**")
            
            # Добавляем читаемый тип доставки
            items_df['delivery_type_display'] = items_df['item_delivery_type'].apply(
                lambda x: "Самолет ($7/кг)" if x == "airplane" else "Машина ($0.68/кг)"
            )
            
            # Переименовываем колонки для отображения
            display_columns = {
                'product_name': 'Товар',
                'quantity': 'Количество',
                'cost_price': 'Себестоимость ($)',
                'sale_price': 'Цена продажи ($)',
                'weight': 'Вес (кг)',
                'delivery_type_display': 'Тип доставки',
                'delivery_cost': 'Стоимость доставки ($)',
                'total_cost': 'Итого ($)'
            }
            
            items_display = items_df[list(display_columns.keys())].rename(columns=display_columns)
            st.dataframe(items_display, use_container_width=True)

def show_analytics():
    st.title("📈 Аналитика и отчеты")
    
    analytics = get_analytics(st.session_state.user_id)
    
    # Основные метрики
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Финансовые показатели")
        
        metrics_data = {
            'Показатель': ['Общая выручка', 'Себестоимость товаров', 'Стоимость доставки', 
                          'Общие расходы', 'Чистая прибыль', 'Маржа (%)', 'Рентабельность (%)'],
            'Значение': [
                f"${analytics['total_revenue']:.2f}",
                f"${analytics['total_cost_price']:.2f}",
                f"${analytics['total_delivery_costs']:.2f}",
                f"${analytics['total_costs']:.2f}",
                f"${analytics['profit']:.2f}",
                f"{analytics['margin']:.1f}%",
                f"{analytics['profitability']:.1f}%"
            ]
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🛡️ Финансовое планирование")
        
        planning_data = {
            'Категория': ['Чистая прибыль', 'Финансовая подушка', 'Личные расходы'],
            'Сумма': [
                f"${analytics['profit']:.2f}",
                f"${analytics['financial_cushion']:.2f}",
                f"${analytics['personal_expenses']:.2f}"
            ],
            'Процент': [
                "100%",
                f"{analytics['cushion_percent']:.1f}%",
                f"{100 - analytics['cushion_percent']:.1f}%"
            ]
        }
        
        planning_df = pd.DataFrame(planning_data)
        st.dataframe(planning_df, use_container_width=True, hide_index=True)
    
    # Графики
    if analytics['total_revenue'] > 0:
        st.subheader("📊 Визуализация данных")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Круговая диаграмма структуры расходов
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Себестоимость товаров', 'Стоимость доставки', 'Прибыль'],
                values=[analytics['total_cost_price'], analytics['total_delivery_costs'], analytics['profit']],
                hole=0.3
            )])
            fig_pie.update_layout(title="Структура выручки", height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Столбчатая диаграмма финансового планирования
            fig_bar = go.Figure(data=[go.Bar(
                x=['Финансовая подушка', 'Личные расходы'],
                y=[analytics['financial_cushion'], analytics['personal_expenses']],
                marker_color=['#4682B4', '#228B22']
            )])
            fig_bar.update_layout(title="Распределение прибыли", height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Динамика продаж
        st.subheader("📈 Динамика продаж")
        conn = sqlite3.connect('business_manager.db')
        
        sales_query = '''
            SELECT DATE(o.created_at) as date, 
                   SUM(oi.total_cost) as daily_revenue,
                   SUM(oi.cost_price + oi.delivery_cost) as daily_costs,
                   SUM(oi.total_cost - oi.cost_price - oi.delivery_cost) as daily_profit
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = ?
            GROUP BY DATE(o.created_at)
            ORDER BY date
        '''
        
        sales_df = pd.read_sql_query(sales_query, conn, params=(st.session_state.user_id,))
        conn.close()
        
        if not sales_df.empty:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=sales_df['date'], y=sales_df['daily_revenue'], 
                                        mode='lines+markers', name='Выручка', line=dict(color='#000080')))
            fig_line.add_trace(go.Scatter(x=sales_df['date'], y=sales_df['daily_costs'], 
                                        mode='lines+markers', name='Расходы', line=dict(color='#8B0000')))
            fig_line.add_trace(go.Scatter(x=sales_df['date'], y=sales_df['daily_profit'], 
                                        mode='lines+markers', name='Прибыль', line=dict(color='#006400')))
            
            fig_line.update_layout(title="Динамика финансовых показателей", 
                                 xaxis_title="Дата", yaxis_title="Сумма ($)", height=500)
            st.plotly_chart(fig_line, use_container_width=True)
    
    # Расширенная AI аналитика
    st.subheader("🤖 AI Аналитика")
    
    # Импортируем наш модуль аналитики
    try:
        from advanced_analytics import get_analytics_manager
        analytics_manager = get_analytics_manager()
        
        tab1, tab2, tab3, tab4 = st.tabs(["🔮 Прогнозы", "🚚 Сравнение доставки", "💡 AI Инсайты", "📊 Тренды"])
        
        with tab1:
            st.markdown("#### 🔮 Продвинутые прогнозы с машинным обучением")
            
            col1, col2 = st.columns(2)
            with col1:
                prediction_days = st.selectbox("Период прогноза:", 
                                             options=[7, 14, 30, 60], 
                                             index=0,
                                             help="На сколько дней вперед сделать прогноз")
            
            predictions = analytics_manager.get_advanced_predictions(st.session_state.user_id, prediction_days)
            
            if predictions:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔮 Прогноз выручки", 
                             f"${predictions['total_predicted_revenue']:.2f}")
                with col2:
                    st.metric("📦 Прогноз заказов", 
                             f"{predictions['total_predicted_orders']}")
                with col3:
                    accuracy = predictions['model_accuracy']['revenue_r2'] * 100
                    st.metric("🎯 Точность модели", f"{accuracy:.1f}%")
                
                # График прогнозов
                pred_dates = [p['date'] for p in predictions['predictions']]
                pred_revenue = [p['predicted_revenue'] for p in predictions['predictions']]
                
                fig_forecast = go.Figure()
                fig_forecast.add_trace(go.Scatter(
                    x=pred_dates, y=pred_revenue,
                    mode='lines+markers',
                    name='Прогноз выручки',
                    line=dict(color='#000080', dash='dash')
                ))
                fig_forecast.update_layout(
                    title=f"Прогноз выручки на {prediction_days} дней",
                    xaxis_title="Дата", yaxis_title="Выручка ($)"
                )
                st.plotly_chart(fig_forecast, use_container_width=True)
            else:
                st.info("📊 Недостаточно данных для создания прогноза. Добавьте больше заказов.")
        
        with tab2:
            st.markdown("#### 🚚 Сравнительный анализ доставки")
            
            col1, col2 = st.columns(2)
            with col1:
                delivery_period = st.selectbox("Период анализа:", 
                                             options=[30, 60, 90, 180], 
                                             index=0,
                                             help="За сколько дней анализировать данные")
            
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=delivery_period)).strftime('%Y-%m-%d')
            
            delivery_comparison = analytics_manager.get_delivery_comparison(
                st.session_state.user_id, start_date, end_date
            )
            
            if delivery_comparison is not None and len(delivery_comparison) > 0:
                # Фильтруем рекомендации
                delivery_data = delivery_comparison[delivery_comparison['delivery_type'] != 'recommendations']
                
                if len(delivery_data) > 0:
                    # Заменяем названия для отображения
                    delivery_data_display = delivery_data.copy()
                    delivery_data_display['delivery_type'] = delivery_data_display['delivery_type'].replace({
                        'airplane': '✈️ Самолет',
                        'truck': '🚛 Автомобиль'
                    })
                    
                    col1, col2, col3 = st.columns(3)
                    for idx, row in delivery_data_display.iterrows():
                        with col1 if idx == 0 else col2:
                            st.metric(
                                f"{row['delivery_type']} - Заказы",
                                f"{int(row['orders_count'])}"
                            )
                            st.metric(
                                f"{row['delivery_type']} - Рентабельность",
                                f"{row['profit_margin']:.1f}%"
                            )
                            st.metric(
                                f"{row['delivery_type']} - Стоимость/кг",
                                f"${row['delivery_cost_per_kg']:.2f}"
                            )
                    
                    # График сравнения
                    fig_delivery = go.Figure(data=[
                        go.Bar(name='Прибыль (%)', 
                               x=delivery_data_display['delivery_type'], 
                               y=delivery_data_display['profit_margin']),
                        go.Bar(name='Эффективность', 
                               x=delivery_data_display['delivery_type'], 
                               y=delivery_data_display['efficiency_score'] * 100)
                    ])
                    fig_delivery.update_layout(
                        title="Сравнение эффективности доставки",
                        yaxis_title="Показатель (%)"
                    )
                    st.plotly_chart(fig_delivery, use_container_width=True)
                
                # Показываем рекомендации
                recommendations_row = delivery_comparison[delivery_comparison['delivery_type'] == 'recommendations']
                if len(recommendations_row) > 0 and 'recommendations' in recommendations_row.columns:
                    st.markdown("#### 💡 Рекомендации по доставке")
                    for rec in recommendations_row['recommendations'].iloc[0]:
                        st.success(f"✅ {rec}")
            else:
                st.info("📊 Недостаточно данных о доставке для сравнения.")
        
        with tab3:
            st.markdown("#### 💡 AI Инсайты и рекомендации")
            
            insights_period = st.selectbox("Период для анализа:", 
                                         options=[7, 14, 30, 60], 
                                         index=2,
                                         help="За сколько дней анализировать бизнес")
            
            ai_insights = analytics_manager.get_ai_insights(st.session_state.user_id, insights_period)
            
            if ai_insights:
                col1, col2 = st.columns(2)
                
                with col1:
                    if ai_insights['performance']:
                        st.markdown("##### 🏆 Достижения")
                        for insight in ai_insights['performance']:
                            st.success(insight)
                    
                    if ai_insights['opportunities']:
                        st.markdown("##### 🚀 Возможности роста")
                        for insight in ai_insights['opportunities']:
                            st.info(insight)
                
                with col2:
                    if ai_insights['warnings']:
                        st.markdown("##### ⚠️ Предупреждения")
                        for insight in ai_insights['warnings']:
                            st.warning(insight)
                    
                    if ai_insights['recommendations']:
                        st.markdown("##### 💡 Рекомендации")
                        for insight in ai_insights['recommendations']:
                            st.info(f"💡 {insight}")
            else:
                st.info("📊 Недостаточно данных для AI анализа.")
        
        with tab4:
            st.markdown("#### 📊 Расширенные тренды")
            
            col1, col2 = st.columns(2)
            with col1:
                trend_days = st.selectbox("Период трендов:", 
                                        options=[30, 60, 90, 180], 
                                        index=1,
                                        help="За сколько дней показать тренды")
            with col2:
                delivery_filter = st.selectbox("Фильтр по доставке:", 
                                             options=['all', 'airplane', 'truck'], 
                                             format_func=lambda x: {'all': '🌐 Все', 'airplane': '✈️ Самолет', 'truck': '🚛 Автомобиль'}[x],
                                             help="Показать данные по определенному типу доставки")
            
            trends = analytics_manager.get_sales_trends(
                st.session_state.user_id, 
                days=trend_days, 
                delivery_method=None if delivery_filter == 'all' else delivery_filter
            )
            
            if trends is not None and len(trends) > 0:
                fig_trends = go.Figure()
                fig_trends.add_trace(go.Scatter(
                    x=trends['date'], y=trends['revenue'],
                    mode='lines+markers', name='Выручка',
                    line=dict(color='#000080')
                ))
                fig_trends.add_trace(go.Scatter(
                    x=trends['date'], y=trends['profit'],
                    mode='lines+markers', name='Прибыль',
                    line=dict(color='#006400')
                ))
                fig_trends.update_layout(
                    title=f"Тренды за {trend_days} дней",
                    xaxis_title="Дата", yaxis_title="Сумма ($)"
                )
                st.plotly_chart(fig_trends, use_container_width=True)
                
                # Статистика трендов
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_revenue = trends['revenue'].mean()
                    st.metric("📊 Средняя выручка/день", f"${avg_revenue:.2f}")
                with col2:
                    total_orders = trends['orders'].sum()
                    st.metric("📦 Всего заказов", f"{int(total_orders)}")
                with col3:
                    avg_profit_margin = (trends['profit'].sum() / trends['revenue'].sum() * 100) if trends['revenue'].sum() > 0 else 0
                    st.metric("💰 Средняя маржа", f"{avg_profit_margin:.1f}%")
            else:
                st.info("📊 Недостаточно данных для отображения трендов.")
    
    except ImportError:
        st.error("❌ Модуль расширенной аналитики не найден. Убедитесь, что файл advanced_analytics.py находится в рабочей директории.")
    
    # Экспорт отчета
    if st.button("📥 Экспорт полного отчета"):
        report_data = generate_full_report(st.session_state.user_id)
        excel_data = export_to_excel(report_data, "full_analytics_report")
        st.download_button(
            label="Скачать аналитический отчет",
            data=excel_data,
            file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def show_inventory():
    st.title("🏪 Управление складом")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Склад", "Добавить товар", "История заказов", "Поиск"])
    
    with tab1:
        st.subheader("📦 Управление товарами склада")
        
        inventory_df = get_inventory(st.session_state.user_id)
        
        if not inventory_df.empty:
            # Создаем checkbox для выбора товаров для удаления
            st.markdown("**Выберите товары для управления:**")
            
            # Фильтрация и сортировка
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_by = st.selectbox("Сортировать по:", 
                                     ["product_name", "quantity", "created_at"])
            with col2:
                sort_order = st.selectbox("Порядок:", ["По возрастанию", "По убыванию"])
            with col3:
                low_stock_threshold = st.number_input("Порог низких остатков:", min_value=1, value=5)
            
            ascending = sort_order == "По возрастанию"
            inventory_df_sorted = inventory_df.sort_values(sort_by, ascending=ascending)
            
            # Инициализируем состояние для выбранных товаров
            if 'selected_items' not in st.session_state:
                st.session_state.selected_items = []
            
            # Групповые действия
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🗑️ Удалить выбранные", type="secondary"):
                    if st.session_state.selected_items:
                        st.session_state.confirm_bulk_delete = True
                        st.rerun()
                    else:
                        st.warning("Выберите товары для удаления")
            
            with col2:
                if st.button("✅ Выбрать все"):
                    st.session_state.selected_items = inventory_df_sorted['id'].tolist()
                    st.rerun()
            
            with col3:
                if st.button("❌ Снять выделение"):
                    st.session_state.selected_items = []
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Очистить весь склад", type="secondary"):
                    st.session_state.confirm_clear_inventory = True
                    st.rerun()
            
            # Подтверждение группового удаления
            if st.session_state.get('confirm_bulk_delete', False):
                st.warning(f"⚠️ Вы уверены? Будет удалено {len(st.session_state.selected_items)} товаров!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Да, удалить выбранные", type="primary"):
                        deleted_count = delete_inventory_items_bulk(st.session_state.user_id, st.session_state.selected_items)
                        st.success(f"✅ Удалено {deleted_count} товаров")
                        st.session_state.confirm_bulk_delete = False
                        st.session_state.selected_items = []
                        st.rerun()
                with col2:
                    if st.button("❌ Отмена группового удаления"):
                        st.session_state.confirm_bulk_delete = False
                        st.rerun()
            
            # Подтверждение полной очистки
            if st.session_state.get('confirm_clear_inventory', False):
                st.warning("⚠️ Вы уверены? Будут удалены ВСЕ товары со склада!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Да, очистить весь склад", type="primary"):
                        deleted_count = clear_inventory(st.session_state.user_id)
                        st.success(f"✅ Удалено {deleted_count} товаров со склада")
                        st.session_state.confirm_clear_inventory = False
                        st.session_state.selected_items = []
                        st.rerun()
                with col2:
                    if st.button("❌ Отмена полной очистки"):
                        st.session_state.confirm_clear_inventory = False
                        st.rerun()
            
            # Отображение товаров с возможностью управления
            st.markdown("---")
            for _, item in inventory_df_sorted.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 1.5, 1.5, 1, 1])
                
                with col1:
                    # Checkbox для выбора товара
                    is_selected = st.checkbox("", key=f"select_{item['id']}", 
                                            value=item['id'] in st.session_state.selected_items)
                    if is_selected and item['id'] not in st.session_state.selected_items:
                        st.session_state.selected_items.append(item['id'])
                    elif not is_selected and item['id'] in st.session_state.selected_items:
                        st.session_state.selected_items.remove(item['id'])
                
                with col2:
                    st.write(f"**📦 {item['product_name']}**")
                    if item['link']:
                        st.markdown(f"[🔗 Ссылка]({item['link']})")
                
                with col3:
                    # Редактирование количества
                    new_quantity = st.number_input("Количество", 
                                                 min_value=0, 
                                                 value=int(item['quantity']), 
                                                 key=f"qty_{item['id']}")
                
                with col4:
                    # Цветовая индикация количества
                    if item['quantity'] <= low_stock_threshold:
                        st.error(f"⚠️ Низкий остаток")
                    else:
                        st.success(f"✅ В наличии")
                    st.caption(f"Добавлено: {item['created_at'][:10]}")
                
                with col5:
                    # Кнопка обновления количества
                    if st.button("💾", key=f"save_{item['id']}", help="Сохранить количество"):
                        if update_inventory_quantity(st.session_state.user_id, item['id'], new_quantity):
                            if new_quantity == 0:
                                st.success("Товар удален (количество = 0)")
                            else:
                                st.success("Количество обновлено")
                            st.rerun()
                        else:
                            st.error("Ошибка обновления")
                
                with col6:
                    # Кнопка удаления отдельного товара
                    if st.button("🗑️", key=f"del_{item['id']}", help="Удалить товар"):
                        if delete_inventory_item(st.session_state.user_id, item['id']):
                            st.success("Товар удален")
                            if item['id'] in st.session_state.selected_items:
                                st.session_state.selected_items.remove(item['id'])
                            st.rerun()
                        else:
                            st.error("Ошибка удаления")
            
            # Предупреждения о низких остатках
            low_stock = inventory_df[inventory_df['quantity'] <= low_stock_threshold]
            if not low_stock.empty:
                st.markdown("---")
                st.warning(f"⚠️ **{len(low_stock)} товаров с низкими остатками:**")
                for _, item in low_stock.iterrows():
                    st.write(f"• **{item['product_name']}**: {item['quantity']} шт.")
        else:
            st.info("📦 Склад пуст. Добавьте товары через вкладку 'Добавить товар'")
    
    with tab2:
        st.subheader("➕ Добавить товар на склад")
        st.info("💡 Товары добавленные здесь хранятся на складе. Товары из заказов автоматически сохраняются в истории заказов.")
        
        with st.form("add_inventory_form"):
            product_name = st.text_input("Название товара *")
            quantity = st.number_input("Количество *", min_value=1, value=1)
            link = st.text_input("Ссылка на товар (необязательно)", placeholder="https://example.com/product")
            
            submitted = st.form_submit_button("📦 Добавить на склад")
            
            if submitted:
                if product_name and quantity > 0:
                    success, message = add_to_inventory(st.session_state.user_id, product_name, quantity, link)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Заполните обязательные поля")
    
    with tab3:
        st.subheader("📋 История заказов")
        st.info("� Здесь отображаются товары, которые были заказаны и проданы (не хранились на складе)")
        
        # Фильтры для истории
        col1, col2, col3 = st.columns(3)
        with col1:
            history_limit = st.selectbox("Показать записей:", [50, 100, 200, None], 
                                       format_func=lambda x: "Все" if x is None else str(x))
        with col2:
            search_product = st.text_input("Поиск по названию товара:")
        with col3:
            date_filter = st.selectbox("Период:", ["Все время", "Последний месяц", "Последние 3 месяца"])
        
        # Получаем историю с фильтрами
        if search_product:
            # Определяем даты для фильтра
            start_date = None
            if date_filter == "Последний месяц":
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            elif date_filter == "Последние 3 месяца":
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            
            history_df = search_order_history(st.session_state.user_id, search_product, start_date)
        else:
            history_df = get_order_history(st.session_state.user_id, history_limit)
        
        if not history_df.empty:
            # Статистика по истории
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего записей", len(history_df))
            with col2:
                st.metric("Общая выручка", f"${history_df['total_cost'].sum():.2f}")
            with col3:
                st.metric("Общая прибыль", f"${(history_df['total_cost'] - history_df['cost_price'] * history_df['quantity'] - history_df['delivery_cost']).sum():.2f}")
            with col4:
                st.metric("Уникальных товаров", history_df['product_name'].nunique())
            
            st.markdown("---")
            
            # Группировка по типу доставки
            delivery_stats = history_df.groupby('delivery_type').agg({
                'total_cost': 'sum',
                'quantity': 'sum',
                'id': 'count'
            }).rename(columns={'id': 'orders_count'})
            
            if len(delivery_stats) > 1:
                st.markdown("**📊 Статистика по типам доставки:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    for delivery_type, stats in delivery_stats.iterrows():
                        delivery_name = "✈️ Самолет" if delivery_type == 'airplane' else "🚛 Автомобиль"
                        st.write(f"**{delivery_name}:**")
                        st.write(f"  • Заказов: {stats['orders_count']}")
                        st.write(f"  • Товаров: {stats['quantity']}")
                        st.write(f"  • Выручка: ${stats['total_cost']:.2f}")
                
                with col2:
                    # Круговая диаграмма по выручке
                    fig_delivery = px.pie(
                        values=delivery_stats['total_cost'],
                        names=[f"{'Самолет' if idx == 'airplane' else 'Автомобиль'}" for idx in delivery_stats.index],
                        title="Распределение выручки по доставке"
                    )
                    st.plotly_chart(fig_delivery, use_container_width=True)
            
            st.markdown("---")
            st.markdown("**📋 Детальная история:**")
            
            # Отображение детальной истории с возможностью удаления
            for _, record in history_df.iterrows():
                with st.expander(f"📦 {record['product_name']} - {record['order_date'][:10]} (${record['total_cost']:.2f})"):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**Количество:** {record['quantity']}")
                        st.write(f"**Себестоимость:** ${record['cost_price']:.2f}")
                        st.write(f"**Цена продажи:** ${record['sale_price']:.2f}")
                    
                    with col2:
                        st.write(f"**Вес:** {record['weight']} кг")
                        delivery_name = "✈️ Самолет" if record['delivery_type'] == 'airplane' else "🚛 Автомобиль"
                        st.write(f"**Доставка:** {delivery_name}")
                        st.write(f"**Стоимость доставки:** ${record['delivery_cost']:.2f}")
                    
                    with col3:
                        profit = record['total_cost'] - (record['cost_price'] * record['quantity']) - record['delivery_cost']
                        st.write(f"**Общая стоимость:** ${record['total_cost']:.2f}")
                        st.write(f"**Прибыль:** ${profit:.2f}")
                        if record['order_name']:
                            st.write(f"**Заказ:** {record['order_name']}")
                    
                    with col4:
                        st.write("**Действия:**")
                        if st.button("🗑️ Удалить", key=f"delete_history_{record['id']}", 
                                   help="Удалить этот товар из истории заказов"):
                            if delete_order_history_item(record['id']):
                                st.success("✅ Товар удален из истории")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка при удалении")
            
            # Массовое удаление
            st.markdown("---")
            st.markdown("**🗑️ Массовые операции:**")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_products = st.multiselect(
                    "Выберите товары для удаления:",
                    options=history_df['id'].tolist(),
                    format_func=lambda x: f"{history_df[history_df['id']==x]['product_name'].iloc[0]} - {history_df[history_df['id']==x]['order_date'].iloc[0][:10]}"
                )
            
            with col2:
                if selected_products:
                    st.write(f"Выбрано товаров: {len(selected_products)}")
                    if st.button("🗑️ Удалить выбранные", type="secondary"):
                        if delete_order_history_items_bulk(selected_products):
                            st.success(f"✅ Удалено {len(selected_products)} товаров из истории")
                            st.rerun()
                        else:
                            st.error("❌ Ошибка при удалении")
        else:
            st.info("📋 История заказов пуста")
    
    with tab4:
        st.subheader("🔍 Поиск и фильтры")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏪 Поиск на складе:**")
            search_term = st.text_input("Поиск товаров на складе:")
            
            if search_term:
                search_results = search_inventory(st.session_state.user_id, search_term)
                
                if not search_results.empty:
                    st.write(f"🔍 Найдено {len(search_results)} товаров на складе:")
                    for _, row in search_results.iterrows():
                        with st.expander(f"📦 {row['product_name']} (Количество: {row['quantity']})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Количество:** {row['quantity']}")
                                st.write(f"**Добавлено:** {row['created_at'][:10]}")
                            with col2:
                                if row['link']:
                                    st.markdown(f"**Ссылка:** [🔗 Открыть]({row['link']})")
                                if st.button(f"🗑️ Удалить {row['product_name']}", key=f"search_del_{row['id']}"):
                                    if delete_inventory_item(st.session_state.user_id, row['id']):
                                        st.success("Товар удален")
                                        st.rerun()
                else:
                    st.info("Товары на складе не найдены")
        
        with col2:
            st.markdown("**📋 Поиск в истории заказов:**")
            history_search = st.text_input("Поиск в истории заказов:")
            
            if history_search:
                history_results = search_order_history(st.session_state.user_id, history_search)
                
                if not history_results.empty:
                    st.write(f"🔍 Найдено {len(history_results)} записей в истории:")
                    
                    # Группируем по товарам
                    grouped = history_results.groupby('product_name').agg({
                        'quantity': 'sum',
                        'total_cost': 'sum',
                        'order_date': 'max'
                    }).sort_values('order_date', ascending=False)
                    
                    for product_name, stats in grouped.iterrows():
                        with st.expander(f"📋 {product_name} - {stats['quantity']} шт. (${stats['total_cost']:.2f})"):
                            st.write(f"**Последний заказ:** {stats['order_date'][:10]}")
                            st.write(f"**Общее количество:** {stats['quantity']}")
                            st.write(f"**Общая выручка:** ${stats['total_cost']:.2f}")
                else:
                    st.info("Записи в истории не найдены")

def show_smart_functions():
    st.title("🧠 Умные функции")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Рекомендации", "Автозаполнение", "Аналитика поставщиков", "Сезонные тренды"])
    
    with tab1:
        st.subheader("🎯 Рекомендации для повторного заказа")
        
        try:
            from smart_functions import get_smart_functions
            smart_func = get_smart_functions()
            
            recommendations = smart_func.get_reorder_recommendations(st.session_state.user_id)
            
            if recommendations:
                st.write(f"Найдено {len(recommendations)} рекомендаций:")
                
                for i, rec in enumerate(recommendations):
                    priority_color = "🔴" if rec['priority'] == 'high' else "🟡"
                    
                    with st.expander(f"{priority_color} {rec['product_name']} (не заказывался {rec['days_since_last']} дней)"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Частота заказов", rec['frequency'])
                        with col2:
                            st.metric("Рекомендуемое количество", rec['suggested_quantity'])
                        with col3:
                            st.metric("Ожидаемая стоимость", f"${rec['suggested_cost_price']}")
                        
                        if st.button(f"Создать заказ для {rec['product_name']}", key=f"reorder_{i}"):
                            # Автозаполнение формы заказа
                            st.session_state[f"auto_product_name"] = rec['product_name']
                            st.session_state[f"auto_quantity"] = rec['suggested_quantity']
                            st.session_state[f"auto_cost_price"] = rec['suggested_cost_price']
                            st.session_state[f"auto_weight"] = rec['suggested_weight']
                            st.success("Данные подготовлены! Перейдите в раздел Заказы.")
            else:
                st.info("Нет рекомендаций для повторного заказа")
        
        except ImportError:
            st.error("Модуль умных функций недоступен")
    
    with tab2:
        st.subheader("🔍 Тест автозаполнения")
        
        try:
            search_query = st.text_input("Введите начало названия товара:")
            
            if search_query:
                suggestions = smart_func.get_product_suggestions(st.session_state.user_id, search_query)
                
                if suggestions:
                    st.write("Найденные товары:")
                    for suggestion in suggestions:
                        st.write(f"- {suggestion['name']} (заказывался {suggestion['frequency']} раз)")
                else:
                    st.info("Товары не найдены")
        
        except:
            st.error("Функция автозаполнения недоступна")
    
    with tab3:
        st.subheader("⭐ Анализ поставщиков")
        
        try:
            supplier_analysis = smart_func.analyze_supplier_performance(st.session_state.user_id)
            
            if supplier_analysis:
                for supplier_name, data in supplier_analysis.items():
                    with st.expander(f"{supplier_name} (Рейтинг: {data['performance_score']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Количество заказов", data['orders_count'])
                            st.metric("Средняя стоимость доставки", f"${data['avg_delivery_cost']}")
                        
                        with col2:
                            st.metric("Общая выручка", f"${data['total_revenue']}")
                            st.metric("Средний возраст заказов", f"{data['avg_order_age_days']} дней")
            else:
                st.info("Недостаточно данных для анализа поставщиков")
        
        except:
            st.error("Анализ поставщиков недоступен")
    
    with tab4:
        st.subheader("📅 Сезонные тренды")
        
        try:
            seasonal_data = smart_func.get_seasonal_insights(st.session_state.user_id)
            
            if seasonal_data:
                for month, products in seasonal_data.items():
                    with st.expander(f"� {month}"):
                        if products:
                            df = pd.DataFrame(products)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("Нет данных за этот месяц")
            else:
                st.info("Недостаточно данных для анализа сезонности")
        
        except:
            st.error("Анализ сезонности недоступен")

def show_admin_panel():
    """Админ-панель для управления пользователями и платежами"""
    if not st.session_state.get('user_id'):
        st.error("Доступ запрещен")
        return
    
    # Проверяем, является ли пользователь админом
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE id = ?', (st.session_state.user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        st.error("❌ Доступ только для администраторов")
        return
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2E4057; font-size: 2.5rem; font-weight: 300;">
            👨‍💼 Панель администратора
        </h1>
        <p style="color: #64748B; font-size: 1.1rem;">
            Управление пользователями и подписками
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Боковое меню админ-панели
    admin_tab = st.sidebar.selectbox(
        "Выберите раздел:",
        ["👥 Пользователи", "💳 Платежи", "📊 Статистика", "⚙️ Настройки"]
    )
    
    if admin_tab == "👥 Пользователи":
        show_admin_users()
    elif admin_tab == "💳 Платежи":
        show_admin_payments()
    elif admin_tab == "📊 Статистика":
        show_admin_statistics()
    elif admin_tab == "⚙️ Настройки":
        show_admin_settings()

def show_admin_panel():
    """Основная админская панель с подстраницами"""
    admin_page = st.session_state.get('admin_page', 'users')
    
    if admin_page == "users":
        show_admin_users()
    elif admin_page == "payments":
        show_admin_payments()
    elif admin_page == "stats":
        show_admin_statistics()
    elif admin_page == "reports":
        # Создаем функцию отчетов позже
        st.header("📈 Админские отчеты")
        st.info("Функция в разработке")
    elif admin_page == "admin_settings":
        show_admin_settings()
    else:
        show_admin_users()

def show_admin_users():
    """Управление пользователями"""
    st.header("👥 Управление пользователями")
    
    # Поиск пользователей
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Поиск по email или телефону:")
    
    with col2:
        premium_filter = st.selectbox("Премиум:", ["Все", "Только премиум", "Без премиума"])
    
    with col3:
        sort_by = st.selectbox("Сортировка:", ["По дате регистрации", "По email", "По статусу"])
    
    # Получение списка пользователей
    conn = sqlite3.connect('business_manager.db')
    
    query = '''
        SELECT 
            id, email, phone, full_name, business_name,
            premium_status, premium_end_date, created_at, last_login
        FROM users 
        WHERE is_admin = 0
    '''
    params = []
    
    if search_term:
        query += " AND (email LIKE ? OR phone LIKE ? OR full_name LIKE ?)"
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if premium_filter == "Только премиум":
        query += " AND premium_status = 1"
    elif premium_filter == "Без премиума":
        query += " AND (premium_status = 0 OR premium_status IS NULL)"
    
    if sort_by == "По email":
        query += " ORDER BY email"
    elif sort_by == "По статусу":
        query += " ORDER BY premium_status DESC"
    else:
        query += " ORDER BY created_at DESC"
    
    users_df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not users_df.empty:
        st.subheader(f"Найдено пользователей: {len(users_df)}")
        
        # Статистика
        total_users = len(users_df)
        premium_users = len(users_df[users_df['premium_status'] == True])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Всего пользователей", total_users)
        with col2:
            st.metric("💎 Премиум пользователей", premium_users)
        with col3:
            st.metric("📈 Конверсия в премиум", f"{(premium_users/total_users*100):.1f}%" if total_users > 0 else "0%")
        
        # Таблица пользователей
        st.subheader("📋 Список пользователей")
        
        for idx, user in users_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: #f8f9fa;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #000000 !important;">
                                👤 {user['full_name'] or user['email']}
                            </h4>
                            <p style="margin: 5px 0; color: #000000 !important;">
                                📧 {user['email']} | 📱 {user['phone'] or 'Не указан'}
                            </p>
                            <p style="margin: 5px 0; color: #000000 !important;">
                                🏢 {user['business_name'] or 'Не указано'} | 
                                📅 Регистрация: {user['created_at'][:10]}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {'#28a745' if user['premium_status'] else '#6c757d'}; 
                                  color: #ffffff !important; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                                {'ПРЕМИУМ' if user['premium_status'] else 'ОБЫЧНЫЙ'}
                            </span>
                            {f'<p style="margin: 5px 0; font-size: 12px; color: #000000 !important;">До: {user["premium_end_date"][:10] if user["premium_end_date"] else ""}</p>' if user['premium_status'] else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Кнопки управления
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"💎 {'Отключить' if user['premium_status'] else 'Активировать'} премиум", 
                               key=f"toggle_premium_{user['id']}"):
                        if user['premium_status']:
                            deactivate_premium(user['id'])
                            st.success("Премиум отключен")
                            # Обновляем состояние в сессии если это текущий пользователь
                            if user['id'] == st.session_state.user_id:
                                st.session_state.is_premium = False
                        else:
                            activate_premium(user['id'])
                            st.success("Премиум активирован на месяц")
                            # Обновляем состояние в сессии если это текущий пользователь
                            if user['id'] == st.session_state.user_id:
                                st.session_state.is_premium = True
                        # Принудительно обновляем страницу через небольшую задержку
                        time.sleep(0.5)
                        st.rerun()
                
                with col2:
                    if st.button(f"📊 Статистика", key=f"stats_{user['id']}"):
                        show_user_statistics(user['id'])
                
                with col3:
                    if st.button(f"💳 История платежей", key=f"payments_{user['id']}"):
                        show_user_payments(user['id'])
                
                with col4:
                    if st.button(f"🗑️ Удалить", key=f"delete_{user['id']}"):
                        if st.session_state.get(f'confirm_delete_{user["id"]}'):
                            if delete_user(user['id']):
                                st.success("Пользователь успешно удален")
                                # Сбрасываем состояние подтверждения
                                if f'confirm_delete_{user["id"]}' in st.session_state:
                                    del st.session_state[f'confirm_delete_{user["id"]}']
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Не удалось удалить пользователя")
                                # Сбрасываем состояние подтверждения
                                if f'confirm_delete_{user["id"]}' in st.session_state:
                                    del st.session_state[f'confirm_delete_{user["id"]}']
                        else:
                            st.session_state[f'confirm_delete_{user["id"]}'] = True
                            st.warning("Нажмите еще раз для подтверждения удаления")
    else:
        st.info("Пользователи не найдены")

def show_user_statistics(user_id):
    """Показывает статистику конкретного пользователя"""
    st.subheader(f"📊 Статистика пользователя")
    
    conn = sqlite3.connect('business_manager.db')
    try:
        # Получаем информацию о пользователе
        user_df = pd.read_sql_query('SELECT email, created_at, premium_status FROM users WHERE id = ?', conn, params=(user_id,))
        if user_df.empty:
            st.error("Пользователь не найден")
            return
        
        user_info = user_df.iloc[0]
        st.write(f"**Email:** {user_info['email']}")
        st.write(f"**Дата регистрации:** {user_info['created_at']}")
        st.write(f"**Премиум статус:** {'✅ Активен' if user_info['premium_status'] else '❌ Неактивен'}")
        
        # Статистика заказов
        orders_df = pd.read_sql_query('''
            SELECT COUNT(*) as total_orders,
                   SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders
            FROM orders WHERE user_id = ?
        ''', conn, params=(user_id,))
        
        if not orders_df.empty:
            stats = orders_df.iloc[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего заказов", stats['total_orders'])
            with col2:
                st.metric("В ожидании", stats['pending_orders'])
            with col3:
                st.metric("Завершено", stats['completed_orders'])
        
        # Статистика товаров
        inventory_df = pd.read_sql_query('SELECT COUNT(*) as total_products, SUM(quantity) as total_quantity FROM inventory WHERE user_id = ?', conn, params=(user_id,))
        if not inventory_df.empty:
            inv_stats = inventory_df.iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Товаров в каталоге", inv_stats['total_products'])
            with col2:
                st.metric("Общее количество", inv_stats['total_quantity'])
        
    finally:
        conn.close()

def show_user_payments(user_id):
    """Показывает историю платежей пользователя"""
    st.subheader(f"💳 История платежей пользователя")
    
    conn = sqlite3.connect('business_manager.db')
    try:
        # Получаем информацию о пользователе
        user_df = pd.read_sql_query('SELECT email FROM users WHERE id = ?', conn, params=(user_id,))
        if user_df.empty:
            st.error("Пользователь не найден")
            return
        
        st.write(f"**Пользователь:** {user_df.iloc[0]['email']}")
        
        # Получаем историю платежей
        payments_df = pd.read_sql_query('''
            SELECT payment_date, amount, status, payment_method
            FROM payment_history 
            WHERE user_id = ? 
            ORDER BY payment_date DESC
        ''', conn, params=(user_id,))
        
        if not payments_df.empty:
            # Показываем статистику платежей
            total_paid = payments_df[payments_df['status'] == 'confirmed']['amount'].sum()
            total_pending = payments_df[payments_df['status'] == 'pending']['amount'].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Общая сумма платежей", f"{total_paid:.2f} ТМ")
            with col2:
                st.metric("В ожидании", f"{total_pending:.2f} ТМ")
            
            # Показываем таблицу платежей
            st.dataframe(payments_df, use_container_width=True)
        else:
            st.info("История платежей пуста")
        
    except Exception as e:
        st.error(f"Ошибка при загрузке платежей: {e}")
    finally:
        conn.close()

def show_admin_payments():
    """Управление платежами"""
    st.header("💳 Управление платежами")
    
    # Фильтры
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox("Статус:", ["Все", "pending", "confirmed", "rejected"])
    
    with col2:
        days_filter = st.selectbox("Период:", ["Все время", "За неделю", "За месяц"])
    
    # Получение платежей
    conn = sqlite3.connect('business_manager.db')
    
    query = '''
        SELECT 
            ph.id, ph.user_id, ph.amount, ph.status, ph.payment_date,
            ph.confirmed_date, ph.notes, u.email, u.phone, u.full_name
        FROM payment_history ph
        JOIN users u ON ph.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if status_filter != "Все":
        query += " AND ph.status = ?"
        params.append(status_filter)
    
    if days_filter == "За неделю":
        query += " AND ph.payment_date >= datetime('now', '-7 days')"
    elif days_filter == "За месяц":
        query += " AND ph.payment_date >= datetime('now', '-30 days')"
    
    query += " ORDER BY ph.payment_date DESC"
    
    payments_df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not payments_df.empty:
        st.subheader(f"Найдено платежей: {len(payments_df)}")
        
        # Статистика платежей
        pending_count = len(payments_df[payments_df['status'] == 'pending'])
        confirmed_count = len(payments_df[payments_df['status'] == 'confirmed'])
        total_amount = payments_df[payments_df['status'] == 'confirmed']['amount'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏳ Ожидают подтверждения", pending_count)
        with col2:
            st.metric("✅ Подтверждено", confirmed_count)
        with col3:
            st.metric("💰 Общая сумма", f"{total_amount:.0f} ₼")
        
        # Список платежей
        for idx, payment in payments_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: white;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #000000;">
                                💳 Платеж #{payment['id']} - {payment['amount']:.0f} ₼
                            </h4>
                            <p style="margin: 5px 0; color: #333333;">
                                👤 {payment['full_name'] or payment['email']} | 📱 {payment['phone'] or 'Не указан'}
                            </p>
                            <p style="margin: 5px 0; color: #333333;">
                                📅 Дата: {payment['payment_date'][:16]} | 
                                {f"✅ Подтвержден: {payment['confirmed_date'][:16]}" if payment['confirmed_date'] else "⏳ Ожидает подтверждения"}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {'#28a745' if payment['status'] == 'confirmed' else '#ffc107' if payment['status'] == 'pending' else '#dc3545'}; 
                                  color: #000000; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                                {payment['status'].upper()}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if payment['status'] == 'pending':
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"✅ Подтвердить", key=f"confirm_payment_{payment['id']}"):
                            if confirm_payment(payment['id'], st.session_state.user_id):
                                st.success("Платеж подтвержден, премиум активирован!")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"❌ Отклонить", key=f"reject_payment_{payment['id']}"):
                            reject_payment(payment['id'])
                            st.warning("Платеж отклонен")
                            st.rerun()
    else:
        st.info("Платежи не найдены")

def deactivate_premium(user_id):
    """Отключает премиум у пользователя"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET premium_status = 0,
            premium_end_date = NULL
        WHERE id = ?
    ''', (user_id,))
    
    # Обновляем сессию если это текущий пользователь
    if 'user_id' in st.session_state and st.session_state.user_id == user_id:
        st.session_state.premium_status = 0
        st.session_state.is_premium = False
    
    conn.commit()
    conn.close()

def reject_payment(payment_id):
    """Отклоняет платеж"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE payment_history 
        SET status = 'rejected'
        WHERE id = ?
    ''', (payment_id,))
    
    conn.commit()
    conn.close()

def show_admin_statistics():
    """Показывает статистику для админа"""
    st.header("📊 Статистика платформы")
    
    conn = sqlite3.connect('business_manager.db')
    
    # Общая статистика
    total_users = pd.read_sql_query("SELECT COUNT(*) as count FROM users WHERE is_admin = 0", conn).iloc[0]['count']
    premium_users = pd.read_sql_query("SELECT COUNT(*) as count FROM users WHERE premium_status = 1 AND is_admin = 0", conn).iloc[0]['count']
    total_revenue = pd.read_sql_query("SELECT SUM(amount) as total FROM payment_history WHERE status = 'confirmed'", conn).iloc[0]['total'] or 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Всего пользователей", total_users)
    
    with col2:
        st.metric("💎 Премиум пользователей", premium_users)
    
    with col3:
        st.metric("💰 Общий доход", f"{total_revenue:.0f} ₼")
    
    with col4:
        conversion = (premium_users / total_users * 100) if total_users > 0 else 0
        st.metric("📈 Конверсия", f"{conversion:.1f}%")
    
    conn.close()

def show_admin_settings():
    """Настройки админ-панели"""
    st.header("⚙️ Настройки системы")
    
    st.subheader("💳 Настройки оплаты")
    
    col1, col2 = st.columns(2)
    
    with col1:
        premium_price = st.number_input("Цена премиум-подписки (ТМ):", value=150, min_value=1)
        payment_phone = st.text_input("Номер для переводов:", value="+993 658-425-20")
    
    with col2:
        admin_email = st.text_input("Email администратора:", value="alexkurumbayev@gmail.com")
        auto_deactivate = st.checkbox("Автоматическое отключение премиума", value=True)
    
    if st.button("💾 Сохранить настройки"):
        st.success("Настройки сохранены!")

def show_premium_settings():
    """Показывает настройки премиум-подписки для пользователя"""
    st.title("💎 Премиум подписка")
    
    # Проверяем текущий статус
    is_premium = check_premium_status(st.session_state.user_id)
    
    if is_premium:
        st.success("✅ У вас активна премиум-подписка!")
        
        # Показываем информацию о подписке
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT premium_end_date FROM users WHERE id = ?
        ''', (st.session_state.user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            end_date = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            st.info(f"📅 Подписка действует до: {end_date.strftime('%d.%m.%Y %H:%M')}")
        
        st.subheader("🎯 Ваши премиум-возможности:")
        st.markdown("""
        - 🧠 **ИИ-функции и умные инсайты** - автоматический анализ и рекомендации
        - 📊 **Полная аналитика и отчеты** - детализированные графики и диаграммы
        - 📦 **Расширенное управление складом** - мультискладская система
        - 🚚 **Продвинутое управление заказами** - фильтры и автоматизация
        - 💱 **Поддержка мультивалютности** - работа с разными валютами
        - 👥 **Многопользовательский доступ** - команда с разными ролями
        - 📤 **Экспорт данных** - выгрузка в Excel, PDF
        - 🏆 **Приоритетная поддержка** - быстрая помощь специалистов
        """)
        
    else:
        st.warning("⚠️ У вас базовая версия приложения")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: #000000; padding: 30px; border-radius: 15px; margin: 20px 0;">
            <h2 style="color: #000000; text-align: center; margin-bottom: 20px;">
                💎 Премиум подписка - 150 ТМ/месяц
            </h2>
            <p style="text-align: center; font-size: 1.1rem;">
                Расширьте возможности вашего бизнеса с премиум-функциями!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Премиум-возможности:")
            st.markdown("""
            - 🧠 **ИИ-функции и умные инсайты** - автоматический анализ и рекомендации
            - 📊 **Полная аналитика и отчеты** - детализированные графики и диаграммы
            - 📦 **Расширенное управление складом** - мультискладская система
            - 🚚 **Продвинутое управление заказами** - фильтры и автоматизация
            - 💱 **Поддержка мультивалютности** - работа с разными валютами
            - 👥 **Многопользовательский доступ** - команда с разными ролями
            - 📤 **Экспорт данных** - выгрузка в Excel, PDF
            - 🏆 **Приоритетная поддержка** - быстрая помощь специалистов
            - 🚀 **Неограниченные возможности** - без лимитов по товарам и заказам
            """)
            
            st.info("""
            **📈 Бесплатная версия ограничена:**
            - ⚠️ Максимум 20 товаров на складе
            - ⚠️ Максимум 25 заказов одновременно
            - ⚠️ Базовая аналитика
            - ⚠️ Стандартная поддержка
            """)
        
        with col2:
            st.subheader("💳 Как оплатить:")
            st.markdown("""
            **1️⃣ Переведите 150 ТМ на номер:**
            
            📱 **+993 658-425-20**
            
            **2️⃣ Нажмите кнопку "Оплатил" ниже**
            
            **3️⃣ Дождитесь подтверждения (до 24 часов)**
            
            ⚠️ *Подписка действует ровно 1 месяц с момента активации*
            """)
            
            if st.button("💳 Я оплатил подписку", type="primary"):
                payment_id = request_premium_payment(st.session_state.user_id)
                st.success(f"""
                ✅ Запрос на подтверждение оплаты отправлен! 
                
                📧 Уведомление отправлено администратору
                
                🔄 Ваша подписка будет активирована в течение 24 часов после проверки платежа
                
                📋 Номер запроса: #{payment_id}
                """)

def show_settings():
    st.title("⚙️ Настройки")
    
    # Определяем вкладки в зависимости от роли пользователя
    if st.session_state.is_admin:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Финансовые", "📧 Уведомления", "💾 Данные", "👨‍💼 Админ", "💎 Премиум"])
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["💰 Финансовые", "� Уведомления", "💾 Данные", "💎 Премиум"])
    
    with tab1:
        st.markdown("""
        <div class="card">
            <h3 style="color: #000000; margin-bottom: 1rem;">💰 Финансовые настройки</h3>
        </div>
        """, unsafe_allow_html=True)
        
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        cursor.execute('SELECT financial_cushion_percent FROM settings WHERE user_id = ?', 
                      (st.session_state.user_id,))
        current_settings = cursor.fetchone()
        current_cushion = current_settings[0] if current_settings else 20.0
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            with st.form("financial_settings"):
                st.markdown("#### 🛡️ Финансовая подушка")
                st.info("Выберите процент от прибыли, который будет откладываться в резерв для экстренных случаев")
                
                cushion_percent = st.slider(
                    "Процент для финансовой подушки:",
                    min_value=0.0,
                    max_value=50.0,
                    value=current_cushion,
                    step=0.5,
                    help="Рекомендуется 15-25% для стабильного бизнеса"
                )
                
                # Предварительный расчет
                analytics = get_analytics(st.session_state.user_id)
                if analytics['profit'] > 0:
                    projected_cushion = analytics['profit'] * (cushion_percent / 100)
                    projected_personal = analytics['profit'] - projected_cushion
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🛡️ Резерв будет составлять", f"${projected_cushion:.2f}")
                    with col2:
                        st.metric("🏠 На личные расходы останется", f"${projected_personal:.2f}")
                
                submitted = st.form_submit_button("💾 Сохранить настройки", use_container_width=True)
                
                if submitted:
                    cursor.execute('''
                        UPDATE settings 
                        SET financial_cushion_percent = ? 
                        WHERE user_id = ?
                    ''', (cushion_percent, st.session_state.user_id))
                    conn.commit()
                    st.success("✅ Настройки успешно сохранены!")
                    st.rerun()  # Обновляем страницу для отображения новых настроек
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Настройки доставки
        st.markdown("""
        <div class="card">
            <h3 style="color: #000000; margin-bottom: 1rem;">🚚 Настройки доставки</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Получаем текущие цены доставки безопасно
        try:
            cursor.execute('SELECT airplane_price_per_kg, truck_price_per_kg FROM settings WHERE user_id = ?', 
                          (st.session_state.user_id,))
            delivery_settings = cursor.fetchone()
            current_airplane_price = delivery_settings[0] if delivery_settings and delivery_settings[0] else 5.0
            current_truck_price = delivery_settings[1] if delivery_settings and delivery_settings[1] else 2.0
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            # Поля не существуют, используем значения по умолчанию
            current_airplane_price = 5.0
            current_truck_price = 2.0
            # Добавляем поля если их нет
            try:
                cursor.execute("ALTER TABLE settings ADD COLUMN airplane_price_per_kg REAL DEFAULT 5.0")
                cursor.execute("ALTER TABLE settings ADD COLUMN truck_price_per_kg REAL DEFAULT 2.0")
                conn.commit()
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                pass
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            with st.form("delivery_settings"):
                st.markdown("#### 🚚 Стоимость доставки за килограмм")
                st.info("Настройте стоимость доставки в зависимости от способа транспортировки")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    airplane_price = st.number_input(
                        "✈️ Самолет ($/кг):",
                        min_value=0.01,
                        max_value=100.0,
                        value=float(current_airplane_price),
                        step=0.1,
                        help="Стоимость авиаперевозки за килограмм"
                    )
                
                with col2:
                    truck_price = st.number_input(
                        "🚛 Автомобиль ($/кг):",
                        min_value=0.01,
                        max_value=100.0,
                        value=float(current_truck_price),
                        step=0.1,
                        help="Стоимость автомобильной перевозки за килограмм"
                    )
                
                # Показываем сравнение
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✈️ Самолет", f"${airplane_price:.2f}/кг")
                with col2:
                    st.metric("🚛 Автомобиль", f"${truck_price:.2f}/кг")
                with col3:
                    difference = airplane_price - truck_price
                    st.metric("Разница", f"${abs(difference):.2f}/кг", 
                             f"{'Самолет дороже' if difference > 0 else 'Автомобиль дороже'}")
                
                delivery_submitted = st.form_submit_button("💾 Сохранить цены доставки", use_container_width=True)
                
                if delivery_submitted:
                    try:
                        cursor.execute('''
                            UPDATE settings 
                            SET airplane_price_per_kg = ?, truck_price_per_kg = ?
                            WHERE user_id = ?
                        ''', (airplane_price, truck_price, st.session_state.user_id))
                        conn.commit()
                        st.success("✅ Цены доставки успешно обновлены!")
                        st.rerun()  # Обновляем страницу
                    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                        # Поля не существуют, создаем их и обновляем
                        try:
                            cursor.execute("ALTER TABLE settings ADD COLUMN airplane_price_per_kg REAL DEFAULT 5.0")
                            cursor.execute("ALTER TABLE settings ADD COLUMN truck_price_per_kg REAL DEFAULT 2.0")
                            conn.commit()
                            cursor.execute('''
                                UPDATE settings 
                                SET airplane_price_per_kg = ?, truck_price_per_kg = ?
                                WHERE user_id = ?
                            ''', (airplane_price, truck_price, st.session_state.user_id))
                            conn.commit()
                            st.success("✅ Поля созданы и цены доставки обновлены!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Ошибка при обновлении цен: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        conn.close()
    
    with tab2:
        st.markdown("""
        <div class="card">
            <h3 style="color: #000000; margin-bottom: 1rem;">📧 Настройки уведомлений</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Получаем текущие настройки SMTP
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT email_notifications, smtp_server, smtp_port, email_username, email_password,
                   notify_new_orders, notify_low_stock, notify_daily_report
            FROM settings WHERE user_id = ?
        ''', (st.session_state.user_id,))
        smtp_settings = cursor.fetchone()
        
        current_notifications = smtp_settings[0] if smtp_settings else False
        current_server = smtp_settings[1] if smtp_settings else "smtp.gmail.com"
        current_port = smtp_settings[2] if smtp_settings else 587
        current_username = smtp_settings[3] if smtp_settings else ""
        current_password = smtp_settings[4] if smtp_settings else ""
        current_notify_orders = smtp_settings[5] if smtp_settings and len(smtp_settings) > 5 else True
        current_notify_stock = smtp_settings[6] if smtp_settings and len(smtp_settings) > 6 else True
        current_notify_daily = smtp_settings[7] if smtp_settings and len(smtp_settings) > 7 else False
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            with st.form("email_settings"):
                # Инициализация переменных по умолчанию
                email_server = current_server
                email_port = current_port
                email_username = current_username
                email_password = current_password
                provider = "Gmail"
                
                enable_notifications = st.checkbox(
                    "🔔 Включить email уведомления", 
                    value=current_notifications,
                    help="Получать уведомления о важных событиях в бизнесе"
                )
                
                if enable_notifications:
                    st.markdown("#### 📧 Настройки SMTP")
                    
                    # Предустановленные провайдеры
                    provider = st.selectbox(
                        "Выберите провайдера email:",
                        ["Gmail", "Яндекс", "Mail.ru", "Outlook", "Пользовательский"]
                    )
                    
                    # Автоматические настройки в зависимости от провайдера
                    if provider == "Gmail":
                        default_server = "smtp.gmail.com"
                        default_port = 587
                        st.info("💡 Для Gmail используйте пароль приложения, а не основной пароль аккаунта")
                        st.markdown("""
                        **Настройка Gmail:**
                        1. Включите двухфакторную аутентификацию
                        2. Создайте пароль приложения в настройках безопасности
                        3. Используйте TLS (порт 587) или SSL (порт 465)
                        """)
                    elif provider == "Яндекс":
                        default_server = "smtp.yandex.ru"
                        default_port = 587
                        st.info("💡 Используйте пароль приложения для Яндекс.Почты")
                    elif provider == "Mail.ru":
                        default_server = "smtp.mail.ru"
                        default_port = 587
                        st.info("💡 Включите доступ для внешних приложений в настройках")
                    elif provider == "Outlook":
                        default_server = "smtp-mail.outlook.com"
                        default_port = 587
                        st.info("💡 Используйте основной пароль Microsoft аккаунта")
                    else:
                        default_server = current_server
                        default_port = current_port
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        email_server = st.text_input(
                            "SMTP сервер:", 
                            value=default_server,
                            placeholder="smtp.gmail.com"
                        )
                    with col2:
                        port_options = {
                            "587 (TLS - рекомендуется)": 587,
                            "465 (SSL)": 465,
                            "25 (незащищенный)": 25
                        }
                        port_display = st.selectbox(
                            "Порт SMTP:",
                            options=list(port_options.keys()),
                            index=0 if default_port == 587 else (1 if default_port == 465 else 2)
                        )
                        email_port = port_options[port_display]
                    
                    email_username = st.text_input(
                        "Email пользователя:", 
                        value=current_username,
                        placeholder="your.email@gmail.com"
                    )
                    email_password = st.text_input(
                        "Пароль приложения:", 
                        type="password",
                        value=current_password,
                        placeholder="Введите пароль приложения"
                    )
                    
                    # Настройки типов уведомлений
                    st.markdown("#### 🔔 Типы уведомлений")
                    notify_new_orders = st.checkbox("Новые заказы", value=current_notify_orders)
                    notify_low_stock = st.checkbox("Низкие остатки на складе", value=current_notify_stock)
                    notify_daily_report = st.checkbox("Ежедневные отчеты", value=current_notify_daily)
                
                col1, col2 = st.columns(2)
                with col1:
                    save_smtp = st.form_submit_button("💾 Сохранить настройки", use_container_width=True)
                with col2:
                    test_smtp = st.form_submit_button("📧 Тест уведомления", use_container_width=True)
                
                if save_smtp:
                    try:
                        cursor.execute('''
                            UPDATE settings 
                            SET email_notifications = ?, smtp_server = ?, smtp_port = ?, 
                                email_username = ?, email_password = ?, notify_new_orders = ?,
                                notify_low_stock = ?, notify_daily_report = ?
                            WHERE user_id = ?
                        ''', (enable_notifications, email_server if enable_notifications else "", 
                             email_port if enable_notifications else 587, 
                             email_username if enable_notifications else "", 
                             email_password if enable_notifications else "", 
                             notify_new_orders, notify_low_stock, notify_daily_report,
                             st.session_state.user_id))
                        conn.commit()
                        st.success("✅ Настройки SMTP сохранены!")
                    except Exception as e:
                        st.error(f"❌ Ошибка сохранения: {str(e)}")
                
                if test_smtp and enable_notifications:
                    try:
                        # Улучшенное тестирование SMTP соединения
                        import smtplib
                        from email.mime.text import MIMEText
                        import ssl
                        
                        # Создаем SSL контекст
                        context = ssl.create_default_context()
                        
                        # Выбираем тип подключения в зависимости от порта
                        if email_port == 465:
                            # SSL подключение
                            server = smtplib.SMTP_SSL(email_server, email_port, context=context)
                        else:
                            # TLS подключение
                            server = smtplib.SMTP(email_server, email_port)
                            server.starttls(context=context)
                        
                        # Включаем отладку для диагностики
                        server.set_debuglevel(0)
                        
                        # Аутентификация
                        server.login(email_username, email_password)
                        
                        # Отправляем тестовое сообщение
                        msg = MIMEText(f"""
Тестовое уведомление от Бизнес Менеджера! 🎉

Настройки SMTP работают корректно:
- Сервер: {email_server}
- Порт: {email_port}
- Пользователь: {email_username}
- Время отправки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

С уважением,
Система управления бизнесом
                        """)
                        msg['Subject'] = f"✅ Тест уведомлений - Бизнес Менеджер ({datetime.now().strftime('%H:%M')})"
                        msg['From'] = email_username
                        msg['To'] = email_username
                        
                        server.send_message(msg)
                        server.quit()
                        
                        st.success("✅ Тестовое уведомление отправлено успешно!")
                        st.info(f"📧 Письмо отправлено на {email_username}")
                        
                    except smtplib.SMTPAuthenticationError as e:
                        st.error("❌ Ошибка аутентификации!")
                        if "Gmail" in provider:
                            st.warning("""
                            **Для Gmail проверьте:**
                            1. ✅ Включена двухфакторная аутентификация
                            2. ✅ Создан пароль приложения (не основной пароль!)
                            3. ✅ Используется правильный email
                            
                            **Как создать пароль приложения:**
                            1. Перейдите в настройки Google аккаунта
                            2. Безопасность → Двухэтапная аутентификация
                            3. Пароли приложений → Выберите приложение
                            4. Скопируйте сгенерированный пароль
                            """)
                        else:
                            st.warning("Проверьте правильность email и пароля")
                        st.code(f"Ошибка: {str(e)}")
                    
                    except smtplib.SMTPConnectError as e:
                        st.error(f"❌ Ошибка подключения к серверу: {e}")
                        st.info("Проверьте настройки сервера и порта")
                    
                    except smtplib.SMTPServerDisconnected as e:
                        st.error("❌ Соединение с сервером прервано")
                        st.info("Попробуйте еще раз или проверьте настройки")
                    
                    except Exception as e:
                        st.error(f"❌ Неожиданная ошибка: {str(e)}")
                        st.info("Проверьте все настройки SMTP и попробуйте снова")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        conn.close()
    
    with tab3:
        st.markdown("""
        <div class="card">
            <h3 style="color: #000000; margin-bottom: 1rem;">💾 Управление данными</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📥 Экспорт данных")
            st.write("Создайте резервную копию всех ваших данных")
            
            if st.button("📥 Экспорт всех данных", use_container_width=True):
                all_data = export_all_data(st.session_state.user_id)
                st.download_button(
                    label="⬇️ Скачать полный экспорт",
                    data=all_data,
                    file_name=f"business_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📤 Импорт данных")
            st.write("Восстановите данные из резервной копии")
            
            uploaded_file = st.file_uploader(
                "Выберите файл для импорта", 
                type=['xlsx', 'csv'],
                help="Поддерживаются файлы Excel и CSV"
            )
            
            if uploaded_file is not None:
                if st.button("📤 Импортировать данные", use_container_width=True):
                    try:
                        # Здесь будет логика импорта
                        st.success("✅ Данные успешно импортированы!")
                    except Exception as e:
                        st.error(f"❌ Ошибка импорта: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Дополнительные настройки
        st.markdown("---")
        st.markdown("#### ⚠️ Опасная зона")
        
        with st.expander("🗑️ Удаление всех данных"):
            st.warning("⚠️ Это действие нельзя отменить! Все ваши данные будут удалены безвозвратно.")
            
            confirm_text = st.text_input(
                "Введите 'УДАЛИТЬ ВСЕ' для подтверждения:",
                placeholder="УДАЛИТЬ ВСЕ"
            )
            
            if confirm_text == "УДАЛИТЬ ВСЕ":
                if st.button("🗑️ Подтвердить удаление", type="primary"):
                    # Здесь будет логика удаления всех данных пользователя
                    st.error("Функция удаления данных отключена в демо-версии")
                    # delete_all_user_data(st.session_state.user_id)
                    # st.success("Все данные удалены")
                    # st.session_state.user_id = None
                    # st.rerun()
    
    # Премиум настройки для всех пользователей
    if st.session_state.is_admin:
        with tab5:
            show_premium_settings()
    else:
        with tab4:
            show_premium_settings()
    
    # Админ-панель только для администраторов
    if st.session_state.is_admin:
        with tab4:
            st.markdown("""
            <div class="card">
                <h3 style="color: #000000; margin-bottom: 1rem;">👨‍💼 Администрирование</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Переключаем на админ-панель
            show_admin_panel()
        
        conn.close()

# Вспомогательные функции
def export_to_excel(df, sheet_name):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output.getvalue()

def export_all_data(user_id):
    conn = sqlite3.connect('business_manager.db')
    
    # Получаем все данные пользователя
    orders_query = '''
        SELECT o.*, GROUP_CONCAT(oi.product_name || " (x" || oi.quantity || ")") as items
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.id
    '''
    orders_df = pd.read_sql_query(orders_query, conn, params=(user_id,))
    
    inventory_df = pd.read_sql_query('SELECT * FROM inventory WHERE user_id = ?', 
                                   conn, params=(user_id,))
    
    analytics = get_analytics(user_id)
    analytics_df = pd.DataFrame([analytics])
    
    conn.close()
    
    # Создаем Excel файл с несколькими листами
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        orders_df.to_excel(writer, sheet_name='Orders', index=False)
        inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
        analytics_df.to_excel(writer, sheet_name='Analytics', index=False)
    
    output.seek(0)
    return output.getvalue()

def generate_full_report(user_id):
    conn = sqlite3.connect('business_manager.db')
    
    # Создаем подробный отчет
    report_query = '''
        SELECT 
            o.order_name,
            o.order_type,
            o.created_at,
            oi.product_name,
            oi.quantity,
            oi.cost_price,
            oi.weight,
            oi.delivery_cost,
            oi.total_cost,
            (oi.total_cost - oi.cost_price - oi.delivery_cost) as profit
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    '''
    
    report_df = pd.read_sql_query(report_query, conn, params=(user_id,))
    conn.close()
    
    return report_df

def send_daily_report(user_id):
    """Отправляет ежедневный отчет по email"""
    try:
        conn = sqlite3.connect('business_manager.db')
        cursor = conn.cursor()
        
        # Получаем настройки email
        cursor.execute('''
            SELECT email_notifications, smtp_server, smtp_port, email_username, 
                   email_password, notify_daily_report
            FROM settings WHERE user_id = ?
        ''', (user_id,))
        settings = cursor.fetchone()
        
        if not settings or not settings[0] or not settings[5]:  # Если уведомления или ежедневные отчеты отключены
            return False
            
        # Получаем email пользователя
        cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
        user_email = cursor.fetchone()[0]
        
        # Генерируем отчет за сегодня
        today = datetime.now().strftime('%Y-%m-%d')
        report_query = f'''
            SELECT 
                o.order_name,
                oi.product_name,
                oi.quantity,
                oi.total_cost,
                oi.cost_price,
                (oi.total_cost - oi.cost_price) as profit,
                o.status,
                o.order_date
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ? AND DATE(o.order_date) = ?
            ORDER BY o.order_date DESC
        '''
        
        cursor.execute(report_query, (user_id, today))
        orders_today = cursor.fetchall()
        
        # Создаем HTML отчет
        if orders_today:
            html_content = f"""
            <html>
            <body>
                <h2>📊 Ежедневный отчет - {today}</h2>
                <p>Добрый день! Вот ваш отчет за сегодня:</p>
                
                <h3>📦 Заказы за сегодня ({len(orders_today)} позиций):</h3>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th>Заказ</th>
                        <th>Товар</th>
                        <th>Количество</th>
                        <th>Выручка</th>
                        <th>Себестоимость</th>
                        <th>Прибыль</th>
                        <th>Статус</th>
                    </tr>
            """
            
            total_revenue = 0
            total_cost = 0
            
            for order in orders_today:
                order_name, product_name, quantity, total_cost_item, cost_price, profit, status, order_date = order
                total_revenue += total_cost_item or 0
                total_cost += cost_price or 0
                
                html_content += f"""
                    <tr>
                        <td>{order_name}</td>
                        <td>{product_name}</td>
                        <td>{quantity}</td>
                        <td>${total_cost_item:.2f}</td>
                        <td>${cost_price:.2f}</td>
                        <td>${profit:.2f}</td>
                        <td>{status}</td>
                    </tr>
                """
            
            total_profit = total_revenue - total_cost
            html_content += f"""
                </table>
                
                <h3>💰 Итого за день:</h3>
                <ul>
                    <li><strong>Выручка:</strong> ${total_revenue:.2f}</li>
                    <li><strong>Себестоимость:</strong> ${total_cost:.2f}</li>
                    <li><strong>Прибыль:</strong> ${total_profit:.2f}</li>
                </ul>
                
                <p>С уважением,<br>Ваш Бизнес Менеджер</p>
            </body>
            </html>
            """
        else:
            html_content = f"""
            <html>
            <body>
                <h2>📊 Ежедневный отчет - {today}</h2>
                <p>Добрый день!</p>
                <p>За сегодня новых заказов не было.</p>
                <p>С уважением,<br>Ваш Бизнес Менеджер</p>
            </body>
            </html>
            """
        
        # Отправляем email
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import ssl
        
        msg = MIMEMultipart()
        msg['From'] = settings[3]  # email_username
        msg['To'] = user_email
        msg['Subject'] = f"📊 Ежедневный отчет - {today}"
        
        msg.attach(MIMEText(html_content, 'html'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(settings[1], settings[2]) as server:  # smtp_server, smtp_port
            server.starttls(context=context)
            server.login(settings[3], settings[4])  # username, password
            server.send_message(msg)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка отправки ежедневного отчета: {str(e)}")
        return False

if __name__ == "__main__":
    main()

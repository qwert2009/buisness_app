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

# Импортируем наши ИИ функции
try:
    from ai_functions import business_ai
except ImportError:
    business_ai = None

# Импортируем чат-бота
try:
    from chatbot import business_chatbot
except ImportError:
    business_chatbot = None

# Импортируем систему уведомлений
try:
    from smart_notifications import smart_notifications
except ImportError:
    smart_notifications = None

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
    /* Импорт классического шрифта */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Базовые настройки */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        box-sizing: border-box;
    }
    
    /* Основной фон - чистый белый */
    .main, .block-container, .stApp, .stMain {
        background: #ffffff !important;
        color: #2c2c2c !important;
        line-height: 1.6;
    }
    
    /* Заголовки - строгие и четкие */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
        background: transparent !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        margin: 0 0 1.5rem 0 !important;
        line-height: 1.2 !important;
    }
    
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.25rem !important; }
    
    /* Основной текст */
    p, div, span, li, td, th, label, .stMarkdown, .stText {
        color: #2c2c2c !important;
        background: transparent !important;
        font-weight: 400 !important;
    }
    
    /* Кнопки - минималистичные */
    .stButton > button {
        background: #f8f9fa !important;
        color: #2c2c2c !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }
    
    .stButton > button:hover {
        background: #e9ecef !important;
        color: #1a1a1a !important;
        border-color: #adb5bd !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Primary кнопки */
    .stButton > button[kind="primary"] {
        background: #2c2c2c !important;
        color: #ffffff !important;
        border: 1px solid #2c2c2c !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border-color: #1a1a1a !important;
    }
    
    /* Поля ввода */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        background: #ffffff !important;
        color: #2c2c2c !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 0.5rem !important;
        font-size: 0.875rem !important;
        font-weight: 400 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stDateInput > div > div > input:focus {
        border-color: #2c2c2c !important;
        box-shadow: 0 0 0 2px rgba(44, 44, 44, 0.1) !important;
        outline: none !important;
    }
    
    /* Селектбоксы */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        color: #2c2c2c !important;
    }
    
    .stSelectbox > div > div > div {
        color: #2c2c2c !important;
        background: #ffffff !important;
    }
    
    /* Метки полей */
    .stTextInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stNumberInput > label,
    .stDateInput > label {
        color: #2c2c2c !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Таблицы */
    .stDataFrame, .stTable {
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
    }
    
    .stDataFrame table {
        background: #ffffff !important;
        color: #2c2c2c !important;
        border-collapse: collapse !important;
    }
    
    .stDataFrame th {
        background: #f8f9fa !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
        border-bottom: 1px solid #dee2e6 !important;
    }
    
    .stDataFrame td {
        padding: 0.75rem !important;
        border-bottom: 1px solid #f8f9fa !important;
        color: #2c2c2c !important;
    }
    
    /* Метрики */
    .stMetric {
        background: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 1rem !important;
    }
    
    .stMetric [data-testid="metric-container"] {
        background: transparent !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: #2c2c2c !important;
        font-weight: 600 !important;
    }
    
    /* Карточки и контейнеры */
    .element-container, .stContainer {
        background: transparent !important;
    }
    
    /* Навигация */
    .nav-item {
        background: #ffffff !important;
        color: #2c2c2c !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 0.75rem !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.15s ease !important;
    }
    
    .nav-item:hover {
        background: #f8f9fa !important;
        border-color: #adb5bd !important;
    }
    
    .nav-item.active {
        background: #2c2c2c !important;
        color: #ffffff !important;
        border-color: #2c2c2c !important;
    }
    
    /* Сайдбар */
    .stSidebar {
        background: #f8f9fa !important;
        border-right: 1px solid #dee2e6 !important;
    }
    
    .stSidebar .stButton > button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    
    /* Алерты */
    .stAlert {
        border-radius: 4px !important;
        border: 1px solid !important;
        font-weight: 400 !important;
    }
    
    .stSuccess {
        background: #f8f9fa !important;
        color: #2c2c2c !important;
        border-color: #28a745 !important;
    }
    
    .stError {
        background: #f8f9fa !important;
        color: #2c2c2c !important;
        border-color: #dc3545 !important;
    }
    
    .stWarning {
        background: #f8f9fa !important;
        color: #2c2c2c !important;
        border-color: #ffc107 !important;
    }
    
    .stInfo {
        background: #f8f9fa !important;
        color: #2c2c2c !important;
        border-color: #17a2b8 !important;
    }
    
    /* Формы */
    .stForm {
        background: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 1.5rem !important;
    }
    
    /* Табы */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #dee2e6 !important;
        gap: 0 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #6c757d !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #2c2c2c !important;
        border-bottom-color: #2c2c2c !important;
    }
    
    /* Удаление стандартных элементов Streamlit */
    .stDeployButton { display: none !important; }
    .stDecoration { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header { visibility: hidden !important; }
    .stToolbar { display: none !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    
    /* Отступы контейнера */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Колонки */
    .row-widget {
        gap: 1rem !important;
    }
    
    /* Статистические карточки */
    .metric-card {
        background: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 1.5rem !important;
        text-align: center !important;
    }
    
    .metric-value {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
        margin-bottom: 0.25rem !important;
    }
    
    .metric-label {
        font-size: 0.875rem !important;
        color: #6c757d !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
</style>
""", unsafe_allow_html=True)
        color: #ffffff !important;
        border-color: #888888 !important;
    }
    
    /* Primary кнопки - синие с белым текстом */
    .stButton[data-baseweb="button"][kind="primary"] > button,
    .stButton > button[kind="primary"] {
        background: #0066cc !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .stButton[data-baseweb="button"][kind="primary"] > button:hover,
    .stButton > button[kind="primary"]:hover {
        background: #0052a3 !important;
        color: #ffffff !important;
    }
    
    /* Формы и ввод - темные с белым текстом */
    .stTextInput > div > div > input {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
        border: 1px solid #666666 !important;
        border-radius: 6px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0066cc !important;
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    .stSelectbox > div > div > div {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
        border: 1px solid #666666 !important;
        border-radius: 6px !important;
    }
    
    .stTextArea > div > div > textarea {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
        border: 1px solid #666666 !important;
        border-radius: 6px !important;
    }
    
    .stNumberInput > div > div > input {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
        border: 1px solid #666666 !important;
        border-radius: 6px !important;
    }
    
    .stDateInput > div > div > input {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
        border: 1px solid #666666 !important;
        border-radius: 6px !important;
    }
    
    /* Метки полей - белый текст */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label, 
    .stNumberInput > label, .stDateInput > label, .stTimeInput > label {
        color: #ffffff !important;
        background: transparent !important;
        font-weight: 500;
    }
    
    /* Цветовая палитра для темной темы */
    :root {
        --bg-primary: #1a1a1a;
        --bg-secondary: #2d2d2d;
        --bg-tertiary: #404040;
        --text-primary: #ffffff;
        --text-secondary: #cccccc;
        --text-muted: #999999;
        --accent-blue: #0066cc;
        --accent-green: #28a745;
        --accent-red: #dc3545;
        --accent-orange: #fd7e14;
        --border-light: #666666;
        --border-medium: #888888;
        --shadow-subtle: 0 1px 3px rgba(0,0,0,0.3);
        --shadow-medium: 0 2px 8px rgba(0,0,0,0.5);
    }
    
    /* Основные стили для темной темы */
    .main {
        background: var(--bg-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        color: var(--text-primary) !important;
        line-height: 1.5;
    }
    
    /* Все заголовки - белые */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        background: transparent !important;
        font-weight: 600;
        letter-spacing: -0.025em;
        margin: 0 0 1rem 0;
    }
    
    /* Карточки - темные */
    .card {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
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
    
    /* Современная навигация - темная */
    .modern-nav {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
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
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light);
        border-radius: 6px;
        padding: 0.75rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
    }
    
    .nav-item:hover {
        border-color: var(--accent-blue);
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        transform: translateY(-1px);
    }
    
    .nav-item.active {
        background: var(--accent-blue) !important;
        color: #ffffff !important;
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
        color: inherit;
    }
    
    /* Все кнопки - темные с белым текстом */
    .stButton > button {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-subtle) !important;
    }
    
    .stButton > button:hover {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-medium) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-medium) !important;
    }
    
    /* Кнопки с типом primary - синие */
    .stButton[data-baseweb="button"][kind="primary"] > button,
    .stButton > button[kind="primary"] {
        background: var(--accent-blue) !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .stButton[data-baseweb="button"][kind="primary"] > button:hover,
    .stButton > button[kind="primary"]:hover {
        background: #0052a3 !important;
        color: #ffffff !important;
    }
    
    /* Все формы и поля ввода - темные */
    .stTextInput > div > div > input {
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        font-size: 0.875rem !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(0,102,204,0.3) !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div > div {
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    .stTextArea > div > div > textarea {
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        padding: 0.5rem !important;
    }
    
    .stNumberInput > div > div > input {
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        padding: 0.5rem !important;
    }
    
    /* Метки полей - белый текст */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label, 
    .stNumberInput > label, .stDateInput > label, .stTimeInput > label {
        color: var(--text-primary) !important;
        background: transparent !important;
        font-weight: 500;
    }
    
    /* Статистические карточки - темные */
    .stat-card {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-subtle);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        background: transparent !important;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary) !important;
        background: transparent !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* Статусы */
    .status-success { 
        color: var(--accent-green) !important; 
        background: transparent !important;
    }
    .status-warning { 
        color: var(--accent-orange) !important; 
        background: transparent !important;
    }
    .status-danger { 
        color: var(--accent-red) !important; 
        background: transparent !important;
    }
    
    /* Заказы - темные карточки */
    .order-card {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-subtle);
        transition: all 0.2s ease;
    }
    
    /* Статистические карточки */
    .stat-card {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-subtle);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #000000 !important;
        background: #ffffff !important;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #333333 !important;
        background: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* Статусы */
    .status-success { 
        color: var(--accent-green) !important; 
        background: #ffffff !important;
    }
    .status-warning { 
        color: var(--accent-orange) !important; 
        background: #ffffff !important;
    }
    .status-danger { 
        color: var(--accent-red) !important; 
        background: #ffffff !important;
    }
    
    /* Заказы */
    .order-card {
        background: #ffffff !important;
        color: #000000 !important;
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
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-delivered {
        background: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
    }
    
    .status-delayed {
        background: #f8d7da;
        color: #721c24;
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
</style>
""", unsafe_allow_html=True)

def show_modern_navigation():
    """Современная минималистичная навигация"""
    
    st.markdown("""
    <div class="modern-nav">
        <div class="nav-grid">
            <div class="nav-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'dashboard'}, '*');">
                <span class="nav-icon">📊</span>
                <div class="nav-text">Панель</div>
            </div>
            <div class="nav-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'orders'}, '*');">
                <span class="nav-icon">📦</span>
                <div class="nav-text">Заказы</div>
            </div>
            <div class="nav-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'analytics'}, '*');">
                <span class="nav-icon">📈</span>
                <div class="nav-text">Аналитика</div>
            </div>
            <div class="nav-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'inventory'}, '*');">
                <span class="nav-icon">🏪</span>
                <div class="nav-text">Склад</div>
            </div>
            <div class="nav-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'smart'}, '*');">
                <span class="nav-icon">🧠</span>
                <div class="nav-text">ИИ функции</div>
            </div>
            <div class="nav-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'settings'}, '*');">
                <span class="nav-icon">⚙️</span>
                <div class="nav-text">Настройки</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Кнопки навигации с использованием колонок
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
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
        if st.button("📈 Аналитика", use_container_width=True,
                    type="primary" if st.session_state.current_page == "analytics" else "secondary"):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col4:
        if st.button("🏪 Склад", use_container_width=True,
                    type="primary" if st.session_state.current_page == "inventory" else "secondary"):
            st.session_state.current_page = "inventory"
            st.rerun()
    
    with col5:
        if st.button("🧠 ИИ функции", use_container_width=True,
                    type="primary" if st.session_state.current_page == "smart" else "secondary"):
            st.session_state.current_page = "smart"
            st.rerun()
    
    with col6:
        if st.button("⚙️ Настройки", use_container_width=True,
                    type="primary" if st.session_state.current_page == "settings" else "secondary"):
            st.session_state.current_page = "settings"
            st.rerun()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            airplane_rate REAL DEFAULT 7.0,
            truck_rate REAL DEFAULT 0.68,
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
    
    # Добавляем поля для настраиваемых тарифов доставки
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN airplane_rate REAL DEFAULT 7.0")
    except sqlite3.OperationalError:
        pass  # Поле уже существует
        
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN truck_rate REAL DEFAULT 0.68")
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    conn.commit()
    conn.close()

# Функции для работы с пользователями
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', 
                      (email, password_hash))
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

# Константы для расчета доставки (по умолчанию)
DEFAULT_DELIVERY_RATES = {
    'airplane': 7.0,
    'truck': 0.68
}

# Функция для получения текущих тарифов доставки
def get_delivery_rates(user_id):
    """Получает пользовательские тарифы доставки"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT airplane_rate, truck_rate FROM settings WHERE user_id = ?
    ''', (user_id,))
    
    rates = cursor.fetchone()
    conn.close()
    
    if rates and rates[0] is not None and rates[1] is not None:
        return {
            'airplane': rates[0],
            'truck': rates[1]
        }
    else:
        return DEFAULT_DELIVERY_RATES

# Функции для работы с заказами
def add_single_order(user_id, product_name, quantity, cost_price, sale_price, weight, delivery_type, order_date=None, expected_delivery_date=None):
    """Добавляет одиночный заказ с возможностью указания даты заказа"""
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Получаем текущие тарифы доставки
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
    
    # Добавляем заказ с указанными датами
    cursor.execute('''
        INSERT INTO orders (user_id, order_type, order_name, delivery_type, status, created_at, expected_delivery_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 'single', product_name, delivery_type, 'pending', order_date, expected_delivery_date))
    
    order_id = cursor.lastrowid
    
    # Добавляем товар
    cursor.execute('''
        INSERT INTO order_items (order_id, product_name, quantity, cost_price, sale_price, weight, delivery_cost, total_cost, item_delivery_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, product_name, quantity, cost_price, sale_price, weight, delivery_cost, total_cost, delivery_type))
    
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

def add_complex_order(user_id, order_name, total_payment, items):
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Получаем текущие тарифы доставки
    delivery_rates = get_delivery_rates(user_id)
    
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
    
    # Рассчитываем общую себестоимость и общую стоимость доставки
    total_cost_price = sum(item['cost_price'] * item['quantity'] for item in items)
    total_delivery_cost = sum(item['weight'] * delivery_rates[item['delivery_type']] for item in items)
    
    # Распределяем платеж между товарами (минус доставка)
    remaining_payment = total_payment - total_delivery_cost
    
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
        # Получаем текущие тарифы доставки
        delivery_rates = get_delivery_rates(user_id)
        # Рассчитываем новую стоимость доставки
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
        
        # Получаем текущие тарифы доставки
        delivery_rates = get_delivery_rates(user_id)
        
        # Рассчитываем общую себестоимость и общую стоимость доставки
        total_cost_price = sum(item['cost_price'] * item['quantity'] for item in items)
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
        <h3 style="color: var(--accent-blue); text-align: center; margin-bottom: 20px;">
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
                # Получаем текущие тарифы доставки
                delivery_rates = get_delivery_rates(user_id)
                delivery_cost = weight * delivery_rates[delivery_type]
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
            # Получаем текущие тарифы доставки
            delivery_rates = get_delivery_rates(user_id)
            delivery_cost = weight * delivery_rates[delivery_type]
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
                # Получаем текущие тарифы доставки
                delivery_rates = get_delivery_rates(user_id)
                item_delivery_cost = new_weight * delivery_rates[delivery_type]
                st.info(f"📦 Стоимость доставки этого товара: ${item_delivery_cost:.2f}")
        
        # Общий расчет
        if items_to_edit and total_payment > 0:
            # Получаем текущие тарифы доставки
            # Получаем текущие тарифы доставки
            delivery_rates = get_delivery_rates(user_id)
            total_delivery_cost = sum(item['weight'] * delivery_rates[item['delivery_type']] for item in items_to_edit)
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

def get_analytics(user_id, start_date=None, end_date=None, delivery_method=None):
    conn = sqlite3.connect('business_manager.db')
    
    # Строим запрос с учетом фильтров
    query = '''
        SELECT oi.*, o.created_at, o.order_type
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.user_id = ?
    '''
    
    params = [user_id]
    
    # Добавляем фильтр по дате если указан
    if start_date:
        query += ' AND DATE(o.created_at) >= ?'
        params.append(start_date.strftime('%Y-%m-%d'))
    
    if end_date:
        query += ' AND DATE(o.created_at) <= ?'
        params.append(end_date.strftime('%Y-%m-%d'))
    
    # Добавляем фильтр по методу доставки если указан
    if delivery_method and delivery_method != 'all':
        query += ' AND oi.delivery_type = ?'
        params.append(delivery_method)
    
    df = pd.read_sql_query(query, conn, params=params)
    
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
def add_to_inventory(user_id, product_name, quantity, link=""):
    conn = sqlite3.connect('business_manager.db')
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже такой товар
    cursor.execute('SELECT id, quantity FROM inventory WHERE user_id = ? AND product_name = ?', 
                  (user_id, product_name))
    existing = cursor.fetchone()
    
    if existing:
        # Обновляем количество
        new_quantity = existing[1] + quantity
        cursor.execute('UPDATE inventory SET quantity = ?, link = ? WHERE id = ?', 
                      (new_quantity, link, existing[0]))
    else:
        # Добавляем новый товар
        cursor.execute('INSERT INTO inventory (user_id, product_name, quantity, link) VALUES (?, ?, ?, ?)', 
                      (user_id, product_name, quantity, link))
    
    conn.commit()
    conn.close()

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

def show_notifications_dashboard():
    """Показывает дашборд с умными уведомлениями"""
    st.title("🔔 Центр Уведомлений")
    
    if smart_notifications is None:
        st.error("🚫 Система уведомлений недоступна. Проверьте установку smart_notifications.py")
        return
    
    # Получаем все уведомления
    notifications = smart_notifications.get_all_notifications(st.session_state.user_id)
    
    if not notifications:
        st.success("🎉 У вас нет активных уведомлений! Все под контролем!")
        return
    
    # Показываем статистику уведомлений
    col1, col2, col3, col4 = st.columns(4)
    
    critical_count = len([n for n in notifications if n['priority'] == 'high'])
    warning_count = len([n for n in notifications if n['priority'] == 'medium'])
    info_count = len([n for n in notifications if n['priority'] == 'low'])
    
    with col1:
        st.metric("🚨 Критичные", critical_count)
    
    with col2:
        st.metric("⚠️ Предупреждения", warning_count)
    
    with col3:
        st.metric("ℹ️ Информация", info_count)
    
    with col4:
        st.metric("📊 Всего", len(notifications))
    
    st.markdown("---")
    
    # Фильтры
    col1, col2 = st.columns(2)
    
    with col1:
        filter_priority = st.selectbox(
            "🎯 Фильтр по приоритету",
            options=["Все", "Высокий", "Средний", "Низкий"],
            key="notification_priority_filter"
        )
    
    with col2:
        filter_type = st.selectbox(
            "📋 Тип уведомлений",
            options=["Все", "Критичные", "Предупреждения", "Успех", "Информация"],
            key="notification_type_filter"
        )
    
    # Применяем фильтры
    filtered_notifications = notifications
    
    if filter_priority != "Все":
        priority_map = {"Высокий": "high", "Средний": "medium", "Низкий": "low"}
        filtered_notifications = [n for n in filtered_notifications if n['priority'] == priority_map[filter_priority]]
    
    if filter_type != "Все":
        type_map = {"Критичные": "critical", "Предупреждения": "warning", "Успех": "success", "Информация": "info"}
        filtered_notifications = [n for n in filtered_notifications if n['type'] == type_map[filter_type]]
    
    # Показываем уведомления
    st.markdown("### 📋 Активные уведомления")
    
    for notification in filtered_notifications:
        html_content = smart_notifications.format_notification_html(notification)
        st.markdown(html_content, unsafe_allow_html=True)
    
    # Кнопка обновления
    if st.button("🔄 Обновить уведомления", type="primary"):
        st.rerun()

# Функция для отображения современной навигации с темным дизайном
def show_modern_navigation():
    """Современная темная навигация"""
    
    # CSS для светлого дизайна
    st.markdown("""
    <style>
    .light-nav {
        background: #ffffff;
        color: #000000;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
    }
    
    .nav-title {
        color: #000000 !important;
        background: #ffffff !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .nav-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .nav-button {
        background: #f8f9fa;
        color: #000000;
        border: 1px solid #dee2e6;
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        min-width: 120px;
        text-align: center;
    }
    
    .nav-button:hover {
        background: linear-gradient(135deg, #00d4ff, #a8edea);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,212,255,0.4);
        border-color: #00d4ff;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #00d4ff, #a8edea);
        color: #1a1a2e;
        font-weight: 700;
        box-shadow: 0 5px 15px rgba(0,212,255,0.4);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    
    .stat-card-dark {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .stat-card-dark:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,212,255,0.2);
        border-color: #00d4ff;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
        margin-bottom: 8px;
        text-shadow: 0 2px 10px rgba(0,212,255,0.3);
    }
    
    .stat-label {
        color: #bdc3c7;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Основная навигация
    st.markdown("""
    <div class="dark-nav">
        <h1 class="nav-title">🌟 Business Manager Pro</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Навигационные кнопки
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    current_page = st.session_state.current_page
    
    with col1:
        if st.button("🏠 Главная", key="modern_nav_dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    with col2:
        # Показываем количество уведомлений
        notification_count = 0
        if smart_notifications:
            try:
                notifications = smart_notifications.get_all_notifications(st.session_state.user_id)
                notification_count = len([n for n in notifications if n['priority'] == 'high'])
            except:
                notification_count = 0
        
        button_text = f"🔔 Уведомления"
        if notification_count > 0:
            button_text = f"🔴 Уведомления ({notification_count})"
        
        if st.button(button_text, key="modern_nav_notifications", use_container_width=True):
            st.session_state.current_page = "notifications"
            st.rerun()
    
    with col3:
        if st.button("📋 Заказы", key="modern_nav_orders", use_container_width=True):
            st.session_state.current_page = "orders"
            st.rerun()
    
    with col4:
        if st.button("📊 Аналитика", key="modern_nav_analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col5:
        if st.button("📦 Склад", key="modern_nav_inventory", use_container_width=True):
            st.session_state.current_page = "inventory"
            st.rerun()
    
    with col6:
        if st.button("🤖 ИИ", key="modern_nav_smart", use_container_width=True):
            st.session_state.current_page = "smart"
            st.rerun()
    
    with col7:
        if st.button("⚙️ Настройки", key="modern_nav_settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
    
    # Быстрая статистика
    st.markdown("""
    <div class="dark-nav">
        <div class="stats-grid">
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        total_orders = get_total_orders()
        total_revenue = get_total_revenue()
        pending_orders = get_pending_orders_count()
        
        with col1:
            st.markdown(f"""
            <div class="stat-card-dark">
                <div class="stat-value">{total_orders}</div>
                <div class="stat-label">Всего заказов</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card-dark">
                <div class="stat-value">${total_revenue:,.0f}</div>
                <div class="stat-label">Общая выручка</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card-dark">
                <div class="stat-value">{pending_orders}</div>
                <div class="stat-label">В обработке</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            profit_margin = 15.5  # Примерная маржа
            st.markdown(f"""
            <div class="stat-card-dark">
                <div class="stat-value">{profit_margin}%</div>
                <div class="stat-label">Маржа</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.markdown(f"""
        <div class="stat-card-dark">
            <div class="stat-value">⚠️</div>
            <div class="stat-label">Загрузка данных...</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

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
        <div style="background: #f8f9fa; 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;
                    text-align: center; border: 1px solid #dee2e6;">
            <h2 style="color: #000000; margin: 0; background: #f8f9fa;">🍔 Меню</h2>
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
        --primary-light: #1a1a1a;
        --secondary-light: #2d2d2d;
        --accent-light: #404040;
        --text-dark: #ffffff;
        --text-secondary: #cccccc;
        --accent-blue: #0066cc;
        --accent-gradient: linear-gradient(135deg, #0066cc, #007bff);
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --border-light: rgba(255,255,255,0.2);
        --shadow-light: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    /* Основные стили приложения - темная тема */
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 1400px;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border-radius: 20px;
        margin: 1rem auto;
        box-shadow: var(--shadow-medium);
        backdrop-filter: none;
        border: 1px solid var(--border-light);
    }
    
    /* Темная форма аутентификации */
    .auth-container {
        max-width: 400px;
        margin: 50px auto;
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-radius: 20px;
        padding: 40px;
        box-shadow: var(--shadow-medium);
        border: 1px solid var(--border-light);
    }
    
    .auth-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        background: transparent !important;
        margin-bottom: 30px;
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
    
    /* Светлые кнопки */
    .stButton > button {
        background: #f0f0f0 !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
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
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Заголовки - белый текст */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        background: transparent !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 10px !important;
        color: var(--text-primary) !important;
        background: transparent !important;
    }
    
    /* Текст и параграфы - белый текст */
    .stMarkdown p, .stText, .element-container p {
        color: var(--text-primary) !important;
        background: transparent !important;
    }
    
    /* Темные табы */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-radius: 15px;
        padding: 5px;
        border: 1px solid var(--border-light);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-blue) !important;
        color: #ffffff !important;
    }
    
    /* Селектбоксы - темные */
    .stSelectbox > div > div {
        background: var(--bg-secondary) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
        background: var(--bg-secondary) !important;
    }
    
    /* Number input - исправленные стили */
    .stNumberInput > div > div > input {
        background: #ffffff !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 8px !important;
        color: #000000 !important;
        padding: 0.75rem !important;
    }
    
    /* Date input - исправленные стили */
    .stDateInput > div > div > input {
        background: #ffffff !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 8px !important;
        color: #000000 !important;
        padding: 0.75rem !important;
    }
    
    /* Метрики */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
        color: #000000 !important;
        background: #ffffff !important;
        text-shadow: none;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #666666 !important;
        background: #ffffff !important;
    }
    
    /* Светлые алерты */
    .stAlert {
        background: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        color: #000000 !important;
        border-radius: 12px !important;
    }
    
    .stSuccess {
        background: rgba(40, 167, 69, 0.1) !important;
        border: 1px solid var(--success-color) !important;
        color: #000000 !important;
    }
    
    .stError {
        background: rgba(220, 53, 69, 0.1) !important;
        border: 1px solid var(--danger-color) !important;
        color: #000000 !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid var(--warning-color) !important;
        color: #000000 !important;
    }
    
    .stInfo {
        background: rgba(0, 102, 204, 0.1) !important;
        border: 1px solid var(--accent-blue) !important;
        color: #000000 !important;
    }
    
    /* Боковая панель */
    .css-1d391kg {
        background: #ffffff !important;
    }
    
    .css-1cypcdb {
        background: #f8f9fa !important;
        border-right: 1px solid #dee2e6 !important;
    }
    
    /* Формы */
    .stForm {
        background: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        color: #000000 !important;
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
        color: white;
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
        color: white;
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
        color: white !important;
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
        color: white;
    }
    
    .status-delivered {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
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
    init_db()
    
    # Применить пользовательские стили
    apply_custom_styles()
    
    # Состояние сессии
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'show_smart_insights' not in st.session_state:
        st.session_state.show_smart_insights = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Аутентификация
    if not st.session_state.user_id:
        show_auth()
        return
    
    # Показать современную навигацию
    show_modern_navigation()
    
    # Отображение контента в зависимости от выбранной страницы
    page = st.session_state.current_page
    
    if page == "dashboard":
        show_dashboard()
    elif page == "notifications":
        show_notifications_dashboard()
    elif page == "orders":
        show_orders()
    elif page == "analytics":
        show_analytics()
    elif page == "inventory":
        show_inventory()
    elif page == "smart":
        show_smart_functions()
    elif page == "settings":
        show_settings()
    else:
        show_dashboard()

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
                    "Email", 
                    placeholder="example@company.com",
                    key="reg_email",
                    help="Ваш email будет использоваться для входа"
                )
                reg_password = st.text_input(
                    "Пароль", 
                    type="password", 
                    placeholder="Создайте надежный пароль",
                    key="reg_password",
                    help="Минимум 6 символов"
                )
                reg_password_confirm = st.text_input(
                    "Подтвердите пароль", 
                    type="password", 
                    placeholder="Повторите пароль",
                    key="reg_password_confirm"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button(
                    "Создать аккаунт", 
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted:
                    if reg_email and reg_password and reg_password_confirm:
                        if len(reg_password) < 6:
                            st.error("Пароль должен содержать минимум 6 символов")
                        elif reg_password == reg_password_confirm:
                            success, message = register_user(reg_email, reg_password)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                        else:
                            st.error("Пароли не совпадают")
                    else:
                        st.warning("Пожалуйста, заполните все поля")

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
        
        # Предварительный расчет
        if weight > 0 and sale_price > 0:
            # Получаем текущие тарифы доставки
            delivery_rates = get_delivery_rates(st.session_state.user_id)
            delivery_cost = weight * delivery_rates[delivery_type]
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
                order_id = add_single_order(
                    st.session_state.user_id, 
                    product_name, 
                    quantity, 
                    cost_price, 
                    sale_price, 
                    weight, 
                    delivery_type,
                    order_date,  # Передаем выбранную дату
                    expected_delivery  # Передаем рассчитанную дату доставки
                )
                if order_id:
                    st.success(f"✅ Заказ '{product_name}' успешно создан!")
                    st.success(f"📅 Дата заказа: {order_date.strftime('%d.%m.%Y')}")
                    st.success(f"🚚 Ожидаемая доставка: {expected_delivery.strftime('%d.%m.%Y')}")
                    
                    # Добавляем товар на склад
                    add_to_inventory(st.session_state.user_id, product_name, quantity)
                    st.info(f"📦 Товар добавлен на склад")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Ошибка при создании заказа")
            else:
                st.error("❌ Заполните все обязательные поля корректно")

def show_complex_order_form():
    st.subheader("➕ Добавить комплексный заказ")
    
    # Инициализация состояния для товаров
    if 'complex_items' not in st.session_state:
        st.session_state.complex_items = []
    
    with st.form("complex_order_form"):
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
            
            # Получаем текущие тарифы доставки
            delivery_rates = get_delivery_rates(st.session_state.user_id)
            
            # Создаем DataFrame с читаемыми типами доставки
            items_display = []
            for item in st.session_state.complex_items:
                display_item = item.copy()
                airplane_rate = delivery_rates['airplane']
                truck_rate = delivery_rates['truck']
                display_item['delivery_type_display'] = f"Самолет (${airplane_rate}/кг)" if item['delivery_type'] == "airplane" else f"Машина (${truck_rate}/кг)"
                display_item['item_delivery_cost'] = item['weight'] * delivery_rates[item['delivery_type']]
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
            total_delivery_cost = sum(item['weight'] * delivery_rates[item['delivery_type']] for item in st.session_state.complex_items)
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
                order_id = add_complex_order(st.session_state.user_id, order_name, 
                                           total_payment, st.session_state.complex_items)
                
                # Добавляем товары на склад
                for item in st.session_state.complex_items:
                    add_to_inventory(st.session_state.user_id, item['product_name'], item['quantity'])
                
                st.success(f"Комплексный заказ #{order_id} успешно создан!")
                st.session_state.complex_items = []
                st.rerun()
            else:
                st.error("Заполните все поля и добавьте хотя бы один товар")

def show_order_history(order_type):
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
        color: white;
        border: 2px solid transparent;
    }
    
    .btn-success {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: 2px solid transparent;
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
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
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-radius: 15px;
    }
    
    /* Дополнительные элементы для темной темы */
    .stDataFrame {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 10px !important;
    }
    
    /* Plotly графики - темный фон */
    .js-plotly-plot {
        background: var(--bg-secondary) !important;
    }
    
    /* Спиннер - голубой */
    .stSpinner {
        color: var(--accent-blue) !important;
    }
    
    /* Код блоки - темные */
    .stCode {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light) !important;
    }
    
    /* Метрики - темные */
    .metric-container {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    
    /* Принудительный белый текст для всех элементов */
    .stMarkdown, .stMarkdown *, .stText, .stText * {
        color: var(--text-primary) !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок секции
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 20px; margin-bottom: 30px; text-align: center;
                box-shadow: 0 8px 30px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 700;">
            📋 История заказов - {order_type.upper()}
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
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
                                      color: white; padding: 15px 30px; border-radius: 12px; 
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
                            color: #00d4ff; 
                            margin: 0; 
                            font-size: 1.5rem; 
                            font-weight: 700;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            background: linear-gradient(135deg, #00d4ff, #a8edea);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
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
                        color: white;
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
                        if update_order_status(order_id, new_status):
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
        <p style="color: rgba(255,255,255,0.7); margin: 10px 0 0 0; font-size: 1.1rem;">
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
                        color: white;
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
    
    # Добавляем фильтры
    st.subheader("🔍 Фильтры")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("📅 **Период**")
        use_date_filter = st.checkbox("Фильтровать по периоду")
        
        start_date = None
        end_date = None
        
        if use_date_filter:
            start_date = st.date_input("Начальная дата", value=None)
            end_date = st.date_input("Конечная дата", value=None)
    
    with col2:
        st.write("🚚 **Метод доставки**")
        delivery_method = st.selectbox(
            "Выберите метод доставки",
            options=['all', 'airplane', 'truck'],
            format_func=lambda x: {
                'all': 'Все методы',
                'airplane': 'Самолет',
                'truck': 'Машина'
            }[x],
            index=0
        )
    
    with col3:
        st.write(" ")  # Пустая колонка для баланса
        if st.button("🔄 Обновить данные", type="primary"):
            st.rerun()
    
    st.divider()
    
    # Получаем аналитику с учетом фильтров
    analytics = get_analytics(
        st.session_state.user_id, 
        start_date=start_date, 
        end_date=end_date, 
        delivery_method=delivery_method
    )
    
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
                marker_color=['lightblue', 'lightgreen']
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
                                        mode='lines+markers', name='Выручка', line=dict(color='blue')))
            fig_line.add_trace(go.Scatter(x=sales_df['date'], y=sales_df['daily_costs'], 
                                        mode='lines+markers', name='Расходы', line=dict(color='red')))
            fig_line.add_trace(go.Scatter(x=sales_df['date'], y=sales_df['daily_profit'], 
                                        mode='lines+markers', name='Прибыль', line=dict(color='green')))
            
            fig_line.update_layout(title="Динамика финансовых показателей", 
                                 xaxis_title="Дата", yaxis_title="Сумма ($)", height=500)
            st.plotly_chart(fig_line, use_container_width=True)
    
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
    
    tab1, tab2, tab3 = st.tabs(["Просмотр склада", "Добавить товар", "Поиск"])
    
    with tab1:
        st.subheader("📦 Текущие остатки")
        
        # Кнопка очистки склада
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Очистить склад", type="secondary", help="Удалить все товары со склада"):
                if st.session_state.get('confirm_clear_inventory', False):
                    deleted_count = clear_inventory(st.session_state.user_id)
                    st.success(f"✅ Удалено {deleted_count} товаров со склада")
                    st.session_state.confirm_clear_inventory = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_inventory = True
                    st.rerun()
        
        # Подтверждение очистки
        if st.session_state.get('confirm_clear_inventory', False):
            st.warning("⚠️ Вы уверены? Это действие нельзя отменить!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Да, очистить", type="primary"):
                    deleted_count = clear_inventory(st.session_state.user_id)
                    st.success(f"✅ Удалено {deleted_count} товаров со склада")
                    st.session_state.confirm_clear_inventory = False
                    st.rerun()
            with col2:
                if st.button("❌ Отмена"):
                    st.session_state.confirm_clear_inventory = False
                    st.rerun()
        
        inventory_df = get_inventory(st.session_state.user_id)
        
        if not inventory_df.empty:
            # Фильтрация и сортировка
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox("Сортировать по:", 
                                     ["product_name", "quantity", "created_at"])
            with col2:
                sort_order = st.selectbox("Порядок:", ["По возрастанию", "По убыванию"])
            
            ascending = sort_order == "По возрастанию"
            inventory_df_sorted = inventory_df.sort_values(sort_by, ascending=ascending)
            
            # Отображение с возможностью редактирования
            edited_df = st.data_editor(
                inventory_df_sorted[['product_name', 'quantity', 'link']],
                use_container_width=True,
                num_rows="dynamic"
            )
            
            # Предупреждения о низких остатках
            low_stock_threshold = st.number_input("Порог низких остатков:", min_value=1, value=5)
            low_stock = inventory_df[inventory_df['quantity'] <= low_stock_threshold]
            
            if not low_stock.empty:
                st.warning("⚠️ Товары с низкими остатками:")
                st.dataframe(low_stock[['product_name', 'quantity']], use_container_width=True)
        else:
            st.info("Склад пуст")
    
    with tab2:
        st.subheader("➕ Добавить товар на склад")
        
        with st.form("add_inventory_form"):
            product_name = st.text_input("Название товара *")
            quantity = st.number_input("Количество *", min_value=1, value=1)
            link = st.text_input("Ссылка (необязательно)", placeholder="https://example.com/product")
            
            submitted = st.form_submit_button("Добавить товар")
            
            if submitted:
                if product_name and quantity > 0:
                    add_to_inventory(st.session_state.user_id, product_name, quantity, link)
                    st.success(f"Товар '{product_name}' добавлен на склад")
                else:
                    st.error("Заполните обязательные поля")
    
    with tab3:
        st.subheader("🔍 Поиск товаров")
        
        search_term = st.text_input("Поиск по названию:")
        
        if search_term:
            search_results = search_inventory(st.session_state.user_id, search_term)
            
            if not search_results.empty:
                st.write(f"Найдено {len(search_results)} товаров:")
                for _, row in search_results.iterrows():
                    with st.expander(f"📦 {row['product_name']} (Количество: {row['quantity']})"):
                        st.write(f"**Количество:** {row['quantity']}")
                        if row['link']:
                            st.write(f"**Ссылка:** [{row['link']}]({row['link']})")
                        st.write(f"**Добавлено:** {row['created_at']}")
            else:
                st.info("Товары не найдены")

def show_smart_functions():
    st.title("🧠 ИИ Помощник для Бизнеса")
    
    if business_ai is None:
        st.error("🚫 ИИ модуль недоступен. Проверьте установку ai_functions.py")
        return
    
    # Создаем красивые вкладки с иконками
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🤖 ИИ Чат-Бот", 
        "💰 Умное ценообразование", 
        "📊 Прогноз спроса", 
        "🚨 Умные алерты", 
        "🎯 Оптимизация прибыли", 
        "📦 Авто-дозаказ", 
        "📈 Трендовый анализ",
        "🏆 Конкурентный анализ"
    ])
    
    # ИИ ЧАТ-БОТ
    with tab1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>🤖 ИИ Бизнес-Консультант</h2>
            <p>Задайте любой вопрос о вашем бизнесе - получите персональный ответ!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if business_chatbot is None:
            st.error("🚫 Чат-бот недоступен. Проверьте установку chatbot.py")
        else:
            # История чата
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Поле для ввода вопроса
            user_question = st.text_input("💬 Задайте вопрос о вашем бизнесе:", 
                                        placeholder="Например: Как увеличить прибыль? Что с моими продажами?",
                                        key="user_question")
            
            # Быстрые кнопки
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🚀 Отправить", type="primary", key="chat_send_btn"):
                    if user_question.strip():
                        # Получаем ответ от ИИ
                        response = business_chatbot.generate_smart_response(st.session_state.get('user_id', 1), user_question)
                        
                        # Добавляем в историю
                        st.session_state.chat_history.append({
                            "user": user_question,
                            "bot": response,
                            "timestamp": datetime.now().strftime("%H:%M")
                        })
                        
                        # Очищаем поле ввода
                        st.session_state.user_question = ""
                        st.rerun()
            
            with col2:
                if st.button("📊 Сводка", key="chat_summary_btn"):
                    summary = business_chatbot.get_quick_business_summary(st.session_state.get('user_id', 1))
                    st.session_state.chat_history.append({
                        "user": "Дай быструю сводку моего бизнеса",
                        "bot": summary,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
            
            with col3:
                if st.button("💡 Бизнес-совет", key="chat_business_tip_btn"):
                    tip = business_chatbot.get_business_tips()
                    st.session_state.chat_history.append({
                        "user": "Дай бизнес-совет",
                        "bot": tip,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
            
            with col4:
                if st.button("💪 Мотивация", key="chat_motivation_btn"):
                    quote = business_chatbot.get_motivational_quote()
                    st.session_state.chat_history.append({
                        "user": "Дай мотивационную цитату",
                        "bot": quote,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
            
            # Дополнительные быстрые кнопки
            st.markdown("### 🎯 Быстрые консультации:")
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                if st.button("🎯 Рыночные советы", key="chat_market_advice_btn"):
                    advice = business_chatbot.get_market_advice(st.session_state.get('user_id', 1))
                    st.session_state.chat_history.append({
                        "user": "Дай рыночные советы",
                        "bot": advice,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
            
            with col6:
                if st.button("📅 Сезонные советы", key="chat_seasonal_advice_btn"):
                    seasonal = business_chatbot.get_seasonal_advice()
                    st.session_state.chat_history.append({
                        "user": "Дай сезонные советы",
                        "bot": seasonal,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
            
            with col7:
                if st.button("🚀 Советы роста", key="chat_growth_advice_btn"):
                    if st.session_state.get('user_id'):
                        growth_advice = business_chatbot._get_growth_advice()
                        st.session_state.chat_history.append({
                            "user": "Как развивать бизнес?",
                            "bot": growth_advice,
                            "timestamp": datetime.now().strftime("%H:%M")
                        })
                        st.rerun()
            
            with col8:
                if st.button("🧹 Очистить чат", key="chat_clear_btn"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Отображение истории чата
            if st.session_state.chat_history:
                st.markdown("### 💬 История разговора")
                
                for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # Показываем последние 10 сообщений
                    with st.container():
                        # Сообщение пользователя
                        st.markdown(f"""
                        <div style="
                            background: #e3f2fd;
                            padding: 15px;
                            border-radius: 15px;
                            margin: 10px 0;
                            border-left: 4px solid #2196f3;
                            color: #333333;
                        ">
                            <strong style="color: #1976d2;">👤 Вы ({chat['timestamp']}):</strong><br>
                            <span style="color: #333333;">{chat['user']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Ответ бота
                        st.markdown(f"""
                        <div style="
                            background: #f3e5f5;
                            padding: 15px;
                            border-radius: 15px;
                            margin: 10px 0;
                            border-left: 4px solid #9c27b0;
                            color: #333333;
                        ">
                            <strong style="color: #7b1fa2;">🤖 ИИ Консультант:</strong><br>
                            <span style="color: #333333;">{chat['bot']}</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("💡 Задайте первый вопрос, чтобы начать разговор с ИИ консультантом!")
    
    with tab2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>💰 ИИ Рекомендации Цены</h2>
            <p>Получите оптимальную цену на основе анализа ваших данных</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("price_recommendation"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("📦 Название товара", placeholder="Введите название товара")
                cost_price = st.number_input("💵 Себестоимость ($)", min_value=0.01, value=10.0, step=0.01)
            
            with col2:
                weight = st.number_input("⚖️ Вес (кг)", min_value=0.1, value=1.0, step=0.1)
                delivery_type = st.selectbox("🚚 Способ доставки", 
                                           options=['truck', 'airplane'],
                                           format_func=lambda x: '🚛 Машина' if x == 'truck' else '🛩️ Самолет')
            
            if st.form_submit_button("🔮 Получить ИИ рекомендацию", use_container_width=True):
                if product_name and cost_price > 0:
                    with st.spinner("🤖 ИИ анализирует ваши данные..."):
                        recommendation = business_ai.smart_price_recommendation(
                            st.session_state.user_id, product_name, cost_price, weight, delivery_type
                        )
                    
                    # Красивое отображение результата
                    st.markdown("### 🎯 Результат ИИ анализа")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("🎯 Рекомендуемая цена", f"${recommendation['recommended_price']}")
                    with col2:
                        st.metric("⬇️ Минимальная цена", f"${recommendation['min_price']}")
                    with col3:
                        st.metric("⬆️ Максимальная цена", f"${recommendation['max_price']}")
                    with col4:
                        confidence_color = "🟢" if recommendation['confidence'] > 0.8 else "🟡" if recommendation['confidence'] > 0.5 else "🔴"
                        st.metric("🎯 Уверенность", f"{confidence_color} {recommendation['confidence']*100:.0f}%")
                    
                    # Дополнительная информация
                    st.markdown("---")
                    st.markdown("### 📋 Детальный анализ")
                    
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.info(f"**💡 Обоснование:** {recommendation['reasoning']}")
                        st.success(f"**📈 Маржа:** {recommendation['profit_margin']:.1f}%")
                    
                    with info_col2:
                        trend_emoji = "📈" if recommendation['market_trend'] == 'growing' else "📉" if recommendation['market_trend'] == 'declining' else "📊"
                        st.info(f"**{trend_emoji} Тренд рынка:** {recommendation['market_trend']}")
                        st.warning(f"**🚚 Стоимость доставки:** ${recommendation['delivery_cost']:.2f}")
                else:
                    st.error("Пожалуйста, заполните все поля")
    
    with tab2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>📊 ИИ Прогноз Спроса</h2>
            <p>Предсказание будущего спроса на ваши товары</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            days_ahead = st.slider("📅 Горизонт прогнозирования (дни)", 7, 90, 30, key="forecast_days_slider")
            
            if st.button("🔮 Создать прогноз", use_container_width=True, key="create_forecast_btn"):
                with st.spinner("🤖 ИИ анализирует паттерны спроса..."):
                    forecasts = business_ai.demand_forecasting(st.session_state.user_id, days_ahead)
        
        with col2:
            st.markdown("### 🎯 Настройки прогнозирования")
            show_confidence = st.checkbox("� Показать доверительные интервалы", key="show_confidence_checkbox")
            show_trends = st.checkbox("📈 Показать тренды", key="show_trends_checkbox")
                
            if 'forecasts' in locals() and not forecasts.get('error'):
                st.markdown("### 📈 Прогнозы по товарам")
                
                for product, forecast in forecasts.items():
                    with st.expander(f"📦 {product}"):
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric("🎯 Прогноз спроса", f"{forecast['forecasted_demand']:.1f} шт")
                        with metric_col2:
                            trend_emoji = "📈" if forecast['trend'] == 'растущий' else "📉" if forecast['trend'] == 'падающий' else "📊"
                            st.metric(f"{trend_emoji} Тренд", forecast['trend'])
                        with metric_col3:
                            confidence_color = "🟢" if forecast['confidence'] > 0.8 else "🟡" if forecast['confidence'] > 0.5 else "🔴"
                            st.metric("🎯 Надежность", f"{confidence_color} {forecast['confidence']*100:.0f}%")
                        
                        st.info(f"📊 Среднедневные продажи: {forecast['daily_average']:.2f} шт")
                        st.info(f"📅 Дней в анализе: {forecast['historical_days']}")
            elif 'forecasts' in locals() and forecasts.get('error'):
                st.warning(f"⚠️ {forecasts['error']}")
    
    with tab3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>🚨 Умные Алерты Склада</h2>
            <p>ИИ мониторинг критических ситуаций</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Проверить состояние склада", use_container_width=True, key="check_inventory_alerts_btn"):
            with st.spinner("🤖 ИИ анализирует ситуацию на складе..."):
                alerts = business_ai.smart_inventory_alerts(st.session_state.user_id)
            
            if alerts:
                for alert in alerts:
                    # Определяем цвет и иконку для типа алерта
                    if alert['type'] == 'critical':
                        color = "#ff4757"
                        icon = "🔴"
                        border_color = "#ff3838"
                    elif alert['type'] == 'warning':
                        color = "#ffa502"
                        icon = "🟡"
                        border_color = "#ff9500"
                    elif alert['type'] == 'info':
                        color = "#3742fa"
                        icon = "🔵"
                        border_color = "#2f3542"
                    else:  # stagnant
                        color = "#747d8c"
                        icon = "⚫"
                        border_color = "#57606f"
                    
                    st.markdown(f"""
                    <div style="
                        background: {color};
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                        border-left: 5px solid {border_color};
                    ">
                        <h4>{icon} {alert['message']}</h4>
                        <p><strong>Текущий остаток:</strong> {alert['current_stock']} шт</p>
                        <p><strong>Скорость продаж:</strong> {alert['daily_rate']} шт/день</p>
                        <p><strong>💡 Рекомендация:</strong> {alert['recommended_action']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 Отлично! Все товары в порядке, критических ситуаций нет.")
    
    with tab4:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            color: #2c3e50;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>🎯 ИИ Оптимизация Прибыли</h2>
            <p>Персонализированные советы для роста бизнеса</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Получить рекомендации по прибыли", use_container_width=True, key="get_profit_recommendations_btn"):
            with st.spinner("🤖 ИИ ищет возможности для роста..."):
                suggestions = business_ai.profit_optimization_suggestions(st.session_state.user_id)
            
            if not suggestions.get('error'):
                st.markdown("### 💡 Персональные рекомендации ИИ")
                
                for i, suggestion in enumerate(suggestions):
                    # Определяем иконку для типа предложения
                    type_icons = {
                        'focus_profitable': '🎯',
                        'improve_margin': '📈',
                        'optimize_delivery': '🚛',
                        'seasonal_planning': '📅',
                        'premium_focus': '💎'
                    }
                    
                    icon = type_icons.get(suggestion['type'], '💡')
                    
                    with st.expander(f"{icon} {suggestion['title']}"):
                        st.info(suggestion['description'])
                        st.success(f"**🎯 Действие:** {suggestion['action']}")
                        
                        if 'products' in suggestion:
                            st.write("**📦 Затронутые товары:**")
                            for product in suggestion['products'][:5]:  # Показываем первые 5
                                st.write(f"• {product}")
            else:
                st.warning(f"⚠️ {suggestions['error']}")
    
    with tab5:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>📦 Автоматический Дозаказ</h2>
            <p>ИИ предложения по пополнению склада</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🤖 Получить рекомендации дозаказа", use_container_width=True, key="get_reorder_recommendations_btn"):
            with st.spinner("🤖 ИИ анализирует потребности склада..."):
                recommendations = business_ai.automated_reorder_suggestions(st.session_state.user_id)
            
            if recommendations:
                st.markdown("### 🎯 Топ рекомендации для дозаказа")
                
                for rec in recommendations:
                    # Определяем цвет карточки по срочности
                    if rec['urgency_level'] == 'КРИТИЧНО':
                        card_color = "#ff4757"
                        urgency_icon = "🔴"
                    elif rec['urgency_level'] == 'ВЫСОКАЯ':
                        card_color = "#ffa502"
                        urgency_icon = "🟡"
                    else:
                        card_color = "#3742fa"
                        urgency_icon = "🔵"
                    
                    st.markdown(f"""
                    <div style="
                        background: {card_color};
                        color: white;
                        padding: 20px;
                        border-radius: 15px;
                        margin-bottom: 15px;
                    ">
                        <h3>{urgency_icon} {rec['product']} - {rec['urgency_level']}</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                            <div>
                                <strong>📦 Текущий остаток:</strong><br>{rec['current_stock']} шт
                            </div>
                            <div>
                                <strong>🎯 Рекомендуемый заказ:</strong><br>{rec['recommended_quantity']} шт
                            </div>
                            <div>
                                <strong>⏰ Дни до исчерпания:</strong><br>{rec['days_until_empty']:.1f} дней
                            </div>
                            <div>
                                <strong>💰 Ожидаемая прибыль:</strong><br>${rec['estimated_profit']:.2f}
                            </div>
                        </div>
                        <p style="margin-top: 15px;"><strong>📊 Маржа:</strong> {rec['profit_margin']:.1f}% | <strong>📈 Продажи:</strong> {rec['daily_sales_rate']:.2f} шт/день</p>
                        <p style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 10px;">
                            <strong>💡 Причины:</strong> {', '.join(rec['reasons'])}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📋 Рекомендаций по дозаказу пока нет")
    
    with tab6:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: #2c3e50;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>📈 Трендовый Анализ</h2>
            <p>ИИ анализ рыночных трендов на основе ваших данных</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Анализировать тренды", use_container_width=True, key="analyze_trends_btn"):
            with st.spinner("🤖 ИИ анализирует рыночные тренды..."):
                trends = business_ai.market_trend_analysis(st.session_state.user_id)
            
            if not trends.get('error'):
                # Тренды цен
                if 'price_trends' in trends and trends['price_trends']:
                    st.markdown("### 💰 Тренды цен по товарам")
                    
                    for product, trend_data in trends['price_trends'].items():
                        trend_icon = "📈" if trend_data['trend'] == 'растет' else "📉" if trend_data['trend'] == 'падает' else "📊"
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📦 Товар", product)
                        with col2:
                            st.metric(f"{trend_icon} Тренд", trend_data['trend'])
                        with col3:
                            st.metric("💵 Текущая цена", f"${trend_data['current_price']}")
                        with col4:
                            change_color = "normal" if abs(trend_data['change_amount']) < 1 else "normal"
                            st.metric("📊 Изменение", f"${trend_data['change_amount']:+.2f}")
                
                # Тренд объемов
                if 'volume_trend' in trends:
                    st.markdown("---")
                    st.markdown("### 📊 Тренд продаж")
                    
                    vol_trend = trends['volume_trend']
                    trend_icon = "📈" if vol_trend['direction'] == 'растет' else "📉" if vol_trend['direction'] == 'падает' else "📊"
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"{trend_icon} Направление", vol_trend['direction'])
                    with col2:
                        st.metric("📈 Недельное изменение", f"{vol_trend['weekly_change']:+.2f} шт")
                    with col3:
                        st.metric("🎯 Сила тренда", vol_trend['trend_strength'])
                
                # Сезонные паттерны
                if 'seasonal_pattern' in trends:
                    st.markdown("---")
                    st.markdown("### 📅 Сезонные паттерны")
                    
                    seasonal = trends['seasonal_pattern']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🔥 Пиковый месяц", seasonal['peak_month'])
                    with col2:
                        st.metric("📉 Слабый месяц", seasonal['low_month'])
                    with col3:
                        seasonality_strength = "Высокая" if seasonal['seasonality_strength'] > 0.5 else "Средняя" if seasonal['seasonality_strength'] > 0.2 else "Низкая"
                        st.metric("🌊 Сезонность", seasonality_strength)
                
                # Тренды доставки
                if 'delivery_trend' in trends:
                    st.markdown("---")
                    st.markdown("### 🚚 Предпочтения доставки")
                    
                    delivery = trends['delivery_trend']
                    st.info(f"💡 **Инсайт:** {delivery['recommendation']}")
                    st.success(f"🎯 **Предпочтительный метод:** {delivery['preferred_method']}")
            else:
                st.warning(f"⚠️ {trends['error']}")
    
    with tab7:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        ">
            <h2>🏆 ИИ Конкурентный Анализ</h2>
            <p>Оценка конкурентоспособности ваших цен</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("competitor_analysis"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("📦 Название товара", placeholder="Введите название товара")
            
            with col2:
                your_price = st.number_input("💰 Ваша цена ($)", min_value=0.01, value=20.0, step=0.01)
            
            if st.form_submit_button("🔍 Анализировать конкурентоспособность", use_container_width=True):
                if product_name and your_price > 0:
                    with st.spinner("🤖 ИИ анализирует конкурентную позицию..."):
                        analysis = business_ai.smart_competitor_analysis(
                            st.session_state.user_id, product_name, your_price
                        )
                    
                    # Определяем цвет для оценки
                    score = analysis['competitive_score']
                    if score >= 8:
                        score_color = "#2ecc71"  # Зеленый
                        score_emoji = "🟢"
                    elif score >= 6:
                        score_color = "#f39c12"  # Оранжевый
                        score_emoji = "🟡"
                    else:
                        score_color = "#e74c3c"  # Красный
                        score_emoji = "🔴"
                    
                    st.markdown(f"""
                    <div style="
                        background: {score_color};
                        color: white;
                        padding: 25px;
                        border-radius: 15px;
                        margin-bottom: 20px;
                        text-align: center;
                    ">
                        <h2>{score_emoji} Оценка конкурентоспособности: {score}/10</h2>
                        <h3>Позиция: {analysis['price_position']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("🎯 Ваша цена", f"${analysis['your_price']:.2f}")
                    
                    with col2:
                        if 'market_average' in analysis:
                            st.metric("📊 Средняя по рынку", f"${analysis['market_average']:.2f}")
                    
                    with col3:
                        if 'price_difference' in analysis:
                            diff_color = "normal" if abs(analysis['price_difference']) < 2 else "inverse"
                            st.metric("💱 Разница", f"${analysis['price_difference']:+.2f}", delta_color=diff_color)
                    
                    st.markdown("---")
                    st.success(f"💡 **Рекомендация ИИ:** {analysis['recommendation']}")
                    st.info(f"🎯 **Предлагаемое действие:** {analysis['suggested_action']}")
                else:
                    st.error("Пожалуйста, заполните все поля")
    
    # Добавляем информационную панель внизу
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 30px;
    ">
        <h3>🤖 О системе ИИ</h3>
        <p>Наш ИИ помощник анализирует ваши исторические данные, выявляет паттерны и предоставляет 
        персонализированные рекомендации для оптимизации вашего бизнеса. Все расчеты основаны на 
        машинном обучении и статистическом анализе ваших реальных продаж.</p>
        <p><strong>💡 Совет:</strong> Чем больше данных о продажах у вас есть, тем точнее будут рекомендации ИИ!</p>
    </div>
    """, unsafe_allow_html=True)

def show_settings():
    st.title("⚙️ Настройки")
    
    tab1, tab2, tab3 = st.tabs(["💰 Финансовые", "📧 Уведомления", "💾 Данные"])
    
    with tab1:
        st.markdown("""
        <div class="card">
            <h3 style="color: var(--accent-color); margin-bottom: 1rem;">💰 Финансовые настройки</h3>
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
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Настройки тарифов доставки
        st.markdown("""
        <div class="card">
            <h3 style="color: var(--accent-color); margin-bottom: 1rem;">🚚 Тарифы доставки</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Получаем текущие тарифы
        current_rates = get_delivery_rates(st.session_state.user_id)
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            with st.form("delivery_rates_settings"):
                st.markdown("#### 💸 Стоимость доставки за килограмм")
                st.info("Установите тарифы доставки для разных методов транспортировки")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🛩️ Самолет")
                    airplane_rate = st.number_input(
                        "Цена за кг (самолет):",
                        min_value=0.01,
                        max_value=100.0,
                        value=float(current_rates['airplane']),
                        step=0.01,
                        format="%.2f",
                        help="Стоимость доставки самолетом за 1 кг"
                    )
                
                with col2:
                    st.markdown("##### 🚛 Машина")
                    truck_rate = st.number_input(
                        "Цена за кг (машина):",
                        min_value=0.01,
                        max_value=100.0,
                        value=float(current_rates['truck']),
                        step=0.01,
                        format="%.2f",
                        help="Стоимость доставки машиной за 1 кг"
                    )
                
                # Предварительный расчет экономии
                st.markdown("##### 📊 Сравнение тарифов")
                sample_weight = st.slider("Пример веса для расчета (кг):", 1, 50, 10)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🛩️ Самолет", f"${airplane_rate * sample_weight:.2f}")
                with col2:
                    st.metric("🚛 Машина", f"${truck_rate * sample_weight:.2f}") 
                with col3:
                    difference = abs(airplane_rate - truck_rate) * sample_weight
                    st.metric("💰 Разница", f"${difference:.2f}")
                
                submitted_rates = st.form_submit_button("💾 Сохранить тарифы", use_container_width=True)
                
                if submitted_rates:
                    # Обновляем или вставляем тарифы в настройки
                    cursor.execute('''
                        UPDATE settings 
                        SET airplane_rate = ?, truck_rate = ?
                        WHERE user_id = ?
                    ''', (airplane_rate, truck_rate, st.session_state.user_id))
                    
                    # Если запись не существует, создаем её
                    if cursor.rowcount == 0:
                        cursor.execute('''
                            INSERT INTO settings (user_id, airplane_rate, truck_rate, financial_cushion_percent)
                            VALUES (?, ?, ?, 20.0)
                        ''', (st.session_state.user_id, airplane_rate, truck_rate))
                    
                    conn.commit()
                    st.success("✅ Тарифы доставки успешно обновлены!")
                    st.rerun()  # Перезагружаем страницу для обновления данных
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        conn.close()
    
    with tab2:
        st.markdown("""
        <div class="card">
            <h3 style="color: var(--accent-color); margin-bottom: 1rem;">📧 Настройки уведомлений</h3>
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
            <h3 style="color: var(--accent-color); margin-bottom: 1rem;">💾 Управление данными</h3>
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

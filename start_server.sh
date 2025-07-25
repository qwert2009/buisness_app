#!/bin/bash
# Скрипт для запуска приложения как веб-сервер

echo "🚀 Запуск Business Manager Web Server..."
echo "=================================="

# Проверяем установку Python и Streamlit
python --version
pip show streamlit > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  Streamlit не установлен. Устанавливаем..."
    pip install streamlit
fi

# Получаем IP адрес
IP=$(hostname -I | awk '{print $1}')
echo "🌐 Приложение будет доступно по адресам:"
echo "   Локально: http://localhost:8501"
echo "   В сети:   http://$IP:8501"
echo "=================================="

# Запускаем приложение
streamlit run business_manager.py --server.address 0.0.0.0 --server.port 8501

echo "✅ Сервер остановлен"

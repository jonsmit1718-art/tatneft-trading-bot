#!/usr/bin/env python3
"""
Бот для трейдинга по Татнефту
Отправляет сводку перед началом торгов
"""

import requests
import json
from datetime import datetime
import pytz

# ========== НАСТРОЙКИ ==========
# Получаем секреты из переменных окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
# ================================

def get_current_time():
    """Текущее московское время"""
    msk_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(msk_tz)

def is_trading_day(date):
    """Проверяем, торговый ли день (упрощенно)"""
    # Праздники Московской биржи 2024 (основные)
    holidays = [
        '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
        '2024-01-08', '2024-02-23', '2024-03-08', '2024-05-01', '2024-05-09',
        '2024-06-12', '2024-11-04'
    ]
    
    # Выходные: суббота (5) и воскресенье (6)
    if date.weekday() >= 5:
        return False
    
    # Проверяем праздники
    if date.strftime('%Y-%m-%d') in holidays:
        return False
    
    return True

def get_stock_prices():
    """Получаем цены акций Татнефта с MOEX ISS API"""
    try:
        # Обыкновенные акции (TATN)
        tatn_url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities/TATN.json"
        tatn_response = requests.get(tatn_url, timeout=10)
        tatn_data = tatn_response.json()
        
        # Привилегированные акции (TATNP)
        tatnp_url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities/TATNP.json"
        tatnp_response = requests.get(tatnp_url, timeout=10)
        tatnp_data = tatnp_response.json()
        
        # Парсим последние цены (упрощенно)
        tatn_price = "Н/Д"
        tatnp_price = "Н/Д"
        
        if 'marketdata' in tatn_data and 'data' in tatn_data['marketdata']:
            tatn_price = tatn_data['marketdata']['data'][0][12]  # LAST цена
        
        if 'marketdata' in tatnp_data and 'data' in tatnp_data['marketdata']:
            tatnp_price = tatnp_data['marketdata']['data'][0][12]
        
        return {
            'TATN': tatn_price,
            'TATNP': tatnp_price
        }
    except:
        return {'TATN': 'Ошибка', 'TATNP': 'Ошибка'}

def get_brent_price():
    """Цена нефти Brent"""
    try:
        # Используем публичный API (пример)
        response = requests.get("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=BZ&apikey=demo", timeout=10)
        data = response.json()
        
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            return data['Global Quote']['05. price']
    except:
        pass
    
    return "Н/Д"

def get_tatneft_news():
    """Последние новости Татнефта"""
    try:
        # RSS Татнефта
        import feedparser
        feed = feedparser.parse("https://www.tatneft.ru/press-tsentr/novosti?format=feed&type=rss")
        
        news_items = []
        for entry in feed.entries[:3]:  # Последние 3 новости
            news_items.append(f"• {entry.title}")
        
        if news_items:
            return "\n".join(news_items)
    except:
        pass
    
    return "Новости временно недоступны"

def send_telegram_message(text):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def generate_report():
    """Генерация трейдинговой сводки"""
    current_time = get_current_time()
    
    # Определяем время отправки
    if is_trading_day(current_time):
        # Будний день - 6:40
        report_time = current_time.replace(hour=6, minute=40, second=0, microsecond=0)
    else:
        # Выходной или праздник - 9:40
        report_time = current_time.replace(hour=9, minute=40, second=0, microsecond=0)
    
    # Получаем данные
    prices = get_stock_prices()
    brent = get_brent_price()
    news = get_tatneft_news()
    
    # Формируем сообщение
    report = f"""
📈 <b>Трейдинговая сводка Татнефть</b>
⏰ <b>Время:</b> {current_time.strftime('%d.%m.%Y %H:%M')} МСК

<b>Акции:</b>
• TATN (обыкн.): {prices['TATN']} руб.
• TATNP (прив.): {prices['TATNP']} руб.

<b>Нефть Brent:</b> ${brent}

<b>Последние новости:</b>
{news}

<b>Следующая сводка:</b> {report_time.strftime('%H:%M')} МСК
"""
    
    return report

def main():
    """Основная функция"""
    print("Запуск бота Татнефть...")
    
    # Проверяем наличие секретов
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не установлены!")
        print("Добавьте секреты в GitHub Actions")
        return
    
    # Генерируем и отправляем отчет
    report = generate_report()
    
    if send_telegram_message(report):
        print("Отчет успешно отправлен!")
    else:
        print("Ошибка отправки отчета")

if __name__ == "__main__":
    main()

import os
import requests
from datetime import datetime
import pytz

def get_stock_prices():
    try:
        def get_current_price(ticker):
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}.json"
            params = {'iss.meta': 'off', 'iss.json': 'extended'}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if len(data) > 1 and 'marketdata' in data[1]:
                marketdata = data[1]['marketdata']
                if marketdata['data']:
                    row = marketdata['data'][0]
                    last_price = float(row[0]) if row[0] else 0
                    return f"{last_price:.2f}"
            return "Н/Д"
        
        return {
            'TATN': get_current_price('TATN'),
            'TATNP': get_current_price('TATNP')
        }
    except:
        return {'TATN': '584.30', 'TATNP': '541.00'}

def get_brent_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ%3DF"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                price = result['meta']['regularMarketPrice']
                return f"{price:.2f}"
        return "60.72"
    except:
        return "60.72"

def generate_analytics(tatn_price, tatnp_price):
    try:
        tatn = float(tatn_price) if tatn_price != 'Н/Д' else 584.30
        tatnp = float(tatnp_price) if tatnp_price != 'Н/Д' else 541.00
        
        tatn_support = round(tatn * 0.99, 2)
        tatn_resistance = round(tatn * 1.01, 2)
        spread = round(tatn - tatnp, 2)
        spread_percent = round((spread / tatnp) * 100, 2)
        
        if spread_percent > 8.5:
            arbitrage_status = "🔴 ВЫСОКАЯ"
        elif spread_percent < 7.5:
            arbitrage_status = "🟢 НИЗКАЯ"
        else:
            arbitrage_status = "⚪ НОРМА"
        
        return f"""
📊 <b>КРАТКАЯ АНАЛИТИКА:</b>
🎯 <b>УРОВНИ ДЛЯ TATN:</b>
• Поддержка: {tatn_support} руб.
• Сопротивление: {tatn_resistance} руб.
🔄 <b>АРБИТРАЖ:</b>
• Разница: {spread} руб. ({spread_percent}%)
• Статус: {arbitrage_status}
"""
    except:
        return "📊 <b>Аналитика временно недоступна</b>"

def main():
    prices = get_stock_prices()
    brent = get_brent_price()
    msk_tz = pytz.timezone('Europe/Moscow')
    msk_time = datetime.now(msk_tz)
    
    report = f"""
🟢 <b>ТОРГОВЫЙ ДЕНЬ</b>
📈 <b>ТРЕЙДИНГОВАЯ СВОДКА ТАТНЕФТЬ</b>
⏰ <b>Время:</b> {msk_time.strftime('%d.%m.%Y %H:%M')} МСК

<b>ТЕКУЩИЕ ЦЕНЫ:</b>
• TATN: {prices['TATN']} руб.
• TATNP: {prices['TATNP']} руб.
<b>НЕФТЬ BRENT:</b> ${brent}

{generate_analytics(prices['TATN'], prices['TATNP'])}

<b>СЛЕДУЮЩИЙ ОТЧЕТ:</b> 06:40 МСК
"""
    
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print("DEBUG: Проверка переменных...")
    print(f"Токен: {'Есть' if token else 'Нет'}")
    print(f"Chat ID: {'Есть' if chat_id else 'Нет'}")
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": report,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=data, timeout=10)
            print(f"Статус: {response.status_code}")
            if response.status_code == 200:
                print("✅ Отчет отправлен!")
                return True
            else:
                print(f"Ошибка: {response.text}")
                return False
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            return False
    else:
        print("❌ Нет токена или Chat ID")
        return False

if __name__ == "__main__":
    main()

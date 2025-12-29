# ... остальной код ...

def main():
    """Основная функция"""
    # Получаем данные
    prices = get_stock_prices()
    brent = get_brent_price()
    
    # Время
    msk_tz = pytz.timezone('Europe/Moscow')
    msk_time = datetime.now(msk_tz)
    
    # Формируем отчет
    report = f"""
🟢 <b>ТОРГОВЫЙ ДЕНЬ</b>
📈 <b>ТРЕЙДИНГОВАЯ СВОДКА ТАТНЕФТЬ</b>
⏰ <b>Время:</b> {msk_time.strftime('%d.%m.%Y %H:%M')} МСК

<b>ТЕКУЩИЕ ЦЕНЫ:</b>
• TATN (обыкн.): {prices['TATN']} руб.
• TATNP (прив.): {prices['TATNP']} руб.

<b>НЕФТЬ BRENT:</b> ${brent}

<b>АКТУАЛЬНЫЕ НОВОСТИ:</b>
• Данные по запасам нефти в США в 17:30 МСК
• Акции нефтяного сектора в фокусе
• Дивидендная отсечка ожидается в марте 2026

{generate_analytics(prices['TATN'], prices['TATNP'])}

<b>СЛЕДУЮЩИЙ ОТЧЕТ:</b> 06:40 МСК (завтра)
<b>ДЕЙСТВИЕ:</b> Начало торгов через 20 минут
"""
    
    # Отправляем в Telegram
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    # Добавляем отладку
    print(f"DEBUG: Token exists: {token is not None}")
    print(f"DEBUG: Chat ID exists: {chat_id is not None}")
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": report,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print("✅ Отчет отправлен в Telegram!")
                print(f"Сообщение отправлено в чат: {chat_id}")
            else:
                print(f"❌ Ошибка Telegram API: {response.status_code}")
                print(f"Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
    else:
        print("❌ Не указаны Telegram токен или Chat ID")
        print(f"Token: {'Указан' if token else 'НЕ указан'}")
        print(f"Chat ID: {'Указан' if chat_id else 'НЕ указан'}")

if __name__ == "__main__":
    main()

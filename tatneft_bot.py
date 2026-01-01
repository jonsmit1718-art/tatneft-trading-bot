import os
import requests
from datetime import datetime
import pytz

def main():
    print("=== БОТ ЗАПУЩЕН ===")
    
    # Получаем секреты
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print(f"Токен получен: {'ДА' if token else 'НЕТ'}")
    print(f"Chat ID получен: {'ДА' if chat_id else 'НЕТ'}")
    
    if not token or not chat_id:
        print("❌ ОШИБКА: Не указаны токен или chat_id")
        return False
    
    # Получаем время
    msk_tz = pytz.timezone('Europe/Moscow')
    msk_time = datetime.now(msk_tz)
    
    # Формируем сообщение
    message = f"""
✅ <b>ТОРГОВЫЙ ОТЧЕТ ТАТНЕФТЬ</b>
⏰ <b>Время:</b> {msk_time.strftime('%H:%M')} МСК
📅 <b>Дата:</b> {msk_time.strftime('%d.%m.%Y')}

<b>СТАТУС:</b> Бот работает исправно
<b>СЛЕДУЮЩИЙ ОТЧЕТ:</b> 06:40 МСК

🟢 <b>ВСЕ СИСТЕМЫ В НОРМЕ</b>
"""
    
    # Отправляем в Telegram
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Статус ответа Telegram: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ СООБЩЕНИЕ ОТПРАВЛЕНО В TELEGRAM")
            return True
        else:
            print(f"❌ ОШИБКА TELEGRAM: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА ПРИ ОТПРАВКЕ: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

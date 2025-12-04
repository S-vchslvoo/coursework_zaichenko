import requests

TELEGRAM_BOT_TOKEN = '8377778897:AAEHRtZB2ZzA7iIIZTObhnn3ZOUALnWRjHc'
TELEGRAM_CHAT_ID = '1038056468' 

def send_telegram_order(cart_products, phone, address, total_price):
    if not cart_products:
        return

    message = f"🛒 <b>Новый заказ!</b>\n\n"
    message += f"👤 <b>Телефон:</b> {phone}\n"
    message += f"📍 <b>Адрес:</b> {address}\n\n"
    message += "📦 <b>Товары:</b>\n"

    for p in cart_products:
        art = p.article if p.article else "Без арт."
        message += f"- {p.title} (Арт: {art}) — {p.price} руб.\n"

    message += f"\n💰 <b>Итого:</b> {total_price} руб."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
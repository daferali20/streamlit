import requests

def send_telegram_alert(message: str, bot_token: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        return False

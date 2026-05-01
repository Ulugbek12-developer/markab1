import requests
import logging
from config import config

logger = logging.getLogger(__name__)

def send_admin_notification(text):
    """
    Sends a notification message to the Telegram admin.
    """
    token = config.BOT_TOKEN.get_secret_value()
    admin_id = config.ADMIN_ID
    
    if not admin_id:
        logger.warning("ADMIN_ID not set in config. Telegram notification skipped.")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": admin_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        print(f"DEBUG: Sending telegram notification to {admin_id}...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"DEBUG: Telegram response: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"DEBUG: Error sending Telegram notification: {e}")
        logger.error(f"Error sending Telegram notification: {e}")
        return None

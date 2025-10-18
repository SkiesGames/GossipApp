import requests
import time

import config


def send_notification(text, token=config.TELEGRAM_BOT_TOKEN, chat_id=config.TELEGRAM_CHAT_ID):
    """
    Send a custom message to a Telegram chat via bot.
    
    Args:
        text (str): The message text to send
        token (str): Telegram bot token (default: provided token)
        chat_id (str): Telegram chat ID (default: provided chat ID)
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    
    max_attempts = 3
    timeout = 3
    delay = 5
    
    for attempt in range(max_attempts):
        try:
            response = requests.post(url, timeout=timeout)
            
            if response.status_code == 200:
                print(f"Notification sent successfully on attempt {attempt + 1}")
                return True
            else:
                print(f"Attempt {attempt + 1} failed with status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
        
        # Wait before next attempt (except on last attempt)
        if attempt < max_attempts - 1:
            print(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print("All attempts failed. Notification could not be sent.")
    return False

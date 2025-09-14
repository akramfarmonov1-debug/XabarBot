import requests
import json
import logging

logger = logging.getLogger(__name__)

def send_message_to_telegram(bot_token, chat_id, text):
    """
    Telegram botiga xabar yuborish funksiyasi
    
    Args:
        bot_token (str): Telegram bot tokeni
        chat_id (str/int): Chat ID
        text (str): Yuborilishi kerak bo'lgan xabar matni
    
    Returns:
        dict: Telegram API javobini qaytaradi
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        else:
            logger.error(f"Telegram API xatosi: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        logger.error("Telegram API ga murojaat vaqtida timeout xatosi")
        return {
            'success': False,
            'error': "Timeout xatosi"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API ga murojaat xatosi: {str(e)}")
        return {
            'success': False,
            'error': f"So'rov xatosi: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Kutilmagan xato: {str(e)}")
        return {
            'success': False,
            'error': f"Kutilmagan xato: {str(e)}"
        }

def get_bot_info(bot_token):
    """
    Bot haqida ma'lumot olish funksiyasi
    
    Args:
        bot_token (str): Telegram bot tokeni
    
    Returns:
        dict: Bot ma'lumotlari yoki xato
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return {
                    'success': True,
                    'data': data['result']
                }
            else:
                return {
                    'success': False,
                    'error': data.get('description', 'Noma\'lum xato')
                }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': "Timeout xatosi"
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"So'rov xatosi: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Kutilmagan xato: {str(e)}"
        }
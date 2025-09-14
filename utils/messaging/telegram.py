import requests
import json
import logging
import secrets
import hashlib
import hmac

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

def set_webhook(bot_token, webhook_url, secret_token=None):
    """
    Telegram bot uchun webhook o'rnatish funksiyasi
    
    Args:
        bot_token (str): Telegram bot tokeni
        webhook_url (str): Webhook URL manzili
        secret_token (str, optional): Webhook xavfsizligi uchun maxfiy token
    
    Returns:
        dict: Webhook o'rnatish natijasi
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        payload = {
            'url': webhook_url,
            'max_connections': 40,
            'allowed_updates': ['message', 'callback_query']
        }
        
        if secret_token:
            payload['secret_token'] = secret_token
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logger.info(f"Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
                return {
                    'success': True,
                    'data': data['result']
                }
            else:
                logger.error(f"Webhook o'rnatishda xato: {data.get('description')}")
                return {
                    'success': False,
                    'error': data.get('description', 'Noma\'lum xato')
                }
        else:
            logger.error(f"Telegram API xatosi: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        logger.error("Webhook o'rnatishda timeout xatosi")
        return {
            'success': False,
            'error': "Timeout xatosi"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook o'rnatishda so'rov xatosi: {str(e)}")
        return {
            'success': False,
            'error': f"So'rov xatosi: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Webhook o'rnatishda kutilmagan xato: {str(e)}")
        return {
            'success': False,
            'error': f"Kutilmagan xato: {str(e)}"
        }

def delete_webhook(bot_token):
    """
    Telegram bot uchun webhook o'chirish funksiyasi
    
    Args:
        bot_token (str): Telegram bot tokeni
    
    Returns:
        dict: Webhook o'chirish natijasi
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logger.info("Webhook muvaffaqiyatli o'chirildi")
                return {
                    'success': True,
                    'data': data['result']
                }
            else:
                logger.error(f"Webhook o'chirishda xato: {data.get('description')}")
                return {
                    'success': False,
                    'error': data.get('description', 'Noma\'lum xato')
                }
        else:
            logger.error(f"Telegram API xatosi: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        logger.error("Webhook o'chirishda timeout xatosi")
        return {
            'success': False,
            'error': "Timeout xatosi"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook o'chirishda so'rov xatosi: {str(e)}")
        return {
            'success': False,
            'error': f"So'rov xatosi: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Webhook o'chirishda kutilmagan xato: {str(e)}")
        return {
            'success': False,
            'error': f"Kutilmagan xato: {str(e)}"
        }

def generate_webhook_secret():
    """
    Webhook xavfsizligi uchun tasodifiy maxfiy token yaratish
    
    Returns:
        str: 32 belgilik tasodifiy token
    """
    return secrets.token_urlsafe(32)

def verify_webhook_signature(secret_token, telegram_signature):
    """
    Telegram webhook secret tokenini tekshirish
    
    Args:
        secret_token (str): Webhook maxfiy tokeni
        telegram_signature (str): Telegram tomonidan yuborilgan secret token
    
    Returns:
        bool: Secret token to'g'ri bo'lsa True, aks holda False
    """
    if not secret_token or not telegram_signature:
        return False
    
    try:
        # Telegram X-Telegram-Bot-Api-Secret-Token header orqali yuboradi
        return secret_token == telegram_signature
    except Exception as e:
        logger.error(f"Webhook secret tokenini tekshirishda xato: {str(e)}")
        return False
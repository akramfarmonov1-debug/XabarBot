from models.contact_log import ContactLog

def log_contact_message(user_id, channel, message):
    """Aloqa xabarini log qilish uchun funksiya"""
    contact_log = ContactLog(
        user_id=user_id,
        channel=channel,
        message=message,
        status='pending'
    )
    return contact_log.save()

def log_phone_request(phone_number):
    """Telefon qo'ng'iroq so'rovini log qilish"""
    message = f"Telefon qo'ng'iroq so'rovi: {phone_number}"
    contact_log = ContactLog(
        user_id=None,  # Telefon uchun user_id bo'lmasligi mumkin
        channel='phone',
        message=message,
        status='pending'
    )
    return contact_log.save()

def log_telegram_message(user_id, message, telegram_username=None):
    """Telegram xabarini log qilish"""
    if telegram_username:
        full_message = f"Telegram (@{telegram_username}): {message}"
    else:
        full_message = f"Telegram: {message}"
    
    contact_log = ContactLog(
        user_id=user_id,
        channel='telegram',
        message=full_message,
        status='pending'
    )
    return contact_log.save()
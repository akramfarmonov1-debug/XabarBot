from models import db
from models.contact_log import ContactLog

def log_contact_message(user_id, channel, message):
    """Log contact message to database"""
    try:
        contact_log = ContactLog(
            user_id=user_id,
            channel=channel,
            message=message
        )
        db.session.add(contact_log)
        db.session.commit()
        return contact_log
    except Exception as e:
        db.session.rollback()
        raise e

def log_telegram_message(user_id, message, telegram_username=None):
    """Log telegram message to database"""
    try:
        full_message = f"Telegram: @{telegram_username}\n{message}" if telegram_username else message
        contact_log = ContactLog(
            user_id=user_id,
            channel='telegram',
            message=full_message
        )
        db.session.add(contact_log)
        db.session.commit()
        return contact_log
    except Exception as e:
        db.session.rollback()
        raise e

def log_phone_request(phone_number):
    """Log phone call request to database"""
    try:
        contact_log = ContactLog(
            user_id=None,
            channel='phone',
            message=f"Telefon qo'ng'iroq so'rovi: {phone_number}"
        )
        db.session.add(contact_log)
        db.session.commit()
        return contact_log
    except Exception as e:
        db.session.rollback()
        raise e
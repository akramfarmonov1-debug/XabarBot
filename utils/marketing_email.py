import os
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message, Mail
from models import db
from models.user import User
from sqlalchemy import and_

def send_trial_reminder(user):
    """Send trial reminder email to user"""
    try:
        # Skip if user doesn't have active trial or email is not configured
        if not user.is_trial_active() or not current_app.config.get('MAIL_USERNAME'):
            return False
        
        # Calculate days left in trial
        days_left = (user.trial_ends_at - datetime.utcnow()).days
        
        mail = Mail(current_app)
        
        if days_left <= 1:
            # Final reminder
            subject = "XabarBot.UZ - Sinov muddatingiz tugayapti! 10% chegirma"
            body = f"""
Hurmatli {user.full_name},

Sizning XabarBot.UZ dagi sinov muddatingiz tugayapti!

Platformamizdan foydalanishni davom ettirish uchun:
✅ 1 oylik reja - faqat 50,000 so'm (10% chegirma bilan)
✅ Cheksiz AI chatbot yaratish
✅ Telegram, webchat va telefon orqali mijozlar bilan aloqa
✅ 24/7 qo'llab-quvvatlash

Chegirmani olish uchun bizga murojaat qiling: +998901234567

Hurmat bilan,
XabarBot.UZ jamoasi
"""
        else:
            # General reminder
            subject = f"XabarBot.UZ - {days_left} kun qoldi, imkoniyatlarni o'tkazib yubormang!"
            body = f"""
Hurmatli {user.full_name},

Sizning sinov muddatingiz {days_left} kundan keyin tugaydi.

Hozircha platformamizdan qanday foydalanmoqdasz:
• AI chatbot yaratish va sozlash
• Mijozlar bilan avtomatik muloqot
• Bilimlar bazasini yuklash

Pullik rejaga o'tish uchun bizga murojaat qiling va 10% chegirma oling!

Aloqa: +998901234567
Email: support@xabarbot.uz

Hurmat bilan,
XabarBot.UZ jamoasi
"""
        
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user.email],
            body=body
        )
        
        # In development, just print the email
        if current_app.config.get('DEBUG'):
            print(f"\n=== EMAIL SENT TO {user.email} ===")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            print("=" * 50)
            return True
        else:
            mail.send(msg)
            return True
            
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {user.email}: {str(e)}")
        return False

def send_trial_reminders_batch():
    """Send trial reminders to all eligible users"""
    try:
        # Find users with trials ending in 1-3 days
        tomorrow = datetime.utcnow() + timedelta(days=1)
        three_days_from_now = datetime.utcnow() + timedelta(days=3)
        
        users_to_remind = User.query.filter(
            and_(
                User.trial_ends_at.between(tomorrow, three_days_from_now),
                User.is_active == True,
                User.plan == 'free'
            )
        ).all()
        
        success_count = 0
        for user in users_to_remind:
            if send_trial_reminder(user):
                success_count += 1
        
        current_app.logger.info(f"Sent {success_count} trial reminder emails")
        return success_count
        
    except Exception as e:
        current_app.logger.error(f"Failed to send trial reminders batch: {str(e)}")
        return 0

def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        if not current_app.config.get('MAIL_USERNAME'):
            return False
            
        mail = Mail(current_app)
        
        subject = "XabarBot.UZ ga xush kelibsiz! 3 kunlik bepul sinov boshlandi"
        body = f"""
Hurmatli {user.full_name},

XabarBot.UZ platformasiga muvaffaqiyatli ro'yxatdan o'tdingiz!

🎉 Sizga 3 kunlik bepul sinov bermoqdamiz:
✅ Cheksiz AI chatbot yaratish
✅ PDF, DOCX fayllarni yuklash va bilimlar bazasini tuzish
✅ Telegram bot integratsiyasi
✅ Webchat va telefon qo'llab-quvvatlash

Boshlash uchun:
1. Tizimga kiring: https://xabarbot.uz/login
2. Bilimlar bazasini yuklang
3. O'zingizning birinchi AI chatbotingizni yarating!

Savollaringiz bo'lsa, biz bilan bog'laning:
📞 +998901234567
📧 support@xabarbot.uz

Muvaffaqiyatlar!
XabarBot.UZ jamoasi
"""
        
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user.email],
            body=body
        )
        
        # In development, just print the email
        if current_app.config.get('DEBUG'):
            print(f"\n=== WELCOME EMAIL SENT TO {user.email} ===")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            print("=" * 50)
            return True
        else:
            mail.send(msg)
            return True
            
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False
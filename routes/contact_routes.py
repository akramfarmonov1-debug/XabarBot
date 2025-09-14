from flask import Blueprint, request, jsonify, session, flash, redirect, url_for
from models.contact_log import ContactLog
from utils.contact_logger import log_contact_message, log_phone_request, log_telegram_message
from functools import wraps
import re

contact_bp = Blueprint('contact', __name__)

def get_current_user_id():
    """Joriy foydalanuvchi ID sini olish"""
    return session.get('user_id')

@contact_bp.route('/contact/webchat', methods=['POST'])
def webchat():
    """Webchat orqali xabar yuborish"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Xabar bo\'sh bo\'lishi mumkin emas'}), 400
        
        user_id = get_current_user_id()
        
        # Xabarni saqlash
        contact_log = log_contact_message(user_id, 'webchat', message)
        
        return jsonify({
            'success': True, 
            'message': 'Xabaringiz yuborildi! Tez orada javob beramiz.',
            'log_id': contact_log.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Xatolik yuz berdi'}), 500

@contact_bp.route('/contact/telegram', methods=['POST'])
def telegram():
    """Telegram bot orqali xabar qabul qilish"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        telegram_user_id = data.get('telegram_user_id')
        telegram_username = data.get('telegram_username')
        
        if not message:
            return jsonify({'success': False, 'error': 'Xabar bo\'sh bo\'lishi mumkin emas'}), 400
        
        # Telegram user_id ni bizning user_id ga bog'lash (kerak bo'lsa)
        # Hozircha None qilib qo'yamiz
        user_id = None
        
        # Xabarni saqlash
        contact_log = log_telegram_message(user_id, message, telegram_username)
        
        return jsonify({
            'success': True, 
            'message': 'Xabar qabul qilindi',
            'log_id': contact_log.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Xatolik yuz berdi'}), 500

@contact_bp.route('/contact/phone', methods=['POST'])
def phone():
    """Telefon qo'ng'iroq so'rovi (mock)"""
    try:
        data = request.get_json() if request.is_json else request.form
        phone_number = data.get('phone', '').strip()
        
        if not phone_number:
            return jsonify({'success': False, 'error': 'Telefon raqami kiritilmagan'}), 400
        
        # Telefon raqami validatsiyasi
        phone_pattern = r'^\+998\d{9}$'
        if not re.match(phone_pattern, phone_number):
            return jsonify({
                'success': False, 
                'error': 'Telefon raqami +998 bilan boshlanishi va 13 ta raqamdan iborat bo\'lishi kerak'
            }), 400
        
        # Qo'ng'iroq so'rovini saqlash
        contact_log = log_phone_request(phone_number)
        
        return jsonify({
            'success': True, 
            'message': 'Qo\'ng\'iroq so\'rovingiz qabul qilindi! Tez orada aloqaga chiqamiz.',
            'log_id': contact_log.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Xatolik yuz berdi'}), 500
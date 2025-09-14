from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.telegram_bot import TelegramBot
from models.user import User
from utils.messaging.telegram import send_message_to_telegram, get_bot_info
from utils.ai_handler import get_ai_response
from models.knowledge_base import KnowledgeBase
import json
import logging

logger = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/bots', methods=['GET', 'POST'])
def manage_bots():
    # Foydalanuvchi tizimga kirganligini tekshirish
    if 'user_id' not in session:
        flash('Bot sozlamalari uchun tizimga kiring', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_bot':
            bot_token = request.form.get('bot_token', '').strip()
            language = request.form.get('language', 'uz')
            
            if not bot_token:
                flash('Bot tokenini kiriting', 'error')
                return render_template('bots.html')
            
            # Bot tokenini tekshirish
            bot_info = get_bot_info(bot_token)
            if not bot_info['success']:
                flash(f'Bot tokeni noto\'g\'ri: {bot_info["error"]}', 'error')
                return render_template('bots.html')
            
            # Botning mavjudligini tekshirish
            existing_bot = TelegramBot.find_by_token(bot_token)
            if existing_bot:
                flash('Bu bot allaqachon ro\'yxatdan o\'tgan', 'error')
                return render_template('bots.html')
            
            # Foydalanuvchining mavjud botini tekshirish
            user_bot = TelegramBot.find_by_user_id(user_id)
            
            # Webhook URL yaratish
            webhook_url = f"{request.url_root}telegram/webhook/{user_id}"
            
            bot_data = bot_info['data']
            
            if user_bot:
                # Mavjud botni yangilash
                user_bot.token = bot_token
                user_bot.username = bot_data.get('username', '')
                user_bot.webhook_url = webhook_url
                user_bot.language = language
                user_bot.save()
                flash('Bot muvaffaqiyatli yangilandi!', 'success')
            else:
                # Yangi bot qo'shish
                new_bot = TelegramBot(
                    user_id=user_id,
                    token=bot_token,
                    username=bot_data.get('username', ''),
                    webhook_url=webhook_url,
                    language=language
                )
                new_bot.save()
                flash('Bot muvaffaqiyatli qo\'shildi!', 'success')
        
        elif action == 'delete_bot':
            user_bot = TelegramBot.find_by_user_id(user_id)
            if user_bot:
                user_bot.delete()
                flash('Bot o\'chirildi', 'info')
            else:
                flash('Bot topilmadi', 'error')
        
        return redirect(url_for('telegram.manage_bots'))
    
    # GET so'rovi uchun
    user_bot = TelegramBot.find_by_user_id(user_id)
    return render_template('bots.html', user_bot=user_bot)

@telegram_bp.route('/webhook/<int:user_id>', methods=['POST'])
def telegram_webhook(user_id):
    """
    Telegram webhook endpoint
    """
    try:
        # Foydalanuvchini topish
        user = User.find_by_email(session.get('user_email')) if 'user_email' in session else None
        if not user or user.id != user_id:
            # Session bo'lmasa ham, user_id orqali botni topishga harakat qilamiz
            telegram_bot = TelegramBot.find_by_user_id(user_id)
            if not telegram_bot:
                logger.error(f"User {user_id} uchun bot topilmadi")
                return jsonify({'error': 'Bot topilmadi'}), 404
        else:
            telegram_bot = TelegramBot.find_by_user_id(user.id)
            if not telegram_bot:
                logger.error(f"User {user_id} uchun bot topilmadi")
                return jsonify({'error': 'Bot topilmadi'}), 404
        
        # Webhook ma'lumotlarini olish
        webhook_data = request.get_json()
        
        if not webhook_data or 'message' not in webhook_data:
            return jsonify({'ok': True})
        
        message = webhook_data['message']
        chat_id = message['chat']['id']
        user_message = message.get('text', '')
        
        if not user_message:
            return jsonify({'ok': True})
        
        # Foydalanuvchining knowledge base dan kontekst olish
        kb = KnowledgeBase.find_by_user_id(user_id)
        context = ""
        if kb and kb.content:
            context = kb.content
        
        # AI javobini olish
        ai_response = get_ai_response(user_message, context)
        
        # Javobni Telegram orqali yuborish
        result = send_message_to_telegram(telegram_bot.token, chat_id, ai_response)
        
        if result['success']:
            logger.info(f"Xabar muvaffaqiyatli yuborildi: {user_id}")
        else:
            logger.error(f"Xabar yuborishda xato: {result['error']}")
        
        return jsonify({'ok': True})
        
    except Exception as e:
        logger.error(f"Webhook xatosi: {str(e)}")
        return jsonify({'error': 'Server xatosi'}), 500
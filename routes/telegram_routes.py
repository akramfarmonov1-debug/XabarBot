from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from models.telegram_bot import TelegramBot
from models.user import User
from utils.messaging.telegram import send_message_to_telegram, get_bot_info, set_webhook, delete_webhook, generate_webhook_secret, verify_webhook_signature
from utils.ai_handler import get_ai_response
from models.knowledge_base import KnowledgeBase
import json
import logging

logger = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/dashboard')
@login_required
def dashboard():
    """Telegram dashboard - redirects to manage bots"""
    return redirect(url_for('telegram.manage_bots'))

@telegram_bp.route('/bots', methods=['GET', 'POST'])
@login_required
def manage_bots():
    # Flask-Login bilan foydalanuvchi ma'lumotlarini olish
    user_id = current_user.id
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_bot':
            bot_token = request.form.get('bot_token', '').strip()
            language = request.form.get('language', 'uz')
            
            # Existing bot check for updates
            user_bot = TelegramBot.find_by_user_id(user_id)
            
            # If this is an update and token is empty, keep existing token
            if user_bot and not bot_token:
                bot_token = user_bot.token
            elif not bot_token:
                flash('Bot tokenini kiriting', 'error')
                return render_template('bots.html')
            
            # Bot tokenini tekshirish
            bot_info = get_bot_info(bot_token)
            if not bot_info['success']:
                flash(f'Bot tokeni noto\'g\'ri: {bot_info["error"]}', 'error')
                return render_template('bots.html')
            
            # Botning mavjudligini tekshirish (faqat boshqa foydalanuvchilarda)
            existing_bot = TelegramBot.find_by_token(bot_token)
            if existing_bot and existing_bot.user_id != user_id:
                flash('Bu bot allaqachon boshqa foydalanuvchi tomonidan ro\'yxatdan o\'tgan', 'error')
                return render_template('bots.html')
            
            # Foydalanuvchining mavjud botini tekshirish
            user_bot = TelegramBot.find_by_user_id(user_id)
            
            # Webhook URL yaratish (external URL)
            webhook_url = url_for('telegram.telegram_webhook', user_id=user_id, _external=True)
            
            bot_data = bot_info['data']
            
            # Webhook secret yaratish
            webhook_secret = generate_webhook_secret()
            
            if user_bot:
                # Eski webhook o'chirish
                if user_bot.token != bot_token:
                    delete_result = delete_webhook(user_bot.token)
                    if not delete_result['success']:
                        logger.warning(f"Eski webhook o'chirishda xato: {delete_result['error']}")
                
                # Mavjud botni yangilash
                user_bot.token = bot_token
                user_bot.username = bot_data.get('username', '')
                user_bot.webhook_url = webhook_url
                user_bot.webhook_secret = webhook_secret
                user_bot.language = language
                user_bot.save()
                
                # Yangi webhook o'rnatish
                webhook_result = set_webhook(bot_token, webhook_url, webhook_secret)
                if webhook_result['success']:
                    flash('Bot va webhook muvaffaqiyatli yangilandi!', 'success')
                else:
                    flash(f'Bot yangilandi, lekin webhook o\'rnatishda xato: {webhook_result["error"]}', 'warning')
            else:
                # Yangi bot qo'shish
                new_bot = TelegramBot(
                    user_id=user_id,
                    token=bot_token,
                    username=bot_data.get('username', ''),
                    webhook_url=webhook_url,
                    webhook_secret=webhook_secret,
                    language=language
                )
                new_bot.save()
                
                # Webhook o'rnatish
                webhook_result = set_webhook(bot_token, webhook_url, webhook_secret)
                if webhook_result['success']:
                    flash('Bot va webhook muvaffaqiyatli qo\'shildi!', 'success')
                else:
                    flash(f'Bot qo\'shildi, lekin webhook o\'rnatishda xato: {webhook_result["error"]}', 'warning')
        
        elif action == 'delete_bot':
            user_bot = TelegramBot.find_by_user_id(user_id)
            if user_bot:
                # Webhook o'chirish
                delete_result = delete_webhook(user_bot.token)
                if not delete_result['success']:
                    logger.warning(f"Webhook o'chirishda xato: {delete_result['error']}")
                
                # Botni o'chirish
                user_bot.delete()
                flash('Bot va webhook muvaffaqiyatli o\'chirildi', 'info')
            else:
                flash('Bot topilmadi', 'error')
        
        return redirect(url_for('telegram.manage_bots'))
    
    # GET so'rovi uchun
    user_bot = TelegramBot.find_by_user_id(user_id)
    return render_template('bots.html', user_bot=user_bot)

@telegram_bp.route('/webhook/<int:user_id>', methods=['POST'])
def telegram_webhook(user_id):
    """
    Telegram webhook endpoint with security verification
    """
    try:
        # Botni topish
        telegram_bot = TelegramBot.find_by_user_id(user_id)
        if not telegram_bot:
            logger.error(f"User {user_id} uchun bot topilmadi")
            return jsonify({'error': 'Bot topilmadi'}), 404
        
        # Webhook xavfsizligini tekshirish
        if telegram_bot.webhook_secret:
            telegram_signature = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
            request_data = request.get_data()
            
            if not verify_webhook_signature(telegram_bot.webhook_secret, telegram_signature):
                logger.warning(f"Webhook xavfsizlik tekshiruvi muvaffaqiyatsiz: {user_id}")
                return jsonify({'error': 'Forbidden'}), 403
        
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
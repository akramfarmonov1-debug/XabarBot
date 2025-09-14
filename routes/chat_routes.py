from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.knowledge_base import KnowledgeBase
from utils.ai_handler import get_ai_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat():
    # Foydalanuvchi tizimga kirganligini tekshirish
    if 'user_id' not in session:
        flash('Chat uchun tizimga kiring', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Chat tarixini session dan olish
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        
        if not user_message:
            flash('Xabar kiritilmadi', 'error')
            return render_template('chat.html', chat_history=session['chat_history'])
        
        # Foydalanuvchining yuklangan faylini olish
        kb = KnowledgeBase.find_by_user_id(user_id)
        context = ""
        if kb and kb.content:
            context = kb.content
        
        # AI javobini olish
        ai_response = get_ai_response(user_message, context)
        
        # Chat tarixiga qo'shish
        chat_entry = {
            'user_message': user_message,
            'ai_response': ai_response,
            'has_context': bool(context and context.strip())
        }
        
        session['chat_history'].append(chat_entry)
        
        # Session o'zgarishlarini saqlash
        session.modified = True
        
        # Tarixni cheklash (oxirgi 50 ta suhbat)
        if len(session['chat_history']) > 50:
            session['chat_history'] = session['chat_history'][-50:]
    
    return render_template('chat.html', 
                         chat_history=session['chat_history'],
                         has_knowledge_base=bool(kb and kb.content) if 'kb' in locals() else False)

@chat_bp.route('/clear-chat', methods=['POST'])
def clear_chat():
    # Foydalanuvchi tizimga kirganligini tekshirish
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Chat tarixini tozalash
    session['chat_history'] = []
    session.modified = True
    
    flash('Chat tarixi tozalandi', 'info')
    return redirect(url_for('chat.chat'))
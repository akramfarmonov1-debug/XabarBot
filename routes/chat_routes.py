from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime
from models.knowledge_base import KnowledgeBase
from utils.ai_handler import get_ai_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': _('Xabar bo\'sh bo\'lishi mumkin emas')}), 400
        
        # Get user's latest knowledge base content
        kb = KnowledgeBase.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).order_by(KnowledgeBase.uploaded_at.desc()).first()
        
        context = kb.content if kb else None
        
        # Get language from session
        language = session.get('language', 'uz')
        
        # Get AI response
        response = get_ai_response(message, context, language)
        
        # Store chat history in session
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'user': message,
            'ai': response,
            'timestamp': str(datetime.utcnow())
        })
        
        # Keep only last 20 messages
        if len(session['chat_history']) > 20:
            session['chat_history'] = session['chat_history'][-20:]
        
        session.modified = True
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': _('Xatolik yuz berdi')}), 500

@chat_bp.route('/history')
@login_required
def get_history():
    history = session.get('chat_history', [])
    return jsonify({'history': history})

@chat_bp.route('/clear')
@login_required
def clear_history():
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})
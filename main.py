import os
import google.generativeai as genai
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel, _, get_locale
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.kb_routes import kb_bp
from routes.chat_routes import chat_bp
from routes.telegram_routes import telegram_bp
from routes.admin_routes import admin_bp
from routes.contact_routes import contact_bp
from models.user import User
from models.knowledge_base import KnowledgeBase
from models.telegram_bot import TelegramBot
from models.contact_log import ContactLog

load_dotenv()

app = Flask(__name__)

# Babel konfiguratsiyasi (xalqarolashtirish)
app.config['LANGUAGES'] = {
    'uz': 'O\'zbekcha',
    'ru': 'Русский', 
    'en': 'English'
}
babel = Babel(app)

@babel.localeselector
def get_locale():
    # URL parametridan til olish
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
    return session.get('language', 'uz')

# SESSION_SECRET muhim bo'lib, har safar restart qilganda o'zgarib ketmasligi kerak
session_secret = os.environ.get('SESSION_SECRET')
if not session_secret:
    raise ValueError("SESSION_SECRET environment variable is required for security!")

app.config['SECRET_KEY'] = session_secret
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB maksimal fayl hajmi

# CSRF himoyasini yoqish
csrf = CSRFProtect(app)

# Google Gemini API konfiguratsiyasi
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# Blueprint ro'yxatdan o'tkazish
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(kb_bp, url_prefix='/')
app.register_blueprint(chat_bp, url_prefix='/')
app.register_blueprint(telegram_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/')
app.register_blueprint(contact_bp, url_prefix='/')

# Ma'lumotlar bazasi jadvallarini yaratish
User.create_table()
KnowledgeBase.create_table()
TelegramBot.create_table()
ContactLog.create_table()

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html', 
                             user_name=session.get('user_name'),
                             user_email=session.get('user_email'))
    else:
        return redirect(url_for('auth.login'))

@app.route('/set_language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(request.referrer or url_for('main.home'))

@app.errorhandler(413)
def too_large(e):
    flash('Fayl hajmi 10MB dan oshmasin', 'error')
    if 'user_id' in session:
        return render_template('upload_kb.html'), 413
    else:
        return redirect(url_for('auth.login')), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
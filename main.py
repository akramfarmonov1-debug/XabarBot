import os
from datetime import datetime, timedelta
from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_babel import Babel, _, get_locale
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import google.generativeai as genai
from dotenv import load_dotenv
import atexit

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError("SECRET_KEY environment variable is required")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise RuntimeError("DATABASE_URL environment variable is required")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Security settings for production
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Initialize extensions
from models import db
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
csrf = CSRFProtect(app)
mail = Mail(app)

# Babel configuration
app.config['LANGUAGES'] = {
    'uz': 'O\'zbekcha',
    'ru': 'Русский',
    'en': 'English'
}

def get_locale():
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
    return session.get('language', 'uz')

babel = Babel(app, locale_selector=get_locale)

# Google Gemini AI configuration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# Import models after db initialization
from models.user import User
from models.knowledge_base import KnowledgeBase
from models.telegram_bot import TelegramBot
from models.contact_log import ContactLog

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.chat_routes import chat_bp
from routes.kb_routes import kb_bp
from routes.telegram_routes import telegram_bp
from routes.contact_routes import contact_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(kb_bp, url_prefix='/kb')
app.register_blueprint(telegram_bp, url_prefix='/telegram')
app.register_blueprint(contact_bp, url_prefix='/contact')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for autoscale deployment"""
    try:
        # Check database connection
        from sqlalchemy import text
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

@app.route('/set-language/<locale>')
def set_language(locale=None):
    session['language'] = locale
    return redirect(request.referrer or url_for('home'))

@app.errorhandler(413)
def too_large(e):
    flash(_('Fayl hajmi 10MB dan oshmasin'), 'error')
    return redirect(request.referrer or url_for('kb.upload')), 413

@app.context_processor
def inject_conf_vars():
    return {
        'LANGUAGES': app.config['LANGUAGES'],
        'CURRENT_LANGUAGE': session.get('language', 'uz')
    }

# Create tables and default admin user
with app.app_context():
    db.create_all()
    
    # Create admin user only if explicitly configured
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_email and admin_password:
        admin_exists = User.query.filter_by(email=admin_email).first()
        if not admin_exists:
            admin_user = User(
                full_name='Administrator',
                phone='+998901234567',
                email=admin_email,
                password=generate_password_hash(admin_password),
                is_admin=True,
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()

# Email scheduler setup
def setup_email_scheduler():
    """Setup automated email scheduler"""
    try:
        scheduler = BackgroundScheduler()
        
        # Send trial reminder emails every 12 hours
        from utils.marketing_email import send_trial_reminders_batch
        scheduler.add_job(
            func=send_trial_reminders_batch,
            trigger=IntervalTrigger(hours=12),
            id='trial_reminders',
            name='Send trial reminder emails',
            replace_existing=True
        )
        
        scheduler.start()
        app.logger.info("Email scheduler started successfully")
        
        # Shutdown scheduler on app exit
        atexit.register(lambda: scheduler.shutdown())
        
    except Exception as e:
        app.logger.error(f"Failed to start email scheduler: {str(e)}")

# Initialize scheduler
with app.app_context():
    setup_email_scheduler()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
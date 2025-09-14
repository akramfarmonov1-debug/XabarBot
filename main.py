import os
from flask import Flask, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.kb_routes import kb_bp
from models.user import User
from models.knowledge_base import KnowledgeBase

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'your_super_secret_key_1234567890!')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB maksimal fayl hajmi

# Blueprint ro'yxatdan o'tkazish
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(kb_bp, url_prefix='/')

# Ma'lumotlar bazasi jadvallarini yaratish
User.create_table()
KnowledgeBase.create_table()

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', 
                             user_name=session.get('user_name'),
                             user_email=session.get('user_email'))
    else:
        return redirect(url_for('auth.login'))

@app.errorhandler(413)
def too_large(e):
    flash('Fayl hajmi 10MB dan oshmasin', 'error')
    if 'user_id' in session:
        return render_template('upload_kb.html'), 413
    else:
        return redirect(url_for('auth.login')), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
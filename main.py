import os
from flask import Flask, render_template, session, redirect, url_for
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from models.user import User

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'your_super_secret_key_1234567890!')

# Blueprint ro'yxatdan o'tkazish
app.register_blueprint(auth_bp, url_prefix='/')

# Ma'lumotlar bazasi jadvalini yaratish
User.create_table()

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', 
                             user_name=session.get('user_name'),
                             user_email=session.get('user_email'))
    else:
        return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
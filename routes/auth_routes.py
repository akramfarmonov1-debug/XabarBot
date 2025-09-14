from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from models import db
from models.user import User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if not all([full_name, phone, email, password]):
            flash(_('Barcha maydonlarni to\'ldiring'), 'error')
            return render_template('register.html')
        
        # Phone number validation
        if not User.validate_phone(phone):
            flash(_('Telefon raqami +998 bilan boshlanishi va 13 ta raqamdan iborat bo\'lishi kerak'), 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash(_('Bu email allaqachon ro\'yxatdan o\'tgan'), 'error')
            return render_template('register.html')
        
        if User.query.filter_by(phone=phone).first():
            flash(_('Bu telefon raqami allaqachon ro\'yxatdan o\'tgan'), 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            full_name=full_name,
            phone=phone,
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        
        flash(_('Ro\'yxatdan o\'tish muvaffaqiyatli!'), 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([email, password]):
            flash(_('Email va parolni kiriting'), 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user)
                flash(_('Muvaffaqiyatli kirildi!'), 'success')
                
                # Redirect admin to admin panel
                if user.is_admin:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('home'))
            else:
                flash(_('Sizning akkauntingiz faol emas'), 'error')
        else:
            flash(_('Email yoki parol noto\'g\'ri'), 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Tizimdan chiqildi'), 'info')
    return redirect(url_for('auth.login'))
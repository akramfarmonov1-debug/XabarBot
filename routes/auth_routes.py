import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from utils.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validatsiya
        if not all([full_name, phone, email, password]):
            flash('Barcha maydonlarni to\'ldiring', 'error')
            return render_template('register.html')
        
        # Telefon raqami validatsiyasi
        phone_pattern = r'^\+998\d{9}$'
        if not phone or not re.match(phone_pattern, phone):
            flash('Telefon raqami +998 bilan boshlanishi va 13 ta raqamdan iborat bo\'lishi kerak', 'error')
            return render_template('register.html')
        
        # Foydalanuvchi mavjudligini tekshirish
        if User.find_by_email(email):
            flash('Bu email allaqachon ro\'yxatdan o\'tgan', 'error')
            return render_template('register.html')
        
        if User.find_by_phone(phone):
            flash('Bu telefon raqami allaqachon ro\'yxatdan o\'tgan', 'error')
            return render_template('register.html')
        
        # Parolni hash qilish va foydalanuvchini saqlash
        password_hash = generate_password_hash(password)
        user = User(
            full_name=full_name,
            phone=phone,
            email=email,
            password_hash=password_hash
        )
        user.save()
        
        flash('Ro\'yxatdan o\'tish muvaffaqiyatli!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([email, password]):
            flash('Email va parolni kiriting', 'error')
            return render_template('login.html')
        
        user = User.find_by_email(email)
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_name'] = user.full_name
                session['is_admin'] = user.is_admin
                flash('Muvaffaqiyatli kirildi!', 'success')
                
                # Admin foydalanuvchini admin panelga yo'naltirish
                if user.is_admin:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('Sizning akkauntingiz faol emas', 'error')
        else:
            flash('Email yoki parol noto\'g\'ri', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Tizimdan chiqildi', 'info')
    return redirect(url_for('auth.login'))
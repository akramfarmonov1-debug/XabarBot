from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.user import User
from models.contact_log import ContactLog

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Iltimos, tizimga kiring', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.find_by_id(session['user_id'])
        if not user or not user.is_admin:
            flash('Bu sahifaga kirish uchun admin huquqi kerak', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    users = User.get_all_users()
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/admin/approve/<int:user_id>')
@admin_required
def approve_user(user_id):
    user = User.find_by_id(user_id)
    if user:
        user.approve()
        flash(f'{user.full_name} foydalanuvchisi tasdiqlandi', 'success')
    else:
        flash('Foydalanuvchi topilmadi', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.find_by_id(user_id)
    if user:
        if user.is_admin:
            flash('Admin foydalanuvchisini o\'chirish mumkin emas', 'error')
        else:
            full_name = user.full_name
            user.delete_user()
            flash(f'{full_name} foydalanuvchisi o\'chirildi', 'success')
    else:
        flash('Foydalanuvchi topilmadi', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/contacts')
@admin_required
def contacts():
    """Admin kontaktlar sahifasi - barcha xabarlar"""
    contact_logs = ContactLog.get_all_logs()
    return render_template('admin/contacts.html', contact_logs=contact_logs)


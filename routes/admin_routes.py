from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from models import db
from models.user import User
from models.contact_log import ContactLog

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(_('Iltimos, tizimga kiring'), 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash(_('Bu sahifaga kirish uchun admin huquqi kerak'), 'error')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/approve/<int:user_id>')
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(_('Foydalanuvchi tasdiqlandi'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash(_('Admin foydalanuvchisini o\'chirish mumkin emas'), 'error')
    else:
        full_name = user.full_name
        db.session.delete(user)
        db.session.commit()
        flash(_('Foydalanuvchi o\'chirildi'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/contacts')
@login_required
@admin_required
def contacts():
    """Admin contacts page - all messages"""
    contact_logs = ContactLog.query.order_by(ContactLog.created_at.desc()).all()
    return render_template('admin/contacts.html', contact_logs=contact_logs)
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re

from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    trial_ends_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=3))
    plan = db.Column(db.String(20), default='free')
    plan_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    knowledge_bases = db.relationship('KnowledgeBase', backref='user', lazy=True, cascade='all, delete-orphan')
    telegram_bots = db.relationship('TelegramBot', backref='user', lazy=True, cascade='all, delete-orphan')
    contact_logs = db.relationship('ContactLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, full_name, phone, email, password=None, password_hash=None, **kwargs):
        self.full_name = full_name
        self.phone = phone
        self.email = email
        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number - accept various formats"""
        if not phone:
            return False
            
        # Remove spaces, dashes, and other non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Must have at least 9 digits (minimum for valid phone)
        digits_only = re.sub(r'[^\d]', '', phone)
        if len(digits_only) < 9:
            return False
            
        # Accept various formats:
        # +998XXXXXXXXX (Uzbek format)
        # 998XXXXXXXXX (without +)
        # Any international format +XXXXXXXXXXX
        # Local format XXXXXXXXX (at least 9 digits)
        
        # If starts with +998 or 998, ensure it has correct length for Uzbek
        if phone.startswith('+998'):
            return len(digits_only) >= 12  # 998 + 9 digits
        elif phone.startswith('998') and not phone.startswith('+'):
            return len(digits_only) >= 12  # 998 + 9 digits
        elif phone.startswith('+'):
            return len(digits_only) >= 10  # Any international format
        else:
            return len(digits_only) >= 9   # Local format
        
        return True
    
    def is_trial_active(self):
        """Check if user's trial period is still active"""
        return self.trial_ends_at and datetime.utcnow() < self.trial_ends_at
    
    def is_plan_active(self):
        """Check if user's paid plan is still active"""
        return self.plan_expires_at and datetime.utcnow() < self.plan_expires_at
    
    def has_active_subscription(self):
        """Check if user has any active subscription (trial or paid)"""
        return self.is_trial_active() or self.is_plan_active()
    
    def save(self):
        """Ma'lumotlar bazasiga saqlash"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Ma'lumotlar bazasidan o'chirish"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs):
        """Ma'lumotlarni yangilash"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    def __repr__(self):
        return f'<User {self.email}>'
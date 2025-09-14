from datetime import datetime

from models import db

class ContactLog(db.Model):
    __tablename__ = 'contact_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    channel = db.Column(db.String(20), nullable=False)  # 'webchat', 'telegram', 'phone'
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text)
    status = db.Column(db.String(20), default='new')  # 'new', 'answered'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, channel, message, user_id=None, reply=None, status='new', **kwargs):
        self.channel = channel
        self.message = message
        self.user_id = user_id
        self.reply = reply
        self.status = status
        for key, value in kwargs.items():
            setattr(self, key, value)
    
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
        return f'<ContactLog {self.channel}: {self.message[:50]}>'
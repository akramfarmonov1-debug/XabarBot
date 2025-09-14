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
    
    def __repr__(self):
        return f'<ContactLog {self.channel}: {self.message[:50]}>'
from datetime import datetime

from models import db

class TelegramBot(db.Model):
    __tablename__ = 'telegram_bots'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255))
    webhook_url = db.Column(db.String(500))
    language = db.Column(db.String(10), default='uz')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, token, username=None, webhook_url=None, language='uz', **kwargs):
        self.user_id = user_id
        self.token = token
        self.username = username
        self.webhook_url = webhook_url
        self.language = language
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f'<TelegramBot {self.username or self.token[:10]}>'
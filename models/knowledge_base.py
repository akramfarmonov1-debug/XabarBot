from datetime import datetime

from models import db

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, user_id, file_name, file_path, content=None, **kwargs):
        self.user_id = user_id
        self.file_name = file_name
        self.file_path = file_path
        self.content = content
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f'<KnowledgeBase {self.file_name}>'
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Foydalanuvchi ID bo'yicha bilim bazasi ma'lumotlarini topish"""
        return cls.query.filter_by(user_id=user_id, is_active=True).all()
    
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
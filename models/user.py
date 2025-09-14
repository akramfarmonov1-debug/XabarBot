import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self, id=None, full_name=None, phone=None, email=None, password_hash=None, trial_ends_at=None, is_active=True, is_admin=False):
        self.id = id
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.password_hash = password_hash
        self.trial_ends_at = trial_ends_at
        self.is_active = is_active
        self.is_admin = is_admin
    
    @staticmethod
    def get_db_connection():
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    
    @staticmethod
    def create_table():
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                phone VARCHAR(13) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                trial_ends_at TIMESTAMP,
                is_active BOOLEAN DEFAULT true,
                is_admin BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # is_admin ustunini qo'shish (agar mavjud bo'lmasa)
        try:
            cursor.execute('SELECT is_admin FROM users LIMIT 1')
        except psycopg2.errors.UndefinedColumn:
            conn.rollback()  # Avvalgi xatolikni rollback qilish
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT false')
            conn.commit()
        
        # Default admin user yaratish
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = true')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            from utils.security import generate_password_hash
            admin_password_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (full_name, phone, email, password_hash, is_active, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('Admin', '+998901234567', 'admin@example.com', admin_password_hash, True, True))
        conn.commit()
        cursor.close()
        conn.close()
    
    def save(self):
        conn = User.get_db_connection()
        cursor = conn.cursor()
        if self.trial_ends_at is None:
            self.trial_ends_at = datetime.utcnow() + timedelta(days=3)
        
        cursor.execute('''
            INSERT INTO users (full_name, phone, email, password_hash, trial_ends_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        ''', (self.full_name, self.phone, self.email, self.password_hash, self.trial_ends_at, self.is_active))
        
        result = cursor.fetchone()
        if result:
            self.id = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        return self
    
    @staticmethod
    def find_by_email(email):
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                full_name=row[1], 
                phone=row[2],
                email=row[3],
                password_hash=row[4],
                trial_ends_at=row[5],
                is_active=row[6],
                is_admin=row[7] if len(row) > 7 else False
            )
        return None
    
    @staticmethod
    def find_by_phone(phone):
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE phone = %s', (phone,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                full_name=row[1], 
                phone=row[2],
                email=row[3],
                password_hash=row[4],
                trial_ends_at=row[5],
                is_active=row[6],
                is_admin=row[7] if len(row) > 7 else False
            )
        return None
    
    @staticmethod
    def get_all_users():
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        users = []
        for row in rows:
            users.append(User(
                id=row[0],
                full_name=row[1], 
                phone=row[2],
                email=row[3],
                password_hash=row[4],
                trial_ends_at=row[5],
                is_active=row[6],
                is_admin=row[7] if len(row) > 7 else False
            ))
        return users
    
    @staticmethod
    def find_by_id(user_id):
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                full_name=row[1], 
                phone=row[2],
                email=row[3],
                password_hash=row[4],
                trial_ends_at=row[5],
                is_active=row[6],
                is_admin=row[7] if len(row) > 7 else False
            )
        return None
    
    def approve(self):
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_active = true WHERE id = %s', (self.id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.is_active = True
    
    def delete_user(self):
        conn = User.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (self.id,))
        conn.commit()
        cursor.close()
        conn.close()
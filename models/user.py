import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self, id=None, full_name=None, phone=None, email=None, password_hash=None, trial_ends_at=None, is_active=True):
        self.id = id
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.password_hash = password_hash
        self.trial_ends_at = trial_ends_at
        self.is_active = is_active
    
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
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
                is_active=row[6]
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
                is_active=row[6]
            )
        return None
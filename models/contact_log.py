import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ContactLog:
    def __init__(self, id=None, user_id=None, channel=None, message=None, reply=None, status='pending', created_at=None):
        self.id = id
        self.user_id = user_id
        self.channel = channel  # 'webchat', 'telegram', 'phone'
        self.message = message
        self.reply = reply
        self.status = status  # 'pending', 'replied', 'closed'
        self.created_at = created_at
    
    @staticmethod
    def get_db_connection():
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    
    @staticmethod
    def create_table():
        conn = ContactLog.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                channel VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                reply TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    
    def save(self):
        conn = ContactLog.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_logs (user_id, channel, message, reply, status)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        ''', (self.user_id, self.channel, self.message, self.reply, self.status))
        
        result = cursor.fetchone()
        if result:
            self.id = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        return self
    
    @staticmethod
    def get_all_logs():
        conn = ContactLog.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cl.*, u.full_name, u.email, u.phone 
            FROM contact_logs cl
            LEFT JOIN users u ON cl.user_id = u.id
            ORDER BY cl.created_at DESC
        ''')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logs = []
        for row in rows:
            log = ContactLog(
                id=row[0],
                user_id=row[1],
                channel=row[2],
                message=row[3],
                reply=row[4],
                status=row[5],
                created_at=row[6]
            )
            # User ma'lumotlarini qo'shish
            log.user_name = row[7] if row[7] else 'Anonim'
            log.user_email = row[8] if row[8] else '-'
            log.user_phone = row[9] if row[9] else '-'
            logs.append(log)
        return logs
    
    @staticmethod
    def find_by_id(log_id):
        conn = ContactLog.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contact_logs WHERE id = %s', (log_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return ContactLog(
                id=row[0],
                user_id=row[1],
                channel=row[2],
                message=row[3],
                reply=row[4],
                status=row[5],
                created_at=row[6]
            )
        return None
    
    def update_reply(self, reply):
        conn = ContactLog.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE contact_logs SET reply = %s, status = 'replied' 
            WHERE id = %s
        ''', (reply, self.id))
        conn.commit()
        cursor.close()
        conn.close()
        self.reply = reply
        self.status = 'replied'
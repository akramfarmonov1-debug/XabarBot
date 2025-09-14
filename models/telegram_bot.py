import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TelegramBot:
    def __init__(self, id=None, user_id=None, token=None, username=None, webhook_url=None, webhook_secret=None, language='uz', created_at=None):
        self.id = id
        self.user_id = user_id
        self.token = token
        self.username = username
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret
        self.language = language
        self.created_at = created_at
    
    @staticmethod
    def get_db_connection():
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    
    @staticmethod
    def create_table():
        conn = TelegramBot.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_bots (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(255),
                webhook_url VARCHAR(500),
                webhook_secret VARCHAR(255),
                language VARCHAR(10) DEFAULT 'uz',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')  
        
        # Add webhook_secret column if it doesn't exist (for existing databases)
        cursor.execute('''
            DO $$ 
            BEGIN
                BEGIN
                    ALTER TABLE telegram_bots ADD COLUMN webhook_secret VARCHAR(255);
                EXCEPTION
                    WHEN duplicate_column THEN
                        -- Column already exists, do nothing
                        NULL;
                END;
            END $$;
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    
    def save(self):
        conn = TelegramBot.get_db_connection()
        cursor = conn.cursor()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.id:
            # Update existing bot
            cursor.execute('''
                UPDATE telegram_bots 
                SET token = %s, username = %s, webhook_url = %s, webhook_secret = %s, language = %s
                WHERE id = %s
            ''', (self.token, self.username, self.webhook_url, self.webhook_secret, self.language, self.id))
        else:
            # Insert new bot
            cursor.execute('''
                INSERT INTO telegram_bots (user_id, token, username, webhook_url, webhook_secret, language, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            ''', (self.user_id, self.token, self.username, self.webhook_url, self.webhook_secret, self.language, self.created_at))
            
            result = cursor.fetchone()
            if result:
                self.id = result[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        return self
    
    @staticmethod
    def find_by_user_id(user_id):
        conn = TelegramBot.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM telegram_bots WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return TelegramBot(
                id=row[0],
                user_id=row[1],
                token=row[2],
                username=row[3],
                webhook_url=row[4],
                webhook_secret=row[5] if len(row) > 6 else None,
                language=row[6] if len(row) > 6 else row[5],
                created_at=row[7] if len(row) > 7 else row[6]
            )
        return None
    
    @staticmethod
    def find_by_token(token):
        conn = TelegramBot.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM telegram_bots WHERE token = %s', (token,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return TelegramBot(
                id=row[0],
                user_id=row[1],
                token=row[2],
                username=row[3],
                webhook_url=row[4],
                webhook_secret=row[5] if len(row) > 6 else None,
                language=row[6] if len(row) > 6 else row[5],
                created_at=row[7] if len(row) > 7 else row[6]
            )
        return None
    
    def delete(self):
        if self.id:
            conn = TelegramBot.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM telegram_bots WHERE id = %s', (self.id,))
            conn.commit()
            cursor.close()
            conn.close()
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class KnowledgeBase:
    def __init__(self, id=None, user_id=None, file_name=None, file_path=None, content=None, uploaded_at=None):
        self.id = id
        self.user_id = user_id
        self.file_name = file_name
        self.file_path = file_path
        self.content = content
        self.uploaded_at = uploaded_at
    
    @staticmethod
    def get_db_connection():
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    
    @staticmethod
    def create_table():
        conn = KnowledgeBase.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                content TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    
    def save(self):
        conn = KnowledgeBase.get_db_connection()
        cursor = conn.cursor()
        if self.uploaded_at is None:
            self.uploaded_at = datetime.utcnow()
        
        cursor.execute('''
            INSERT INTO knowledge_base (user_id, file_name, file_path, content, uploaded_at)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        ''', (self.user_id, self.file_name, self.file_path, self.content, self.uploaded_at))
        
        result = cursor.fetchone()
        if result:
            self.id = result[0]
        conn.commit()
        cursor.close()
        conn.close()
        return self
    
    @staticmethod
    def find_by_user_id(user_id):
        conn = KnowledgeBase.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM knowledge_base WHERE user_id = %s ORDER BY uploaded_at DESC', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return KnowledgeBase(
                id=row[0],
                user_id=row[1],
                file_name=row[2],
                file_path=row[3],
                content=row[4],
                uploaded_at=row[5]
            )
        return None
    
    @staticmethod
    def delete_by_user_id(user_id):
        conn = KnowledgeBase.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM knowledge_base WHERE user_id = %s', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    
    def delete(self):
        if self.id:
            conn = KnowledgeBase.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM knowledge_base WHERE id = %s', (self.id,))
            conn.commit()
            cursor.close()
            conn.close()
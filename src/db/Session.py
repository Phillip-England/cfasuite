from datetime import datetime, timedelta
import secrets
import string

from sqlite3 import Cursor


class Session:
    def __init__(self, id, user_id, key, expires_at):
        self.id = id
        self.user_id = user_id
        self.key = key
        self.expires_at = expires_at

    @staticmethod
    def generate_key():
        alpha = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alpha) for _ in range(16))
    
    @staticmethod
    def generate_expiration():
        return (datetime.now() + timedelta(minutes=30)).isoformat()

    @staticmethod
    def sqlite_create_table(c: Cursor):
        sql = '''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        '''
        c.execute(sql)

    @staticmethod
    def sqlite_insert(c: Cursor, user_id):
        key = Session.generate_key()
        expires_at = Session.generate_expiration()
        sql = '''
            INSERT INTO sessions (user_id, key, expires_at)
            VALUES (?, ?, ?)
        '''
        c.execute(sql, (user_id, key, expires_at))
        return Session(c.lastrowid, user_id, key, expires_at)

    @staticmethod
    def sqlite_get_by_id(c: Cursor, id: int):
        sql = 'SELECT * FROM sessions WHERE id = ?'
        c.execute(sql, (id,))
        row = c.fetchone()
        if row:
            (id, user_id, key, expires_at) = row
            return Session(id, user_id, key, expires_at)
        return None

    def is_expired(self):
        return datetime.fromisoformat(self.expires_at) < datetime.now()
    
    @staticmethod 
    def sqlite_get_by_user_id(c: Cursor, user_id: int):
        sql = 'SELECT * FROM  sessions WHERE user_id = ?'
        c.execute(sql, (user_id,))
        row = c.fetchone()
        if row:
            (id, user_id, key, expires_at) = row
            return Session(id, user_id, key, expires_at)
        return None
    
    @staticmethod
    def sqlite_delete_by_id(c: Cursor, id: int):
        sql = 'DELETE from sessions WHERE id = ?'
        c.execute(sql, (id,))
        return c.rowcount

    def __str__(self):
        return f'''
            id: {self.id}
            user_id: {self.user_id}
            key: {self.key}
            expires_at: {self.expires_at}
        '''
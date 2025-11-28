# database.py - исправленная версия
import sqlite3
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных с исправленной схемой"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Таблица для данных сенсоров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    device_type TEXT,
                    location TEXT,
                    temperature REAL,
                    humidity REAL,
                    light_level INTEGER,
                    voltage REAL,
                    timestamp TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    sent INTEGER DEFAULT 0  -- 0 = не отправлено, 1 = отправлено
                )
            ''')
            
            # Таблица для информации об устройствах
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    device_type TEXT,
                    location TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    total_records INTEGER DEFAULT 0
                )
            ''')
            
            # Индексы для оптимизации
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_device_id ON sensor_data(device_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_sent ON sensor_data(sent)')
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def save_sensor_data(self, data):
        """Сохранение данных сенсора"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Сохраняем данные сенсора
            cursor.execute('''
                INSERT INTO sensor_data 
                (device_id, device_type, location, temperature, humidity, light_level, voltage, timestamp, received_at, sent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                data['device_id'],
                data.get('device_type'),
                data.get('location'),
                data.get('temperature'),
                data.get('humidity'),
                data.get('light_level'),
                data.get('voltage'),
                data['timestamp'],
                datetime.now().isoformat()
            ))
            
            # Обновляем информацию об устройстве
            cursor.execute('''
                INSERT OR REPLACE INTO devices 
                (device_id, device_type, location, first_seen, last_seen, total_records)
                VALUES (
                    ?,
                    ?,
                    ?,
                    COALESCE((SELECT first_seen FROM devices WHERE device_id = ?), ?),
                    ?,
                    COALESCE((SELECT total_records FROM devices WHERE device_id = ?), 0) + 1
                )
            ''', (
                data['device_id'],
                data.get('device_type'),
                data.get('location'),
                data['device_id'],
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                data['device_id']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Error saving sensor data: {e}")
            return False
    
    def get_unsent_data(self, limit=10):
        """Получение неотправленных данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, device_id, temperature, humidity, light_level, timestamp 
                FROM sensor_data 
                WHERE sent = 0 
                ORDER BY timestamp 
                LIMIT ?
            ''', (limit,))
            
            data = cursor.fetchall()
            conn.close()
            return data
            
        except Exception as e:
            logging.error(f"Error getting unsent data: {e}")
            return []
    
    def mark_as_sent(self, record_id):
        """Пометить запись как отправленную"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE sensor_data SET sent = 1 WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Error marking record as sent: {e}")
            return False
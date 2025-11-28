# data_logger.py - Логирование данных системы
from datetime import datetime
import sqlite3
import json

class DataLogger:
    def __init__(self, system_manager):
        self.system = system_manager
        self.log_buffer = []
        self.setup_database()
    
    def setup_database(self):
        """Настройка базы данных"""
        try:
            self.conn = sqlite3.connect('drone_system.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Создание таблиц
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level TEXT,
                    message TEXT
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS flight_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    position_x REAL,
                    position_y REAL,
                    position_z REAL,
                    battery_level REAL
                )
            ''')
            
            self.conn.commit()
            self.log("📊 База данных инициализирована")
        except Exception as e:
            print(f"Ошибка базы данных: {e}")
    
    def log(self, message, level="INFO"):
        """Логирование сообщения"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Вывод в консоль
        print(formatted_message)
        
        # Сохранение в базу данных
        try:
            self.cursor.execute(
                "INSERT INTO system_logs (timestamp, level, message) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), level, message)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка записи в лог: {e}")
        
        # Буферизация для UI
        self.log_buffer.append(formatted_message)
        if len(self.log_buffer) > 1000:
            self.log_buffer.pop(0)
    
    def save_flight_data(self):
        """Сохранение данных полета"""
        try:
            physics = self.system.physics
            self.cursor.execute(
                """INSERT INTO flight_data 
                (timestamp, position_x, position_y, position_z, battery_level) 
                VALUES (?, ?, ?, ?, ?)""",
                (datetime.now().isoformat(), 
                 physics.drone_position[0],
                 physics.drone_position[1], 
                 physics.drone_position[2],
                 physics.battery_level)
            )
            self.conn.commit()
        except Exception as e:
            self.log(f"Ошибка сохранения данных полета: {e}", "ERROR")
    
    def get_recent_logs(self, limit=50):
        """Получение последних логов"""
        return self.log_buffer[-limit:] if self.log_buffer else []
    
    def close(self):
        """Закрытие соединения с базой данных"""
        try:
            self.conn.close()
        except:
            pass
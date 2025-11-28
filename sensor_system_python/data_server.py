# data_server.py - исправленная версия
import socket
import json
import threading
import logging
import sys
import os
from datetime import datetime

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(__file__))

try:
    from database import DatabaseManager
    from config import Config
except ImportError as e:
    print(f"Import error: {e} - data_server.py:17")
    # Создаем простые заглушки для классов
    class DatabaseManager:
        def __init__(self, db_path):
            self.db_path = db_path
            print(f"DatabaseManager initialized with {db_path} - data_server.py:22")
        
        def save_sensor_data(self, data):
            print(f"Would save data: {data} - data_server.py:25")
            return True
    
    class Config:
        class SERVER:
            HOST = 'localhost'
            PORT = 8080
        class DATABASE:
            DB_PATH = 'data/sensor_data.db'

class SensorDataServer:
    def __init__(self, config):
        self.config = config
        self.host = config.SERVER.HOST
        self.port = config.SERVER.PORT
        
        # Создаем папку data если её нет
        os.makedirs('data', exist_ok=True)
        
        try:
            self.db_manager = DatabaseManager(config.DATABASE.DB_PATH)
            print("Database manager initialized successfully - data_server.py:46")
        except Exception as e:
            print(f"Database initialization error: {e} - data_server.py:48")
            self.db_manager = None
        
        self.is_running = False
        self.server_socket = None
        
    def handle_client(self, client_socket, address):
        """Обработка клиентского подключения"""
        try:
            print(f"Handling connection from {address} - data_server.py:57")
            
            # Получаем данные
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return
            
            print(f"Received data from {address}: {data[:100]}... - data_server.py:64")
            
            # Парсим JSON
            try:
                sensor_data = json.loads(data)
                print(f"Parsed data from {sensor_data.get('device_id', 'unknown')}: - data_server.py:69"
                      f"temp={sensor_data.get('temperature')}, "
                      f"humidity={sensor_data.get('humidity')}")
                
                # Сохраняем в базу данных
                success = False
                if self.db_manager:
                    success = self.db_manager.save_sensor_data(sensor_data)
                
                # Отправляем ответ
                response = {
                    'status': 'success' if success else 'error',
                    'message': 'Data received and saved' if success else 'Error saving data',
                    'timestamp': datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} - data_server.py:86")
                response = {
                    'status': 'error',
                    'message': 'Invalid JSON data',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Отправляем ответ клиенту
            response_json = json.dumps(response)
            client_socket.send(response_json.encode('utf-8'))
            print(f"Sent response: {response_json} - data_server.py:96")
            
        except Exception as e:
            print(f"Error handling client {address}: {e} - data_server.py:99")
            try:
                error_response = {
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                client_socket.send(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()
            print(f"Connection with {address} closed - data_server.py:111")
    
    def start_server(self):
        """Запуск TCP сервера"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            self.is_running = True
            print(f"✅ Sensor data server started on {self.host}:{self.port} - data_server.py:123")
            print("Server is ready to accept connections... - data_server.py:124")
            
            while self.is_running:
                try:
                    # Принимаем подключения с таймаутом
                    client_socket, address = self.server_socket.accept()
                    print(f"New connection from {address} - data_server.py:130")
                    
                    # Запускаем обработку в отдельном потоке
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    # Таймаут для проверки флага is_running
                    continue
                except OSError as e:
                    if self.is_running:
                        print(f"Server socket error: {e} - data_server.py:145")
                    break
                except Exception as e:
                    print(f"Unexpected error: {e} - data_server.py:148")
                    continue
                    
        except Exception as e:
            print(f"Server startup error: {e} - data_server.py:152")
        finally:
            self.stop_server()
    
    def stop_server(self):
        """Остановка сервера"""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
                print("Server socket closed - data_server.py:162")
            except Exception as e:
                print(f"Error closing socket: {e} - data_server.py:164")
        print("❌ Sensor data server stopped - data_server.py:165")

def main():
    """Основная функция запуска сервера"""
    print("Starting Sensor Data Server... - data_server.py:169")
    
    try:
        config = Config()
    except:
        config = Config()  # Используем заглушку
    
    server = SensorDataServer(config)
    
    print("Press Ctrl+C to stop the server - data_server.py:178")
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nStopping server... - data_server.py:183")
        server.stop_server()
    except Exception as e:
        print(f"Critical error: {e} - data_server.py:186")
        server.stop_server()

if __name__ == "__main__":
    main()
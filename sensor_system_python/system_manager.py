# system_manager.py - Главный системный менеджер дрона
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime

# Импорт модулей
from drone_physics import DronePhysics
from system_controller import SystemController
from ui_manager import UIManager
from data_logger import DataLogger
from sensors import SensorSystem

class DroneSystemManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Control System Manager")
        self.root.geometry("1400x900")
        
        # Инициализация модулей
        self.physics = DronePhysics(self)
        self.controller = SystemController(self)
        self.sensors = SensorSystem(self)
        self.ui = UIManager(self, root)
        self.logger = DataLogger(self)
        
        # Статус системы
        self.system_running = True
        
        self.initialize_system()
    
    def initialize_system(self):
        """Инициализация всей системы"""
        self.logger.log("🚀 Инициализация системы управления дроном")
        
        # Запуск основных потоков
        self.start_main_threads()
        
        self.logger.log("✅ Система успешно инициализирована")
    
    def start_main_threads(self):
        """Запуск основных потоков системы"""
        # Поток физики дрона
        physics_thread = threading.Thread(target=self.physics.run, daemon=True)
        physics_thread.start()
        
        # Поток сенсоров
        sensors_thread = threading.Thread(target=self.sensors.run, daemon=True)
        sensors_thread.start()
        
        # Поток мониторинга системы
        monitor_thread = threading.Thread(target=self.system_monitor, daemon=True)
        monitor_thread.start()
    
    def system_monitor(self):
        """Мониторинг состояния системы"""
        while self.system_running:
            try:
                # Обновление данных сенсоров на основе физики
                self.sensors.update_from_physics()
                
                # Обновление UI
                self.root.after(0, self.ui.update_all_displays)
                time.sleep(0.1)
            except Exception as e:
                self.logger.log(f"❌ Ошибка в системном мониторе: {e}")
    
    def emergency_stop(self):
        """Экстренная остановка всей системы"""
        self.logger.log("🚨 ЭКСТРЕННАЯ ОСТАНОВКА СИСТЕМЫ!")
        self.system_running = False
        self.controller.stop_all()
        self.physics.emergency_stop()
    
    def shutdown(self):
        """Корректное завершение работы системы"""
        self.logger.log("🛑 Завершение работы системы...")
        self.system_running = False
        self.controller.stop_all()
        self.logger.close()

def main():
    """Запуск приложения"""
    try:
        root = tk.Tk()
        app = DroneSystemManager(root)
        
        # Обработка закрытия окна
        def on_closing():
            app.shutdown()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"Критическая ошибка: {e} - system_manager.py:98")
        with open("system_error.log", "w") as f:
            f.write(f"{datetime.now()}: {e}\n")

if __name__ == "__main__":
    main()


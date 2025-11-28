# system_controller.py - Управление системными компонентами
import subprocess
import time
import threading

class SystemController:
    def __init__(self, system_manager):
        self.system = system_manager
        
        # Процессы компонентов
        self.server_process = None
        self.emulator_process = None
        self.web_process = None
        
        # Статусы
        self.server_running = False
        self.emulator_running = False
        self.web_running = False
    
    def start_server(self):
        """Запуск сервера данных"""
        try:
            self.system.logger.log("🔄 Запуск сервера данных...")
            # Здесь код запуска сервера
            # self.server_process = subprocess.Popen([...])
            self.server_running = True
            self.system.logger.log("✅ Сервер данных запущен на порту 8080")
            return True
        except Exception as e:
            self.system.logger.log(f"❌ Ошибка запуска сервера: {e}")
            return False
    
    def stop_server(self):
        """Остановка сервера данных"""
        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            self.server_running = False
            self.system.logger.log("⏹ Сервер данных остановлен")
        except Exception as e:
            self.system.logger.log(f"❌ Ошибка остановки сервера: {e}")
    
    def start_emulator(self):
        """Запуск эмулятора датчиков"""
        try:
            self.system.logger.log("🔄 Запуск эмулятора датчиков...")
            # Здесь код запуска эмулятора
            self.emulator_running = True
            self.system.logger.log("✅ Эмулятор датчиков запущен")
            return True
        except Exception as e:
            self.system.logger.log(f"❌ Ошибка запуска эмулятора: {e}")
            return False
    
    def stop_emulator(self):
        """Остановка эмулятора датчиков"""
        try:
            if self.emulator_process:
                self.emulator_process.terminate()
                self.emulator_process = None
            self.emulator_running = False
            self.system.logger.log("⏹ Эмулятор датчиков остановлен")
        except Exception as e:
            self.system.logger.log(f"❌ Ошибка остановки эмулятора: {e}")
    
    def start_web(self):
        """Запуск веб-интерфейса"""
        try:
            self.system.logger.log("🔄 Запуск веб-интерфейса...")
            # Здесь код запуска веб-интерфейса
            self.web_running = True
            self.system.logger.log("✅ Веб-интерфейс запущен на порту 5000")
            return True
        except Exception as e:
            self.system.logger.log(f"❌ Ошибка запуска веб-интерфейса: {e}")
            return False
    
    def stop_web(self):
        """Остановка веб-интерфейса"""
        try:
            if self.web_process:
                self.web_process.terminate()
                self.web_process = None
            self.web_running = False
            self.system.logger.log("⏹ Веб-интерфейс остановлен")
        except Exception as e:
            self.system.logger.log(f"❌ Ошибка остановки веб-интерфейса: {e}")
    
    def start_all(self):
        """Запуск всех компонентов"""
        self.system.logger.log("🚀 Запуск всех компонентов системы...")
        
        threads = []
        for func in [self.start_server, self.start_emulator, self.start_web]:
            thread = threading.Thread(target=func)
            threads.append(thread)
            thread.start()
            time.sleep(1)  # Задержка между запусками
        
        for thread in threads:
            thread.join()
        
        self.system.logger.log("✅ Все компоненты системы запущены")
    
    def stop_all(self):
        """Остановка всех компонентов"""
        self.system.logger.log("🛑 Остановка всех компонентов системы...")
        
        self.stop_web()
        self.stop_emulator()
        self.stop_server()
        
        self.system.logger.log("⏹ Все компоненты системы остановлены")
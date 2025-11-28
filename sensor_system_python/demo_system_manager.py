# demo_system_manager.py - Демо версия системы управления сенсорами
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from datetime import datetime

class DemoSensorSystemManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Демо: Sensor Data System Manager")
        self.root.geometry("800x600")
        
        # Демо данные
        self.demo_data = []
        self.generate_demo_data()
        
        # Статусы компонентов (для демо)
        self.server_running = False
        self.emulator_running = False
        self.web_running = False
        
        self.setup_ui()
        self.start_demo_monitor()
        
    def generate_demo_data(self):
        """Генерация демо данных"""
        devices = ["sensor_001", "sensor_002", "sensor_003"]
        for i in range(20):
            device = devices[i % 3]
            self.demo_data.append({
                "id": i + 1,
                "device_id": device,
                "temperature": round(20 + (i * 0.5), 1),
                "humidity": round(40 + (i * 1.2), 1),
                "light_level": round(100 + (i * 10), 1),
                "timestamp": f"2024-01-{(i % 28) + 1:02d} {i % 24:02d}:{(i * 3) % 60:02d}:00"
            })
    
    def setup_ui(self):
        """Настройка упрощенного интерфейса"""
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        
        # Вкладка управления
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Управление")
        
        # Вкладка данных
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="Данные")
        
        # Вкладка отправки
        send_frame = ttk.Frame(notebook)
        notebook.add(send_frame, text="Отправка")
        
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === ВКЛАДКА УПРАВЛЕНИЯ ===
        self.setup_control_tab(control_frame)
        
        # === ВКЛАДКА ДАННЫХ ===
        self.setup_data_tab(data_frame)
        
        # === ВКЛАДКА ОТПРАВКИ ===
        self.setup_send_tab(send_frame)
    
    def setup_control_tab(self, parent):
        """Настройка вкладки управления"""
        # Статус системы
        status_frame = ttk.LabelFrame(parent, text="Статус системы", padding=10)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.server_status = tk.Label(status_frame, text="❌ Сервер данных: Остановлен", fg="red")
        self.server_status.pack(anchor=tk.W)
        
        self.emulator_status = tk.Label(status_frame, text="❌ Эмулятор: Остановлен", fg="red")
        self.emulator_status.pack(anchor=tk.W)
        
        self.web_status = tk.Label(status_frame, text="❌ Веб-интерфейс: Остановлен", fg="red")
        self.web_status.pack(anchor=tk.W)
        
        # Кнопки управления
        button_frame = ttk.LabelFrame(parent, text="Демо управление", padding=10)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Простые кнопки управления
        ttk.Button(button_frame, text="▶ Запуск всех компонентов", 
                  command=self.start_all_demo).pack(pady=5)
        ttk.Button(button_frame, text="⏹ Остановка всех компонентов", 
                  command=self.stop_all_demo).pack(pady=5)
        
        # Информация
        info_frame = ttk.LabelFrame(parent, text="Информация", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        info_text = """
ДЕМО-РЕЖИМ

Эта демо-версия показывает основные возможности системы:

✓ Управление компонентами системы
✓ Просмотр данных сенсоров
✓ Отправка данных через разные протоколы
✓ Мониторинг статуса в реальном времени

Функции в демо-режиме:
• Кнопки управления имитируют запуск/остановку
• Данные генерируются автоматически
• Отправка данных работает в демо-режиме
• Все операции безопасны (не влияют на реальную систему)
"""
        
        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 10))
        info_label.pack(anchor=tk.W, padx=5, pady=5)
    
    def setup_data_tab(self, parent):
        """Настройка вкладки данных"""
        # Управление данными
        control_frame = ttk.LabelFrame(parent, text="Управление данными", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Обновить данные", 
                  command=self.update_data_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Добавить демо-запись", 
                  command=self.add_demo_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Очистить данные", 
                  command=self.clear_demo_data).pack(side=tk.LEFT, padx=5)
        
        # Таблица данных
        data_frame = ttk.LabelFrame(parent, text="Данные сенсоров (демо)", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("ID", "Устройство", "Температура", "Влажность", "Свет", "Время")
        self.data_tree = ttk.Treeview(data_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
        
        self.data_tree.pack(fill=tk.BOTH, expand=True)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        
        # Статистика
        stats_frame = ttk.LabelFrame(parent, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="Загрузка статистики...", justify=tk.LEFT)
        self.stats_label.pack(anchor=tk.W)
    
    def setup_send_tab(self, parent):
        """Настройка вкладки отправки"""
        # Выбор протокола
        protocol_frame = ttk.LabelFrame(parent, text="Выбор протокола (демо)", padding=10)
        protocol_frame.pack(fill=tk.X, pady=5)
        
        self.protocol_var = tk.StringVar(value="http")
        
        ttk.Radiobutton(protocol_frame, text="HTTP REST API", 
                       variable=self.protocol_var, value="http").pack(anchor=tk.W)
        ttk.Radiobutton(protocol_frame, text="TCP Socket", 
                       variable=self.protocol_var, value="tcp").pack(anchor=tk.W)
        ttk.Radiobutton(protocol_frame, text="UDP Socket", 
                       variable=self.protocol_var, value="udp").pack(anchor=tk.W)
        ttk.Radiobutton(protocol_frame, text="Email", 
                       variable=self.protocol_var, value="email").pack(anchor=tk.W)
        
        # Данные для отправки
        data_frame = ttk.LabelFrame(parent, text="Данные для отправки", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопки выбора данных
        select_frame = ttk.Frame(data_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(select_frame, text="Выбрать последние 5 записей", 
                  command=self.select_recent_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="Выбрать все данные", 
                  command=self.select_all_data).pack(side=tk.LEFT, padx=5)
        
        # Поле для данных
        self.send_data_text = scrolledtext.ScrolledText(data_frame, height=8, width=80)
        self.send_data_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопка отправки
        send_frame = ttk.Frame(data_frame)
        send_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(send_frame, text="📤 Отправить данные (демо)", 
                  command=self.send_data_demo).pack(side=tk.LEFT, padx=5)
        
        self.send_status = ttk.Label(send_frame, text="")
        self.send_status.pack(side=tk.LEFT, padx=10)
        
        # Лог отправки
        log_frame = ttk.LabelFrame(parent, text="Лог отправки", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def start_demo_monitor(self):
        """Запуск демо-мониторинга"""
        def monitor():
            while True:
                self.update_status_demo()
                self.update_statistics()
                time.sleep(3)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.update_data_view()
    
    def update_status_demo(self):
        """Обновление статусов в демо-режиме"""
        # Имитация случайного изменения статусов
        import random
        
        if random.random() > 0.8:  # 20% chance to change status
            self.server_running = not self.server_running if random.random() > 0.7 else self.server_running
        
        server_color = "green" if self.server_running else "red"
        server_text = "✅ Сервер данных: Запущен" if self.server_running else "❌ Сервер данных: Остановлен"
        self.server_status.config(text=server_text, fg=server_color)
        
        emulator_color = "green" if self.emulator_running else "red"
        emulator_text = "✅ Эмулятор: Запущен" if self.emulator_running else "❌ Эмулятор: Остановлен"
        self.emulator_status.config(text=emulator_text, fg=emulator_color)
        
        web_color = "green" if self.web_running else "red"
        web_text = "✅ Веб-интерфейс: Запущен" if self.web_running else "❌ Веб-интерфейс: Остановлен"
        self.web_status.config(text=web_text, fg=web_color)
    
    def update_statistics(self):
        """Обновление статистики"""
        total_records = len(self.demo_data)
        devices = len(set(item['device_id'] for item in self.demo_data))
        last_record = self.demo_data[-1]['timestamp'] if self.demo_data else "Нет данных"
        
        stats_text = f"""Статистика (демо):
• Всего записей: {total_records}
• Уникальных устройств: {devices}
• Последняя запись: {last_record}
• Сервер: {'✅ Запущен' if self.server_running else '❌ Остановлен'}
• Эмулятор: {'✅ Запущен' if self.emulator_running else '❌ Остановлен'}"""
        
        self.stats_label.config(text=stats_text)
    
    def update_data_view(self):
        """Обновление таблицы данных"""
        # Очищаем таблицу
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Добавляем данные (последние 15 записей)
        for item in self.demo_data[-15:]:
            self.data_tree.insert("", tk.END, values=(
                item['id'],
                item['device_id'],
                item['temperature'],
                item['humidity'],
                item['light_level'],
                item['timestamp']
            ))
    
    def add_demo_record(self):
        """Добавление демо-записи"""
        import random
        
        devices = ["sensor_001", "sensor_002", "sensor_003"]
        new_id = len(self.demo_data) + 1
        new_record = {
            "id": new_id,
            "device_id": random.choice(devices),
            "temperature": round(15 + random.random() * 20, 1),
            "humidity": round(30 + random.random() * 40, 1),
            "light_level": round(50 + random.random() * 150, 1),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.demo_data.append(new_record)
        self.update_data_view()
        self.log_message(f"Добавлена новая демо-запись: {new_record['device_id']}")
    
    def clear_demo_data(self):
        """Очистка демо-данных"""
        if messagebox.askyesno("Подтверждение", "Очистить все демо-данные?"):
            self.demo_data.clear()
            self.generate_demo_data()  # Генерируем базовые данные заново
            self.update_data_view()
            self.log_message("Демо-данные очищены")
    
    def select_recent_data(self):
        """Выбор последних записей"""
        recent_data = self.demo_data[-5:]  # Последние 5 записей
        self.send_data_text.delete(1.0, tk.END)
        self.send_data_text.insert(1.0, json.dumps(recent_data, indent=2, ensure_ascii=False))
        self.log_message("Выбраны последние 5 записей для отправки")
    
    def select_all_data(self):
        """Выбор всех данных"""
        self.send_data_text.delete(1.0, tk.END)
        self.send_data_text.insert(1.0, json.dumps(self.demo_data, indent=2, ensure_ascii=False))
        self.log_message(f"Выбраны все записи ({len(self.demo_data)} шт.) для отправки")
    
    def send_data_demo(self):
        """Демо-отправка данных"""
        data_text = self.send_data_text.get(1.0, tk.END).strip()
        if not data_text:
            messagebox.showwarning("Предупреждение", "Нет данных для отправки")
            return
        
        protocol = self.protocol_var.get()
        
        # Имитация отправки
        self.log_message(f"⚡ Начинается отправка данных через {protocol.upper()}...")
        self.send_status.config(text="⏳ Отправка...", foreground="orange")
        
        # Имитация задержки сети
        self.root.after(2000, lambda: self.finish_send_demo(protocol, data_text))
    
    def finish_send_demo(self, protocol, data):
        """Завершение демо-отправки"""
        try:
            # Парсим данные для проверки
            json_data = json.loads(data)
            record_count = len(json_data) if isinstance(json_data, list) else 1
            
            success_msg = f"✅ Успешно отправлено {record_count} записей через {protocol.upper()}"
            self.log_message(success_msg)
            self.send_status.config(text="✅ Успешно отправлено", foreground="green")
            
            # Демо-ответы для разных протоколов
            responses = {
                "http": "HTTP 200 OK - Данные приняты сервером",
                "tcp": "TCP ACK - Соединение установлено, данные доставлены",
                "udp": "UDP - Данные отправлены (без подтверждения)",
                "email": "Email отправлен успешно - SMTP 250 OK"
            }
            
            self.log_message(f"📨 Ответ: {responses.get(protocol, 'Успешно')}")
            
        except json.JSONDecodeError:
            error_msg = "❌ Ошибка: Неверный формат JSON данных"
            self.log_message(error_msg)
            self.send_status.config(text="❌ Ошибка формата", foreground="red")
    
    def start_all_demo(self):
        """Демо-запуск всех компонентов"""
        self.log_message("🚀 Запуск всех компонентов системы...")
        self.send_status.config(text="", foreground="black")
        
        # Имитация последовательного запуска
        def simulate_start():
            self.server_running = True
            self.update_status_demo()
            self.log_message("✅ Сервер данных запущен (порт 8080)")
            
            self.root.after(1000, lambda: [
                setattr(self, 'emulator_running', True),
                self.update_status_demo(),
                self.log_message("✅ Эмулятор датчиков запущен")
            ])
            
            self.root.after(2000, lambda: [
                setattr(self, 'web_running', True),
                self.update_status_demo(),
                self.log_message("✅ Веб-интерфейс запущен (порт 5000)"),
                self.log_message("🎉 Все компоненты успешно запущены!")
            ])
        
        simulate_start()
    
    def stop_all_demo(self):
        """Демо-остановка всех компонентов"""
        self.log_message("🛑 Остановка всех компонентов системы...")
        
        # Имитация последовательной остановки
        def simulate_stop():
            self.web_running = False
            self.update_status_demo()
            self.log_message("✅ Веб-интерфейс остановлен")
            
            self.root.after(1000, lambda: [
                setattr(self, 'emulator_running', False),
                self.update_status_demo(),
                self.log_message("✅ Эмулятор датчиков остановлен")
            ])
            
            self.root.after(2000, lambda: [
                setattr(self, 'server_running', False),
                self.update_status_demo(),
                self.log_message("✅ Сервер данных остановлен"),
                self.log_message("🔴 Все компоненты остановлены")
            ])
        
        simulate_stop()
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

def main():
    """Запуск демо-приложения"""
    root = tk.Tk()
    app = DemoSensorSystemManager(root)
    
    # Добавляем информацию о демо-режиме
    root.after(1000, lambda: messagebox.showinfo(
        "Демо-режим", 
        "Вы используете демо-версию системы управления сенсорами.\n\n"
        "Все функции работают в имитационном режиме и не влияют на реальную систему."
    ))
    
    root.mainloop()

if __name__ == "__main__":
    main()
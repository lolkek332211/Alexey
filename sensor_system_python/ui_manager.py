# ui_manager.py - Управление пользовательским интерфейсом с 3D визуализацией
import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import time

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib не установлен. 3D визуализация будет недоступна. - ui_manager.py:15")

class UIManager:
    def __init__(self, system_manager, root):
        self.system = system_manager
        self.root = root
        
        # 3D визуализация
        self.fig_3d = None
        self.ax_3d = None
        self.canvas_3d = None
        self.drone_3d_objects = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        
        # Вкладка управления
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Управление системой")
        
        # Вкладка 3D визуализации
        visualization_3d_frame = ttk.Frame(notebook)
        notebook.add(visualization_3d_frame, text="3D Модель дрона")
        
        # Вкладка мониторинга дрона
        drone_frame = ttk.Frame(notebook)
        notebook.add(drone_frame, text="Мониторинг дрона")
        
        # Вкладка лопастей
        blades_frame = ttk.Frame(notebook)
        notebook.add(blades_frame, text="Состояние лопастей")
        
        # Вкладка навигации
        navigation_frame = ttk.Frame(notebook)
        notebook.add(navigation_frame, text="Навигация и сенсоры")
        
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Настройка вкладок
        self.setup_control_tab(control_frame)
        self.setup_3d_visualization_tab(visualization_3d_frame)
        self.setup_drone_tab(drone_frame)
        self.setup_blades_tab(blades_frame)
        self.setup_navigation_tab(navigation_frame)
    
    def setup_control_tab(self, parent):
        """Настройка вкладки управления системой"""
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
        button_frame = ttk.LabelFrame(parent, text="Управление компонентами", padding=10)
        button_frame.pack(fill=tk.X, pady=5)
        
        server_frame = ttk.Frame(button_frame)
        server_frame.pack(fill=tk.X, pady=2)
        ttk.Label(server_frame, text="Сервер данных:").pack(side=tk.LEFT)
        ttk.Button(server_frame, text="Запуск", 
                  command=self.system.controller.start_server).pack(side=tk.LEFT, padx=5)
        ttk.Button(server_frame, text="Остановка", 
                  command=self.system.controller.stop_server).pack(side=tk.LEFT, padx=5)
        
        emulator_frame = ttk.Frame(button_frame)
        emulator_frame.pack(fill=tk.X, pady=2)
        ttk.Label(emulator_frame, text="Эмулятор датчиков:").pack(side=tk.LEFT)
        ttk.Button(emulator_frame, text="Запуск", 
                  command=self.system.controller.start_emulator).pack(side=tk.LEFT, padx=5)
        ttk.Button(emulator_frame, text="Остановка", 
                  command=self.system.controller.stop_emulator).pack(side=tk.LEFT, padx=5)
        
        web_frame = ttk.Frame(button_frame)
        web_frame.pack(fill=tk.X, pady=2)
        ttk.Label(web_frame, text="Веб-интерфейс:").pack(side=tk.LEFT)
        ttk.Button(web_frame, text="Запуск", 
                  command=self.system.controller.start_web).pack(side=tk.LEFT, padx=5)
        ttk.Button(web_frame, text="Остановка", 
                  command=self.system.controller.stop_web).pack(side=tk.LEFT, padx=5)
        
        group_frame = ttk.Frame(button_frame)
        group_frame.pack(fill=tk.X, pady=10)
        ttk.Button(group_frame, text="▶ Запуск всего", 
                  command=self.system.controller.start_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(group_frame, text="⏹ Остановка всего", 
                  command=self.system.controller.stop_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(group_frame, text="🚨 Аварийная остановка", 
                  command=self.system.emergency_stop).pack(side=tk.LEFT, padx=5)
        
        # Лог системы
        log_frame = ttk.LabelFrame(parent, text="Лог системы", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def setup_drone_tab(self, parent):
        """Настройка вкладки мониторинга дрона"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Управление дроном
        control_frame = ttk.LabelFrame(main_frame, text="Управление дроном", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.drone_status_label = tk.Label(control_frame, text="🛑 ДРОН НА ЗЕМЛЕ", 
                                          font=("Arial", 12, "bold"), fg="red")
        self.drone_status_label.pack()
        
        flight_frame = ttk.LabelFrame(control_frame, text="Управление полетом", padding=5)
        flight_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(flight_frame, text="🛫 Взлет", 
                  command=self.system.physics.takeoff).pack(fill=tk.X, pady=2)
        ttk.Button(flight_frame, text="🛬 Посадка", 
                  command=self.system.physics.land).pack(fill=tk.X, pady=2)
        ttk.Button(flight_frame, text="🎯 Автополет к цели", 
                  command=self.system.physics.auto_pilot).pack(fill=tk.X, pady=2)
        
        # Информация о дроне
        info_frame = ttk.LabelFrame(main_frame, text="Информация о дроне", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.drone_info_text = scrolledtext.ScrolledText(info_frame, height=15)
        self.drone_info_text.pack(fill=tk.BOTH, expand=True)
        self.drone_info_text.config(state=tk.DISABLED)
    
    def setup_blades_tab(self, parent):
        """Настройка вкладки состояния лопастей"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        blades_frame = ttk.Frame(main_frame)
        blades_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фреймы для лопастей
        self.blade_frames = []
        positions = ["Передняя левая", "Передняя правая", "Задняя левая", "Задняя правая"]
        
        for i in range(4):
            frame = ttk.LabelFrame(blades_frame, text=f"🔄 Лопасть {i+1} ({positions[i]})", padding=10)
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            self.blade_frames.append(frame)
            self.setup_blade_display(frame, i)
        
        blades_frame.columnconfigure(0, weight=1)
        blades_frame.columnconfigure(1, weight=1)
        blades_frame.rowconfigure(0, weight=1)
        blades_frame.rowconfigure(1, weight=1)
    
    def setup_blade_display(self, parent, blade_index):
        """Настройка отображения лопасти"""
        # RPM
        rpm_frame = ttk.Frame(parent)
        rpm_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rpm_frame, text="RPM:").pack(side=tk.LEFT)
        setattr(self, f'rpm_label_{blade_index}', 
                tk.Label(rpm_frame, text="0", font=("Arial", 10, "bold")))
        getattr(self, f'rpm_label_{blade_index}').pack(side=tk.RIGHT)
        
        # Температура
        temp_frame = ttk.Frame(parent)
        temp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(temp_frame, text="Температура:").pack(side=tk.LEFT)
        setattr(self, f'temp_label_{blade_index}', 
                tk.Label(temp_frame, text="25°C", font=("Arial", 10)))
        getattr(self, f'temp_label_{blade_index}').pack(side=tk.RIGHT)
        
        # Вибрация
        vib_frame = ttk.Frame(parent)
        vib_frame.pack(fill=tk.X, pady=2)
        ttk.Label(vib_frame, text="Вибрация:").pack(side=tk.LEFT)
        setattr(self, f'vib_label_{blade_index}', 
                tk.Label(vib_frame, text="0.0", font=("Arial", 10)))
        getattr(self, f'vib_label_{blade_index}').pack(side=tk.RIGHT)
        
        # Здоровье
        health_frame = ttk.Frame(parent)
        health_frame.pack(fill=tk.X, pady=2)
        ttk.Label(health_frame, text="Здоровье:").pack(side=tk.LEFT)
        setattr(self, f'health_label_{blade_index}', 
                tk.Label(health_frame, text="100%", font=("Arial", 10, "bold")))
        getattr(self, f'health_label_{blade_index}').pack(side=tk.RIGHT)
        
        # Статус
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=2)
        ttk.Label(status_frame, text="Статус:").pack(side=tk.LEFT)
        setattr(self, f'status_label_{blade_index}', 
                tk.Label(status_frame, text="Остановлена", font=("Arial", 10)))
        getattr(self, f'status_label_{blade_index}').pack(side=tk.RIGHT)
    
    def setup_3d_visualization_tab(self, parent):
        """Настройка вкладки 3D визуализации"""
        if not MATPLOTLIB_AVAILABLE:
            error_frame = ttk.Frame(parent)
            error_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            error_label = tk.Label(error_frame, 
                                 text="Matplotlib не установлен!\n\n"
                                      "Установите для 3D визуализации:\n"
                                      "pip install matplotlib numpy",
                                 font=("Arial", 12), fg="red", justify=tk.CENTER)
            error_label.pack(expand=True)
            return
        
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаем 3D график
        self.fig_3d = plt.Figure(figsize=(10, 8), dpi=100)
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        
        # Настраиваем canvas для Tkinter
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, main_frame)
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Кнопки управления 3D видом
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Вид сверху", 
                  command=lambda: self.set_3d_view('top')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Вид сбоку", 
                  command=lambda: self.set_3d_view('side')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Вид спереди", 
                  command=lambda: self.set_3d_view('front')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Изометрический вид", 
                  command=lambda: self.set_3d_view('isometric')).pack(side=tk.LEFT, padx=5)
        
        # Инициализация 3D сцены
        self.setup_3d_scene()
    
    def setup_3d_scene(self):
        """Инициализация 3D сцены"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        # Настраиваем 3D сцену
        self.ax_3d.set_xlabel('X (м)')
        self.ax_3d.set_ylabel('Y (м)')
        self.ax_3d.set_zlabel('Z (м)')
        self.ax_3d.set_title('3D Модель дрона в полете')
        
        # Устанавливаем начальные пределы
        self.ax_3d.set_xlim(-10, 30)
        self.ax_3d.set_ylim(-10, 30)
        self.ax_3d.set_zlim(0, 30)
        
        # Создаем сетку земли
        self.create_ground_grid()
        
        # Создаем начальную модель дрона
        self.create_drone_3d_model()
        
        # Создаем целевую точку
        self.create_target_3d()
        
        # Настраиваем изометрический вид
        self.set_3d_view('isometric')
    
    def create_ground_grid(self):
        """Создание сетки земли"""
        x = np.linspace(-10, 30, 20)
        y = np.linspace(-10, 30, 20)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        
        self.ax_3d.plot_surface(X, Y, Z, alpha=0.3, color='gray')
        
        # Добавляем линии сетки
        for i in range(len(x)):
            self.ax_3d.plot([x[i], x[i]], [y[0], y[-1]], [0, 0], 'k-', alpha=0.2, linewidth=0.5)
        for i in range(len(y)):
            self.ax_3d.plot([x[0], x[-1]], [y[i], y[i]], [0, 0], 'k-', alpha=0.2, linewidth=0.5)
    
    def create_drone_3d_model(self):
        """Создание 3D модели дрона"""
        # Параметры дрона
        body_size = 0.5
        arm_length = 1.0
        propeller_radius = 0.3
        
        # Корпус дрона (куб)
        body_vertices = np.array([
            [-body_size, -body_size, -body_size],
            [body_size, -body_size, -body_size],
            [body_size, body_size, -body_size],
            [-body_size, body_size, -body_size],
            [-body_size, -body_size, body_size],
            [body_size, -body_size, body_size],
            [body_size, body_size, body_size],
            [-body_size, body_size, body_size]
        ])
        
        # Руки дрона
        arm_positions = [
            [-arm_length, 0, 0],  # левая
            [arm_length, 0, 0],   # правая
            [0, -arm_length, 0],  # передняя
            [0, arm_length, 0]    # задняя
        ]
        
        # Создаем корпус (упрощенный)
        self.drone_3d_objects['body'] = self.ax_3d.plot(
            [0], [0], [0], 'o', color='blue', markersize=10
        )[0]
        
        # Создаем руки
        for i, pos in enumerate(arm_positions):
            # Линия руки
            self.drone_3d_objects[f'arm_{i}'] = self.ax_3d.plot(
                [0, pos[0]], [0, pos[1]], [0, 0], 
                color='black', linewidth=3
            )[0]
            
            # Основание пропеллера
            self.drone_3d_objects[f'motor_{i}'] = self.ax_3d.plot(
                [pos[0]], [pos[1]], [0], 
                'o', color='gray', markersize=8
            )[0]
        
        # Создаем пропеллеры
        self.create_propellers_3d(arm_positions, propeller_radius)
        
        # Траектория
        self.drone_3d_objects['trajectory'] = self.ax_3d.plot(
            [], [], [], 'b-', alpha=0.5, linewidth=2
        )[0]
        
        # Вектор скорости
        self.drone_3d_objects['velocity_vector'] = self.ax_3d.quiver(
            0, 0, 0, 0, 0, 0, 
            color='red', linewidth=2, arrow_length_ratio=0.3
        )
    
    def create_propellers_3d(self, arm_positions, radius):
        """Создание 3D пропеллеров"""
        for i, pos in enumerate(arm_positions):
            # Лопасти пропеллера
            self.drone_3d_objects[f'propeller_blade1_{i}'] = self.ax_3d.plot(
                [pos[0] - radius, pos[0] + radius],
                [pos[1], pos[1]],
                [0, 0],
                color='orange', linewidth=3
            )[0]
            
            self.drone_3d_objects[f'propeller_blade2_{i}'] = self.ax_3d.plot(
                [pos[0], pos[0]],
                [pos[1] - radius, pos[1] + radius],
                [0, 0],
                color='orange', linewidth=3
            )[0]
    
    def create_target_3d(self):
        """Создание 3D целевой точки"""
        physics = self.system.physics
        
        # Целевая точка (сфера)
        u = np.linspace(0, 2 * np.pi, 10)
        v = np.linspace(0, np.pi, 10)
        x = 0.5 * np.outer(np.cos(u), np.sin(v)) + physics.target_point[0]
        y = 0.5 * np.outer(np.sin(u), np.sin(v)) + physics.target_point[1]
        z = 0.5 * np.outer(np.ones(np.size(u)), np.cos(v)) + physics.target_point[2]
        
        self.drone_3d_objects['target'] = self.ax_3d.plot_surface(
            x, y, z, color='red', alpha=0.6
        )
    
    def update_3d_visualization(self):
        """Обновление 3D визуализации"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        try:
            physics = self.system.physics
            
            # Обновляем позицию дрона
            x, y, z = physics.drone_position
            
            # Обновляем корпус
            self.drone_3d_objects['body'].set_data([x], [y])
            self.drone_3d_objects['body'].set_3d_properties([z])
            
            # Обновляем руки
            arm_positions = [
                [-1.0, 0, 0], [1.0, 0, 0], [0, -1.0, 0], [0, 1.0, 0]
            ]
            
            for i, arm_pos in enumerate(arm_positions):
                # Руки
                self.drone_3d_objects[f'arm_{i}'].set_data(
                    [x, x + arm_pos[0]], [y, y + arm_pos[1]]
                )
                self.drone_3d_objects[f'arm_{i}'].set_3d_properties([z, z])
                
                # Моторы
                self.drone_3d_objects[f'motor_{i}'].set_data(
                    [x + arm_pos[0]], [y + arm_pos[1]]
                )
                self.drone_3d_objects[f'motor_{i}'].set_3d_properties([z])
            
            # Обновляем траекторию
            if len(physics.trajectory) > 1:
                traj_array = np.array(physics.trajectory)
                self.drone_3d_objects['trajectory'].set_data(traj_array[:, 0], traj_array[:, 1])
                self.drone_3d_objects['trajectory'].set_3d_properties(traj_array[:, 2])
            
            # Обновляем векторы
            vx, vy, vz = physics.drone_velocity
            
            # Удаляем старые векторы
            self.drone_3d_objects['velocity_vector'].remove()
            
            # Создаем новые векторы
            self.drone_3d_objects['velocity_vector'] = self.ax_3d.quiver(
                x, y, z, vx, vy, vz, 
                color='red', linewidth=2, arrow_length_ratio=0.3
            )
            
            # Обновляем вращение пропеллеров
            self.update_propellers_rotation()
            
            # Автоматическое масштабирование
            self.auto_scale_3d_view()
            
            # Обновляем canvas
            self.canvas_3d.draw_idle()
            
        except Exception as e:
            print(f"Ошибка обновления 3D: {e} - ui_manager.py:458")
    
    def update_propellers_rotation(self):
        """Обновление вращения пропеллеров"""
        physics = self.system.physics
        x, y, z = physics.drone_position
        
        for i, blade in enumerate(physics.blades):
            if blade['status'] == 'running' and blade['rpm'] > 0:
                # Позиции моторов
                arm_positions = [
                    [-1.0, 0], [1.0, 0], [0, -1.0], [0, 1.0]
                ]
                pos = arm_positions[i]
                
                # Лопасть 1
                x1 = x + pos[0] + 0.3 * math.cos(blade['rotation_angle'])
                y1 = y + pos[1] + 0.3 * math.sin(blade['rotation_angle'])
                x2 = x + pos[0] - 0.3 * math.cos(blade['rotation_angle'])
                y2 = y + pos[1] - 0.3 * math.sin(blade['rotation_angle'])
                
                self.drone_3d_objects[f'propeller_blade1_{i}'].set_data([x1, x2], [y1, y2])
                self.drone_3d_objects[f'propeller_blade1_{i}'].set_3d_properties([z, z])
                
                # Лопасть 2 (перпендикулярна первой)
                x1 = x + pos[0] + 0.3 * math.cos(blade['rotation_angle'] + math.pi/2)
                y1 = y + pos[1] + 0.3 * math.sin(blade['rotation_angle'] + math.pi/2)
                x2 = x + pos[0] - 0.3 * math.cos(blade['rotation_angle'] + math.pi/2)
                y2 = y + pos[1] - 0.3 * math.sin(blade['rotation_angle'] + math.pi/2)
                
                self.drone_3d_objects[f'propeller_blade2_{i}'].set_data([x1, x2], [y1, y2])
                self.drone_3d_objects[f'propeller_blade2_{i}'].set_3d_properties([z, z])
    
    def auto_scale_3d_view(self):
        """Автоматическое масштабирование 3D вида"""
        physics = self.system.physics
        x, y, z = physics.drone_position
        
        # Вычисляем подходящие пределы
        margin = 10
        x_min = min(-10, x - margin)
        x_max = max(30, x + margin)
        y_min = min(-10, y - margin)
        y_max = max(30, y + margin)
        z_min = 0
        z_max = max(30, z + margin)
        
        self.ax_3d.set_xlim(x_min, x_max)
        self.ax_3d.set_ylim(y_min, y_max)
        self.ax_3d.set_zlim(z_min, z_max)
    
    def set_3d_view(self, view_type):
        """Установка типа 3D вида"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        if view_type == 'top':
            self.ax_3d.view_init(elev=90, azim=-90)
        elif view_type == 'side':
            self.ax_3d.view_init(elev=0, azim=-90)
        elif view_type == 'front':
            self.ax_3d.view_init(elev=0, azim=0)
        elif view_type == 'isometric':
            self.ax_3d.view_init(elev=30, azim=45)
        
        self.canvas_3d.draw_idle()
    
    def setup_navigation_tab(self, parent):
        """Настройка вкладки навигации и сенсоров"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - GPS
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Правая панель - Барометр и IMU
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # GPS панель
        gps_frame = ttk.LabelFrame(left_frame, text="🌍 GPS Навигация", padding=10)
        gps_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Координаты GPS
        coords_frame = ttk.LabelFrame(gps_frame, text="Координаты", padding=5)
        coords_frame.pack(fill=tk.X, pady=5)
        
        # Широта
        lat_frame = ttk.Frame(coords_frame)
        lat_frame.pack(fill=tk.X, pady=2)
        ttk.Label(lat_frame, text="Широта:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.gps_lat_label = tk.Label(lat_frame, text="55.7558°", font=("Arial", 10, "bold"))
        self.gps_lat_label.pack(side=tk.RIGHT)
        
        # Долгота
        lon_frame = ttk.Frame(coords_frame)
        lon_frame.pack(fill=tk.X, pady=2)
        ttk.Label(lon_frame, text="Долгота:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.gps_lon_label = tk.Label(lon_frame, text="37.6173°", font=("Arial", 10, "bold"))
        self.gps_lon_label.pack(side=tk.RIGHT)
        
        # Высота
        alt_frame = ttk.Frame(coords_frame)
        alt_frame.pack(fill=tk.X, pady=2)
        ttk.Label(alt_frame, text="Высота:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.gps_alt_label = tk.Label(alt_frame, text="0.0 м", font=("Arial", 10, "bold"))
        self.gps_alt_label.pack(side=tk.RIGHT)
        
        # Параметры GPS
        params_frame = ttk.LabelFrame(gps_frame, text="Параметры GPS", padding=5)
        params_frame.pack(fill=tk.X, pady=5)
        
        # Скорость
        speed_frame = ttk.Frame(params_frame)
        speed_frame.pack(fill=tk.X, pady=2)
        ttk.Label(speed_frame, text="Скорость:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.gps_speed_label = tk.Label(speed_frame, text="0.0 м/с", font=("Arial", 9))
        self.gps_speed_label.pack(side=tk.RIGHT)
        
        # Курс
        course_frame = ttk.Frame(params_frame)
        course_frame.pack(fill=tk.X, pady=2)
        ttk.Label(course_frame, text="Курс:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.gps_course_label = tk.Label(course_frame, text="0°", font=("Arial", 9))
        self.gps_course_label.pack(side=tk.RIGHT)
        
        # Спутники
        sat_frame = ttk.Frame(params_frame)
        sat_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sat_frame, text="Спутники:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.gps_satellites_label = tk.Label(sat_frame, text="8", font=("Arial", 9))
        self.gps_satellites_label.pack(side=tk.RIGHT)
        
        # HDOP
        hdop_frame = ttk.Frame(params_frame)
        hdop_frame.pack(fill=tk.X, pady=2)
        ttk.Label(hdop_frame, text="Точность (HDOP):", font=("Arial", 9)).pack(side=tk.LEFT)
        self.gps_hdop_label = tk.Label(hdop_frame, text="1.2", font=("Arial", 9))
        self.gps_hdop_label.pack(side=tk.RIGHT)
        
        # Барометр панель
        baro_frame = ttk.LabelFrame(right_frame, text="📊 Барометр", padding=10)
        baro_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Давление
        pressure_frame = ttk.Frame(baro_frame)
        pressure_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pressure_frame, text="Давление:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.baro_pressure_label = tk.Label(pressure_frame, text="1013.25 hPa", font=("Arial", 10, "bold"))
        self.baro_pressure_label.pack(side=tk.RIGHT)
        
        # Температура
        temp_frame = ttk.Frame(baro_frame)
        temp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(temp_frame, text="Температура:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.baro_temp_label = tk.Label(temp_frame, text="15.0°C", font=("Arial", 10, "bold"))
        self.baro_temp_label.pack(side=tk.RIGHT)
        
        # Высота по барометру
        baro_alt_frame = ttk.Frame(baro_frame)
        baro_alt_frame.pack(fill=tk.X, pady=2)
        ttk.Label(baro_alt_frame, text="Барометрическая высота:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.baro_alt_label = tk.Label(baro_alt_frame, text="0.0 м", font=("Arial", 10, "bold"))
        self.baro_alt_label.pack(side=tk.RIGHT)
        
        # Вертикальная скорость
        vspeed_frame = ttk.Frame(baro_frame)
        vspeed_frame.pack(fill=tk.X, pady=2)
        ttk.Label(vspeed_frame, text="Вертикальная скорость:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.baro_vspeed_label = tk.Label(vspeed_frame, text="0.0 м/с", font=("Arial", 10, "bold"))
        self.baro_vspeed_label.pack(side=tk.RIGHT)
        
        # IMU панель
        imu_frame = ttk.LabelFrame(right_frame, text="🎯 IMU (Inertial Measurement Unit)", padding=10)
        imu_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Акселерометр
        accel_frame = ttk.LabelFrame(imu_frame, text="Акселерометр", padding=5)
        accel_frame.pack(fill=tk.X, pady=2)
        
        accel_x_frame = ttk.Frame(accel_frame)
        accel_x_frame.pack(fill=tk.X, pady=1)
        ttk.Label(accel_x_frame, text="X:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.imu_accel_x_label = tk.Label(accel_x_frame, text="0.00 g", font=("Arial", 8))
        self.imu_accel_x_label.pack(side=tk.RIGHT)
        
        accel_y_frame = ttk.Frame(accel_frame)
        accel_y_frame.pack(fill=tk.X, pady=1)
        ttk.Label(accel_y_frame, text="Y:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.imu_accel_y_label = tk.Label(accel_y_frame, text="0.00 g", font=("Arial", 8))
        self.imu_accel_y_label.pack(side=tk.RIGHT)
        
        accel_z_frame = ttk.Frame(accel_frame)
        accel_z_frame.pack(fill=tk.X, pady=1)
        ttk.Label(accel_z_frame, text="Z:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.imu_accel_z_label = tk.Label(accel_z_frame, text="0.00 g", font=("Arial", 8))
        self.imu_accel_z_label.pack(side=tk.RIGHT)
        
        # Гироскоп
        gyro_frame = ttk.LabelFrame(imu_frame, text="Гироскоп", padding=5)
        gyro_frame.pack(fill=tk.X, pady=2)
        
        gyro_x_frame = ttk.Frame(gyro_frame)
        gyro_x_frame.pack(fill=tk.X, pady=1)
        ttk.Label(gyro_x_frame, text="X:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.imu_gyro_x_label = tk.Label(gyro_x_frame, text="0.00 °/s", font=("Arial", 8))
        self.imu_gyro_x_label.pack(side=tk.RIGHT)
        
        gyro_y_frame = ttk.Frame(gyro_frame)
        gyro_y_frame.pack(fill=tk.X, pady=1)
        ttk.Label(gyro_y_frame, text="Y:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.imu_gyro_y_label = tk.Label(gyro_y_frame, text="0.00 °/s", font=("Arial", 8))
        self.imu_gyro_y_label.pack(side=tk.RIGHT)
        
        gyro_z_frame = ttk.Frame(gyro_frame)
        gyro_z_frame.pack(fill=tk.X, pady=1)
        ttk.Label(gyro_z_frame, text="Z:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.imu_gyro_z_label = tk.Label(gyro_z_frame, text="0.00 °/s", font=("Arial", 8))
        self.imu_gyro_z_label.pack(side=tk.RIGHT)
    
    def update_all_displays(self):
        """Обновление всех дисплеев"""
        try:
            self.update_status_displays()
            self.update_drone_display()
            self.update_blades_display()
            self.update_sensors_display()
            self.update_log_display()
            if MATPLOTLIB_AVAILABLE:
                self.update_3d_visualization()
        except Exception as e:
            print(f"Ошибка обновления дисплеев: {e} - ui_manager.py:690")
    
    def update_status_displays(self):
        """Обновление статусов системы"""
        try:
            controller = self.system.controller
            
            # Сервер
            server_text = "✅ Сервер данных: Запущен" if controller.server_running else "❌ Сервер данных: Остановлен"
            server_color = "green" if controller.server_running else "red"
            self.server_status.config(text=server_text, fg=server_color)
            
            # Эмулятор
            emulator_text = "✅ Эмулятор: Запущен" if controller.emulator_running else "❌ Эмулятор: Остановлен"
            emulator_color = "green" if controller.emulator_running else "red"
            self.emulator_status.config(text=emulator_text, fg=emulator_color)
            
            # Веб-интерфейс
            web_text = "✅ Веб-интерфейс: Запущен" if controller.web_running else "❌ Веб-интерфейс: Остановлен"
            web_color = "green" if controller.web_running else "red"
            self.web_status.config(text=web_text, fg=web_color)
        except Exception as e:
            print(f"Ошибка обновления статусов: {e} - ui_manager.py:712")
    
    def update_drone_display(self):
        """Обновление информации о дроне"""
        try:
            physics = self.system.physics
            
            # Статус дрона
            status_text = physics.get_flight_status()
            
            # Цвет статуса
            if physics.flight_mode == 'stopped':
                status_color = "red"
            elif physics.flight_mode in ['taking_off', 'landing']:
                status_color = "orange"
            elif physics.flight_mode == 'auto_pilot':
                status_color = "blue"
            elif physics.flight_mode == 'emergency':
                status_color = "red"
            else:
                status_color = "green"
            
            self.drone_status_label.config(text=status_text, fg=status_color)
            
            # Информация о дроне
            info_text = physics.get_drone_info()
            
            self.drone_info_text.config(state=tk.NORMAL)
            self.drone_info_text.delete(1.0, tk.END)
            self.drone_info_text.insert(1.0, info_text)
            self.drone_info_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Ошибка обновления информации о дроне: {e} - ui_manager.py:744")
    
    def update_blades_display(self):
        """Обновление отображения лопастей"""
        try:
            physics = self.system.physics
            
            for i, blade in enumerate(physics.blades):
                # RPM
                rpm_label = getattr(self, f'rpm_label_{i}')
                rpm_label.config(text=f"{blade['rpm']:.0f}")
                rpm_label.config(fg="red" if blade['rpm'] > 2000 else 
                               "orange" if blade['rpm'] > 1000 else "green")
                
                # Температура
                temp_label = getattr(self, f'temp_label_{i}')
                temp_label.config(text=f"{blade['temperature']:.1f}°C")
                temp_label.config(fg="red" if blade['temperature'] > 60 else 
                                "orange" if blade['temperature'] > 40 else "green")
                
                # Вибрация
                vib_label = getattr(self, f'vib_label_{i}')
                vib_label.config(text=f"{blade['vibration']:.1f}")
                vib_label.config(fg="red" if blade['vibration'] > 8 else 
                               "orange" if blade['vibration'] > 4 else "green")
                
                # Здоровье
                health_label = getattr(self, f'health_label_{i}')
                health_label.config(text=f"{blade['health']:.1f}%")
                health_label.config(fg="red" if blade['health'] < 50 else 
                                  "orange" if blade['health'] < 80 else "green")
                
                # Статус
                status_label = getattr(self, f'status_label_{i}')
                status_translation = {
                    'stopped': 'Остановлена',
                    'spinning_up': 'Запуск',
                    'running': 'Работает',
                    'landing': 'Посадка',
                    'emergency_stop': 'АВАРИЯ'
                }
                display_text = status_translation.get(blade['status'], blade['status'])
                status_label.config(text=display_text)
                
                status_color = ("red" if blade['status'] == 'emergency_stop' else
                              "green" if blade['status'] == 'running' else
                              "orange" if blade['status'] in ['spinning_up', 'landing'] else "gray")
                status_label.config(fg=status_color)
        except Exception as e:
            print(f"Ошибка обновления лопастей: {e} - ui_manager.py:793")
    
    def update_sensors_display(self):
        """Обновление отображения сенсоров"""
        try:
            sensors = self.system.sensors
            
            # GPS данные
            self.gps_lat_label.config(text=f"{sensors.gps_data['latitude']:.6f}°")
            self.gps_lon_label.config(text=f"{sensors.gps_data['longitude']:.6f}°")
            self.gps_alt_label.config(text=f"{sensors.gps_data['altitude']:.1f} м")
            self.gps_speed_label.config(text=f"{sensors.gps_data['speed']:.1f} м/с")
            self.gps_course_label.config(text=f"{sensors.gps_data['course']:.0f}°")
            self.gps_satellites_label.config(text=f"{sensors.gps_data['satellites']}")
            self.gps_hdop_label.config(text=f"{sensors.gps_data['hdop']:.1f}")
            
            # Барометр данные
            self.baro_pressure_label.config(text=f"{sensors.barometer_data['pressure']:.1f} hPa")
            self.baro_temp_label.config(text=f"{sensors.barometer_data['temperature']:.1f}°C")
            self.baro_alt_label.config(text=f"{sensors.barometer_data['altitude']:.1f} м")
            self.baro_vspeed_label.config(text=f"{sensors.barometer_data['vertical_speed']:.1f} м/с")
            
            # IMU данные
            self.imu_accel_x_label.config(text=f"{sensors.imu_data['acceleration_x']:.2f} g")
            self.imu_accel_y_label.config(text=f"{sensors.imu_data['acceleration_y']:.2f} g")
            self.imu_accel_z_label.config(text=f"{sensors.imu_data['acceleration_z']:.2f} g")
            self.imu_gyro_x_label.config(text=f"{sensors.imu_data['gyro_x']:.2f} °/s")
            self.imu_gyro_y_label.config(text=f"{sensors.imu_data['gyro_y']:.2f} °/s")
            self.imu_gyro_z_label.config(text=f"{sensors.imu_data['gyro_z']:.2f} °/s")
        except Exception as e:
            print(f"Ошибка обновления сенсоров: {e} - ui_manager.py:823")
    
    def update_log_display(self):
        """Обновление лога системы"""
        try:
            # Получаем последние логи из системы
            recent_logs = self.system.logger.get_recent_logs(20)
            
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            for log in recent_logs:
                self.log_text.insert(tk.END, log + "\n")
            
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Ошибка обновления лога: {e} - ui_manager.py:840")
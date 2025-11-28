# drone_physics.py - Моделирование физики дрона
import math
import time
import random
import numpy as np
from datetime import datetime

class DronePhysics:
    def __init__(self, system_manager):
        self.system = system_manager
        
        # Данные для симуляции дрона
        self.drone_position = [0, 0, 0]  # Начинаем с земли
        self.drone_velocity = [0, 0, 0]
        self.drone_orientation = [0, 0, 0]  # pitch, roll, yaw
        self.thrust_vector = [0, 0, 0]
        self.trajectory = []
        
        # Состояние лопастей
        self.blades = [
            {'rpm': 0, 'health': 100, 'temperature': 25, 'vibration': 0, 
             'status': 'stopped', 'rotation_angle': 0, 'target_rpm': 0},
            {'rpm': 0, 'health': 100, 'temperature': 25, 'vibration': 0, 
             'status': 'stopped', 'rotation_angle': 0, 'target_rpm': 0},
            {'rpm': 0, 'health': 100, 'temperature': 25, 'vibration': 0, 
             'status': 'stopped', 'rotation_angle': 0, 'target_rpm': 0},
            {'rpm': 0, 'health': 100, 'temperature': 25, 'vibration': 0, 
             'status': 'stopped', 'rotation_angle': 0, 'target_rpm': 0}
        ]
        
        # Целевая точка
        self.target_point = [20, 15, 15]
        
        # Статистика полета
        self.flight_time = 0
        self.distance_traveled = 0
        self.battery_level = 100
        self.signal_strength = 100
        
        # Режим полета
        self.flight_mode = 'stopped'
        self.running = True
    
    def run(self):
        """Главный цикл физики"""
        while self.running:
            try:
                self.update_blades_physics()
                self.update_drone_physics()
                time.sleep(0.1)
            except Exception as e:
                self.system.logger.log(f"❌ Ошибка в физике: {e}")
    
    def takeoff(self):
        """Взлет дрона"""
        if self.drone_position[2] <= 1:
            self.system.logger.log("🛫 ДРОН: Запуск взлета")
            self.flight_mode = 'taking_off'
            
            for i, blade in enumerate(self.blades):
                blade['target_rpm'] = 3000
                blade['status'] = 'spinning_up'
                self.system.logger.log(f"🔄 Лопасть {i+1}: запуск до 3000 RPM")
    
    def land(self):
        """Посадка дрона"""
        self.system.logger.log("🛬 ДРОН: Начало посадки")
        self.flight_mode = 'landing'
        
        for i, blade in enumerate(self.blades):
            blade['target_rpm'] = 0
            blade['status'] = 'landing'
            self.system.logger.log(f"🔄 Лопасть {i+1}: остановка")
    
    def auto_pilot(self):
        """Автополет к целевой точке"""
        self.system.logger.log("🎯 ДРОН: Автополет к целевой точке")
        self.flight_mode = 'auto_pilot'
        
        # Рассчитываем направление к цели
        dx = self.target_point[0] - self.drone_position[0]
        dy = self.target_point[1] - self.drone_position[1]
        dz = self.target_point[2] - self.drone_position[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        self.system.logger.log(f"🎯 Цель: X={self.target_point[0]}, Y={self.target_point[1]}, Z={self.target_point[2]}")
        self.system.logger.log(f"🎯 Дистанция до цели: {distance:.1f} м")
    
    def emergency_stop(self):
        """Экстренная остановка"""
        self.system.logger.log("🚨 ДРОН: ЭКСТРЕННАЯ ОСТАНОВКА!")
        self.flight_mode = 'emergency'
        
        for i, blade in enumerate(self.blades):
            blade['rpm'] = 0
            blade['target_rpm'] = 0
            blade['status'] = 'emergency_stop'
            self.system.logger.log(f"🛑 Лопасть {i+1}: экстренная остановка")
        
        self.drone_velocity = [0, 0, 0]
        self.thrust_vector = [0, 0, 0]
    
    def update_blades_physics(self):
        """Обновление физики лопастей"""
        for i, blade in enumerate(self.blades):
            target_rpm = blade.get('target_rpm', 0)
            
            # Плавное изменение RPM
            if blade['rpm'] < target_rpm:
                blade['rpm'] = min(blade['rpm'] + 200, target_rpm)
            elif blade['rpm'] > target_rpm:
                blade['rpm'] = max(blade['rpm'] - 300, target_rpm)
            
            # Обновление статуса
            if blade['rpm'] >= 2500 and blade['status'] != 'running':
                blade['status'] = 'running'
                if self.flight_mode == 'taking_off':
                    self.system.logger.log(f"✅ Лопасть {i+1}: достигла рабочей скорости")
            elif blade['rpm'] <= 100 and blade['status'] != 'stopped':
                blade['status'] = 'stopped'
                if self.flight_mode == 'landing':
                    self.system.logger.log(f"✅ Лопасть {i+1}: полностью остановлена")
            
            # Температура и вибрация
            blade['temperature'] = 25 + (blade['rpm'] / 100) * 0.5
            blade['vibration'] = random.randint(0, 5) + (blade['rpm'] / 1000)
            
            # Износ
            if blade['rpm'] > 0 and random.random() < 0.01:
                blade['health'] = max(blade['health'] - 0.1, 0)
            
            # Вращение для 3D визуализации
            if blade['status'] == 'running' and blade['rpm'] > 0:
                rotation_speed = blade['rpm'] / 60
                blade['rotation_angle'] += rotation_speed * 2 * math.pi * 0.1
    
    def update_drone_physics(self):
        """Обновление физики дрона"""
        total_thrust = sum(blade['rpm'] for blade in self.blades) / 1000
        
        # Вертикальная тяга
        if self.drone_position[2] < 1:
            # На земле
            if total_thrust > 2:
                self.thrust_vector[2] = total_thrust - 2
            else:
                self.thrust_vector[2] = 0
        else:
            # В воздухе
            target_height = 10
            height_error = target_height - self.drone_position[2]
            self.thrust_vector[2] = height_error * 0.5
        
        # Автопилот
        if self.flight_mode == 'auto_pilot':
            dx = self.target_point[0] - self.drone_position[0]
            dy = self.target_point[1] - self.drone_position[1]
            dz = self.target_point[2] - self.drone_position[2]
            
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distance > 1:
                self.thrust_vector[0] = dx * 0.1
                self.thrust_vector[1] = dy * 0.1
                self.thrust_vector[2] += dz * 0.05
            
            # Логирование достижения цели
            if distance < 2 and self.flight_mode == 'auto_pilot':
                self.system.logger.log("🎯 ДРОН: Целевая точка достигнута!")
                self.flight_mode = 'hovering'
        
        dt = 0.1
        
        # Интегрирование скорости
        self.drone_velocity[0] += self.thrust_vector[0] * dt
        self.drone_velocity[1] += self.thrust_vector[1] * dt
        self.drone_velocity[2] += (self.thrust_vector[2] - 1) * dt  # -1 для гравитации
        
        # Сопротивление воздуха
        self.drone_velocity[0] *= 0.95
        self.drone_velocity[1] *= 0.95
        self.drone_velocity[2] *= 0.98
        
        # Интегрирование позиции
        self.drone_position[0] += self.drone_velocity[0] * dt
        self.drone_position[1] += self.drone_velocity[1] * dt
        self.drone_position[2] += self.drone_velocity[2] * dt
        
        # Ограничение по земле
        if self.drone_position[2] < 0:
            self.drone_position[2] = 0
            self.drone_velocity[2] = 0
            if self.flight_mode == 'landing':
                self.system.logger.log("✅ ДРОН: Успешная посадка!")
                self.flight_mode = 'stopped'
        
        # Взлет завершен
        if self.drone_position[2] > 8 and self.flight_mode == 'taking_off':
            self.system.logger.log("✅ ДРОН: Взлет завершен, переход в режим висения")
            self.flight_mode = 'hovering'
        
        # Траектория
        self.trajectory.append(tuple(self.drone_position))
        if len(self.trajectory) > 100:
            self.trajectory.pop(0)
        
        # Статистика полета
        if self.drone_position[2] > 1:
            self.flight_time += dt
            self.distance_traveled += math.sqrt(
                self.drone_velocity[0]**2 + 
                self.drone_velocity[1]**2 + 
                self.drone_velocity[2]**2
            ) * dt
            
            self.battery_level = max(0, self.battery_level - dt * 0.1)
            
            # Сигнал ухудшается с расстоянием
            distance_from_home = math.sqrt(
                self.drone_position[0]**2 + 
                self.drone_position[1]**2
            )
            self.signal_strength = max(10, 100 - distance_from_home * 2)
    
    def get_flight_status(self):
        """Получение текстового статуса полета"""
        status_translation = {
            'stopped': '🛑 НА ЗЕМЛЕ',
            'taking_off': '🛫 ВЗЛЕТАЕТ',
            'hovering': '✈️ ВИСЕНИЕ',
            'auto_pilot': '🎯 АВТОПИЛОТ',
            'landing': '🛬 САДИТСЯ',
            'emergency': '🚨 АВАРИЯ'
        }
        return status_translation.get(self.flight_mode, self.flight_mode)
    
    def get_drone_info(self):
        """Получение информации о дроне в текстовом формате"""
        return f"""ПОЗИЦИЯ ДРОНА:
X: {self.drone_position[0]:.2f} м
Y: {self.drone_position[1]:.2f} м
Z: {self.drone_position[2]:.2f} м

СКОРОСТЬ:
Vx: {self.drone_velocity[0]:.2f} м/с
Vy: {self.drone_velocity[1]:.2f} м/с
Vz: {self.drone_velocity[2]:.2f} м/с

ОРИЕНТАЦИЯ:
Крен: {self.drone_orientation[0]:.1f}°
Тангаж: {self.drone_orientation[1]:.1f}°
Рыскание: {self.drone_orientation[2]:.1f}°

СТАТИСТИКА:
Время полета: {self.flight_time:.1f} с
Дистанция: {self.distance_traveled:.1f} м
Батарея: {self.battery_level:.1f}%
Сигнал: {self.signal_strength:.1f}%"""
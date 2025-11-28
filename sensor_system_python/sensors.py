# sensors.py - Система сенсоров дрона (GPS, барометр)
import math
import random
import time
from datetime import datetime

class SensorSystem:
    def __init__(self, system_manager):
        self.system = system_manager
        
        # GPS данные
        self.gps_data = {
            'latitude': 55.7558,  # Москва
            'longitude': 37.6173,
            'altitude': 0,
            'speed': 0,
            'course': 0,
            'satellites': 8,
            'hdop': 1.2,  # Horizontal Dilution of Precision
            'fix_quality': 3,  # 3D fix
            'timestamp': datetime.now()
        }
        
        # Барометр данные
        self.barometer_data = {
            'pressure': 1013.25,  # hPa
            'temperature': 15,    # °C
            'altitude': 0,
            'sea_level_pressure': 1013.25,
            'vertical_speed': 0,
            'timestamp': datetime.now()
        }
        
        # IMU данные (Inertial Measurement Unit)
        self.imu_data = {
            'acceleration_x': 0,
            'acceleration_y': 0,
            'acceleration_z': 0,
            'gyro_x': 0,
            'gyro_y': 0,
            'gyro_z': 0,
            'magnetometer_x': 0,
            'magnetometer_y': 0,
            'magnetometer_z': 0
        }
        
        self.running = True
    
    def run(self):
        """Главный цикл сенсоров"""
        while self.running:
            try:
                self.update_sensors()
                self.add_sensor_noise()
                time.sleep(0.1)
            except Exception as e:
                self.system.logger.log(f"❌ Ошибка в сенсорах: {e}")
    
    def update_sensors(self):
        """Основной метод обновления всех сенсоров"""
        if hasattr(self.system, 'physics') and self.system.physics is not None:
            self.update_from_physics()
        else:
            # Если физика недоступна, обновляем базовые значения
            self.update_basic_sensors()
    
    def update_basic_sensors(self):
        """Обновление сенсоров без данных физики"""
        # Обновление временных меток
        self.gps_data['timestamp'] = datetime.now()
        self.barometer_data['timestamp'] = datetime.now()
        
        # Базовые обновления IMU
        self.imu_data['acceleration_x'] = random.gauss(0, 0.1)
        self.imu_data['acceleration_y'] = random.gauss(0, 0.1)
        self.imu_data['acceleration_z'] = 9.81 + random.gauss(0, 0.05)
        self.imu_data['gyro_x'] = random.gauss(0, 0.5)
        self.imu_data['gyro_y'] = random.gauss(0, 0.5)
        self.imu_data['gyro_z'] = random.gauss(0, 0.5)
    
    def update_from_physics(self):
        """Обновление данных сенсоров на основе физики дрона"""
        physics = self.system.physics
        
        # Обновление GPS на основе позиции дрона
        self.gps_data['latitude'] = 55.7558 + (physics.drone_position[0] / 111320)  # 1 градус ≈ 111 км
        self.gps_data['longitude'] = 37.6173 + (physics.drone_position[1] / (111320 * math.cos(math.radians(55.7558))))
        self.gps_data['altitude'] = physics.drone_position[2]
        
        # Расчет скорости и курса
        speed_2d = math.sqrt(physics.drone_velocity[0]**2 + physics.drone_velocity[1]**2)
        self.gps_data['speed'] = speed_2d  # м/с
        
        if speed_2d > 0.1:
            course = math.degrees(math.atan2(physics.drone_velocity[1], physics.drone_velocity[0]))
            self.gps_data['course'] = (90 - course) % 360  # Преобразование в географический курс
        else:
            self.gps_data['course'] = 0
        
        self.gps_data['timestamp'] = datetime.now()
        
        # Обновление барометра
        self.update_barometer(physics.drone_position[2], physics.drone_velocity[2])
        
        # Обновление IMU
        self.update_imu(physics.drone_orientation, physics.drone_velocity)
    
    def update_barometer(self, altitude, vertical_speed):
        """Обновление данных барометра"""
        # Барометрическая формула
        self.barometer_data['altitude'] = altitude
        self.barometer_data['pressure'] = 1013.25 * math.exp(-altitude / 8430)  # Упрощенная формула
        self.barometer_data['temperature'] = 15 - (altitude * 0.0065)  # Температурный градиент
        self.barometer_data['vertical_speed'] = vertical_speed
        self.barometer_data['timestamp'] = datetime.now()
    
    def update_imu(self, orientation, velocity):
        """Обновление данных IMU"""
        # Имитация данных акселерометра
        self.imu_data['acceleration_x'] = random.gauss(0, 0.1)
        self.imu_data['acceleration_y'] = random.gauss(0, 0.1)
        self.imu_data['acceleration_z'] = 9.81 + random.gauss(0, 0.05)  # Гравитация + шум
        
        # Имитация гироскопа
        self.imu_data['gyro_x'] = random.gauss(0, 0.5)
        self.imu_data['gyro_y'] = random.gauss(0, 0.5)
        self.imu_data['gyro_z'] = random.gauss(0, 0.5)
        
        # Имитация магнитометра (ориентация по компасу)
        if orientation and len(orientation) > 2:
            self.imu_data['magnetometer_x'] = math.cos(math.radians(orientation[2]))
            self.imu_data['magnetometer_y'] = math.sin(math.radians(orientation[2]))
            self.imu_data['magnetometer_z'] = 0
    
    def add_sensor_noise(self):
        """Добавление шума к данным сенсоров для реалистичности"""
        # Шум GPS
        self.gps_data['latitude'] += random.gauss(0, 0.000001)  # ~10 см шума
        self.gps_data['longitude'] += random.gauss(0, 0.000001)
        self.gps_data['altitude'] += random.gauss(0, 0.1)
        self.gps_data['speed'] += random.gauss(0, 0.05)
        self.gps_data['hdop'] = max(0.8, random.gauss(1.2, 0.2))
        
        # Шум барометра
        self.barometer_data['pressure'] += random.gauss(0, 0.1)
        self.barometer_data['temperature'] += random.gauss(0, 0.1)
        
        # Количество спутников может меняться
        self.gps_data['satellites'] = random.randint(6, 12)
    
    def get_gps_string(self):
        """Получение GPS данных в формате NMEA"""
        lat = self.gps_data['latitude']
        lon = self.gps_data['longitude']
        
        # Конвертация в градусы-минуты
        lat_deg = int(lat)
        lat_min = (lat - lat_deg) * 60
        lon_deg = int(lon)
        lon_min = (lon - lon_deg) * 60
        
        return f"GPS: {lat_deg}°{lat_min:.4f}'N, {lon_deg}°{lon_min:.4f}'E"
    
    def get_barometer_summary(self):
        """Получение сводки барометра"""
        return (f"Давление: {self.barometer_data['pressure']:.1f} hPa | "
                f"Температура: {self.barometer_data['temperature']:.1f}°C | "
                f"Высота: {self.barometer_data['altitude']:.1f} м")
    
    def stop(self):
        """Остановка системы сенсоров"""
        self.running = False
    
    def get_sensor_summary(self):
        """Получение сводки по всем сенсорам"""
        return {
            'gps': self.gps_data.copy(),
            'barometer': self.barometer_data.copy(),
            'imu': self.imu_data.copy()
        }
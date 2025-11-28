# web_interface.py - Веб-интерфейс для мониторинга данных
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
from config import Config
import logging
import os

class WebInterface:
    def __init__(self, config: Config):
        self.config = config
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'sensor_system_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.setup_routes()
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(level=logging.INFO)
        
    def setup_routes(self):
        """Настройка маршрутов Flask"""
        
        @self.app.route('/')
        def index():
            """Главная страница"""
            # Создаем папку templates если ее нет
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            os.makedirs(templates_dir, exist_ok=True)
            
            # Создаем index.html если его нет
            index_file = os.path.join(templates_dir, 'index.html')
            if not os.path.exists(index_file):
                self.create_default_template(index_file)
                
            return render_template('index.html')
        
        @self.app.route('/api/devices')
        def get_devices():
            """API для получения списка устройств"""
            try:
                devices = self.get_devices_from_db()
                return jsonify({
                    'status': 'success',
                    'devices': devices,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/data/recent')
        def get_recent_data():
            """API для получения последних данных"""
            try:
                device_id = request.args.get('device_id')
                limit = int(request.args.get('limit', 50))
                
                data = self.get_recent_sensor_data(device_id, limit)
                
                return jsonify({
                    'status': 'success',
                    'data': data,
                    'count': len(data)
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/statistics')
        def get_statistics():
            """API для получения статистики"""
            try:
                stats = self.get_system_statistics()
                return jsonify({
                    'status': 'success',
                    'statistics': stats
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/data/export')
        def export_data():
            """API для экспорта данных"""
            try:
                format_type = request.args.get('format', 'json')
                data = self.get_recent_sensor_data(limit=1000)
                
                if format_type == 'csv':
                    return self.export_to_csv(data)
                else:
                    return jsonify({
                        'status': 'success',
                        'data': data,
                        'exported_at': datetime.now().isoformat()
                    })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.socketio.on('connect')
        def handle_connect():
            """Обработчик подключения WebSocket"""
            logging.info('WebSocket client connected - web_interface.py:118')
            self.socketio.emit('connected', {'message': 'Connected to sensor data stream'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Обработчик отключения WebSocket"""
            logging.info('WebSocket client disconnected - web_interface.py:124')
    
    def create_default_template(self, filepath):
        """Создание шаблона по умолчанию"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Data Monitoring System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #666; margin-bottom: 10px; font-size: 14px; }
        .stat-card .value { font-size: 24px; font-weight: bold; color: #333; }
        .content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        @media (max-width: 768px) { .content-grid { grid-template-columns: 1fr; } }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h2 { margin-bottom: 15px; color: #333; }
        .device-item { background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px; border-left: 4px solid #007bff; }
        .device-item.online { border-left-color: #28a745; }
        .device-item.offline { border-left-color: #dc3545; }
        .btn { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .chart-container { height: 300px; margin-top: 15px; }
        .data-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .data-table th, .data-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .data-table th { background: #f8f9fa; }
        .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
        .status-online { background: #28a745; }
        .status-offline { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sensor Data Monitoring System</h1>
            <p>Real-time monitoring of sensor data from connected devices</p>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <h3>Connected Devices</h3>
                <div class="value" id="deviceCount">0</div>
            </div>
            <div class="stat-card">
                <h3>Total Records</h3>
                <div class="value" id="totalRecords">0</div>
            </div>
            <div class="stat-card">
                <h3>System Status</h3>
                <div class="value" id="systemStatus">Online</div>
            </div>
        </div>

        <div class="content-grid">
            <div class="card">
                <h2>Connected Devices</h2>
                <button class="btn btn-primary" onclick="refreshDevices()">Refresh</button>
                <div id="deviceList"></div>
            </div>

            <div class="card">
                <h2>Real-time Data</h2>
                <div class="chart-container">
                    <canvas id="temperatureChart"></canvas>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Recent Sensor Data</h2>
            <select id="deviceFilter" onchange="loadRecentData()">
                <option value="">All Devices</option>
            </select>
            <button class="btn btn-primary" onclick="loadRecentData()">Refresh</button>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Temperature</th>
                        <th>Humidity</th>
                        <th>Light</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody"></tbody>
            </table>
        </div>
    </div>

    <script>
        let socket;
        let temperatureChart;

        document.addEventListener('DOMContentLoaded', function() {
            initializeSocket();
            initializeChart();
            loadDevices();
            loadRecentData();
            loadStatistics();
        });

        function initializeSocket() {
            socket = io();
            socket.on('connect', function() {
                console.log('Connected');
                updateConnectionStatus(true);
            });
            socket.on('disconnect', function() {
                updateConnectionStatus(false);
            });
            socket.on('data_update', function(data) {
                updateRealTimeData(data.data);
            });
        }

        function initializeChart() {
            const ctx = document.getElementById('temperatureChart').getContext('2d');
            temperatureChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Temperature',
                        data: [],
                        borderColor: 'red',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        function updateConnectionStatus(connected) {
            document.getElementById('systemStatus').textContent = connected ? 'Online' : 'Offline';
            document.getElementById('systemStatus').style.color = connected ? 'green' : 'red';
        }

        async function loadDevices() {
            try {
                const response = await fetch('/api/devices');
                const data = await response.json();
                if (data.status === 'success') {
                    displayDevices(data.devices);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function displayDevices(devices) {
            const deviceList = document.getElementById('deviceList');
            deviceList.innerHTML = '';
            document.getElementById('deviceCount').textContent = devices.length;
            
            devices.forEach(device => {
                const div = document.createElement('div');
                div.className = `device-item ${isDeviceOnline(device.last_seen) ? 'online' : 'offline'}`;
                div.innerHTML = `
                    <div><span class="status-indicator ${isDeviceOnline(device.last_seen) ? 'status-online' : 'status-offline'}"></span>
                    ${device.device_id}</div>
                    <div>Location: ${device.location}</div>
                    <div>Records: ${device.total_records}</div>
                `;
                deviceList.appendChild(div);
            });
        }

        async function loadRecentData() {
            try {
                const deviceFilter = document.getElementById('deviceFilter').value;
                const url = deviceFilter ? `/api/data/recent?device_id=${deviceFilter}&limit=10` : '/api/data/recent?limit=10';
                const response = await fetch(url);
                const data = await response.json();
                if (data.status === 'success') {
                    displayRecentData(data.data);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function displayRecentData(data) {
            const tbody = document.getElementById('dataTableBody');
            tbody.innerHTML = '';
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.device_id}</td>
                    <td>${row.temperature || 'N/A'}°C</td>
                    <td>${row.humidity || 'N/A'}%</td>
                    <td>${row.light_level || 'N/A'}</td>
                    <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const data = await response.json();
                if (data.status === 'success') {
                    document.getElementById('totalRecords').textContent = data.statistics.total_records || 0;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function updateRealTimeData(data) {
            // Simple chart update with first temperature value
            if (data.length > 0 && data[0].temperature) {
                const chart = temperatureChart.data;
                chart.labels.push(new Date().toLocaleTimeString());
                chart.datasets[0].data.push(data[0].temperature);
                if (chart.labels.length > 20) {
                    chart.labels.shift();
                    chart.datasets[0].data.shift();
                }
                temperatureChart.update();
            }
        }

        function refreshDevices() {
            loadDevices();
            loadStatistics();
        }

        function isDeviceOnline(lastSeen) {
            if (!lastSeen) return false;
            return (new Date() - new Date(lastSeen)) < 300000; // 5 minutes
        }
    </script>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Created default template at {filepath} - web_interface.py:374")
    
    def get_db_connection(self):
        """Создание подключения к базе данных"""
        conn = sqlite3.connect(self.config.DATABASE.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_devices_from_db(self):
        """Получение списка устройств из базы данных"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    device_id,
                    device_type,
                    location,
                    first_seen,
                    last_seen,
                    total_records
                FROM devices 
                ORDER BY last_seen DESC
            ''')
            
            devices = []
            for row in cursor.fetchall():
                devices.append({
                    'device_id': row['device_id'],
                    'device_type': row['device_type'],
                    'location': row['location'],
                    'first_seen': row['first_seen'],
                    'last_seen': row['last_seen'],
                    'total_records': row['total_records']
                })
            
            conn.close()
            return devices
            
        except Exception as e:
            logging.error(f"Error getting devices: {e}")
            return []
    
    def get_recent_sensor_data(self, device_id=None, limit=50):
        """Получение последних данных сенсоров"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            if device_id:
                cursor.execute('''
                    SELECT * FROM sensor_data 
                    WHERE device_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (device_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM sensor_data 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    'id': row['id'],
                    'device_id': row['device_id'],
                    'temperature': row['temperature'],
                    'humidity': row['humidity'],
                    'light_level': row['light_level'],
                    'voltage': row['voltage'],
                    'timestamp': row['timestamp'],
                    'received_at': row['received_at']
                })
            
            conn.close()
            return data
            
        except Exception as e:
            logging.error(f"Error getting sensor data: {e}")
            return []
    
    def get_system_statistics(self):
        """Получение системной статистики"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as total_records FROM sensor_data')
            total_records = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT device_id) as device_count FROM sensor_data')
            device_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_records': total_records,
                'device_count': device_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {}
    
    def export_to_csv(self, data):
        """Экспорт данных в CSV формат"""
        import csv
        from io import StringIO
        
        if not data:
            return "No data to export", 400
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['ID', 'Device ID', 'Temperature', 'Humidity', 'Light Level', 'Voltage', 'Timestamp'])
        
        for row in data:
            writer.writerow([
                row['id'],
                row['device_id'],
                row['temperature'],
                row['humidity'],
                row['light_level'],
                row['voltage'],
                row['timestamp']
            ])
        
        from flask import Response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=sensor_data_export.csv'}
        )
        
        return response
    
    def start_realtime_updates(self):
        """Запуск потока для обновления данных в реальном времени"""
        def update_loop():
            while True:
                try:
                    recent_data = self.get_recent_sensor_data(limit=10)
                    self.socketio.emit('data_update', {
                        'data': recent_data,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    logging.error(f"Error in update loop: {e}")
                time.sleep(5)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def run(self, host='localhost', port=5000, debug=False):
        """Запуск веб-сервера"""
        self.start_realtime_updates()
        logging.info(f"Starting web interface on http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

def main():
    """Основная функция запуска веб-интерфейса"""
    config = Config()
    config.initialize_directories()
    
    web_interface = WebInterface(config)
    web_interface.run(host='localhost', port=5000, debug=True)

if __name__ == "__main__":
    main()
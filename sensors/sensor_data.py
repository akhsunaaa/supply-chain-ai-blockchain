# sensor_data.py
from datetime import datetime
import json

class SensorBase:
    def __init__(self, sensor_id, location):
        self.sensor_id = sensor_id
        self.location = location
        self.last_reading_time = None

    def _read_temperature(self):
        # To be implemented with actual sensor hardware
        pass

    def _read_humidity(self):
        # To be implemented with actual sensor hardware
        pass

    def get_timestamp(self):
        return datetime.now().isoformat()

    def to_json(self):
        return json.dumps(self.__dict__)

class WarehouseSensor(SensorBase):
    def __init__(self, sensor_id, warehouse_location):
        super().__init__(sensor_id, warehouse_location)
        self.temperature = None
        self.humidity = None

    def read_data(self):
        """Read temperature and humidity data from warehouse sensors"""
        self.temperature = self._read_temperature()
        self.humidity = self._read_humidity()
        self.last_reading_time = self.get_timestamp()
        
        return {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'timestamp': self.last_reading_time
        }

class CrateSensor(SensorBase):
    def __init__(self, sensor_id, crate_id):
        super().__init__(sensor_id, f"crate_{crate_id}")
        self.crate_id = crate_id
        self.temperature = None
        self.humidity = None
        self.ethylene_level = None
        self.gps_location = None

    def _read_ethylene(self):
        # To be implemented with actual sensor hardware
        pass

    def _read_gps(self):
        # To be implemented with actual GPS module
        pass

    def read_data(self):
        """Read temperature, humidity, ethylene, and GPS data from crate sensors"""
        self.temperature = self._read_temperature()
        self.humidity = self._read_humidity()
        self.ethylene_level = self._read_ethylene()
        self.gps_location = self._read_gps()
        self.last_reading_time = self.get_timestamp()

        return {
            'sensor_id': self.sensor_id,
            'crate_id': self.crate_id,
            'location': self.location,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'ethylene_level': self.ethylene_level,
            'gps_location': self.gps_location,
            'timestamp': self.last_reading_time
        }

class SensorNetwork:
    def __init__(self):
        self.warehouse_sensors = {}
        self.crate_sensors = {}

    def add_warehouse_sensor(self, sensor_id, warehouse_location):
        """Add a new warehouse sensor to the network"""
        sensor = WarehouseSensor(sensor_id, warehouse_location)
        self.warehouse_sensors[sensor_id] = sensor
        return sensor

    def add_crate_sensor(self, sensor_id, crate_id):
        """Add a new crate sensor to the network"""
        sensor = CrateSensor(sensor_id, crate_id)
        self.crate_sensors[sensor_id] = sensor
        return sensor

    def collect_all_data(self):
        """Collect data from all sensors in the network"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'warehouse_readings': [],
            'crate_readings': []
        }

        # Collect warehouse sensor data
        for sensor in self.warehouse_sensors.values():
            data['warehouse_readings'].append(sensor.read_data())

        # Collect crate sensor data
        for sensor in self.crate_sensors.values():
            data['crate_readings'].append(sensor.read_data())

        return data

    def get_sensor_status(self):
        """Get the status of all sensors in the network"""
        return {
            'total_warehouse_sensors': len(self.warehouse_sensors),
            'total_crate_sensors': len(self.crate_sensors),
            'warehouse_sensors': list(self.warehouse_sensors.keys()),
            'crate_sensors': list(self.crate_sensors.keys())
        }

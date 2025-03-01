# sensor_data.py
from datetime import datetime
import json
import random  # For demo data generation
from typing import Dict, List, Optional

class SensorBase:
    """Base class for all sensors"""
    def __init__(self, sensor_id: str, location: str):
        self.sensor_id = sensor_id
        self.location = location
        self.last_reading_time = None
        self.is_active = True
        self.error_count = 0
        self.calibration_date = datetime.now()

    def _read_temperature(self) -> float:
        """Simulate temperature reading"""
        # In production, this would interface with actual hardware
        base_temp = 4.0  # Base temperature in Celsius
        variation = random.uniform(-1.0, 1.0)
        return round(base_temp + variation, 2)

    def _read_humidity(self) -> float:
        """Simulate humidity reading"""
        # In production, this would interface with actual hardware
        base_humidity = 65.0  # Base humidity percentage
        variation = random.uniform(-5.0, 5.0)
        return round(base_humidity + variation, 2)

    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    def to_json(self) -> str:
        """Convert sensor data to JSON"""
        return json.dumps(self.__dict__)

    def check_status(self) -> Dict:
        """Check sensor status"""
        return {
            'sensor_id': self.sensor_id,
            'is_active': self.is_active,
            'error_count': self.error_count,
            'last_reading': self.last_reading_time,
            'calibration_date': self.calibration_date.isoformat()
        }

class WarehouseSensor(SensorBase):
    """Sensor class for warehouse monitoring"""
    def __init__(self, sensor_id: str, warehouse_location: str):
        super().__init__(sensor_id, warehouse_location)
        self.temperature = None
        self.humidity = None
        self.sensor_type = 'warehouse'

    def read_data(self) -> Dict:
        """Read temperature and humidity data from warehouse sensors"""
        try:
            self.temperature = self._read_temperature()
            self.humidity = self._read_humidity()
            self.last_reading_time = self.get_timestamp()
            
            return {
                'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type,
                'location': self.location,
                'temperature': self.temperature,
                'humidity': self.humidity,
                'timestamp': self.last_reading_time,
                'status': 'operational'
            }
        except Exception as e:
            self.error_count += 1
            return {
                'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type,
                'error': str(e),
                'timestamp': self.get_timestamp(),
                'status': 'error'
            }

class CrateSensor(SensorBase):
    """Sensor class for individual crate monitoring"""
    def __init__(self, sensor_id: str, crate_id: str):
        super().__init__(sensor_id, f"crate_{crate_id}")
        self.crate_id = crate_id
        self.temperature = None
        self.humidity = None
        self.ethylene_level = None
        self.gps_location = None
        self.sensor_type = 'crate'

    def _read_ethylene(self) -> float:
        """Simulate ethylene level reading"""
        # In production, this would interface with actual hardware
        base_ethylene = 0.5  # Base ethylene level in ppm
        variation = random.uniform(-0.2, 0.2)
        return round(base_ethylene + variation, 3)

    def _read_gps(self) -> Dict:
        """Simulate GPS reading"""
        # In production, this would interface with actual GPS module
        # Using New York coordinates as example
        return {
            'latitude': round(40.7128 + random.uniform(-0.01, 0.01), 6),
            'longitude': round(-74.0060 + random.uniform(-0.01, 0.01), 6)
        }

    def read_data(self) -> Dict:
        """Read all sensor data from crate"""
        try:
            self.temperature = self._read_temperature()
            self.humidity = self._read_humidity()
            self.ethylene_level = self._read_ethylene()
            self.gps_location = self._read_gps()
            self.last_reading_time = self.get_timestamp()

            return {
                'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type,
                'crate_id': self.crate_id,
                'location': self.location,
                'temperature': self.temperature,
                'humidity': self.humidity,
                'ethylene_level': self.ethylene_level,
                'gps_location': self.gps_location,
                'timestamp': self.last_reading_time,
                'status': 'operational'
            }
        except Exception as e:
            self.error_count += 1
            return {
                'sensor_id': self.sensor_id,
                'sensor_type': self.sensor_type,
                'crate_id': self.crate_id,
                'error': str(e),
                'timestamp': self.get_timestamp(),
                'status': 'error'
            }

class SensorNetwork:
    """Manage network of sensors"""
    def __init__(self):
        self.warehouse_sensors: Dict[str, WarehouseSensor] = {}
        self.crate_sensors: Dict[str, CrateSensor] = {}
        self.reading_interval = 300  # 5 minutes in seconds
        self.last_network_check = None

    def add_warehouse_sensor(self, sensor_id: str, warehouse_location: str) -> WarehouseSensor:
        """Add a new warehouse sensor to the network"""
        if sensor_id in self.warehouse_sensors:
            raise ValueError(f"Sensor ID {sensor_id} already exists")
        
        sensor = WarehouseSensor(sensor_id, warehouse_location)
        self.warehouse_sensors[sensor_id] = sensor
        return sensor

    def add_crate_sensor(self, sensor_id: str, crate_id: str) -> CrateSensor:
        """Add a new crate sensor to the network"""
        if sensor_id in self.crate_sensors:
            raise ValueError(f"Sensor ID {sensor_id} already exists")
        
        sensor = CrateSensor(sensor_id, crate_id)
        self.crate_sensors[sensor_id] = sensor
        return sensor

    def remove_sensor(self, sensor_id: str) -> bool:
        """Remove a sensor from the network"""
        if sensor_id in self.warehouse_sensors:
            del self.warehouse_sensors[sensor_id]
            return True
        if sensor_id in self.crate_sensors:
            del self.crate_sensors[sensor_id]
            return True
        return False

    def collect_all_data(self) -> Dict:
        """Collect data from all sensors in the network"""
        self.last_network_check = datetime.now()
        
        data = {
            'timestamp': self.last_network_check.isoformat(),
            'warehouse_readings': [],
            'crate_readings': [],
            'network_status': {
                'total_sensors': len(self.warehouse_sensors) + len(self.crate_sensors),
                'active_sensors': 0,
                'error_sensors': 0
            }
        }

        # Collect warehouse sensor data
        for sensor in self.warehouse_sensors.values():
            reading = sensor.read_data()
            data['warehouse_readings'].append(reading)
            if reading['status'] == 'operational':
                data['network_status']['active_sensors'] += 1
            else:
                data['network_status']['error_sensors'] += 1

        # Collect crate sensor data
        for sensor in self.crate_sensors.values():
            reading = sensor.read_data()
            data['crate_readings'].append(reading)
            if reading['status'] == 'operational':
                data['network_status']['active_sensors'] += 1
            else:
                data['network_status']['error_sensors'] += 1

        return data

    def get_sensor_status(self) -> Dict:
        """Get the status of all sensors in the network"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_warehouse_sensors': len(self.warehouse_sensors),
            'total_crate_sensors': len(self.crate_sensors),
            'warehouse_sensors': [
                sensor.check_status() for sensor in self.warehouse_sensors.values()
            ],
            'crate_sensors': [
                sensor.check_status() for sensor in self.crate_sensors.values()
            ],
            'last_network_check': self.last_network_check.isoformat() if self.last_network_check else None
        }

    def get_sensor_by_id(self, sensor_id: str) -> Optional[SensorBase]:
        """Get a sensor by its ID"""
        return self.warehouse_sensors.get(sensor_id) or self.crate_sensors.get(sensor_id)

    def get_sensors_by_location(self, location: str) -> List[SensorBase]:
        """Get all sensors in a specific location"""
        sensors = []
        for sensor in self.warehouse_sensors.values():
            if sensor.location == location:
                sensors.append(sensor)
        for sensor in self.crate_sensors.values():
            if sensor.location.startswith(location):
                sensors.append(sensor)
        return sensors

    def calibrate_sensor(self, sensor_id: str) -> bool:
        """Calibrate a specific sensor"""
        sensor = self.get_sensor_by_id(sensor_id)
        if sensor:
            sensor.calibration_date = datetime.now()
            sensor.error_count = 0
            return True
        return False

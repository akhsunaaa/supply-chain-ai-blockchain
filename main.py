# main.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sensors.sensor_data import SensorNetwork
from data_processing.ripeness_analysis import RipenessAnalyzer
from logistics.route_optimizer import RouteOptimizer, Order, Vehicle

class SupplyChainManager:
    def __init__(self):
        """Initialize the supply chain management system"""
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SupplyChainManager')

        # Initialize components
        self.sensor_network = SensorNetwork()
        self.ripeness_analyzer = RipenessAnalyzer()
        self.route_optimizer = RouteOptimizer()
        
        # Store orders and shipments in memory
        self.orders = {}
        self.shipments = {}

        self.logger.info("Supply Chain Management System initialized")

    def register_warehouse(self, warehouse_id: str, location: str) -> None:
        """Register a new warehouse in the system"""
        try:
            self.route_optimizer.add_warehouse(warehouse_id, location)
            self.logger.info(f"Registered warehouse: {warehouse_id} at {location}")
        except Exception as e:
            self.logger.error(f"Failed to register warehouse: {str(e)}")
            raise

    def register_vehicle(self, vehicle_data: Dict) -> None:
        """Register a new delivery vehicle"""
        try:
            vehicle = Vehicle(
                vehicle_id=vehicle_data['vehicle_id'],
                capacity=vehicle_data['capacity'],
                avg_speed=vehicle_data['avg_speed'],
                refrigeration=vehicle_data.get('refrigeration', True)
            )
            self.route_optimizer.add_vehicle(vehicle)
            self.logger.info(f"Registered vehicle: {vehicle.vehicle_id}")
        except Exception as e:
            self.logger.error(f"Failed to register vehicle: {str(e)}")
            raise

    def add_warehouse_sensor(self, sensor_id: str, warehouse_location: str) -> None:
        """Add a new sensor to a warehouse"""
        try:
            sensor = self.sensor_network.add_warehouse_sensor(sensor_id, warehouse_location)
            self.logger.info(f"Added warehouse sensor: {sensor_id}")
        except Exception as e:
            self.logger.error(f"Failed to add warehouse sensor: {str(e)}")
            raise

    def add_crate_sensor(self, sensor_id: str, crate_id: str) -> None:
        """Add a new sensor to a crate"""
        try:
            sensor = self.sensor_network.add_crate_sensor(sensor_id, crate_id)
            self.logger.info(f"Added crate sensor: {sensor_id}")
        except Exception as e:
            self.logger.error(f"Failed to add crate sensor: {str(e)}")
            raise

    def process_sensor_data(self) -> Dict:
        """Process data from all sensors and analyze fruit conditions"""
        try:
            # Collect sensor data
            sensor_data = self.sensor_network.collect_all_data()
            self.logger.info("Collected sensor data from network")
            return sensor_data
        except Exception as e:
            self.logger.error(f"Failed to process sensor data: {str(e)}")
            raise

    def analyze_fruit_conditions(self, sensor_data: Dict, fruit_type: str) -> Dict:
        """Analyze fruit conditions based on sensor data"""
        try:
            analysis = self.ripeness_analyzer.analyze_ripeness(sensor_data, fruit_type)
            self.logger.info(f"Completed ripeness analysis for {fruit_type}")
            return analysis
        except Exception as e:
            self.logger.error(f"Failed to analyze fruit conditions: {str(e)}")
            raise

    def create_order(self, order_data: Dict) -> str:
        """Create a new customer order"""
        try:
            order = Order(
                order_id=order_data['order_id'],
                destination=order_data['destination'],
                fruit_type=order_data['fruit_type'],
                quantity=order_data['quantity'],
                required_delivery_time=datetime.fromisoformat(order_data['delivery_time'])
            )
            
            self.route_optimizer.add_order(order)
            self.orders[order.order_id] = order_data
            
            self.logger.info(f"Created new order: {order.order_id}")
            return order.order_id
        except Exception as e:
            self.logger.error(f"Failed to create order: {str(e)}")
            raise

    def optimize_delivery_routes(self, ripeness_data: Dict) -> Dict:
        """Optimize delivery routes based on current conditions"""
        try:
            routes = self.route_optimizer.optimize_routes(ripeness_data)
            self.logger.info("Completed route optimization")
            return routes
        except Exception as e:
            self.logger.error(f"Failed to optimize routes: {str(e)}")
            raise

    def get_route_details(self, vehicle_id: str) -> Dict:
        """Get detailed information about a vehicle's route"""
        try:
            return self.route_optimizer.get_route_details(vehicle_id)
        except Exception as e:
            self.logger.error(f"Failed to get route details: {str(e)}")
            raise

    def update_shipment_status(self, shipment_id: str, status: str, location: Dict = None) -> None:
        """Update the status of a shipment"""
        try:
            if shipment_id not in self.shipments:
                self.shipments[shipment_id] = []
            
            self.shipments[shipment_id].append({
                'status': status,
                'location': location,
                'timestamp': datetime.now().isoformat()
            })
            self.logger.info(f"Updated shipment {shipment_id} status to {status}")
        except Exception as e:
            self.logger.error(f"Failed to update shipment status: {str(e)}")
            raise

    def get_shipment_history(self, shipment_id: str) -> List[Dict]:
        """Get the history of a shipment"""
        try:
            return self.shipments.get(shipment_id, [])
        except Exception as e:
            self.logger.error(f"Failed to get shipment history: {str(e)}")
            raise

    def get_inventory_status(self) -> Dict:
        """Get current inventory status across all warehouses"""
        try:
            sensor_data = self.process_sensor_data()
            inventory_status = {
                'timestamp': datetime.now().isoformat(),
                'warehouses': {},
                'total_stock': 0
            }

            for reading in sensor_data['warehouse_readings']:
                warehouse_id = reading['location']
                if warehouse_id not in inventory_status['warehouses']:
                    inventory_status['warehouses'][warehouse_id] = {
                        'temperature': reading['temperature'],
                        'humidity': reading['humidity'],
                        'stock': []
                    }

            for reading in sensor_data['crate_readings']:
                warehouse_id = reading['location'].split('_')[0]
                if warehouse_id in inventory_status['warehouses']:
                    crate_info = {
                        'crate_id': reading['crate_id'],
                        'fruit_type': reading.get('fruit_type', 'unknown'),
                        'quantity': reading.get('quantity', 0),
                        'condition': self.analyze_fruit_conditions(reading, reading.get('fruit_type', 'unknown'))
                    }
                    inventory_status['warehouses'][warehouse_id]['stock'].append(crate_info)
                    inventory_status['total_stock'] += crate_info['quantity']

            return inventory_status
        except Exception as e:
            self.logger.error(f"Failed to get inventory status: {str(e)}")
            raise

def main():
    """Main function to demonstrate system functionality"""
    try:
        # Initialize the system
        system = SupplyChainManager()

        # Register a warehouse (using a real address that can be geocoded)
        system.register_warehouse(
            "WH001",
            "1600 Amphitheatre Parkway, Mountain View, CA 94043"  # Google HQ address as example
        )

        # Register a vehicle
        system.register_vehicle({
            'vehicle_id': 'VH001',
            'capacity': 1000,  # kg
            'avg_speed': 60,   # km/h
            'refrigeration': True
        })

        # Add sensors
        system.add_warehouse_sensor('WHS001', 'WH001')
        system.add_crate_sensor('CRS001', 'CRT001')

        # Process sensor data
        sensor_data = system.process_sensor_data()

        # Analyze fruit conditions
        ripeness_data = system.analyze_fruit_conditions(
            sensor_data['crate_readings'][0],
            'apple'
        )

        # Create an order (using a real address that can be geocoded)
        order_data = {
            'order_id': 'ORD001',
            'destination': '1 Apple Park Way, Cupertino, CA 95014',  # Apple HQ address as example
            'fruit_type': 'apple',
            'quantity': 100,  # kg
            'delivery_time': (datetime.now() + timedelta(days=2)).isoformat()
        }
        system.create_order(order_data)

        # Optimize routes
        routes = system.optimize_delivery_routes(ripeness_data)

        print("Supply Chain Management System Demo Completed Successfully")
        return 0

    except Exception as e:
        logging.error(f"System error: {str(e)}")
        return 1

if __name__ == "__main__":
    main()

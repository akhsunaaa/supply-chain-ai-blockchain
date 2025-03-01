# route_optimizer.py
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

class Order:
    """Class representing a customer order"""
    def __init__(self, order_id: str, destination: str, fruit_type: str, 
                 quantity: float, required_delivery_time: datetime):
        self.order_id = order_id
        self.destination = destination
        self.fruit_type = fruit_type
        self.quantity = quantity  # in kg
        self.required_delivery_time = required_delivery_time
        self.assigned_crates: List[str] = []
        self.coordinates: Optional[Tuple[float, float]] = None
        self.priority_score: Optional[float] = None
        self.status = 'pending'
        self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'destination': self.destination,
            'fruit_type': self.fruit_type,
            'quantity': self.quantity,
            'required_delivery_time': self.required_delivery_time.isoformat(),
            'assigned_crates': self.assigned_crates,
            'coordinates': self.coordinates,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Vehicle:
    """Class representing a delivery vehicle"""
    def __init__(self, vehicle_id: str, capacity: float, avg_speed: float,
                 refrigeration: bool = True):
        self.vehicle_id = vehicle_id
        self.capacity = capacity  # in kg
        self.avg_speed = avg_speed  # km/h
        self.refrigeration = refrigeration
        self.current_location: Optional[Tuple[float, float]] = None
        self.assigned_orders: List[Order] = []
        self.route: List[Dict] = []
        self.status = 'available'
        self.total_distance = 0.0
        self.maintenance_due = datetime.now()

    def to_dict(self) -> Dict:
        """Convert vehicle to dictionary"""
        return {
            'vehicle_id': self.vehicle_id,
            'capacity': self.capacity,
            'avg_speed': self.avg_speed,
            'refrigeration': self.refrigeration,
            'current_location': self.current_location,
            'status': self.status,
            'total_distance': self.total_distance,
            'maintenance_due': self.maintenance_due.isoformat()
        }

class RouteOptimizer:
    """Class for optimizing delivery routes"""
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.vehicles: Dict[str, Vehicle] = {}
        self.warehouses: Dict[str, Dict] = {}
        self.logger = logging.getLogger('RouteOptimizer')
        
        # Initialize geocoder with a longer timeout
        self.geocoder = Nominatim(
            user_agent="supply_chain_management",
            timeout=10
        )

    def _geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Geocode a location with error handling and retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                location_data = self.geocoder.geocode(location)
                if location_data:
                    return (location_data.latitude, location_data.longitude)
                
                # If geocoding failed but didn't raise an exception
                if attempt == max_retries - 1:
                    # On last attempt, use dummy coordinates for testing
                    self.logger.warning(f"Could not geocode location: {location}. Using dummy coordinates.")
                    return (37.7749, -122.4194)  # San Francisco coordinates as default
                
            except (GeocoderTimedOut, GeocoderUnavailable) as e:
                if attempt == max_retries - 1:
                    self.logger.warning(f"Geocoding failed after {max_retries} attempts: {str(e)}. Using dummy coordinates.")
                    return (37.7749, -122.4194)  # San Francisco coordinates as default
                self.logger.warning(f"Geocoding attempt {attempt + 1} failed: {str(e)}. Retrying...")
            
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.warning(f"Unexpected geocoding error: {str(e)}. Using dummy coordinates.")
                    return (37.7749, -122.4194)  # San Francisco coordinates as default
                self.logger.warning(f"Unexpected error in attempt {attempt + 1}: {str(e)}. Retrying...")

    def add_warehouse(self, warehouse_id: str, location: str) -> None:
        """Add a warehouse location"""
        try:
            coordinates = self._geocode_location(location)
            if coordinates:
                self.warehouses[warehouse_id] = {
                    'location': location,
                    'coordinates': coordinates
                }
                self.logger.info(f"Added warehouse: {warehouse_id}")
            else:
                raise ValueError(f"Could not geocode warehouse location: {location}")
        except Exception as e:
            self.logger.error(f"Error adding warehouse: {str(e)}")
            raise

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a new vehicle to the fleet"""
        try:
            self.vehicles[vehicle.vehicle_id] = vehicle
            self.logger.info(f"Added vehicle: {vehicle.vehicle_id}")
        except Exception as e:
            self.logger.error(f"Error adding vehicle: {str(e)}")
            raise

    def add_order(self, order: Order) -> None:
        """Add a new order to the system"""
        try:
            coordinates = self._geocode_location(order.destination)
            if coordinates:
                order.coordinates = coordinates
                self.orders[order.order_id] = order
                self.logger.info(f"Added order: {order.order_id}")
            else:
                raise ValueError(f"Could not geocode destination: {order.destination}")
        except Exception as e:
            self.logger.error(f"Error adding order: {str(e)}")
            raise

    def _calculate_distance(self, point1: Tuple[float, float],
                          point2: Tuple[float, float]) -> float:
        """Calculate distance between two points using Euclidean distance"""
        return np.sqrt(
            (point2[0] - point1[0])**2 + 
            (point2[1] - point1[1])**2
        ) * 111  # Rough conversion to kilometers

    def _calculate_travel_time(self, distance: float, speed: float) -> float:
        """Calculate travel time in hours"""
        return distance / speed

    def optimize_routes(self, ripeness_data: Dict) -> Dict:
        """Optimize delivery routes"""
        try:
            routes = {}
            unassigned_orders = []

            # Simple greedy algorithm for route optimization
            for vehicle in self.vehicles.values():
                if vehicle.status != 'available':
                    continue

                vehicle_orders = []
                current_load = 0
                current_pos = list(self.warehouses.values())[0]['coordinates']

                # Sort orders by distance from current position
                available_orders = [
                    order for order in self.orders.values()
                    if order.status == 'pending' and 
                    order.quantity + current_load <= vehicle.capacity
                ]

                while available_orders:
                    # Find closest order
                    closest_order = min(
                        available_orders,
                        key=lambda o: self._calculate_distance(current_pos, o.coordinates)
                    )

                    # Add order to route
                    vehicle_orders.append(closest_order)
                    current_load += closest_order.quantity
                    current_pos = closest_order.coordinates
                    available_orders.remove(closest_order)

                    # Update order status
                    closest_order.status = 'assigned'

                if vehicle_orders:
                    # Calculate route metrics
                    total_distance = 0
                    current_pos = list(self.warehouses.values())[0]['coordinates']
                    route_stops = []

                    for order in vehicle_orders:
                        distance = self._calculate_distance(current_pos, order.coordinates)
                        total_distance += distance
                        route_stops.append({
                            'order': order.to_dict(),
                            'distance': distance,
                            'estimated_time': self._calculate_travel_time(distance, vehicle.avg_speed)
                        })
                        current_pos = order.coordinates

                    routes[vehicle.vehicle_id] = {
                        'vehicle': vehicle.to_dict(),
                        'stops': route_stops,
                        'total_distance': total_distance,
                        'total_time': total_distance / vehicle.avg_speed
                    }

            # Collect unassigned orders
            unassigned_orders = [
                order.to_dict() for order in self.orders.values()
                if order.status == 'pending'
            ]

            return {
                'routes': routes,
                'unassigned_orders': unassigned_orders
            }

        except Exception as e:
            self.logger.error(f"Error optimizing routes: {str(e)}")
            raise

    def get_route_details(self, vehicle_id: str) -> Dict:
        """Get detailed information about a vehicle's route"""
        try:
            if vehicle_id not in self.vehicles:
                raise ValueError(f"Vehicle {vehicle_id} not found")

            vehicle = self.vehicles[vehicle_id]
            route_stops = []
            current_pos = list(self.warehouses.values())[0]['coordinates']

            for order in vehicle.assigned_orders:
                distance = self._calculate_distance(current_pos, order.coordinates)
                travel_time = self._calculate_travel_time(distance, vehicle.avg_speed)

                route_stops.append({
                    'order_id': order.order_id,
                    'destination': order.destination,
                    'distance': distance,
                    'estimated_travel_time': travel_time,
                    'quantity': order.quantity,
                    'fruit_type': order.fruit_type
                })

                current_pos = order.coordinates

            return {
                'vehicle_id': vehicle_id,
                'total_stops': len(route_stops),
                'route_stops': route_stops,
                'has_refrigeration': vehicle.refrigeration,
                'total_cargo': sum(stop['quantity'] for stop in route_stops)
            }

        except Exception as e:
            self.logger.error(f"Error getting route details: {str(e)}")
            raise

    def get_fleet_status(self) -> Dict:
        """Get status of entire fleet"""
        return {
            'total_vehicles': len(self.vehicles),
            'available_vehicles': sum(1 for v in self.vehicles.values() if v.status == 'available'),
            'active_routes': sum(1 for v in self.vehicles.values() if len(v.assigned_orders) > 0),
            'vehicles': [v.to_dict() for v in self.vehicles.values()]
        }

# route_optimizer.py
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import logging

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
        self.maintenance_due = datetime.now() + timedelta(days=30)

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
        self.geocoder = Nominatim(user_agent="supply_chain_management")
        self.logger = logging.getLogger('RouteOptimizer')

    def add_order(self, order: Order) -> None:
        """Add a new order to the system"""
        try:
            # Geocode the destination
            location = self.geocoder.geocode(order.destination)
            if not location:
                raise ValueError(f"Could not geocode destination: {order.destination}")
            
            order.coordinates = (location.latitude, location.longitude)
            self.orders[order.order_id] = order
            self.logger.info(f"Added order: {order.order_id}")
        except Exception as e:
            self.logger.error(f"Error adding order: {str(e)}")
            raise

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a new vehicle to the fleet"""
        try:
            self.vehicles[vehicle.vehicle_id] = vehicle
            self.logger.info(f"Added vehicle: {vehicle.vehicle_id}")
        except Exception as e:
            self.logger.error(f"Error adding vehicle: {str(e)}")
            raise

    def add_warehouse(self, warehouse_id: str, location: str) -> None:
        """Add a warehouse location"""
        try:
            loc = self.geocoder.geocode(location)
            if not loc:
                raise ValueError(f"Could not geocode warehouse location: {location}")
            
            self.warehouses[warehouse_id] = {
                'location': location,
                'coordinates': (loc.latitude, loc.longitude)
            }
            self.logger.info(f"Added warehouse: {warehouse_id}")
        except Exception as e:
            self.logger.error(f"Error adding warehouse: {str(e)}")
            raise

    def _calculate_travel_time(self, point1: Tuple[float, float],
                             point2: Tuple[float, float],
                             vehicle_speed: float) -> float:
        """Calculate travel time between two points"""
        try:
            distance = geodesic(point1, point2).kilometers
            return distance / vehicle_speed  # hours
        except Exception as e:
            self.logger.error(f"Error calculating travel time: {str(e)}")
            raise

    def _calculate_priority_score(self, order: Order,
                                ripeness_data: Dict) -> float:
        """Calculate priority score for an order"""
        try:
            # Time until delivery deadline
            time_remaining = (order.required_delivery_time - datetime.now()).total_seconds() / 3600
            
            # Ripeness factor
            ripeness_score = ripeness_data.get('condition_score', 0.5)
            
            # Priority increases as deadline approaches and if fruit is riper
            priority = (1 / max(time_remaining, 1)) * (1 / ripeness_score)
            return priority
        except Exception as e:
            self.logger.error(f"Error calculating priority score: {str(e)}")
            raise

    def optimize_routes(self, ripeness_data: Dict) -> Dict:
        """Optimize delivery routes"""
        try:
            # Calculate priority scores for all orders
            for order in self.orders.values():
                if order.status == 'pending':
                    order.priority_score = self._calculate_priority_score(order, ripeness_data)

            # Sort orders by priority
            prioritized_orders = sorted(
                [order for order in self.orders.values() if order.status == 'pending'],
                key=lambda x: x.priority_score or 0,
                reverse=True
            )

            routes = {}
            unassigned_orders = []

            # Assign orders to vehicles
            for order in prioritized_orders:
                assigned = False
                best_vehicle = None
                min_delivery_time = float('inf')

                for vehicle in self.vehicles.values():
                    if vehicle.status != 'available':
                        continue

                    current_load = sum(o.quantity for o in vehicle.assigned_orders)
                    if current_load + order.quantity <= vehicle.capacity:
                        # Find nearest warehouse
                        nearest_warehouse = min(
                            self.warehouses.items(),
                            key=lambda w: geodesic(
                                w[1]['coordinates'],
                                order.coordinates
                            ).kilometers
                        )

                        delivery_time = self._calculate_travel_time(
                            nearest_warehouse[1]['coordinates'],
                            order.coordinates,
                            vehicle.avg_speed
                        )

                        if delivery_time < min_delivery_time:
                            min_delivery_time = delivery_time
                            best_vehicle = vehicle

                if best_vehicle and min_delivery_time * 3600 <= (
                    order.required_delivery_time - datetime.now()
                ).total_seconds():
                    best_vehicle.assigned_orders.append(order)
                    order.status = 'assigned'
                    assigned = True
                    
                    if best_vehicle.vehicle_id not in routes:
                        routes[best_vehicle.vehicle_id] = {
                            'vehicle': best_vehicle.to_dict(),
                            'route': [],
                            'total_distance': 0,
                            'total_time': 0
                        }

                    routes[best_vehicle.vehicle_id]['route'].append({
                        'order': order.to_dict(),
                        'pickup': nearest_warehouse[0],
                        'estimated_delivery_time': datetime.now() + timedelta(hours=min_delivery_time)
                    })

                if not assigned:
                    unassigned_orders.append(order.to_dict())

            # Calculate route metrics
            for vehicle_id, route_info in routes.items():
                route = route_info['route']
                total_distance = 0
                current_pos = self.warehouses[route[0]['pickup']]['coordinates']

                for stop in route:
                    order = self.orders[stop['order']['order_id']]
                    distance = geodesic(current_pos, order.coordinates).kilometers
                    total_distance += distance
                    current_pos = order.coordinates

                route_info['total_distance'] = total_distance
                route_info['total_time'] = total_distance / self.vehicles[vehicle_id].avg_speed

            self.logger.info("Route optimization completed")
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
            current_pos = None

            for order in vehicle.assigned_orders:
                # Find nearest warehouse for pickup
                nearest_warehouse = min(
                    self.warehouses.items(),
                    key=lambda w: geodesic(
                        w[1]['coordinates'],
                        order.coordinates
                    ).kilometers
                )

                if not current_pos:
                    current_pos = nearest_warehouse[1]['coordinates']

                travel_time = self._calculate_travel_time(
                    current_pos,
                    order.coordinates,
                    vehicle.avg_speed
                )

                route_stops.append({
                    'order_id': order.order_id,
                    'pickup_location': nearest_warehouse[0],
                    'delivery_location': order.destination,
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

    def update_vehicle_location(self, vehicle_id: str, 
                              coordinates: Tuple[float, float]) -> None:
        """Update vehicle's current location"""
        try:
            if vehicle_id not in self.vehicles:
                raise ValueError(f"Vehicle {vehicle_id} not found")
            
            vehicle = self.vehicles[vehicle_id]
            vehicle.current_location = coordinates
            self.logger.info(f"Updated location for vehicle: {vehicle_id}")
        except Exception as e:
            self.logger.error(f"Error updating vehicle location: {str(e)}")
            raise

    def get_fleet_status(self) -> Dict:
        """Get status of entire fleet"""
        return {
            'total_vehicles': len(self.vehicles),
            'available_vehicles': sum(1 for v in self.vehicles.values() if v.status == 'available'),
            'active_routes': sum(1 for v in self.vehicles.values() if len(v.assigned_orders) > 0),
            'vehicles': [v.to_dict() for v in self.vehicles.values()]
        }

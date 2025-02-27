# route_optimizer.py
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

class Order:
    def __init__(self, order_id: str, destination: str, fruit_type: str, quantity: float,
                 required_delivery_time: datetime):
        self.order_id = order_id
        self.destination = destination
        self.fruit_type = fruit_type
        self.quantity = quantity  # in kg
        self.required_delivery_time = required_delivery_time
        self.assigned_crates = []
        self.coordinates = None
        self.priority_score = None

class Vehicle:
    def __init__(self, vehicle_id: str, capacity: float, avg_speed: float,
                 refrigeration: bool = True):
        self.vehicle_id = vehicle_id
        self.capacity = capacity  # in kg
        self.avg_speed = avg_speed  # km/h
        self.refrigeration = refrigeration
        self.current_location = None
        self.assigned_orders = []
        self.route = []

class RouteOptimizer:
    def __init__(self):
        self.orders = {}
        self.vehicles = {}
        self.warehouses = {}
        self.geocoder = Nominatim(user_agent="supply_chain_management")
        
    def add_order(self, order: Order) -> None:
        """Add a new order to the system"""
        # Geocode the destination
        try:
            location = self.geocoder.geocode(order.destination)
            order.coordinates = (location.latitude, location.longitude)
        except:
            raise ValueError(f"Could not geocode destination: {order.destination}")
            
        self.orders[order.order_id] = order

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a new vehicle to the fleet"""
        self.vehicles[vehicle.vehicle_id] = vehicle

    def add_warehouse(self, warehouse_id: str, location: str) -> None:
        """Add a warehouse location"""
        try:
            loc = self.geocoder.geocode(location)
            self.warehouses[warehouse_id] = {
                'location': location,
                'coordinates': (loc.latitude, loc.longitude)
            }
        except:
            raise ValueError(f"Could not geocode warehouse location: {location}")

    def _calculate_travel_time(self, point1: Tuple[float, float],
                             point2: Tuple[float, float],
                             vehicle_speed: float) -> float:
        """Calculate travel time between two points"""
        distance = geodesic(point1, point2).kilometers
        return distance / vehicle_speed  # hours

    def _calculate_priority_score(self, order: Order,
                                ripeness_data: Dict) -> float:
        """Calculate priority score for an order based on multiple factors"""
        # Time until delivery deadline
        time_remaining = (order.required_delivery_time - datetime.now()).total_seconds() / 3600
        
        # Ripeness factor
        ripeness_score = ripeness_data.get('condition_score', 0.5)
        
        # Priority increases as deadline approaches and if fruit is riper
        priority = (1 / time_remaining) * (1 / ripeness_score)
        return priority

    def optimize_routes(self, ripeness_data: Dict) -> Dict:
        """
        Optimize delivery routes based on orders, vehicle availability,
        and fruit conditions
        """
        # Calculate priority scores for all orders
        for order in self.orders.values():
            order.priority_score = self._calculate_priority_score(order, ripeness_data)

        # Sort orders by priority
        prioritized_orders = sorted(
            self.orders.values(),
            key=lambda x: x.priority_score,
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
                if sum(o.quantity for o in vehicle.assigned_orders) + order.quantity <= vehicle.capacity:
                    # Find nearest warehouse
                    nearest_warehouse = min(
                        self.warehouses.items(),
                        key=lambda w: geodesic(
                            w[1]['coordinates'],
                            order.coordinates
                        ).kilometers
                    )

                    # Calculate delivery time
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
                assigned = True
                
                # Update route for this vehicle
                if best_vehicle.vehicle_id not in routes:
                    routes[best_vehicle.vehicle_id] = {
                        'vehicle': best_vehicle,
                        'route': [],
                        'total_distance': 0,
                        'total_time': 0
                    }

                routes[best_vehicle.vehicle_id]['route'].append({
                    'order': order,
                    'pickup': nearest_warehouse[0],
                    'estimated_delivery_time': datetime.now() + timedelta(hours=min_delivery_time)
                })

            if not assigned:
                unassigned_orders.append(order)

        # Calculate route metrics
        for vehicle_id, route_info in routes.items():
            route = route_info['route']
            total_distance = 0
            current_pos = self.warehouses[route[0]['pickup']]['coordinates']

            for stop in route:
                distance = geodesic(
                    current_pos,
                    stop['order'].coordinates
                ).kilometers
                total_distance += distance
                current_pos = stop['order'].coordinates

            route_info['total_distance'] = total_distance
            route_info['total_time'] = total_distance / route_info['vehicle'].avg_speed

        return {
            'routes': routes,
            'unassigned_orders': unassigned_orders
        }

    def get_route_details(self, vehicle_id: str) -> Dict:
        """Get detailed information about a vehicle's route"""
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

            # Calculate times
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

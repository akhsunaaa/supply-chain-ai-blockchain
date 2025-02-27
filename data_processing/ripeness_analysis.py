# ripeness_analysis.py
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class FruitParameters:
    """Class to store fruit-specific parameters and thresholds"""
    def __init__(self, fruit_type: str):
        self.fruit_type = fruit_type
        # Define optimal conditions for different fruits
        self.parameters = {
            'apple': {
                'optimal_temp': (0, 4),  # °C
                'optimal_humidity': (90, 95),  # %
                'ethylene_threshold': 1.0,  # ppm
                'max_shelf_life': 180  # days
            },
            'banana': {
                'optimal_temp': (13, 15),
                'optimal_humidity': (85, 90),
                'ethylene_threshold': 0.5,
                'max_shelf_life': 14
            },
            'orange': {
                'optimal_temp': (7, 10),
                'optimal_humidity': (85, 90),
                'ethylene_threshold': 0.1,
                'max_shelf_life': 56
            }
            # Add more fruits as needed
        }

class RipenessAnalyzer:
    def __init__(self):
        self.fruit_params = {}
        self._initialize_fruit_parameters()
        self.historical_data = []

    def _initialize_fruit_parameters(self):
        """Initialize parameters for different types of fruits"""
        fruit_types = ['apple', 'banana', 'orange']
        for fruit in fruit_types:
            self.fruit_params[fruit] = FruitParameters(fruit)

    def _calculate_condition_score(self, 
                                 current_conditions: Dict, 
                                 fruit_type: str) -> float:
        """
        Calculate a score (0-1) indicating how close the conditions are to optimal
        """
        params = self.fruit_params[fruit_type].parameters
        
        # Temperature score
        temp = current_conditions['temperature']
        opt_temp_min, opt_temp_max = params['optimal_temp']
        temp_score = 1.0 - min(abs(temp - opt_temp_min), abs(temp - opt_temp_max)) / 10.0
        
        # Humidity score
        humidity = current_conditions['humidity']
        opt_hum_min, opt_hum_max = params['optimal_humidity']
        humidity_score = 1.0 - min(abs(humidity - opt_hum_min), abs(humidity - opt_hum_max)) / 100.0
        
        # Ethylene score
        ethylene = current_conditions['ethylene_level']
        ethylene_score = 1.0 - min(ethylene / params['ethylene_threshold'], 1.0)
        
        # Weighted average of scores
        total_score = (0.4 * temp_score + 0.3 * humidity_score + 0.3 * ethylene_score)
        return max(0.0, min(1.0, total_score))

    def analyze_ripeness(self, 
                        sensor_data: Dict, 
                        fruit_type: str) -> Dict:
        """
        Analyze fruit ripeness based on sensor data
        Returns ripeness status and estimated shelf life
        """
        condition_score = self._calculate_condition_score(sensor_data, fruit_type)
        
        # Store historical data for trend analysis
        self.historical_data.append({
            'timestamp': datetime.now(),
            'condition_score': condition_score,
            'sensor_data': sensor_data
        })
        
        # Calculate remaining shelf life based on conditions
        max_shelf_life = self.fruit_params[fruit_type].parameters['max_shelf_life']
        estimated_shelf_life = max_shelf_life * condition_score
        
        # Determine ripeness stage
        ripeness_stages = {
            (0.8, 1.0): 'Unripe',
            (0.6, 0.8): 'Nearly Ripe',
            (0.4, 0.6): 'Ripe',
            (0.2, 0.4): 'Very Ripe',
            (0.0, 0.2): 'Overripe'
        }
        
        current_stage = next(
            stage for (score_range, stage) in ripeness_stages.items()
            if score_range[0] <= condition_score <= score_range[1]
        )

        return {
            'fruit_type': fruit_type,
            'ripeness_stage': current_stage,
            'condition_score': condition_score,
            'estimated_shelf_life_days': round(estimated_shelf_life, 1),
            'optimal_temperature': self.fruit_params[fruit_type].parameters['optimal_temp'],
            'optimal_humidity': self.fruit_params[fruit_type].parameters['optimal_humidity'],
            'timestamp': datetime.now().isoformat()
        }

    def predict_quality_degradation(self, 
                                  current_data: Dict, 
                                  fruit_type: str, 
                                  hours_ahead: int = 24) -> List[Dict]:
        """
        Predict quality degradation over time based on current conditions
        """
        predictions = []
        current_score = self._calculate_condition_score(current_data, fruit_type)
        
        # Simple degradation model - can be replaced with ML model
        for hour in range(hours_ahead):
            # Assume exponential decay of quality
            degradation_factor = np.exp(-0.01 * hour)
            predicted_score = current_score * degradation_factor
            
            predictions.append({
                'hours_ahead': hour,
                'predicted_score': predicted_score,
                'timestamp': (datetime.now() + timedelta(hours=hour)).isoformat()
            })
        
        return predictions

    def get_shipping_recommendations(self, 
                                   analysis_result: Dict, 
                                   destination_time_hours: float) -> Dict:
        """
        Provide recommendations for shipping based on ripeness analysis
        """
        condition_score = analysis_result['condition_score']
        
        if condition_score < 0.2:
            recommendation = "Not suitable for shipping - fruit quality too low"
            priority = "Do not ship"
        elif condition_score < 0.4:
            recommendation = "Ship only to nearby destinations (< 24 hours)"
            priority = "High priority - ship immediately"
        elif condition_score < 0.6:
            recommendation = "Suitable for medium-distance shipping (< 72 hours)"
            priority = "Medium priority"
        else:
            recommendation = "Suitable for all shipping distances"
            priority = "Normal priority"
            
        return {
            'recommendation': recommendation,
            'priority': priority,
            'max_recommended_shipping_time': self._calculate_max_shipping_time(condition_score),
            'requires_refrigeration': condition_score < 0.8
        }

    def _calculate_max_shipping_time(self, condition_score: float) -> int:
        """Calculate maximum recommended shipping time in hours based on condition"""
        base_time = 168  # One week in hours
        return int(base_time * condition_score)

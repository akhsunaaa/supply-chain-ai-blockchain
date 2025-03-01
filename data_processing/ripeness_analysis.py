# ripeness_analysis.py
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

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
                'max_shelf_life': 180,  # days
                'ripening_rate': 0.05  # % per day
            },
            'banana': {
                'optimal_temp': (13, 15),
                'optimal_humidity': (85, 90),
                'ethylene_threshold': 0.5,
                'max_shelf_life': 14,
                'ripening_rate': 0.15
            },
            'orange': {
                'optimal_temp': (7, 10),
                'optimal_humidity': (85, 90),
                'ethylene_threshold': 0.1,
                'max_shelf_life': 56,
                'ripening_rate': 0.08
            }
        }

class RipenessAnalyzer:
    """Class for analyzing fruit ripeness using AI/ML"""
    def __init__(self):
        self.fruit_params = {}
        self.historical_data = []
        self.model = None
        self.logger = logging.getLogger('RipenessAnalyzer')
        self._initialize_fruit_parameters()
        self._initialize_ml_model()

    def _initialize_fruit_parameters(self) -> None:
        """Initialize parameters for different types of fruits"""
        fruit_types = ['apple', 'banana', 'orange']
        for fruit in fruit_types:
            self.fruit_params[fruit] = FruitParameters(fruit)

    def _initialize_ml_model(self) -> None:
        """Initialize or load the ML model"""
        try:
            if os.path.exists('ripeness_model.joblib'):
                self.model = joblib.load('ripeness_model.joblib')
            else:
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42
                )
                # Model will be trained as historical data is collected
        except Exception as e:
            self.logger.error(f"Error initializing ML model: {str(e)}")
            self.model = None

    def _calculate_condition_score(self, 
                                 current_conditions: Dict, 
                                 fruit_type: str) -> float:
        """Calculate condition score based on environmental conditions"""
        try:
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
            ethylene = current_conditions.get('ethylene_level', 0)
            ethylene_score = 1.0 - min(ethylene / params['ethylene_threshold'], 1.0)
            
            # Weighted average of scores
            total_score = (0.4 * temp_score + 0.3 * humidity_score + 0.3 * ethylene_score)
            return max(0.0, min(1.0, total_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating condition score: {str(e)}")
            raise

    def analyze_ripeness(self, sensor_data: Dict, fruit_type: str) -> Dict:
        """Analyze fruit ripeness using sensor data and ML model"""
        try:
            # Calculate basic condition score
            condition_score = self._calculate_condition_score(sensor_data, fruit_type)
            
            # Prepare data for ML prediction
            if self.model:
                features = np.array([[
                    sensor_data['temperature'],
                    sensor_data['humidity'],
                    sensor_data.get('ethylene_level', 0),
                    condition_score
                ]])
                predicted_shelf_life = self.model.predict(features)[0]
            else:
                # Fallback to basic calculation if model isn't ready
                max_shelf_life = self.fruit_params[fruit_type].parameters['max_shelf_life']
                predicted_shelf_life = max_shelf_life * condition_score
            
            # Store data for model training
            self.historical_data.append({
                'timestamp': datetime.now(),
                'fruit_type': fruit_type,
                'conditions': sensor_data,
                'condition_score': condition_score
            })
            
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
                'estimated_shelf_life_days': round(predicted_shelf_life, 1),
                'optimal_temperature': self.fruit_params[fruit_type].parameters['optimal_temp'],
                'optimal_humidity': self.fruit_params[fruit_type].parameters['optimal_humidity'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing ripeness: {str(e)}")
            raise

    def predict_quality_degradation(self, 
                                  current_data: Dict, 
                                  fruit_type: str, 
                                  hours_ahead: int = 24) -> List[Dict]:
        """Predict quality degradation over time"""
        try:
            predictions = []
            current_score = self._calculate_condition_score(current_data, fruit_type)
            ripening_rate = self.fruit_params[fruit_type].parameters['ripening_rate']
            
            for hour in range(hours_ahead):
                # Calculate degradation using exponential decay and ripening rate
                time_factor = hour / 24.0  # Convert hours to days
                degradation_factor = np.exp(-ripening_rate * time_factor)
                predicted_score = current_score * degradation_factor
                
                predictions.append({
                    'hours_ahead': hour,
                    'predicted_score': predicted_score,
                    'timestamp': (datetime.now() + timedelta(hours=hour)).isoformat()
                })
            
            return predictions

        except Exception as e:
            self.logger.error(f"Error predicting quality degradation: {str(e)}")
            raise

    def get_shipping_recommendations(self, 
                                   analysis_result: Dict, 
                                   destination_time_hours: float) -> Dict:
        """Provide shipping recommendations based on ripeness analysis"""
        try:
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

        except Exception as e:
            self.logger.error(f"Error generating shipping recommendations: {str(e)}")
            raise

    def _calculate_max_shipping_time(self, condition_score: float) -> int:
        """Calculate maximum recommended shipping time in hours"""
        try:
            base_time = 168  # One week in hours
            return int(base_time * condition_score)
        except Exception as e:
            self.logger.error(f"Error calculating max shipping time: {str(e)}")
            raise

    def train_model(self) -> None:
        """Train the ML model using collected historical data"""
        try:
            if len(self.historical_data) < 100:  # Need minimum amount of data
                return

            # Prepare training data
            X = []
            y = []
            
            for data in self.historical_data:
                conditions = data['conditions']
                X.append([
                    conditions['temperature'],
                    conditions['humidity'],
                    conditions.get('ethylene_level', 0),
                    data['condition_score']
                ])
                y.append(self.fruit_params[data['fruit_type']].parameters['max_shelf_life'])

            X = np.array(X)
            y = np.array(y)

            # Train model
            self.model.fit(X, y)
            
            # Save model
            joblib.dump(self.model, 'ripeness_model.joblib')
            self.logger.info("ML model trained and saved successfully")

        except Exception as e:
            self.logger.error(f"Error training ML model: {str(e)}")
            raise

    def get_analysis_history(self, fruit_type: str = None) -> List[Dict]:
        """Get historical analysis data, optionally filtered by fruit type"""
        try:
            if fruit_type:
                return [data for data in self.historical_data if data['fruit_type'] == fruit_type]
            return self.historical_data
        except Exception as e:
            self.logger.error(f"Error retrieving analysis history: {str(e)}")
            raise

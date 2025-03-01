"""
Supply Chain Management System
============================

An AI and blockchain-based system for managing fruit supply chains.

Core Components:
- Sensor monitoring and data collection
- AI-based ripeness analysis
- Route optimization
- Blockchain integration
- Web interface
"""

from .main import SupplyChainManager
from .sensors import SensorNetwork
from .data_processing import RipenessAnalyzer
from .logistics import RouteOptimizer
from .blockchain import BlockchainIntegration
from .web import app

__version__ = '1.0.0'

__all__ = [
    'SupplyChainManager',
    'SensorNetwork',
    'RipenessAnalyzer',
    'RouteOptimizer',
    'BlockchainIntegration',
    'app'
]

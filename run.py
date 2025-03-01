#!/usr/bin/env python3
"""
Supply Chain Management System Runner
==================================

This script initializes and runs the supply chain management system.
"""

import os
import sys
import logging

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app
from web.models import create_test_accounts
from main import SupplyChainManager

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('SupplyChainSystem')
    return logger

def initialize_system():
    """Initialize the supply chain management system"""
    logger = setup_logging()
    
    try:
        # Initialize supply chain manager
        logger.info("Initializing Supply Chain Manager...")
        supply_chain = SupplyChainManager()

        # Create test accounts
        logger.info("Creating test accounts...")
        create_test_accounts()

        # Register test warehouse
        logger.info("Registering test warehouse...")
        supply_chain.register_warehouse(
            "WH001",
            "123 Warehouse St, Storage City, SC 12345"
        )

        # Register test vehicle
        logger.info("Registering test vehicle...")
        supply_chain.register_vehicle({
            'vehicle_id': 'VH001',
            'capacity': 1000,  # kg
            'avg_speed': 60,   # km/h
            'refrigeration': True
        })

        # Add test sensors
        logger.info("Adding test sensors...")
        supply_chain.add_warehouse_sensor('WHS001', 'WH001')
        supply_chain.add_crate_sensor('CRS001', 'CRT001')

        logger.info("System initialization completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during system initialization: {str(e)}")
        return False

def main():
    """Main function to run the application"""
    # Set Flask environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_APP'] = 'web.app'
    
    # Initialize the system
    if not initialize_system():
        print("Error: System initialization failed")
        return 1

    # Run the Flask application
    try:
        print("\n" + "="*50)
        print("Supply Chain Management System")
        print("="*50)
        print("\nAccess the web interface at http://localhost:5000")
        print("\nTest Accounts:")
        print("Farmer Login:")
        print("  Username: test_farmer")
        print("  Password: password")
        print("\nCustomer Login:")
        print("  Username: test_customer")
        print("  Password: password")
        print("\nPress Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        return 0
        
    except Exception as e:
        print(f"Error starting the application: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())

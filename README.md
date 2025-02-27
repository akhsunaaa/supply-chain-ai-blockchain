# AI and Blockchain-Based Supply Chain Management System

## Overview
This system provides an end-to-end solution for managing fruit supply chains using AI for ripeness analysis and blockchain for transparency. It features a web-based dashboard for both farmers and customers, real-time sensor monitoring, and intelligent route optimization.

## Features

### 1. Web Dashboard
- **Farmer Interface**:
  - Real-time sensor monitoring
  - Inventory management
  - Order processing
  - Analytics and reporting
- **Customer Interface**:
  - Order placement
  - Real-time order tracking
  - Delivery status updates
  - Order history

### 2. Sensor Integration
- Warehouse sensors for monitoring:
  - Temperature
  - Humidity
- Crate-level sensors tracking:
  - Temperature
  - Humidity
  - Ethylene presence
  - GPS location

### 3. AI-Powered Analysis
- Real-time fruit ripeness assessment
- Shelf life prediction
- Quality degradation forecasting
- Shipping recommendations based on fruit conditions

### 4. Route Optimization
- Dynamic route planning based on:
  - Customer demands
  - Fruit conditions
  - Delivery deadlines
  - Vehicle capacity
  - Distance optimization
- Real-time tracking of shipments

### 5. Blockchain Integration
- Immutable record of:
  - Sensor readings
  - Quality assessments
  - Shipment details
  - Route changes
  - Delivery confirmations

## System Architecture

### Components
1. `web/`: Web dashboard interface
   - `templates/`: HTML templates
   - `models.py`: Data models
   - `app.py`: Flask application

2. `sensors/`
   - `sensor_data.py`: Sensor data collection and management

3. `data_processing/`
   - `ripeness_analysis.py`: AI algorithms for fruit analysis

4. `logistics/`
   - `route_optimizer.py`: Delivery route optimization

5. `blockchain/`
   - `integration.py`: Blockchain integration

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd supply_chain_management_system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

The web interface will be available at `http://localhost:5000`

## Usage

### Accessing the Dashboard

1. **For Farmers**:
   - Login with farmer credentials
   - Access sensor data, inventory, and orders
   - Monitor fruit conditions
   - Process customer orders

2. **For Customers**:
   - Register/login with customer credentials
   - Browse available products
   - Place new orders
   - Track existing orders

### Managing Sensors

1. Add new sensors:
```python
from sensors.sensor_data import SensorNetwork

network = SensorNetwork()
network.add_warehouse_sensor("WH001", "Warehouse A")
network.add_crate_sensor("CR001", "Crate 1")
```

### Processing Orders

1. Create new order:
```python
from main import SupplyChainManager

system = SupplyChainManager()
order_data = {
    'order_id': 'ORD001',
    'destination': '123 Customer St',
    'fruit_type': 'apple',
    'quantity': 100
}
system.create_order(order_data)
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
The project follows PEP 8 guidelines. Format code using:
```bash
black .
```

### Database Migrations
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

## API Documentation

### REST API Endpoints

#### Authentication
- POST `/api/auth/login`
- POST `/api/auth/register`

#### Farmer Endpoints
- GET `/api/farmer/sensors`
- GET `/api/farmer/inventory`
- GET `/api/farmer/orders`

#### Customer Endpoints
- GET `/api/customer/products`
- POST `/api/customer/orders`
- GET `/api/customer/orders/{order_id}`

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## Security Considerations
- All API endpoints are secured with JWT authentication
- Sensor data is encrypted in transit
- Blockchain ensures data immutability
- Regular security audits are recommended

## Deployment

### Production Setup
1. Set up a production database
2. Configure SSL certificates
3. Set up environment variables
4. Deploy using Docker (recommended)

### Docker Deployment
```bash
docker-compose up -d
```

## Monitoring and Maintenance

### System Monitoring
- Monitor sensor health
- Check blockchain network status
- Monitor server resources
- Set up alerts for critical conditions

### Backup Procedures
- Regular database backups
- Blockchain node synchronization
- Sensor data archival

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support and queries:
- Create an issue in the repository
- Contact the development team

## Authors
- [Your Name]
- [Contributors]

## Acknowledgments
- Thanks to all contributors
- Special thanks to [Organizations/People] for their support

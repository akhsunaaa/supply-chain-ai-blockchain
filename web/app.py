# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import os
import sys
from datetime import datetime
import logging

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import user_manager
from main import SupplyChainManager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change in production

# Initialize supply chain system
supply_chain = SupplyChainManager()
logger = logging.getLogger('WebApp')

# Middleware to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware to check user role
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page', 'warning')
                return redirect(url_for('login'))
            
            user = user_manager.get_user_by_id(session['user_id'])
            if not user or user.role not in allowed_roles:
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = user_manager.authenticate_user(username, password)
        if user:
            session['user_id'] = user.user_id
            flash(f'Welcome back, {user.username}!', 'success')
            if user.role == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            
            user = user_manager.create_user(username, email, password, role)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Farmer Routes
@app.route('/farmer/dashboard')
@login_required
@role_required(['farmer'])
def farmer_dashboard():
    try:
        user = user_manager.get_user_by_id(session['user_id'])
        
        # Get system status
        sensor_data = supply_chain.process_sensor_data()
        inventory = supply_chain.get_inventory_status()
        
        return render_template('farmer/dashboard.html',
                            user=user,
                            sensor_data=sensor_data,
                            inventory=inventory)
    except Exception as e:
        logger.error(f"Error in farmer dashboard: {str(e)}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/farmer/inventory')
@login_required
@role_required(['farmer'])
def farmer_inventory():
    try:
        inventory = supply_chain.get_inventory_status()
        return render_template('farmer/inventory.html', inventory=inventory)
    except Exception as e:
        logger.error(f"Error in inventory page: {str(e)}")
        flash('Error loading inventory', 'error')
        return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/sensors')
@login_required
@role_required(['farmer'])
def farmer_sensors():
    try:
        sensor_data = supply_chain.process_sensor_data()
        return render_template('farmer/sensors.html', sensor_data=sensor_data)
    except Exception as e:
        logger.error(f"Error in sensors page: {str(e)}")
        flash('Error loading sensor data', 'error')
        return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/orders')
@login_required
@role_required(['farmer'])
def farmer_orders():
    try:
        # Get all orders from the system
        return render_template('farmer/orders.html')
    except Exception as e:
        logger.error(f"Error in orders page: {str(e)}")
        flash('Error loading orders', 'error')
        return redirect(url_for('farmer_dashboard'))

# Customer Routes
@app.route('/customer/dashboard')
@login_required
@role_required(['customer'])
def customer_dashboard():
    try:
        user = user_manager.get_user_by_id(session['user_id'])
        return render_template('customer/dashboard.html', user=user)
    except Exception as e:
        logger.error(f"Error in customer dashboard: {str(e)}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/customer/orders')
@login_required
@role_required(['customer'])
def customer_orders():
    try:
        user = user_manager.get_user_by_id(session['user_id'])
        return render_template('customer/orders.html', user=user)
    except Exception as e:
        logger.error(f"Error loading orders: {str(e)}")
        flash('Error loading orders', 'error')
        return redirect(url_for('customer_dashboard'))

@app.route('/customer/track/<order_id>')
@login_required
@role_required(['customer'])
def track_order(order_id):
    try:
        shipment_history = supply_chain.get_shipment_history(order_id)
        return render_template('customer/track_order.html', 
                            order_id=order_id,
                            shipment_history=shipment_history)
    except Exception as e:
        logger.error(f"Error tracking order: {str(e)}")
        flash('Error tracking order', 'error')
        return redirect(url_for('customer_orders'))

@app.route('/customer/place-order', methods=['GET', 'POST'])
@login_required
@role_required(['customer'])
def place_order():
    try:
        if request.method == 'POST':
            order_data = {
                'order_id': f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'customer_id': session['user_id'],
                'destination': request.form['delivery_address'],
                'fruit_type': request.form.get('fruit_type'),
                'quantity': float(request.form.get('quantity', 0)),
                'delivery_time': request.form['delivery_date']
            }
            
            order_id = supply_chain.create_order(order_data)
            flash('Order placed successfully!', 'success')
            return redirect(url_for('track_order', order_id=order_id))
            
        # Get available products and inventory
        inventory = supply_chain.get_inventory_status()
        return render_template('customer/place_order.html', inventory=inventory)
    except Exception as e:
        logger.error(f"Error placing order: {str(e)}")
        flash('Error placing order', 'error')
        return redirect(url_for('customer_dashboard'))

# API Routes
@app.route('/api/sensor-data')
@login_required
def api_sensor_data():
    """API endpoint for getting sensor data"""
    try:
        data = supply_chain.process_sensor_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in sensor data API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory')
@login_required
def api_inventory():
    """API endpoint for getting inventory status"""
    try:
        data = supply_chain.get_inventory_status()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in inventory API: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
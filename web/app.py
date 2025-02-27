# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import uuid
from models import User, users

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Middleware to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware to check user role
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or users[session['user_id']].role not in allowed_roles:
                flash('Unauthorized access', 'error')
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
        
        for user in users.values():
            if user.username == username and user.check_password(password):
                session['user_id'] = user.user_id
                if user.role == 'farmer':
                    return redirect(url_for('farmer_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Check if username exists
        if any(user.username == username for user in users.values()):
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user_id = str(uuid.uuid4())
        user = User(user_id, username, email, role)
        user.set_password(password)
        users[user_id] = user
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/farmer/dashboard')
@login_required
@role_required(['farmer'])
def farmer_dashboard():
    user = users[session['user_id']]
    # Here you would get real data from your SupplyChainManager
    return render_template('farmer/dashboard.html', user=user)

@app.route('/farmer/inventory')
@login_required
@role_required(['farmer'])
def farmer_inventory():
    # Get inventory data from SupplyChainManager
    return render_template('farmer/inventory.html')

@app.route('/farmer/sensors')
@login_required
@role_required(['farmer'])
def farmer_sensors():
    # Get sensor data from SupplyChainManager
    return render_template('farmer/sensors.html')

@app.route('/farmer/orders')
@login_required
@role_required(['farmer'])
def farmer_orders():
    # Get orders data from SupplyChainManager
    return render_template('farmer/orders.html')

@app.route('/customer/dashboard')
@login_required
@role_required(['customer'])
def customer_dashboard():
    user = users[session['user_id']]
    # Get customer-specific data from SupplyChainManager
    return render_template('customer/dashboard.html', user=user)

@app.route('/customer/orders')
@login_required
@role_required(['customer'])
def customer_orders():
    # Get customer's orders from SupplyChainManager
    return render_template('customer/orders.html')

@app.route('/customer/track/<order_id>')
@login_required
@role_required(['customer'])
def track_order(order_id):
    # Get tracking information from SupplyChainManager
    return render_template('customer/track_order.html', order_id=order_id)

@app.route('/customer/place-order', methods=['GET', 'POST'])
@login_required
@role_required(['customer'])
def place_order():
    if request.method == 'POST':
        # Process the order using SupplyChainManager
        flash('Order placed successfully!', 'success')
        return redirect(url_for('customer_orders'))
    return render_template('customer/place_order.html')

if __name__ == '__main__':
    # Create a test farmer account
    farmer = User('1', 'test_farmer', 'farmer@example.com', 'farmer')
    farmer.set_password('password')
    users[farmer.user_id] = farmer
    
    # Create a test customer account
    customer = User('2', 'test_customer', 'customer@example.com', 'customer')
    customer.set_password('password')
    users[customer.user_id] = customer
    
    app.run(debug=True)

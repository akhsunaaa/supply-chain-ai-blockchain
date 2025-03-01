# models.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User:
    """User model for both farmers and customers"""
    def __init__(self, user_id: str, username: str, email: str, role: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role  # 'farmer' or 'customer'
        self.password_hash = None
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True

    def set_password(self, password: str) -> None:
        """Set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

class UserManager:
    """Manage user operations"""
    def __init__(self):
        self.users = {}  # In-memory storage (replace with database in production)

    def create_user(self, username: str, email: str, password: str, role: str) -> User:
        """Create a new user"""
        if self.get_user_by_username(username):
            raise ValueError("Username already exists")
        
        if self.get_user_by_email(email):
            raise ValueError("Email already exists")

        user_id = str(uuid.uuid4())
        user = User(user_id, username, email, role)
        user.set_password(password)
        self.users[user_id] = user
        return user

    def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID"""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> User:
        """Get user by username"""
        return next(
            (user for user in self.users.values() if user.username == username),
            None
        )

    def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        return next(
            (user for user in self.users.values() if user.email == email),
            None
        )

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            user.last_login = datetime.now()
            return user
        return None

    def update_user(self, user_id: str, **kwargs) -> User:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def list_users(self, role: str = None) -> list:
        """List all users, optionally filtered by role"""
        users = self.users.values()
        if role:
            users = [user for user in users if user.role == role]
        return [user.to_dict() for user in users]

# Initialize user manager
user_manager = UserManager()

# Create test accounts
def create_test_accounts():
    """Create test accounts for farmer and customer"""
    try:
        # Create test farmer
        user_manager.create_user(
            username="test_farmer",
            email="farmer@example.com",
            password="password",
            role="farmer"
        )
        
        # Create test customer
        user_manager.create_user(
            username="test_customer",
            email="customer@example.com",
            password="password",
            role="customer"
        )
    except ValueError:
        # Test accounts might already exist
        pass

create_test_accounts()

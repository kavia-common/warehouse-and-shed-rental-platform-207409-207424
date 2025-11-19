from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# PUBLIC_INTERFACE
class User(db.Model):
    """Represents a user in the system."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    is_owner = db.Column(db.Boolean, default=False)

    rental_requests = db.relationship('RentalRequest', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# PUBLIC_INTERFACE
class Warehouse(db.Model):
    """Represents a warehouse or shed that can be rented."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(40), nullable=False)  # e.g., 'shed', 'warehouse'
    description = db.Column(db.Text)
    city = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', foreign_keys=[owner_id])

    rental_requests = db.relationship('RentalRequest', backref='warehouse', lazy=True)

# PUBLIC_INTERFACE
class RentalRequest(db.Model):
    """Represents a rental request for a warehouse."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    message = db.Column(db.String(300))
    status = db.Column(db.String(30), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

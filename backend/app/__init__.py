from flask import Flask, jsonify
from flask_cors import CORS
from .routes.health import blp as health_blp
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError  # <-- Fix: import ValidationError

import os

from app.models import db
from app.schemas import UserSchema, WarehouseSchema, RentalRequestSchema

# Blueprints
from .auth import auth_blp
from .routes.warehouse import blp as warehouse_blp
from .routes.rental import blp as rental_blp

app = Flask(__name__)
app.url_map.strict_slashes = False

CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SECRET_KEY"] = "dev-key"  # Set via .env in prod
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "dev-jwt"  # Set via .env in prod
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

db.init_app(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

api = Api(app)

api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(warehouse_blp)
api.register_blueprint(rental_blp)

@app.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    return jsonify({"errors": e.messages}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/seed", methods=["POST"])
def seed():
    """Seed the database with sample data (dev only)"""
    from app.models import User, Warehouse
    # Removed unused: from sqlalchemy.exc import IntegrityError
    db.drop_all()
    db.create_all()
    u1 = User(username="alice", email="alice@test.com", is_owner=True)
    u1.set_password("password123")
    u2 = User(username="bob", email="bob@test.com", is_owner=False)
    u2.set_password("password123")
    db.session.add_all([u1, u2])
    db.session.commit()
    w1 = Warehouse(
        name="Big Warehouse", type="warehouse", description="Spacious modern warehouse",
        city="Mumbai", address="123 Main Rd, Mumbai", owner_id=u1.id, is_available=True,
        image_url="https://picsum.photos/200/300"
    )
    w2 = Warehouse(
        name="Cozy Shed", type="shed", description="Perfect for storage",
        city="Bangalore", address="Green Lane, Bangalore", owner_id=u1.id, is_available=True,
        image_url="https://picsum.photos/200/301"
    )
    db.session.add_all([w1, w2])
    db.session.commit()
    return jsonify({"message": "Seeded"}), 201

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from app.models import db, User
from app.schemas import UserSchema
# Removed: from flask.views import MethodView and marshmallow.ValidationError (unused)

auth_blp = Blueprint("auth", __name__, url_prefix="/auth")

user_schema = UserSchema()

# PUBLIC_INTERFACE
@auth_blp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    post:
      summary: Register a new user.
      requestBody:
        required: true
        content:
          application/json:
            schema: UserSchema
      responses:
        201:
          description: Registered successfully.
        400:
          description: Username/email exists or validation error.
    """
    data = request.get_json()
    try:
        username = data["username"]
        email = data["email"]
        password = data["password"]
    except Exception:
        return {"message": "Missing required fields."}, 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return {"message": "User with this username or email already exists."}, 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201

# PUBLIC_INTERFACE
@auth_blp.route('/login', methods=['POST'])
def login():
    """
    Login a user and return JWT token.
    ---
    post:
      summary: User login.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        200:
          description: Token returned.
        401:
          description: Invalid credentials.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return {"message": "Username and password are required."}, 400
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        additional = {"username": user.username, "email": user.email}
        token = create_access_token(identity=user.id, additional_claims=additional)
        return jsonify(access_token=token)
    return {"message": "Invalid credentials."}, 401

# PUBLIC_INTERFACE
@auth_blp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """
    Get current user details.
    ---
    get:
      summary: Get logged-in user's info.
      responses:
        200:
          description: User info.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return user_schema.dump(user)
    return {"message": "User not found"}, 404

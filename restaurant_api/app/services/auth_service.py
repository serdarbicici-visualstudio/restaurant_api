from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.db import mysql

# Blueprint for Authentication
auth_bp = Blueprint('auth', __name__)

# Register a new user (for both admins and regular users)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Default to 'user' if not provided
    
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    
    # Hash password
    hashed_password = generate_password_hash(password)
    
    # Insert user into MySQL
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"msg": "User registered successfully"}), 201

# User login (authentication)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    # Fetch user from database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user[2], password):  # user[2] is the password
        # Create a JWT token
        access_token = create_access_token(identity={"username": user[1], "role": user[3]})  # user[1] = username, user[3] = role
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401
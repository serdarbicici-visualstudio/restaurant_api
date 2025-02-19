from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql

# Create a Blueprint for 'tables'
tables_bp = Blueprint('tables', __name__)

# Helper function to validate role-based access
def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

# POST route to add a new table
@tables_bp.route('/add', methods=['POST'])
@jwt_required()
def add_table():
    data = request.get_json()

    # Validate required fields
    if 'capacity' not in data or 'location' not in data:
        return jsonify({"msg": "Missing required fields: capacity, location"}), 422
    

    # Get current user identity (the username or user ID from JWT)
    current_user = get_jwt_identity()

    # Check if the current user has 'admin' role
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Unauthorized. You need admin privileges."}), 403

    capacity = data['capacity']
    location = data['location']

    try:
        # Get MySQL connection
        cursor = mysql.connection.cursor()

        # Insert data into the Tables table
        cursor.execute('''INSERT INTO Tables (capacity, location) VALUES (%s, %s)''', (capacity, location))
        mysql.connection.commit()

        cursor.close()

        return jsonify({"msg": "Table created successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    

# GET /api/tables - Fetch all tables
@tables_bp.route('', methods=['GET'])
@jwt_required()
def get_tables():
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Tables")
        tables = cursor.fetchall()
        cursor.close()

        return jsonify(tables), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500


# GET /api/tables/<id> - Fetch a specific table by ID
@tables_bp.route('/<int:table_id>', methods=['GET'])
@jwt_required()
def get_table_by_id(table_id):
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Tables WHERE table_id = %s", (table_id,))
        table = cursor.fetchone()
        cursor.close()

        if not table:
            return jsonify({"msg": "Table not found"}), 404

        return jsonify(table), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500


# PUT /api/tables/<id> - Update a table
@tables_bp.route('/<int:table_id>', methods=['PUT'])
@jwt_required()
def update_table(table_id):
    current_user = get_jwt_identity()

    # Only admin can update tables
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    # Validate input
    capacity = data.get('capacity')
    location = data.get('location')

    if not capacity and not location:
        return jsonify({"msg": "At least one field (capacity, location) must be provided"}), 422

    try:
        cursor = mysql.connection.cursor()

        # Build dynamic query for updates
        query = "UPDATE Tables SET "
        params = []
        if capacity:
            query += "capacity = %s, "
            params.append(capacity)
        if location:
            query += "location = %s, "
            params.append(location)
        query = query.rstrip(', ') + " WHERE table_id = %s"
        params.append(table_id)

        cursor.execute(query, tuple(params))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Table updated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500


# DELETE /api/tables/<id> - Delete a table
@tables_bp.route('/<int:table_id>', methods=['DELETE'])
@jwt_required()
def delete_table(table_id):
    current_user = get_jwt_identity()

    # Only admin can delete tables
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        cursor = mysql.connection.cursor()

        # Check if the table exists
        cursor.execute("SELECT * FROM Tables WHERE table_id = %s", (table_id,))
        table = cursor.fetchone()
        if not table:
            return jsonify({"msg": "Table not found"}), 404

        # Check if the table is referenced in Reservations
        cursor.execute("SELECT * FROM Reservations WHERE table_id = %s", (table_id,))
        reservation = cursor.fetchone()
        if reservation:
            return jsonify({"msg": "Cannot delete table. It is referenced in reservations."}), 409

        # Delete the table if not referenced
        cursor.execute("DELETE FROM Tables WHERE table_id = %s", (table_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Table deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
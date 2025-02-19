from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql
from datetime import timedelta
from flask_mysqldb import MySQLdb


# Blueprint for reservations
reservations_bp = Blueprint('reservations', __name__)

# Helper functions for role validation
def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

from MySQLdb.cursors import DictCursor

def check_table_capacity(table_id, person_count):
    try:
        cursor = mysql.connection.cursor(DictCursor)  # Use DictCursor here
        print(table_id)
        cursor.execute("SELECT capacity FROM Tables WHERE table_id = %s", (table_id,))
        table = cursor.fetchone()
        cursor.close()
        print(table)
        if not table:
            return False, "Table does not exist."
        if int(person_count) > int(table['capacity']):
            return False, f"Table capacity is insufficient. Available capacity: {table['capacity']}"
        return True, None
    except Exception as e:
        return False, f"Database error: {str(e)}"

# POST /api/reservations - Add a new reservation
@reservations_bp.route('/add', methods=['POST'])
@jwt_required()
def add_reservation():
    current_user = get_jwt_identity()

    # Only admin can create reservations
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data or 'customer_id' not in data or 'table_id' not in data or 'reservation_date' not in data or 'person_count' not in data or 'reservation_time' not in data:
        return jsonify({"msg": "Missing required fields"}), 422

    customer_id = data['customer_id']
    table_id = data['table_id']
    reservation_date = data['reservation_date']
    reservation_time = data['reservation_time']
    person_count = data['person_count']
    if 'status' in data:
        status = data['status']
    else:
        status = "Pending"
    # Check table capacity
    valid, error = check_table_capacity(table_id, person_count)
    if not valid:
        return jsonify({"msg": error}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Reservations (customer_id, table_id, reservation_date,reservation_time, status, person_count) VALUES (%s, %s, %s, %s, %s, %s)",
            (customer_id, table_id, reservation_date,reservation_time, status, person_count)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Reservation added successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/reservations - Fetch all reservations
@reservations_bp.route('', methods=['GET'])
@jwt_required()
def get_reservations():
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        # Use DictCursor to fetch rows as dictionaries
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Reservations")
        reservations = cursor.fetchall()
        cursor.close()

        # Example handling of potential non-JSON-serializable fields
        for reservation in reservations:
            for key, value in reservation.items():
                if isinstance(value, timedelta):
                    reservation[key] = str(value)  # Convert timedelta to string

        return jsonify(reservations), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/reservations/<id> - Fetch a specific reservation
@reservations_bp.route('/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        # Use DictCursor to fetch the reservation as a dictionary
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        reservation = cursor.fetchone()
        cursor.close()

        if not reservation:
            return jsonify({"msg": "Reservation not found"}), 404

        # Handle non-serializable data types (e.g., timedelta) if necessary
        for key, value in reservation.items():
            if isinstance(value, timedelta):
                reservation[key] = str(value)

        return jsonify(reservation), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

from flask_mysqldb import MySQLdb

# PUT /api/reservations/<id> - Update a reservation
@reservations_bp.route('/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def update_reservation(reservation_id):
    current_user = get_jwt_identity()

    # Only admin can update reservations
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data:
        return jsonify({"msg": "Request body is empty"}), 422

    # Use DictCursor for dictionary-based results
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    

    try:
        # Fetch existing reservation data
        cursor.execute("SELECT * FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            return jsonify({"msg": "Reservation not found"}), 404

        # Extract fields from the incoming data or use existing ones
        customer_id = data.get('customer_id', reservation['customer_id'])
        table_id = data.get('table_id', reservation['table_id'])
        reservation_date = data.get('reservation_date', reservation['reservation_date'])
        status = data.get('status', reservation['status'])
        person_count = data.get('person_count', reservation['person_count'])

        # Validate table capacity if table_id or person_count is updated
        if table_id != reservation['table_id'] or person_count != reservation['person_count']:
            valid, error = check_table_capacity(table_id, person_count)
            if not valid:
                return jsonify({"msg": error}), 400

        # Update the reservation
        cursor.execute(
            """
            UPDATE Reservations
            SET customer_id = %s, table_id = %s, reservation_date = %s, status = %s, person_count = %s
            WHERE reservation_id = %s
            """,
            (customer_id, table_id, reservation_date, status, person_count, reservation_id)
        )
        mysql.connection.commit()

        return jsonify({"msg": "Reservation updated successfully"}), 200

    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    finally:
        cursor.close()


# DELETE /api/reservations/<id> - Delete a reservation
@reservations_bp.route('/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(reservation_id):
    current_user = get_jwt_identity()

    # Only admin can delete reservations
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        cursor = mysql.connection.cursor()

        # Check if reservation exists
        cursor.execute("SELECT * FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        reservation = cursor.fetchone()
        if not reservation:
            return jsonify({"msg": "Reservation not found"}), 404

        cursor.execute("DELETE FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Reservation deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql
from MySQLdb.cursors import DictCursor

# Blueprint for customer operations
customer_bp = Blueprint('customer', __name__)

# Helper functions for role validation
def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']


# POST /api/customers - Add a new customer
@customer_bp.route('/add', methods=['POST'])
@jwt_required()
def add_customer():
    current_user = get_jwt_identity()

    # Only admin can create customers
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data or 'name' not in data or 'contact_details' not in data:
        return jsonify({"msg": "Missing required fields: name, contact_details"}), 422

    name = data['name']
    contact_details = data['contact_details']

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Customers (name, contact_details) VALUES (%s, %s)",
            (name, contact_details)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Customer added successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500


# GET /api/customers - Fetch all customers
@customer_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        # Use DictCursor to fetch rows as dictionaries
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Customers")
        customers = cursor.fetchall()
        cursor.close()

        return jsonify(customers), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500


# GET /api/customers/<id> - Fetch a specific customer
@customer_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        # Use DictCursor to fetch the customer as a dictionary
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()

        if not customer:
            return jsonify({"msg": "Customer not found"}), 404

        return jsonify(customer), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500


# PUT /api/customers/<id> - Update a customer
@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    current_user = get_jwt_identity()

    # Only admin can update customers
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data:
        return jsonify({"msg": "Request body is empty"}), 422

    # Validate required fields
    if 'name' not in data and 'contact_details' not in data:
        return jsonify({"msg": "Missing required fields: name or contact_details"}), 422

    try:
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch existing customer data
        cursor.execute("SELECT * FROM Customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            return jsonify({"msg": "Customer not found"}), 404

        # Extract fields from the incoming data or use existing ones
        name = data.get('name', customer['name'])
        contact_details = data.get('contact_details', customer['contact_details'])

        # Update customer
        cursor.execute(
            """
            UPDATE Customers
            SET name = %s, contact_details = %s
            WHERE customer_id = %s
            """,
            (name, contact_details, customer_id)
        )
        mysql.connection.commit()

        return jsonify({"msg": "Customer updated successfully"}), 200

    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    finally:
        cursor.close()


# DELETE /api/customers/<id> - Delete a customer
@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    current_user = get_jwt_identity()

    # Only admin can delete customers
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:

        # Check if the customer exists, if not return 404
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()

        if not customer:
            return jsonify({"msg": "Customer not found"}), 404

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Customers WHERE customer_id = %s", (customer_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Customer deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

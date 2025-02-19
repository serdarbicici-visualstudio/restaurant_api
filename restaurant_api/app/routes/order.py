from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql
from flask_mysqldb import MySQLdb

# Blueprint for orders
orders_bp = Blueprint('orders', __name__)

# Helper functions for role validation
def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

# POST /api/orders - Add a new order
@orders_bp.route('/add', methods=['POST'])
@jwt_required()
def add_order():
    current_user = get_jwt_identity()
    # Only admin can create orders
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data or 'reservation_id' not in data or 'total_amount' not in data:
        return jsonify({"msg": "Missing required fields"}), 422

    reservation_id = data['reservation_id']
    total_amount = data['total_amount']
    if 'order_status' in data:
        order_status = data['order_status']
    else:
        order_status = "Pending"

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Orders (reservation_id, total_amount, order_status) VALUES (%s, %s, %s)",
            (reservation_id, total_amount, order_status)
        )
        
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Order added successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/orders - Fetch all orders
@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        # Use DictCursor to fetch rows as dictionaries
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Orders")
        orders = cursor.fetchall()
        cursor.close()

        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/orders/<id> - Fetch a specific order
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        # Use DictCursor to fetch the order as a dictionary
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        cursor.close()

        if not order:
            return jsonify({"msg": "Order not found"}), 404

        return jsonify(order), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# PUT /api/orders/<id> - Update an order
@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    current_user = get_jwt_identity()

    # Only admin can update orders
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data:
        return jsonify({"msg": "Request body is empty"}), 422

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch existing order data
        cursor.execute("SELECT * FROM Orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({"msg": "Order not found"}), 404

        # Extract fields from the incoming data or use existing ones
        reservation_id = data.get('reservation_id', order['reservation_id'])
        total_amount = data.get('total_amount', order['total_amount'])
        order_status = data.get('order_status', order['order_status'])

        # Update the order
        cursor.execute(
            """
            UPDATE Orders
            SET reservation_id = %s, total_amount = %s, order_status = %s
            WHERE order_id = %s
            """,
            (reservation_id, total_amount, order_status, order_id)
        )
        mysql.connection.commit()

        return jsonify({"msg": "Order updated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()

# DELETE /api/orders/<id> - Delete an order
@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    current_user = get_jwt_identity()

    # Only admin can delete orders
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        # check if order exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({"msg": "Order not found"}), 404
        
        # delete the order
        cursor.execute("DELETE FROM Orders WHERE order_id = %s", (order_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"msg": "Order deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

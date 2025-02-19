from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql
from MySQLdb.cursors import DictCursor

# Blueprint for order items
order_items_bp = Blueprint('order_items', __name__)

# Helper functions for role validation
def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

# POST /api/order_items - Add a new order item
@order_items_bp.route('/add', methods=['POST'])
@jwt_required()
def add_order_item():
    current_user = get_jwt_identity()

    # Only admin can add order items
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data or 'order_id' not in data or 'dish_id' not in data or 'quantity' not in data:
        return jsonify({"msg": "Missing required fields"}), 422

    order_id = data['order_id']
    dish_id = data['dish_id']
    quantity = data['quantity']

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Order_Items (order_id, dish_id, quantity) VALUES (%s, %s, %s)",
            (order_id, dish_id, quantity)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Order item added successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/order_items - Fetch all order items
@order_items_bp.route('', methods=['GET'])
@jwt_required()
def get_order_items():
    current_user = get_jwt_identity()

    # Allow admin or users to fetch order items
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Order_Items")
        order_items = cursor.fetchall()
        cursor.close()
        return jsonify(order_items), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/order_items/<id> - Fetch a specific order item
@order_items_bp.route('/<int:order_item_id>', methods=['GET'])
@jwt_required()
def get_order_item(order_item_id):
    current_user = get_jwt_identity()

    # Allow admin or users to fetch a specific order item
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Order_Items WHERE order_item_id = %s", (order_item_id,))
        order_item = cursor.fetchone()
        cursor.close()

        if not order_item:
            return jsonify({"msg": "Order item not found"}), 404

        return jsonify(order_item), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# PUT /api/order_items/<id> - Update an order item
@order_items_bp.route('/<int:order_item_id>', methods=['PUT'])
@jwt_required()
def update_order_item(order_item_id):
    current_user = get_jwt_identity()

    # Only admin can update order items
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if not data:
        return jsonify({"msg": "Request body is empty"}), 422

    try:
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch existing order item
        cursor.execute("SELECT * FROM Order_Items WHERE order_item_id = %s", (order_item_id,))
        order_item = cursor.fetchone()

        if not order_item:
            return jsonify({"msg": "Order item not found"}), 404

        # Extract fields or use existing values
        order_id = data.get('order_id', order_item['order_id'])
        dish_id = data.get('dish_id', order_item['dish_id'])
        quantity = data.get('quantity', order_item['quantity'])

        # Update the order item
        cursor.execute(
            """
            UPDATE Order_Items
            SET order_id = %s, dish_id = %s, quantity = %s
            WHERE order_item_id = %s
            """,
            (order_id, dish_id, quantity, order_item_id)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Order item updated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# DELETE /api/order_items/<id> - Delete an order item
@order_items_bp.route('/<int:order_item_id>', methods=['DELETE'])
@jwt_required()
def delete_order_item(order_item_id):
    current_user = get_jwt_identity()

    # Only admin can delete order items
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        # check if order item exists
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Order_Items WHERE order_item_id = %s", (order_item_id,))
        order_item = cursor.fetchone()
        cursor.close()

        if not order_item:
            return jsonify({"msg": "Order item not found"}), 404
        
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Order_Items WHERE order_item_id = %s", (order_item_id,))
        mysql.connection.commit()
        cursor.close()

        
        return jsonify({"msg": "Order item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

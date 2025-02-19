from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql
from MySQLdb.cursors import DictCursor

payments_bp = Blueprint('payments', __name__)

# Helper function for role validation
def is_admin(user):
    return user.get('role') == 'admin'

# Helper function to check if user is admin or user
def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

# POST /api/payments - Add a New Payment
@payments_bp.route('/add', methods=['POST'])
@jwt_required()
def add_payment():
    current_user = get_jwt_identity()

    # Only admin can create payments
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if 'order_id' not in data or 'amount_paid' not in data or 'payment_method' not in data:
        return jsonify({"msg": "Missing required fields: order_id, amount_paid, payment_method"}), 422

    query = "INSERT INTO Payments (order_id, amount_paid, payment_method) VALUES (%s, %s, %s)"
    values = (data['order_id'], data['amount_paid'], data['payment_method'])

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Payment added successfully!"}), 201
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# GET /api/payments - Get All Payments
@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    current_user = get_jwt_identity()

    # Only admin can access all payments
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM Payments")
        payments = cursor.fetchall()
        cursor.close()
        return jsonify(payments), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# PUT /api/payments/<payment_id> - Update a Payment
@payments_bp.route('/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    current_user = get_jwt_identity()

    # Only admin can update payments
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    if 'amount_paid' not in data or 'payment_method' not in data:
        return jsonify({"msg": "Missing required fields: amount_paid, payment_method"}), 422

    query = "UPDATE Payments SET amount_paid = %s, payment_method = %s WHERE payment_id = %s"
    values = (data['amount_paid'], data['payment_method'], payment_id)

    try:
        # Check if payment exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Payments WHERE payment_id = %s", (payment_id,))
        payment = cursor.fetchone()
        if not payment:
            return jsonify({"msg": "Payment not found"}), 404
        
        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()


        return jsonify({"msg": "Payment updated successfully!"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

# DELETE /api/payments/<payment_id> - Delete a Payment
@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    current_user = get_jwt_identity()

    # Only admin can delete payments
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        # Check if payment exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Payments WHERE payment_id = %s", (payment_id,))
        payment = cursor.fetchone()
        if not payment:
            return jsonify({"msg": "Payment not found"}), 404
        
        cursor.execute("DELETE FROM Payments WHERE payment_id = %s", (payment_id,))
        mysql.connection.commit()      
        cursor.close()

        return jsonify({"msg": "Payment deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

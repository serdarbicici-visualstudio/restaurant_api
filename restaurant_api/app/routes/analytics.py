from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.db import mysql

# Create a Blueprint for analytics routes
analytics_bp = Blueprint('analytics', __name__)

# Route 1: Customer Spending
@analytics_bp.route('/customer_spending', methods=['GET'])
@jwt_required()
def customer_spending():
    try:
        query = """
        SELECT c.name AS customer_name, 
               SUM(o.total_amount) AS total_spent
        FROM Customers c
        JOIN Reservations r ON c.customer_id = r.customer_id
        JOIN Orders o ON r.reservation_id = o.reservation_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC;
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route 2: Popular Dishes
@analytics_bp.route('/popular_dishes', methods=['GET'])
@jwt_required()
def popular_dishes():
    try:
        query = """
        SELECT m.dish_name, 
               COUNT(oi.dish_id) AS total_orders
        FROM Menu m
        JOIN Order_Items oi ON m.dish_id = oi.dish_id
        GROUP BY m.dish_id
        ORDER BY total_orders DESC
        LIMIT 5;
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route 3: Get Pending Orders with Dish Names and Quantities
@analytics_bp.route('/pending_orders_details', methods=['GET'])
@jwt_required()
def pending_orders_details():
    try:
        # SQL Query to get pending orders with dish names and quantities
        query = """
        SELECT 
            o.order_id,
            m.dish_name,
            oi.quantity
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Menu m ON oi.dish_id = m.dish_id
        WHERE o.order_status = 'Pending'
        ORDER BY o.order_id;
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        # Return result
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Customers Who Spent Above Average
@analytics_bp.route('/above_average_spenders', methods=['GET'])
@jwt_required()
def above_average_spenders():
    try:
        query = """
        SELECT c.name AS customer_name, 
               total_spent
        FROM (
            SELECT r.customer_id, 
                   SUM(o.total_amount) AS total_spent
            FROM Reservations r
            JOIN Orders o ON r.reservation_id = o.reservation_id
            GROUP BY r.customer_id
        ) AS spending
        JOIN Customers c ON c.customer_id = spending.customer_id
        WHERE spending.total_spent > (
            SELECT AVG(total_spent) 
            FROM (
                SELECT SUM(o.total_amount) AS total_spent
                FROM Reservations r
                JOIN Orders o ON r.reservation_id = o.reservation_id
                GROUP BY r.customer_id
            ) AS avg_spending
        );
        """
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
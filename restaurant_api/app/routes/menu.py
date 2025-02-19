from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql

# -------------------- MENU ENDPOINTS --------------------
menu_bp = Blueprint('menu', __name__)

def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

# Add a dish
@menu_bp.route('/add', methods=['POST'])
@jwt_required()
def add_dish():
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({'msg': 'Unauthorized. Admin privileges required.'}), 403

    data = request.get_json()
    if not data or 'dish_name' not in data or 'category' not in data or 'price' not in data:
        return jsonify({'msg': 'Missing required fields: dish_name, category, price'}), 422

    try:
        query = "INSERT INTO Menu (dish_name, category, price) VALUES (%s, %s, %s)"
        values = (data['dish_name'], data['category'], data['price'])
        cursor = mysql.connection.cursor()
        cursor.execute(query, values)
        mysql.connection.commit()
        return jsonify({'msg': 'Dish added successfully!'}), 201
    except Exception as e:
        return jsonify({'msg': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()


# Get a specific dish by name
@menu_bp.route('/<string:dish_name>', methods=['GET'])
@jwt_required()
def get_dish(dish_name):
    current_user = get_jwt_identity()
    if not is_admin_or_user(current_user):
        return jsonify({'msg': 'Unauthorized. Admin or customer privileges required.'}), 403

    try:
        query = "SELECT * FROM Menu WHERE dish_name = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (dish_name,))
        dish = cursor.fetchone()
        if not dish:
            return jsonify({'msg': 'Dish not found.'}), 404
        return jsonify({'dish': dish}), 200
    except Exception as e:
        return jsonify({'msg': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()


# Get all menu items
@menu_bp.route('', methods=['GET'])
@jwt_required()
def get_menu():
    current_user = get_jwt_identity()
    if not is_admin_or_user(current_user):
        return jsonify({'msg': 'Unauthorized. Admin or customer privileges required.'}), 403

    try:
        query = "SELECT * FROM Menu"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        menu = cursor.fetchall()
        return jsonify({'menu': menu}), 200
    except Exception as e:
        return jsonify({'msg': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()


# Delete a dish
@menu_bp.route('/<int:dish_id>', methods=['DELETE'])
@jwt_required()
def delete_dish(dish_id):
    current_user = get_jwt_identity()
    if is_admin(current_user):
        return jsonify({'msg': 'Unauthorized. Admin privileges required.'}), 403

    try:

        # check if the dish_id exists in the database, if not return an error
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Menu WHERE dish_id = %s", (dish_id,))
        dish = cursor.fetchone()
        cursor.close()

        if not dish:
            return jsonify({'msg': 'Dish not found.'}), 404
    

        query = "DELETE FROM Menu WHERE dish_id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (dish_id,))
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'msg': 'Dish not found.'}), 404
        return jsonify({'msg': 'Dish deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'msg': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()


# Update a dish
@menu_bp.route('/<int:dish_id>', methods=['PUT'])
@jwt_required()
def update_dish(dish_id):
    current_user = get_jwt_identity()
    if not is_admin(current_user):
        return jsonify({'msg': 'Unauthorized. Admin privileges required.'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'msg': 'Request body is empty.'}), 422

    # if data is empty, return an error
    if 'dish_name' not in data and 'category' not in data and 'price' not in data:
        return jsonify({'msg': 'Missing required fields: dish_name, category, price'}), 422

    if not isinstance(data['price'], (int, float)) or data['price'] < 0:
        return jsonify({'msg': 'Price must be a non-negative number.'}), 422
    
    # check if the dish_id exists in the database, if not return an error
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Menu WHERE dish_id = %s", (dish_id,))
    dish = cursor.fetchone()
    cursor.close()

    if not dish:
        return jsonify({'msg': 'Dish not found.'}), 404
    

    dish_name, category, price = None, None, None

    if 'dish_name' in data:
        dish_name = data['dish_name']
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT dish_name FROM Menu WHERE dish_id = %s", (dish_id,))
        dish_name = cursor.fetchone()[0]
        cursor.close()
    if 'category' in data:
        category = data['category']
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT category FROM Menu WHERE dish_id = %s", (dish_id,))
        category = cursor.fetchone()[0]
        cursor.close()
    if 'price' in data:
        price = data['price']
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT price FROM Menu WHERE dish_id = %s", (dish_id,))
        price = cursor.fetchone()[0]
        cursor.close()   
        

    try:
        cursor = mysql.connection.cursor()

        query = "UPDATE Menu SET dish_name = %s, category = %s, price = %s WHERE dish_id = %s"
        values = (dish_name, category, price, dish_id)
        cursor.execute(query, values)

        mysql.connection.commit()
        return jsonify({'msg': 'Dish updated successfully!'}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'msg': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.db import mysql

# Create a Blueprint for 'staff'
staff_bp = Blueprint('staff', __name__)

# Helper function to validate role-based access
def is_admin(user):
    return user.get('role') == 'admin'

def is_admin_or_user(user):
    return user.get('role') in ['admin', 'user']

# POST /api/staff - Add a new staff member
@staff_bp.route('/add', methods=['POST'])
@jwt_required()
def add_staff():
    current_user = get_jwt_identity()

    # Check admin privileges
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    # Validate required fields
    if not data or 'name' not in data or 'role' not in data or 'shift' not in data:
        return jsonify({"msg": "Missing required fields: name, role, shift"}), 422

    name = data['name']
    role = data['role']
    shift = data['shift']

    # Validate input (e.g., ENUM constraints)
    valid_roles = ['Waiter', 'Chef', 'Manager', 'Host']
    valid_shifts = ['Morning', 'Afternoon', 'Evening']
    if role not in valid_roles:
        return jsonify({"msg": f"Invalid role. Allowed values: {', '.join(valid_roles)}"}), 422
    if shift not in valid_shifts:
        return jsonify({"msg": f"Invalid shift. Allowed values: {', '.join(valid_shifts)}"}), 422

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Staff (name, role, shift) VALUES (%s, %s, %s)",
            (name, role, shift)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Staff member added successfully"}), 201
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


# GET /api/staff - Fetch all staff members
@staff_bp.route('', methods=['GET'])
@jwt_required()
def get_all_staff():
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Staff")
        staff = cursor.fetchall()
        cursor.close()

        return jsonify(staff), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


# GET /api/staff/<id> - Fetch a specific staff member by ID
@staff_bp.route('/<int:staff_id>', methods=['GET'])
@jwt_required()
def get_staff_by_id(staff_id):
    current_user = get_jwt_identity()

    # Allow access only to admin or user roles
    if not is_admin_or_user(current_user):
        return jsonify({"msg": "Unauthorized. Admin or user privileges required."}), 403

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Staff WHERE staff_id = %s", (staff_id,))
        staff_member = cursor.fetchone()
        cursor.close()

        if not staff_member:
            return jsonify({"msg": "Staff member not found"}), 404

        return jsonify(staff_member), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


# PUT /api/staff/<id> - Update details for a staff member
@staff_bp.route('/<int:staff_id>', methods=['PUT'])
@jwt_required()
def update_staff(staff_id):
    current_user = get_jwt_identity()

    # Only admin can update staff
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    data = request.get_json()

    # try getting the values from the request data if they exist, if not, get them from the database
    name, role, shift = None, None, None

    if 'name' in data:
        name = data['name']
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name FROM Staff WHERE staff_id = %s", (staff_id,))
        name = cursor.fetchone()[0]
        cursor.close()

    if 'role' in data:
        role = data['role']
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT role FROM Staff WHERE staff_id = %s", (staff_id,))
        role = cursor.fetchone()[0]
        cursor.close()

    if 'shift' in data:
        shift = data['shift']
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT shift FROM Staff WHERE staff_id = %s", (staff_id,))
        shift = cursor.fetchone()[0]
        cursor

    # Validate role and shift if provided
    valid_roles = ['Waiter', 'Chef', 'Manager', 'Host']
    valid_shifts = ['Morning', 'Afternoon', 'Evening']
    if role and role not in valid_roles:
        return jsonify({"msg": f"Invalid role. Allowed values: {', '.join(valid_roles)}"}), 422
    if shift and shift not in valid_shifts:
        return jsonify({"msg": f"Invalid shift. Allowed values: {', '.join(valid_shifts)}"}), 422

    try:
        cursor = mysql.connection.cursor()

        # Update query with dynamic fields
        query = "UPDATE Staff SET "
        params = []
        if name:
            query += "name = %s, "
            params.append(name)
        if role:
            query += "role = %s, "
            params.append(role)
        if shift:
            query += "shift = %s, "
            params.append(shift)
        query = query.rstrip(', ') + " WHERE staff_id = %s"
        params.append(staff_id)

        cursor.execute(query, params)
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Staff member updated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


# DELETE /api/staff/<id> - Delete a staff member
@staff_bp.route('/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    current_user = get_jwt_identity()

    # Only admin can delete staff
    if not is_admin(current_user):
        return jsonify({"msg": "Unauthorized. Admin privileges required."}), 403

    try:
        # chek if the staff member exists in the database if not return a 404 error, else delete the staff member
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Staff WHERE staff_id = %s", (staff_id,))
        staff_member = cursor.fetchone()
        cursor.close()

        if not staff_member:
            return jsonify({"msg": "Staff member not found"}), 404
        
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Staff WHERE staff_id = %s", (staff_id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Staff member deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    

import logging
from flask import request

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mysqldb import MySQL
from app.routes.tables import tables_bp
from app.services.auth_service import auth_bp
from app.routes.menu import menu_bp
from app.routes.reservations import reservations_bp
from app.routes.staff import staff_bp
from app.routes.customers import customer_bp
from app.routes.payments import payments_bp
from app.routes.order_item import order_items_bp
from app.routes.order import orders_bp
from app.routes.analytics import analytics_bp

from app.models.db import mysql

from dotenv import load_dotenv
import os
# app/_init_.py

def create_app():
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = 'restaurant_db'

    # Initialize extensions
    mysql.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(tables_bp, url_prefix='/api/tables')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(order_items_bp, url_prefix='/api/order_items')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    return app
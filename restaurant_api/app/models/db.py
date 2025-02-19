from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

mysql = MySQL()



def init_db(app):

    load_dotenv()

    app.config['MYSQL_HOST'] = app.config['MYSQL_HOST']
    app.config['MYSQL_USER'] = app.config['MYSQL_USER']
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = app.config['MYSQL_DB']

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')

    mysql.init_app(app)
    return mysql

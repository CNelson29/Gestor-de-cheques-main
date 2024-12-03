from flask_mysqldb import MySQL
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib


mysql = MySQL()

def init_db(app):
    mysql.init_app(app)

def query_db(query, args=(), one=False):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Usamos DictCursor para obtener resultados como diccionarios
    cur.execute(query, args)
    r = cur.fetchall()
    cur.close()
    return (r[0] if r else None) if one else r

def execute_db(query, args=()):
    cur = mysql.connection.cursor()
    try:
        cur.execute(query, args)
        mysql.connection.commit()
    except Exception as e:
        print(f"Error ejecutando la consulta: {e}")
        mysql.connection.rollback()
        raise e  # O manejar el error como prefieras
    finally:
        cur.close()

class User(UserMixin):
    def __init__(self, id, name, email, password_hash, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)

def get_user(email):
    user_data = query_db('SELECT * FROM usuarios WHERE email = %s', (email,), one=True)
    if user_data:
        return User(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            is_admin=user_data['is_admin']
        )
    return None

def fetch_all(query, params=None):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Usamos DictCursor para obtener resultados como diccionarios
    try:
        cur.execute(query, params)  # Ejecutamos la consulta con los parámetros proporcionados
        result = cur.fetchall()  # Obtenemos todos los resultados
    except Exception as e:
        print(f"Error ejecutando la consulta: {e}")
        result = None
    finally:
        cur.close()  # Cerramos el cursor después de ejecutar la consulta

    return result

# Ejemplo de uso en una ruta para listar los cheques

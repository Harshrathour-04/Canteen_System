import mysql.connector
import os
import sys

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",     
        password="9541658940",     
        database="canteen_db" 
    )

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
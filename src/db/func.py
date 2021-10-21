import sqlite3
from sqlite3 import Error

def create_connection(d):
    try:
        conn = sqlite3.connect(d)
    except Error as e:
        print(e)
    # Catch keyboard interuppt
    return  conn
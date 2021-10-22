import sqlite3
from sqlite3 import Error

from . import sql_command
from util import CONFIG

def create_connection(d):
    try:
        conn = sqlite3.connect(d)
    except Error as e:
        print(e)
    # Catch keyboard interuppt
    return  conn

def init_db(conn):
    
    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_create_requests_table)
        cur.execute(sql_command.sql_create_machine_table)
        cur.execute(sql_command.sql_create_config_table)

        cur.execute(sql_command.sql_insert_config_table, (int(CONFIG['template_vm']['vm_id']), ))
        conn.commit()

    except Error as e:
        print(e)

def get_user_from_machine(conn, user_id):
    cur = conn.cursor()
    cur.execute(sql_command.sql_select_user_from_machine, (user_id,))
    data = cur.fetchone()
    return data

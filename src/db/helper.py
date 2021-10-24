import sqlite3
from sqlite3 import Error
import datetime

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
    print('init db')
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

def insert_request (conn, info):

    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_insert_requests_table, (info['requester_id'], info['requesters_name'], info['request_time'], info['os'], 'pending',))
        conn.commit()

    except Error as e:
        print(e)

def get_request(conn, requester_id):
    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_select_request, (requester_id,))
        data = cur.fetchone()
        return data
    except Error as e:
        print(e)

def update_request(conn, requester_id , status):
    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_update_status, (status, datetime.datetime.now() , requester_id, ))
        conn.commit()
    except Error as e:
        print(e)

def insert_machine(conn, data):
    try :
        cur = conn.cursor()
        # Fetch vm id
        cur.execute(sql_command.sql_select_config_table)
        
        next_vm_id = cur.fetchone()[0]

        cur.execute(sql_command.sql_insert_machine_table, ( next_vm_id ,  data[0] , data[1] ))

        conn.commit()
    except Error as e :
        print(e) # print for n

def get_vm_id(conn):
    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_select_config_table)
        data = cur.fetchone()
        return data
    except Error as e:
        print(e)

def increment_vm_id(conn):
    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_update_next_vm_id)
        conn.commit()
    except Error as e:
        print(e)

def delete_request(conn, requester_id ):
    try:
        cur = conn.cursor()
        print(type(requester_id))
        print(requester_id)
        cur.execute(sql_command.sql_delete_request, (requester_id,))
        conn.commit()
    except Error as e:
        print(e)
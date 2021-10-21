import db.sql_command as sql_command
from db.func import create_connection
from util import config_parser
from pathlib import Path


db_file = Path(__file__).parent.parent / f"res/{config_parser.CONFIG['db_name']}.db"
db_exists = db_file.is_file()


conn= create_connection(db_file)

if not db_exists:
    try:
        cur = conn.cursor()
        cur.execute(sql_command.sql_create_requests_table)
        cur.execute(sql_command.sql_create_machine_table)
        cur.execute(sql_command.sql_create_config_table)

        cur.execute(sql_command.sql_insert_config_table, (int(config_parser.CONFIG['proxmox']['vm_id']), ))
        conn.commit()

    except Error as e:
        print(e)

conn.close()
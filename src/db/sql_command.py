sql_create_requests_table = """CREATE TABLE  request (
                                requester_id int NOT NULL, 
                                requester_name text NOT NULL, 
                                os_type  NOT NULL, 
                                status text NOT NULL
                            ); """

sql_create_machine_table = """ CREATE TABLE machine (
                            vm_id text NOT NULL, 
                            owner_id int NOT NULL,
                            owner_name text NOT NULL
                            )
                            """

sql_create_config_table =  """CREATE TABLE vm_config (
                            next_vm_id int NOT NULL
                            )
                            """


sql_insert_requests_table = """INSERT INTO request (requester_id, requester_name , os_type, status) 
                            VALUES(?, ? ,?,?) """    

sql_insert_machine_table = """ INSERT INTO machine ( vm_id ,  owner_id , owner_name ) 
                            VALUES (?,?,?)  """     

sql_insert_config_table =  """INSERT INTO vm_config (next_vm_id)
                            VALUES (?) """          

sql_update_satus= """UPDATE request SET status=? 
                    WHERE requester_id=? """    

sql_update_next_vm_id = "UPDATE vm_config SET next_vm_id = next_vm_id + 1"

sql_select_config_table = "SELECT next_vm_id FROM vm_config WHERE rowid=1;"

sql_select_user_from_machine = "SELECT * FROM machine WHERE owner_id = ?"

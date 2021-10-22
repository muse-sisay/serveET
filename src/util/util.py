import ast
import re
from fabric import Connection
import time

from . import CONFIG

def string_to_dict(string):
    try :
        return ast.literal_eval(string)
    except Exception as e :
        print(e)

def get_login_url(host):
    
    connection = Connection(host=f"{CONFIG['template_vm']['user']}@{host}", connect_kwargs={"password": CONFIG['template_vm']['password']})
    connection.run('nohup tailscale up >/dev/null 2>&1 & ')
    
    time.sleep(5) # TODO find a way of runnng the first command in background
    url = connection.run('tailscale status | tail -1', hide=True).stdout
    return url

def string_format(s, *args):
    s = s.format(*args)
    s = re.sub(r"(\[|\]|\(|\)|\~|\>|\+|\-|\=|\||\{|\}|\.|\!)", r'\\\g<0>',  s )
    return s

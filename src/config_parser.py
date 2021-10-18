import configparser
from pathlib import Path

def get_proxmox_creds():

    config_file = Path(__file__).parent.parent.parent.joinpath("config.cfg")

    config = configparser.ConfigParser()
    config.read(str(config_file) )
    pve_host =  config['proxmox']['host']
    pve_user=  config['proxmox']['user']
    pve_password =  config['proxmox']['password']

    return  pve_host, pve_user , pve_password

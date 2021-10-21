from pathlib import Path
import yaml
import sys

def get_proxmox_creds():
    return CONFIG['proxmox']['host'] , CONFIG['proxmox']['user'], CONFIG['proxmox']['password']

def read_config ():
    with open(f"{Path(__file__).parent.parent}/config.yml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.exit(exc)
            

CONFIG = read_config()

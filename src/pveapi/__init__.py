from proxmoxer import ProxmoxAPI
from util import config_parser

proxmox_host , proxmox_user, proxmox_pass = config_parser.get_proxmox_creds()

proxmox = ProxmoxAPI(proxmox_host, user=proxmox_user,
                     password=proxmox_pass, verify_ssl=False)

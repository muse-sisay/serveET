from proxmoxer import ProxmoxAPI
from util import CONFIG, parser


proxomox_cred = CONFIG['proxmox']

proxmox = ProxmoxAPI(proxomox_cred['host'], user=proxomox_cred['user'],
                     password=proxomox_cred['password'], verify_ssl=False)

from proxmoxer import ProxmoxAPI
from util import CONFIG, parser


proxomox_cred = CONFIG['proxmox']

proxmox = ProxmoxAPI(proxomox_cred['host'], user=proxomox_cred['user'],
                    token_name=proxomox_cred['token']['name'],  
                    token_value=proxomox_cred['token']['value'], verify_ssl=False)

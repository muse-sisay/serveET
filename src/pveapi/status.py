from proxmoxer.core import ResourceException
from pprint import pprint

def network_status (proxmox , node, vmID):

    try :
        msg= proxmox.get(f"nodes/{node}/qemu/{vmID}/agent/network-get-interfaces")
        return {"msg" : msg, "success" : 1 }
    except ResourceException as e :
        return {"msg" : e  , "success" : 0 }

def get_local_ip(proxmox , node , vmID):

    msg = get_ip_address (proxmox , node, vmID)

    if msg['success'] == 1 :

        for nic in msg['msg']:
            if nic['if'] == "ens18" :
                return {'msg' : nic['ip'], "success" : 1 }
    else :
        return msg

def get_os_info(proxmox , node , vmID):
    try :
        msg= proxmox.get(f"nodes/{node}/qemu/{vmID}/agent/get-osinfo")
        return {"msg" : msg['result']['pretty-name'], "success" : 1 }
    except ResourceException as e :
        return {"msg" : e  , "success" : 0 }

def get_vmstat(proxmox , node , vmID):
    try :
        msg= proxmox.get(f"nodes/{node}/qemu/{vmID}/status/current")
        return {"msg" : msg, "success" : 1 }
    except ResourceException as e :
        return {"msg" : e  , "success" : 0 }

def get_ip_address(proxmox, node, vmID):

    try :
        msg = network_status (proxmox , node, vmID)

        if msg['success'] == 1 :
            
            nics = []
            for nic in msg['msg']['result']:
                
                if not nic['name'] == 'lo':
                    for ip in nic['ip-addresses'] :
                        if ip['ip-address-type'] == 'ipv4':
                            nics.append ({ "if" : nic['name'] , "ip" : ip['ip-address'] })
            return {"msg" :nics  , "success" : 1 }  
        else :
            return msg
    except ResourceException as e :
        return {"msg" : e  , "success" : 0 }

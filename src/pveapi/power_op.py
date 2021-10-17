from proxmoxer.core import ResourceException


def get_status (proxmox , node, vmID):
    '''
    Get the status of running vm
    '''
    try :
        msg= proxmox.get(f"nodes/{node}/qemu/{vmID}/status/current")['status']
        return {"msg" : msg, "success" : 1 }
    except ResourceException as e :
        return {"msg" : e  , "success" : 0 }

def power_on(proxmox ,node, vmID):
    '''
    Power on vm
    POST /api2/json//nodes/{node}/qemu/{vmid}/status/start
    '''
    status = get_status(proxmox, node, vmID)
    if status['success'] == 1 :
        if status['msg'] == "stopped" :
            msg= proxmox.post(f"nodes/{node}/qemu/{vmID}/status/start")
            return {"msg" : msg, "success" : 1 }
        else :
            return {"msg": "VM already running", "success" : 0 }
    else :
        return {"msg" : status['msg'], "success": 0}

def power_off(proxmox ,node, vmID) :
    '''
    Power off vm
    POST /api2/json//nodes/{node}/qemu/{vmid}/status/shutdown
    '''
    status = get_status(proxmox, node, vmID)
    if status['success'] == 1 :
        if status['msg'] == "running" :
            msg= proxmox.post(f"nodes/{node}/qemu/{vmID}/status/shutdown")
            return {"msg" : msg, "success" : 1 }
        else :
            return {"msg": "VM already running", "success" : 0 }
    else :
        return {"msg" : status['msg'], "success": 0}

def reboot(proxmox ,node, vmID):
    '''
    Reboot vm
    POST /api2/json//nodes/{node}/qemu/{vmid}/status/reboot
    '''
    status = get_status(proxmox, node, vmID)
    if status['success'] == 1 :
        if status['msg'] == "running" :
            msg= proxmox.post(f"nodes/{node}/qemu/{vmID}/status/reboot")
            return {"msg" : msg, "success" : 1 }
        else :
            return {"msg": "VM already running", "success" : 0 }
    else :
        return {"msg" : status['msg'], "success": 0}
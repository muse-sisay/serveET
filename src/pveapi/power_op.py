from proxmoxer.core import ResourceException


def get_status (node, vmID):
    '''
    Get the status of running vm
    '''
    try :
        msg= node.qemu(vmID).status.current.get()['status']
        return {"msg" : msg, "success" : 1 }
    except ResourceException as e :
        return {"msg" : e  , "success" : 0 }

def power_on(node, vmID):
    '''
    Power on vm
    '''
    status = get_status(node, vmID)
    if get_status(node, vmID) == "running" :
        msg = node.qemu(vmID).status.start.post()
        return {"msg" : msg, "success" : 1 }
    else :
        return {"success" : 0 }

def power_off(node, vmID) :
    '''
    Power off vm
    '''
    if get_status(node, vmID) == "running" :
        msg = node.qemu(vmID).status.stop.post()
        return {"msg" : msg, "success" : 1 }
    else :
        return {"success" : 0 }

def reboot( node, vmID):
    '''
    Reboot vm
    '''
    if get_status(node, vmID) == "running" :
        msg = node.qemu(vmID).status.reboot.post()
        return {"msg" : msg, "success" : 1 }
    else :
        return {"success" : 0 }

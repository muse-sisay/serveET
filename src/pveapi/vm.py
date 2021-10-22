from proxmoxer.core import ResourceException

def clone_vm (proxmox, node, TMPL_ID, new_vm):
    '''
    Clone a vm
    POST /api2/json//nodes/{node}/qemu/{vmid}/clone
    '''
    try :
        n = proxmox.nodes(node)
        msg= n.qemu(TMPL_ID).clone.post(**new_vm)
        return {"msg" : msg , "success" : 1 }
    except ResourceException as e:
        return {"msg" : e , "success" : 0 }

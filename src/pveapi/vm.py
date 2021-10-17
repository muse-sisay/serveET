from proxmoxer.core import ResourceException

def clone_vm (node, TMPL_ID, new_vm):
    try :
        msg= node.qemu(TMPL_ID).clone.post(**new_vm)
        return {"msg" : msg , "success" : 1 }
    except ResourceException as e:
        return {"msg" : e , "success" : 0 }

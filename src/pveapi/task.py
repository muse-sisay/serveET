import time

def status (proxmox , node, upid) :
    """
    GET /api2/json//nodes/{node}/tasks/{upid}/status
    """
    msg= proxmox.get(f"nodes/{node}/tasks/{upid}/status/")['status']
    return msg

def notify_when_done(proxmox , node, upid):
    t = proxmox.get(f"nodes/{node}/tasks/{upid}/status/")['status']
    while t == "running" :
        time.sleep(1)
        t=proxmox.get(f"nodes/{node}/tasks/{upid}/status/")['status']
#!/usr/bin/env python3
# Disclaimer: This product is not supported by VMware.
# License: https://github.com/vmware/pyvmomi-community-samples/blob/master/LICENSE
# Source code = https://github.com/dixonly/samples.git
'''
   This script will connect to vCenter and retrieve all the VM instance UUIDs
   that matches the input filter.  This will output a JSON payload that can 
   be used with NSX-T's API: POST /api/v1/migration/cmgroup?action=pre_migrate
'''
from pyVim import connect
from pyVmomi import vim
from pyVmomi import vmodl
#from tools import tasks
import atexit
import argparse
import ssl
import json
import random

def getObjects(inv, vimtype, names, glob=False, ignorecase=False, verbose=False):
    """
    Get object by name from vcenter inventory
    """

    container = inv.viewManager.CreateContainerView(inv.rootFolder, vimtype, True)
    found=[]
    for i in container.view:
        try:
            for n in names:
                if ignorecase:
                    inn=n.lower()
                    frm=i.name.lower()
                else:
                    inn = n
                    frm = i.name
                    
                if glob and inn in frm:
                    found.append(i)
                elif inn == frm:
                    found.append(i)
                    if len(found) == len(names):
                        return found
                
        except vmodl.fault.ManagedObjectNotFound:
            #print("VM %s no longer exist")
            # This is if object was deleted after container view was created
            pass
    return found

def getVMUUID(password, sourcevc, user, name, group=False):
    ignorecase = True
    if hasattr(ssl, 'SSLContext'):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode=ssl.CERT_NONE
        si = connect.SmartConnect(host=sourcevc, user=user, pwd=password, sslContext=context)
    else:
        si = connect.SmartConnect(host=sourcevc, user=user, pwd=password)

    if not si:
        print("Could not connect to vcenter: %s " %sourcevc)
        return -1
    else:
        #print("Connect to vcenter: %s" %args.sourcevc)
        atexit.register(connect.Disconnect, si)

    vms = getObjects(inv = si.RetrieveContent(),
                     vimtype=[vim.VirtualMachine],
                     ignorecase=ignorecase,
                     names=name)
    data={}
    data['vm_instance_ids'] = []
    if group:
        data['group_id'] = group
    else:
        data['group_id'] = random.randint(1,10000)
    for i in vms:
        data['vm_instance_ids'].append(i.summary.config.instanceUuid)
    #print(json.dumps(data, indent=4))
    return data
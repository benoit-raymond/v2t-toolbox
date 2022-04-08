#!/usr/bin/env python3
# Disclaimer: This product is not supported by VMware.
# License: https://github.com/vmware/pyvmomi-community-samples/blob/master/LICENSE
# Source code = https://github.com/dixonly/samples.git
from pyVim import connect
from pyVmomi import vim
from pyVmomi import vmodl
#from tools import tasks
import atexit
import argparse
import subprocess
import ssl
import OpenSSL

def getObject(inv, vimtype, name, verbose=False):
    """
    Get object by name from vcenter inventory
    """

    obj = None
    container = inv.viewManager.CreateContainerView(inv.rootFolder, vimtype, True)
    #print (str(container.view))
    for i in container.view:
        try:
            if verbose:
                print("Checking %s %s against reference %s" %(i.name, i._moId, name))
            if i.name == name:
                obj = i
                break
        except vmodl.fault.ManagedObjectNotFound:
            #print("VM %s no longer exist")
            # This is if object was deleted after container view was created
            pass
    return obj

def setupNetworks(vm, host, networks, vifs=None, autovif=False):
    # this requires vsphere 7 API
    nics = []
    keys = []
    vmId = vm.config.instanceUuid
    for d in vm.config.hardware.device:
        if isinstance(d, vim.vm.device.VirtualEthernetCard):
            nics.append(d)
            keys.append(d.key)


    if len(nics) > len(networks):
        print("not enough networks for %d nics on vm" %len(nics))
        return None

    if vifs and len(vifs) != len(nics):
        print("Number of VIFs must match number of vNICS")
        return None

    netdevs = []
    for i in range(0,len(nics)):
        v = nics[i]
        n = networks[i]
        if isinstance(n, vim.OpaqueNetwork):
            # Is the source opaque net same as destination?
            opaque=False
            if isinstance(v.backing, vim.vm.device.VirtualEthernetCard.OpaqueNetworkBackingInfo):
                if v.backing.opaqueNetworkId == n.summary.opaqueNetworkId:
                    opaque=True
                    originalLs=v.backing.opaqueNetworkId

            v.backing = vim.vm.device.VirtualEthernetCard.OpaqueNetworkBackingInfo()
            v.backing.opaqueNetworkId = n.summary.opaqueNetworkId
            v.backing.opaqueNetworkType = n.summary.opaqueNetworkType

            print("Migrating VM %s NIC %d to destination network %s.." %(vm.name, i, v.backing.opaqueNetworkId))
            if vifs:
                v.externalId = vifs[i]
                print("...with vif %s" %v.externalId)
            elif autovif:
                v.externalId = "%s:%s" % (vmId, keys[i])
                
                
                
        elif isinstance(n, vim.DistributedVirtualPortgroup):
            # create dvpg handling
            vdsPgConn = vim.dvs.PortConnection()
            vdsPgConn.portgroupKey = n.key
            vdsPgConn.switchUuid = n.config.distributedVirtualSwitch.uuid
            v.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            v.backing.port = vdsPgConn
            print("Migrating VM %s NIC %d to destination dvpg %s on switch %s...." %(vm.name, i, vdsPgConn.portgroupKey, vdsPgConn.switchUuid))
            if vifs:
                v.externalId = vifs[i]
                print("...with vif %s" %v.externalId)
            elif autovif:
                v.externalId = "%s:%s" %(vmId, keys[i])

        else:
            v.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            v.backing.network = n
            v.backing.deviceName = n.name

        virdev = vim.vm.device.VirtualDeviceSpec()
        virdev.device = v
        virdev.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        netdevs.append(virdev)
    return netdevs

def do_vmotion(args_password, args_sourcevc, args_user, args_cluster, args_datastore, args_network, args_name, args_vifs = None, args_autovif = True, args_destvc = None, args_server = None):
    #print("This script is not supported by VMware.  Use at your own risk")
    password = args_password
    if hasattr(ssl, 'SSLContext'):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode=ssl.CERT_NONE
        si = connect.SmartConnect(host=args_sourcevc, user=args_user, pwd=password, sslContext=context)
    else:
        si = connect.SmartConnect(host=args_sourcevc, user=args_user, pwd=password)

    if not si:
        print("Could not connect to source vcenter: %s " %args_sourcevc)
        return -1
    else:
        print("Connect to vcenter: %s" %args_sourcevc)
        atexit.register(connect.Disconnect, si)

    if not args_destvc or args_sourcevc == args_destvc:
        di = si
    else:
        if hasattr(ssl, 'SSLContext'):
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode=ssl.CERT_NONE
            di = connect.SmartConnect(host=args_destvc, user=args_user, pwd=password, sslContext=context)
        else:
            di = connect.SmartConnect(host=args_destvc, user=args_user, pwd=password)
        if not di:
            print("Could not connect to destination vcenter: %s " %args_destvc)
            return -1
        else:
            print("Connect to vcenter: %s" %args_destvc)
            atexit.register(connect.Disconnect, di)

    
    sinv = si.RetrieveContent()
    sdc = sinv.rootFolder.childEntity[0]

    if args_destvc:
        dinv = di.RetrieveContent()
        ddc = dinv.rootFolder.childEntity[0]
    else:
        dinv = sinv
        ddc = sdc
        
    relocSpec = vim.vm.RelocateSpec()
    #print(sinv)
    #print(dinv)
    if sinv != dinv:
        if not args_server and not args_cluster and not args_datastore and not args_network:
            print("XV Vmotion requires host, cluster, datastore, and network")
            return -1

        cert = ssl.get_server_certificate((args_destvc, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        thumbprint = x509.digest("SHA1").decode('utf-8')
        
        up = vim.ServiceLocator.NamePassword(username=args_user, password=password)
        sl = vim.ServiceLocator(credential=up,
                                instanceUuid=dinv.about.instanceUuid,
                                url="https://%s" % args_destvc,
                                sslThumbprint=thumbprint)
        relocSpec.service = sl

    vm = getObject(sinv, [vim.VirtualMachine], args_name, verbose=False)
    if not vm:
        print("VM %s not found" %args_name)
        return -1
    else:
        print("VM %s %s found" % (vm.name, vm._moId)) 

    host=None
    if args_server:
        host = getObject(dinv, [vim.HostSystem], args_server)
        if not host:
            print("Host %s not found" %args_server)
            return -1
        else:
            print("Destination host %s found." % host.name)
                

    cluster=None
    if  args_cluster:
        cluster = getObject(dinv, [vim.ClusterComputeResource], args_cluster)
        if not cluster:
            print("Cluster %s not found" % args_cluster)
            return -1
        else:
            print("Destination cluster %s found, checking for DRS recommendation..." % cluster.name)
            if host and host.parent.resourcePool != cluster.resourcePool:
                print("Destination host %s and cluster %s are not resource pool"
                      %(host.name, cluster.name))
                return -1
            if not cluster.configuration.drsConfig.enabled and not host:
                print("Destination cluster %s is not DRS enabled, must specify host"
                      %cluster.name)
                return -1

            if not host and cluster.resourcePool == vm.resourcePool and sinv == dinv:
                print("Must provide host when migrating within same cluster")
                return -1

            if not host:
                if (sinv != dinv):
                    print("Cross VC migration must specify a host")
                    return -1
                rhost = cluster.RecommendHostsForVm(vm=vm, pool=cluster.resourcePool)
                if len(rhost) == 0:
                    print("No hosts found in cluster %s from DRS recommendation for migration"
                          %args_cluster)
                    return -1
                else:
                    print("DRS recommends %d hosts" %len(rhost))
                    host = rhost[0].host
    if host:
        relocSpec.host = host
        
    if cluster:
        relocSpec.pool = cluster.resourcePool
        
    datastore=None
    if args_datastore:
        datastore = getObject(dinv, [vim.Datastore], args_datastore)
        if not datastore:
            print("Datastore %s not found" % args_datastore)
            return -1
        else:
            print("Destination datastore  %s found." % datastore.name)
            relocSpec.datastore = datastore

    networks=[]
    for n in args_network:
        print("Searching VCenter for destination network(s)")
        network = getObject(dinv, [vim.Network], n, verbose=False)
        if not network:
            print("Network %s not found" % args_network)
            return -1 
        else:
            print("Destination network %s found." % network.name)
            networks.append(network)

    netSpec=setupNetworks(vm, host, networks, vifs=args_vifs, autovif=args_autovif)
    relocSpec.deviceChange = netSpec
    print("Initiating migration of VM %s" %args_name)
    vm.RelocateVM_Task(spec=relocSpec, priority=vim.VirtualMachine.MovePriority.highPriority)

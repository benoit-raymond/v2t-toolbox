# v2t-toolbox
NSX v2t Custom toolbox

- [Tool DFW Export version](#tool-dfw-export-version)
- [Tool NSX-v IPSet](#tool-nsx-v-ipset)
- [Tool get VMInstanceId](#tool-get-vminstanceid)
- [Tool vMotion VMs via API](#tool-vmotion-vms-via-api)

>**WARNING**: Experimental ! Use with *CAUTION*.

## Tool DFW Export version
- usage: `python3 v2t-dfw-export-version.py [--help] [--set|-s] [--input|-i </path/file.yml>]`
- objective: Check ESXi hosts DFW Export version is set to 1000. Default mode is check-only. Use --set option to set DFW export version to 1000. 
  - DFW export version = 1000 : Mandatory in case of Lift-Shift Migration using vMotion or In-Place using Maintenance Mode scenario.
- Prerequisistes:
  - Python3 (tested with Pyhton3.8+)
  - Python module: paramiko (SSH connection), yaml (import input file). Installation:`pip3 install xxx`
  - SSH access to ESXi hosts (same user for all hosts)
- Example yaml file `v2t-dfw-export-version.yml`:
  ```
  # hosts => list of ESXi hosts (IPs or FQDN). MANDATORY
  hosts:
    - 192.168.20.4
    - 192.168.20.3
  # user => username to connect to ESXi hosts. MANDATORY
  user: root
  ```

## Tool NSX-v IPSet
- usage: `python3 v2t-add-ipsets-v.py [--help] [--input|-i </path/file.yml>]`
- objective: Add NSX-v a new IPSet to each Security Group with the IP of effective members.
- Prerequisistes:
  - Python3 (tested with Pyhton3.8+)
  - Python module: requests (REST API), yaml (import input file). Installation:`pip3 install xxx`
  - HTTPS access to NSX-v Manager
- Example yaml file `v2t-add-ipsets-v.yml`:
  ```
  # nsx-v => FQDN or IP of NSX-v Manager. MANDATORY
  nsx-v: nsx-l-02a.corp.local
  # user => username to connect to NSX Manager API. MANDATORY
  user: admin
  # scope => NSX-v scope (default NSX-v = globalroot-0). MANDATORY
  scope: "globalroot-0"
  ```
  
## Tool get VMInstanceId
*Note: getVMInstanceId.py script based on this repo = https://github.com/dixonly/samples*

- usage: `usage: python3 main_getVMInstanceId.py [--help] [--input|-i </path/file.yml>]`
- objective: Run VMs GET VM UUIDs API call according to input file arguments. 
  - Input file can be multiple list of VMs to create several VM Group
- Prerequisistes:
  - Python3 (tested with Pyhton3.8+)
  - Python module: pyVim, pyYaml, pyVomi. Installation:`pip3 install xxx`
  - API access to vCenter
- Example yaml file `input_vm_uuid.yml`:
  ```
  # list of list of VM names to get uuids. MANDATORY
  vms:
    - 
      - APP02-P-VM01
      - APP01-WEB02
    - 
      - APP01-APP01
      - APP01-DB01
    - 
      - APP01-WEB01
  # src_vcenter => FQDN/IP Source vCenter. MANDATORY
  src_vcenter: vc-l-01a.corp.local
  # user => FQDN/IP user vCenter. MANDATORY
  user: administrator@vsphere.local
  ```
  
 ## Tool vMotion VMs via API
*Note: vmotion.py script based on this repo = https://github.com/dixonly/samples*

- usage: `usage: python3 main_vmotion.py [--help] [--input|-i </path/file.yml>]`
- objective: Run VMs vMotion API call according to input file arguments in v2t context (to connect VM to the correct destination logical port). 
  - You must run the Pre-Migrate API Call in NSX-T before running the script for this VM group
  - You must run the Post-Migrate API Call in NSX-T after running the script for this VM group, to apply tags etc.
- Prerequisistes:
  - Python3 (tested with Pyhton3.8+)
  - Python module: pyVim, pyYaml, pyVomi, pyOpenSSL. Installation:`pip3 install xxx`
  - API access to vCenter (Source and destination using same SSO user)
  - VM of the same group must have the same target ESXi cluster and Datastore
- Example yaml file `input.yml`:
  ```
  # list => list of VMs to move in this wave. MANDATORY
  list:
  # List of vm
  - vm:
    # networks => List of Destination network, must match number of VM vNICs in VM's HW ordering
    networks: [VLAN1, VLAN3]
    # name => VM name
    name: VM1
  - vm:
    networks: [VLAN2, VLAN3]
    name: VM2
  # src_vcenter => FQDN/IP Source vCenter. MANDATORY
  src_vcenter: vc-l-01a.corp.local
  # user => FQDN/IP user vCenter. MANDATORY
  user: administrator@vsphere.local
  # dst_vcenter => FQDN/IP Destination vCenter. MANDATORY
  dst_vcenter: vc-l-01a.corp.local
  # cluster => ESXi destination Cluster name. OPTION
  cluster: CLS01A
  # datastore => Datastore destination Cluster name. MANDATORY
  datastore: DS01
  ```

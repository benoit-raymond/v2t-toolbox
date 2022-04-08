# v2t-vmotion-complex
NSX v2t Custom toolbox - Lift-Shift Migrate workload VMs Complex Case

>**WARNING**: Experimental ! Use with *CAUTION*.

## Tool v2t lift-shift migration workload complex
- usage: `usage: python3 main_migrateAllSteps.py [--help] [--input|-i </path/file.yml>]`
- objective: Run all steps to migrate VMs using lift-shift ccomplex method using input file as argument 
- Prerequisistes:
  - Python3.5+ (tested with Pyhton3.8+)
  - Custom Module = `module_VMInstanceId.py`,`module_vmotion.py` 
  - Python module: pyVim, pyYaml, pyVomi, pyYaml, requests, urllib3, argparse, json 
    - Installation:`pip3 install xxx`
  - API access to vCenter (SRC + DST)
  - API access to NSX-T Manager
- Example yaml file `input.template.yml`:
  ```
  # nsxt => FQDN/IP NSX-T Mgr. MANDATORY
  nsxt: nsx-l-01a.corp.local
  # nsxt_user => user NSX-T Mgr. MANDATORY
  nsxt_user: admin
  # src_vcenter => FQDN/IP Source vCenter. MANDATORY
  src_vcenter: vc-l-01a.corp.local
  # vc_user => user vCenter. MANDATORY
  vc_user: administrator@vsphere.local
  # dst_vcenter => FQDN/IP Destination vCenter. OPTIONNAL
  #dst_vcenter: vc-l-01a.corp.local
  # cluster => ESXi destination Cluster name. MANDATORY
  cluster: Cluster-01a
  # datastore => Datastore destination name. MANDATORY
  datastore: datastore-01a
  # group-id => Name of VM group ID. OPTIONNAL
  #group-id: app001
  # vms => list of VM to migrate using vmotion script. MANDATORY (min length >= 1)
  vms:
    # vm => List 2 attributes: name and networks. MANDATORY
    - vm:
      # name => VM name. MANDATORY
      name: v2t-vm01
      # networks => VM list of network. MANDATORY (min length >= 1)
      networks: [LS_APP-V-01]
      # host: Destination ESXi host. OPTIONNAL (required if DRS not enabled)
      host: esx-01a.corp.local
    - vm:
      name: v2t-vm02
      networks: [LS_APP-V-01]
      host: esx-02a.corp.local
  ```

- Output script sample :
  <details>
    <summary>Click to expand code</summary>
  
    ```
    # python3 main_migrateAllSteps.py -i input.template.yml 
    vCenter user: administrator@vsphere.local
    NSX-T user: admin


    # STEP 1: GET VMs UUID ...
    {'vm_instance_ids': ['503bdc7c-164e-a7d9-a5ce-56667f7c9546', '503b6e21-1a98-7425-4e96-7366c031b2f2'], 'group_id': 3010}
    # STEP 2: NSX-T Pre-Migrate POST API call ...
    <Response [200]>
    # STEP 3: Migrate VMs using vmotion API script ...
    ## VM: v2t-vm01 => Strating vMotion process...
    Connect to vcenter: vc-l-01a.corp.local
    VM v2t-vm01 vm-39058 found
    Destination host esx-01a.corp.local found.
    Destination cluster Cluster-01a found, checking for DRS recommendation...
    Destination datastore  datastore-01a found.
    Searching VCenter for destination network(s)
    Destination network LS_APP-V-01 found.
    Migrating VM v2t-vm01 NIC 0 to destination dvpg dvportgroup-39083 on switch 50 3b 4f 2f ae 40 47 91-be 25 6e 32 b9 4e 92 27....
    Initiating migration of VM v2t-vm01


    Press enter to continue with next VM vMotion migration...

    ## VM: v2t-vm02 => Strating vMotion process...
    Connect to vcenter: vc-l-01a.corp.local
    VM v2t-vm02 vm-39076 found
    Destination host esx-02a.corp.local found.
    Destination cluster Cluster-01a found, checking for DRS recommendation...
    Destination datastore  datastore-01a found.
    Searching VCenter for destination network(s)
    Destination network LS_APP-V-01 found.
    Migrating VM v2t-vm02 NIC 0 to destination dvpg dvportgroup-39083 on switch 50 3b 4f 2f ae 40 47 91-be 25 6e 32 b9 4e 92 27....
    Initiating migration of VM v2t-vm02


    Press enter to continue with next VM vMotion migration...

    WAIT for all vMotion tasks to finish. THEN press enter to continue ...

    # STEP 4: NSX-T Post-Migrate POST API call ...
    <Response [200]>

    ```
      
  </details>
  
## Tool get VMInstanceId
**Sub-Folder = `vmInstanceId-script`**
      
*Note: getVMInstanceId.py script based on this repo = https://github.com/dixonly/samples*

- usage: `usage: python3 main_getVMInstanceId.py [--help] [--input|-i </path/file.yml>]`
- objective: Run VMs GET VM UUIDs API call according to input file arguments. 
  - Input file can be multiple list of VMs to create several VM Group
- Prerequisistes:
  - Python3.5+ (tested with Pyhton3.8+)
  - Python module: pyVim, pyYaml, pyVomi. Installation:`pip3 install xxx`
  - API access to vCenter
- Example yaml file `input.template.yml`:
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
- Output script sample :
  <details>
    <summary>Click to expand code</summary>
    
    ```
    # python3 main_getVMInstanceId.py -i input.template.yml 
    user: administrator@vsphere.local
    Password: 


    START GET VMs UUIDS ...

    # Starting GET UUID for VM(s): 'APP02-P-VM01 APP01-WEB02'
    ## DEBUG Command = python3 ./getVMInstanceId.py --sourcevc vc-l-01a.corp.local --user administrator@vsphere.local -p VMware1! --name APP02-P-VM01 APP01-WEB02
    {
        "vm_instance_ids": [
            "503b7ada-9ad9-2a05-e008-9bf648fb120b",
            "503b1250-8a87-e59c-8931-dacff07d90bf"
        ],
        "group_id": 8484
    }
    ## SUCCESS => GET uuid VMs 'APP02-P-VM01 APP01-WEB02'
    ```
    
  </details>
  
## Tool vMotion VMs via API
**Sub-Folder = `vmotion-script`**
  
*Note: vmotion.py script based on this repo = https://github.com/dixonly/samples*

- usage: `usage: python3 main_vmotion.py [--help] [--input|-i </path/file.yml>]`
- objective: Run VMs vMotion API call according to input file arguments in v2t context (to connect VM to the correct destination logical port). 
  - You must run the Pre-Migrate API Call in NSX-T before running the script for this VM group
  - You must run the Post-Migrate API Call in NSX-T after running the script for this VM group, to apply tags etc.
- Prerequisistes:
  - Python3.5+ (tested with Pyhton3.8+)
  - Python module: pyVim, pyYaml, pyVomi, pyOpenSSL. Installation:`pip3 install xxx`
  - API access to vCenter (Source and destination using same SSO user)
  - VM of the same group must have the same target ESXi cluster and Datastore
- Example yaml file `input.template.yml`:
  ```
  # list => list of VMs to move in this wave. MANDATORY
  list:
    # List of vm object
    - vm:
      # networks => List of Destination network, must match number of VM vNICs in VM's HW ordering. MANDATORY
      networks: [LS_APP-V-01]
      # name => VM name. MANDATORY
      name: v2t-vm01
      # host => destination ESXi Host name. OPTIONNAL
      host: esxi01a
    - vm:
      networks: [VLAN2, VLAN3]
      name: VM2
      host: esxi02a
  # src_vcenter => FQDN/IP Source vCenter. MANDATORY
  src_vcenter: vc-l-01a.corp.local
  # user => user vCenter. MANDATORY
  user: administrator@vsphere.local
  # dst_vcenter => FQDN/IP Destination vCenter. MANDATORY
  dst_vcenter: vc-l-01a.corp.local
  # cluster => destination ESXi Cluster name. MANDATORY
  cluster: CLS01A
  # datastore => Datastore destination name. MANDATORY
  datastore: DS01
  ```

- Output script sample :
  <details>
    <summary>Click to expand code</summary>
  
    ```
    python3 main_vmotion.py -i input.template.yml
    user: administrator@vsphere.local
    Password: 


    START VMs vMotion ...

    # Starting vMotion VM 'VM1'
    ## DEBUG Command = python3 vmotion.py --sourcevc vc-l-01a.corp.local --destvc vc-l-01a.corp.local --user administrator@vsphere.local --password VMware1! --cluster CLS01A --datastore DS01 --network LS_APP-V-01 --autovif --name v2t-vm01
    This script is not supported by VMware.  Use at your own risk
    Connect to vcenter: vc-l-01a.corp.local
    VM v2t-vm01 vm-39058 found
    Destination host esx-01a.corp.local found.
    Destination cluster Cluster-01a found, checking for DRS recommendation...
    Destination datastore  datastore-01a found.
    Searching VCenter for destination network(s)
    Destination network LS_APP-V-01 found.
    Migrating VM v2t-vm01 NIC 0 to destination dvpg dvportgroup-39083 on switch 50 3b 4f 2f ae 40 47 91-be 25 6e 32 b9 4e 92 27....
    Initiating migration of VM v2t-vm01

    ...
    ```
  </details>

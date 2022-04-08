# v2t-toolbox
NSX v2t Custom toolbox

- [Tool DFW Export version](#tool-dfw-export-version)
- [Tool NSX-v IPSet](#tool-nsx-v-ipset)
- [Tool v2t Migrate Workload Complex VMs via API](#tool-v2t-lift-shift-migration-workload-complex)
  - [Tool migrate workload VMs complex](v2t-vmotion-complex/README.md#Tool-v2t-lift-shift-migration-workload-complex)
  - [Tool get VMInstanceId](v2t-vmotion-complex/README.md#tool-get-vminstanceid)
  - [Tool vMotion VMs via API](v2t-vmotion-complex/README.md#tool-vmotion-vms-via-api)


>**WARNING**: Experimental ! Use with *CAUTION*.

## Tool DFW Export version
**Sub-Folder = `v2t-dfw-export-version`**
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
**Sub-Folder = `v2t-add-ipsets-v`**
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

## Tool v2t lift-shift migration workload complex
**Sub-Folder = `v2t-vmotion-complex`**

For usage detail go to: [v2t-vmotion-complex README file](v2t-vmotion-complex/README.md)

  - [Tool migrate workload VMs complex](v2t-vmotion-complex/README.md#Tool-v2t-lift-shift-migration-workload-complex)
  - [Tool get VMInstanceId](v2t-vmotion-complex/README.md#tool-get-vminstanceid)
  - [Tool vMotion VMs via API](v2t-vmotion-complex/README.md#tool-vmotion-vms-via-api)

# coding: utf-8
#!/usr/bin/env python3
# Disclaimer: This product is not supported by VMware.

# PRE-REQUISISTES
# Python3.5+ (Tested : 3.8.12)
# Python 3rd party module = pyYaml
# Python module : argparse, getpass, pyVomi, pyVim, pyYaml, os, requests, urllib3, json
# pip3 install pyyaml
# API access to vCenter (Source + Destination). Same user/password to login to vCenters


import yaml
import json
import argparse
from getpass import getpass
import os
import requests
import urllib3
# Custom import
import module_VMInstanceId
import module_vmotion


# Colored output Python3.6+
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# HELP ARGPARSE
def print_help():
    print ("usage: python3 main_migrateAllSteps.py [--help] [--input|-i </path/file.yml>]")
    print ("objective: Run all steps to migrate VMs using lift-shift ccomplex method using input file as argument.")
    print ("")
    print ("optional arguments:")
    print ("  --help, -h \t\t\t\tshow this help message and exit")
    print ("  --input, -i </path/file.yml> \t\tPath to YAML config file (Default=input.yml)")
    print ("")

def main():
    # Analyze CLI Args
    parser = argparse.ArgumentParser(description='main_migrateAllSteps', add_help=False)
    parser.add_argument('--help', '-h', required=False, action='store_true', help='Display command help')
    parser.add_argument('--input', '-i', required=False, help='Path to input yaml file (Default=input.yml)', default="input.yml")
    args = parser.parse_args()
    if  args.help == True:
        print_help()
        quit()

    # Read input  YAML file
    with open(args.input, 'r') as file:
        input_yaml = yaml.safe_load(file)

    # Set VARS
    vm_group_id = ""
    try:
        src_vcenter = input_yaml['src_vcenter']
        if 'dst_vcenter-id' in input_yaml:
            dst_vcenter = input_yaml['dst_vcenter']
        else:
            dst_vcenter = None
        cluster = input_yaml['cluster']
        datastore = input_yaml['datastore']
        vc_user = input_yaml['vc_user']
        nsxt = input_yaml['nsxt']
        nsxt_user = input_yaml['nsxt_user']
        if 'group-id' in input_yaml:
            vm_group_id = input_yaml['group-id']
        vm_list = input_yaml['vms']
        for vm in vm_list:
            if 'name' not in vm or 'networks' not in  vm:
                print(bcolors.FAIL+"ERROR loading YAML file, incorrect structure or missing parameters."+bcolors.ENDC)
                quit(-1)
    except yaml.YAMLError as exc:
        print(bcolors.FAIL+"ERROR loading YAML file, incorrect structure or missing parameters."+bcolors.ENDC)
        quit(-1)
    
    # Ask user password
    print ("vCenter user: "+vc_user)
    #vc_password = getpass()
    vc_password = "VMware1!"
    print ("NSX-T user: "+nsxt_user)
    #nsxt_password = getpass()
    nsxt_password = "VMware1!VMware1!"
    print ("\n")

    # Disable HTTPS Cert warnings
    urllib3.disable_warnings()

    # STEP 1 => GET VMs UUID
    print ("# STEP 1: GET VMs UUID ...")
    vms = []
    # Parse vm list and add all name to the list vms
    for vm in vm_list:
        vms.append(vm['name'])
    # retrieve the dict of vms uuid and group_id
    # var result = body for POST API call
    result = module_VMInstanceId.getVMUUID(vc_password, src_vcenter, vc_user, vms, vm_group_id)
    if result == "-1":
        print(bcolors.FAIL+"ERROR getting VMs UUID. Could not connect to vCenter"+bcolors.ENDC)
        quit(-1)
    print (str(result))
    #print (result['group_id'])
    vm_group_id = result['group_id']
    
    # STEP 2 => NSX-T "Pre-Migrate" POST API call
    print ("# STEP 2: NSX-T Pre-Migrate POST API call ...")
    url = 'https://'+nsxt+'/api/v1/migration/vmgroup?action=pre_migrate'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # var result = body for POST API call
    res = requests.post(url, data = json.dumps(result), verify=False, auth=(nsxt_user, nsxt_password), headers = headers)
    if res.status_code != 200:
        print(bcolors.FAIL+"ERROR API call: POST /api/v1/migration/vmgroup?action=pre_migrate.\nRETURN CODE = "+str(res.status_code)+"\nERROR= "+res.text+bcolors.ENDC)
        quit(-1)
    print(res)
    
    # STEP 3 => Migrate VM using vmotion API script
    print ("# STEP 3: Migrate VMs using vmotion API script ...")
    for vm in vm_list:
        name = vm['name']
        print ("## VM: "+name+" => Strating vMotion process...")
        #networks = ' '.join(vm['networks'])
        #command = 'python3 vmotion.py --sourcevc '+src_vcenter+' --destvc '+dst_vcenter+' --user '+vc_user+' --password '+vc_password+' --cluster '+cluster+ ' --datastore ' +datastore+' --network '+networks+' --autovif --name '+name
        #print(command)
        #os.system(command)
        
        ## alternate method
        # Call custom module vmotion
        networks = vm['networks']
        # If host is specified, set in vmotion args
        if 'host' in vm:
            args_server = vm['host']
        else:
            args_server = None
        res = module_vmotion.do_vmotion(vc_password, src_vcenter, vc_user, cluster, datastore, networks, name, args_vifs = None, args_autovif = True, args_destvc = dst_vcenter, args_server = args_server)
        if res == -1:
            print(bcolors.FAIL+"ERROR VM vMotion. VM name = "+name+bcolors.ENDC)
            quit(-1)
        # Ask press key to continue with next vm
        print("\n")
        print("Press enter to continue with next VM vMotion migration...")
        input()
    
    # WAIT all VMs to be migrated
    print(bcolors.WARNING+"WAIT for all vMotion tasks to finish. THEN press enter to continue ..."+bcolors.ENDC)
    input() 

    # STEP 4 => NSX-T "Post-Migrate" POST API call
    print ("# STEP 4: NSX-T Post-Migrate POST API call ...")
    url = 'https://'+nsxt+'/api/v1/migration/vmgroup?action=post_migrate'
    body = {"group_id": vm_group_id}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    res = requests.post(url, data = json.dumps(body), verify=False, auth=(nsxt_user, nsxt_password), headers = headers)
    if res.status_code != 200:
        print(bcolors.FAIL+"ERROR API call: POST /api/v1/migration/vmgroup?action=pre_migrate.\nRETURN CODE = "+str(res.status_code)+"\nERROR= "+res.text+bcolors.ENDC)
        quit(-1)
    print (res)

if __name__ == "__main__":
    main()
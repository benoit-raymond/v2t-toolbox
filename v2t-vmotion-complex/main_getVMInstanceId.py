# coding: utf-8
#!/usr/bin/env python3
# Disclaimer: This product is not supported by VMware.

# PRE-REQUISISTES
# Python3 (Tested : 3.8.12)
# Python 3rd party module = yaml
# Python module : argparse, getpass, os
# pip3 install pyyaml
# API access to vCenter (Source + Destination). Same user/password to login to vCenters


import yaml
import argparse
from getpass import getpass
import os

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
    print ("usage: python3 main_getVMInstanceId.py [--help] [--input|-i </path/file.yml>]")
    print ("objective: Run VMs GET VM UUIDs API call according to input file arguments.")
    print ("")
    print ("optional arguments:")
    print ("  --help, -h \t\t\t\tshow this help message and exit")
    print ("  --input, -i </path/file.yml> \t\tPath to YAML config file (Default=input_vm_uuid.yml)")
    print ("")

def main():
    # Analyze CLI Args
    parser = argparse.ArgumentParser(description='main_getVMInstanceId', add_help=False)
    parser.add_argument('--help', '-h', required=False, action='store_true', help='Display command help')
    parser.add_argument('--input', '-i', required=False, help='Path to input yaml file (Default=input_vm_uuid.yml)', default="input_vm_uuid.yml")
    args = parser.parse_args()
    if  args.help == True:
        print_help()
        quit()

    # Read input  YAML file
    with open(args.input, 'r') as file:
        input_yaml = yaml.safe_load(file)

    # Set VARS
    src_vcenter = input_yaml['src_vcenter']
    user = input_yaml['user']
    
    # Ask user password
    print ("user: "+user)
    password = getpass()
    print ("\n")

    # Parse the list of VMs in YAML input file (= list of VM to get uuid and place in same vmgroup) and get JSON body for API PRE-MIGRATE call
    print ("START GET VMs UUIDS ...\n")
    vm_list = input_yaml['vms']

    for vms in vm_list:
        vms = ' '.join(vms)
        print ("# Starting GET UUID for VM(s): \'"+vms+"\'")
        command = 'python3 ./getVMInstanceId.py --sourcevc '+src_vcenter+' --user '+user+' -p '+password+' --name '+vms
        print ("## "+bcolors.OKBLUE+"DEBUG Command = "+bcolors.ENDC+ command)
        
        # launch python script to retrieve uuids and JSON body for PRE-MIGRATE call
        #res = 0
        res = os.system(command)
        if res == 0:
            print("## "+bcolors.OKGREEN+"SUCCESS "+bcolors.ENDC+"=> GET uuid VMs \'"+vms+"\'")
        else:
            print("## "+bcolors.FAIL+"FAIL "+bcolors.ENDC+"=> Error while GET uuid VMs \'"+vms+"\'")

if __name__ == "__main__":
    main()
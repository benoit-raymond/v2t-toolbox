# coding: utf-8
#!/usr/bin/env python3
# Disclaimer: This product is not supported by VMware.

# PRE-REQUISISTES
# Python3 (Tested : 3.8.12)
# Python 3rd party module = yaml
# Python module : argparse, getpass, os
# pip3 install yaml
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
    print ("usage: python3 main_vmotion.py [--help] [--input|-i </path/file.yml>]")
    print ("objective: Run VMs vMotion API call according to input file arguments.")
    print ("")
    print ("optional arguments:")
    print ("  --help, -h \t\t\t\tshow this help message and exit")
    print ("  --input, -i </path/file.yml> \t\tPath to YAML config file (Default=v2t-dfw-export-version.yml)")
    print ("")

def main():
    # Analyze CLI Args
    parser = argparse.ArgumentParser(description='main_vmotion', add_help=False)
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
    src_vcenter = input_yaml['src_vcenter']
    dst_vcenter = input_yaml['dst_vcenter']
    cluster = input_yaml['cluster']
    user = input_yaml['user']

    # Ask user password
    print ("user: "+user)
    password = getpass()

    # Parse the list of VMs in YAML input file (= list of VM for this wave)
    vm_list = input_yaml['list']
    for vm in vm_list:
        print ("# VM = "+vm)
        print ("# VM nets= "+vm['networks'])
        print ("# VM name= "+vm['name'])
        print ("# VM DS= "+vm['datastore'])
        name = vm['name']
        datastore = vm['datastore']
        networks = ' '.join(vm['networks'])

        os.system('./vmotion.py --sourcevc '+src_vcenter+' --destvc '+dst_vcenter+' --user '+user+' --password '+password+' --cluster '+cluster+ '--datastore ' +datastore+' --network '+networks+' --autovif --name '+name)


if __name__ == "__main__":
    main()
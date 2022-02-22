# coding: utf-8
#!/usr/bin/env python3

# PRE-REQUISISTES
# Python3 (Tested : 3.8.12)
# Python 3rd party module = paramiko (SSH connection) + yaml
# pip3 install paramiko
# pip3 install yaml
# SSH access to NSX-v ESXi hosts. Same user/password allowed to access all ESX
# Script mode =>
#   - check_only = True => will not change DFW Export version if != 1000
#   - check_only = False => will try to change DFW Export version to 1000. Require ESX in Maintenance mode


import yaml
import argparse
import paramiko
import re
from getpass import getpass

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
    print ("usage: python3 v2t-dfw-export-version.py [--help] [--set|-s] [--input|-i </path/file.yml>]")
    print ("objective: Check ESXi hosts DFW Export version is set to 1000.")
    print ("")
    print ("optional arguments:")
    print ("  --help, -h \t\t\t\tshow this help message and exit")
    print ("  --set, -s \t\t\t\tscript will attempt to set DFW export version to 1000. (Default Mode = check only)")
    print ("  --input, -i </path/file.yml> \t\tPath to YAML config file (Default=v2t-dfw-export-version.yml)")
    print ("")

def main():
    # Analyze CLI Args
    parser = argparse.ArgumentParser(description='v2t-dfw-export-version', add_help=False)
    parser.add_argument('--set', '-s', required=False,  action='store_true', help='Script will attempt to set DFW export version to 1000. (Default Mode = check only)', default=False)
    parser.add_argument('--help', '-h', required=False, action='store_true', help='Display command help')
    parser.add_argument('--input', '-i', required=False, help='Path to input yaml file (Default=v2t-dfw-export-version.yml)', default="v2t-dfw-export-version.yml")
    args = parser.parse_args()
    if  args.help == True:
        print_help()
        quit()

    # Read input  YAML file
    with open(args.input, 'r') as file:
        input_yaml = yaml.safe_load(file)

    # Set VARS
    hosts = input_yaml['hosts']
    user = input_yaml['user']
    port = 22
    # Ask user password
    print ("user: "+user)
    password = getpass()
    # ESXi dvfilters command
    command_getfilters = "vsipioctl getfilters | grep \"Filter Name\" | grep \"sfw.2\""
    command_getexport = "vsipioctl getexportversion -f "
    command_setexport = "vsipioctl setexportversion -e 1000 -f "
    pattern_export_version = 'Current export version: (\d+)'

    # Loop to Connect to all ESXhosts
    for esx in hosts:
        print ("####################")
        print ("# HOST = "+esx)
        ssh_stream = paramiko.SSHClient()
        ssh_stream.load_system_host_keys()
        # Add host key to known_hosts
        ssh_stream.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_stream.connect(esx, port, user, password)
        # EXEC ssh command : Get nic ids
        stdin, stdout, stderr = ssh_stream.exec_command(command_getfilters)
        vms = stdout.readlines()

        # Loop For each VM in this hosts, get dfw export version
        for vm_nic in vms:
            # extract VM vnic-id from the result
            # output line format example => name: nic-2112467-eth0-vmware-sfw.2
            nic_line = vm_nic.split(":")
            nic_id = nic_line[1].rstrip("\n")

            # EXEC command : Get Export version
            stdin, stdout, stderr = ssh_stream.exec_command(command_getexport+ nic_id)
            # output one 1 line format example => Current export version: 500
            res = stdout.readlines()
            line = res[0].rstrip("\n")
            # Pattern match : identify dfw export value
            match = re.search(pattern_export_version, res[0])
            if match:
                dfw_export_version = match.group(1)
                if dfw_export_version == "1000":
                    # dfw export value = 1000
                    print("## "+bcolors.OKGREEN+"SUCCESS "+bcolors.ENDC+"=> DFW Export version = 1000 (NIC-Name ="+ nic_id+")")
                if dfw_export_version != "1000" and not args.set:
                    # dfw export value is not 1000 BUT script check-only mode
                    print("## "+bcolors.WARNING+"ACTION REQUIRED "+bcolors.ENDC+"=> DFW Export version = "+ dfw_export_version +" (NIC-Name ="+ nic_id+")")
                if dfw_export_version != "1000" and args.set:
                    # DFW export version not 1000 AND script mode is set to modify the value
                    stdin, stdout, stderr = ssh_stream.exec_command(command_setexport + nic_id)
                    # Verify DFW export version successfullu modified
                    stdin, stdout, stderr = ssh_stream.exec_command(command_getexport+ nic_id)
                    res = stdout.readlines()
                    line = res[0].rstrip("\n")
                    match = re.search(pattern_export_version, res[0])
                    if match and match.group(1) == "1000":
                        print("## "+bcolors.OKGREEN+"SUCCESS "+bcolors.ENDC+"=> DFW Export version changed to 1000 (NIC-Name ="+ nic_id+")")
                    else:
                        print("## "+bcolors.FAIL+"FAIL "+bcolors.ENDC+"=> Unable to change DFW Export version changed to 1000. (NIC-Name ="+ nic_id+")")
            else:
                # ERROR unexpected output while reading dvfilter export version value
                print("## ERROR: export version not found. "+line)
                continue
        # Delete stream paramiko vars
        del stdin, stdout, stderr
        # Close SSH stream
        ssh_stream.close()

if __name__ == "__main__":
    main()

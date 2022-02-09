# coding: utf-8
#!/usr/bin/env python3

# PRE-REQUISISTES
# Python3 (Tested : 3.8.12)
# Python 3rd party module = requests + yaml
# pip3 install requests
# pip3 install yaml
# HTTPS access to NSX-v Manager.


import requests
import json
import socket
import yaml
import argparse
from getpass import getpass

# HELP ARGPARSE
def print_help():
    print ("usage: python3 v2t-add-ipsets-v.py [--help] [--input|-i </path/file.yml>]")
    print ("objective: Add NSX-v a new IPSet to each Security Group with the IP of effective members.")
    print ("")
    print ("optional arguments:")
    print ("  --help, -h \t\t\t\tshow this help message and exit")
    print ("  --input, -i </path/file.yml> \t\tPath to YAML config file (Default=v2t-add-ipsets-v.yml)")
    print ("")

# Function check ipv4 valid
def check_ipv4(address):
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >= 0 and b<=255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False

# Function check ipv6 valid
def check_ipv6(n):
    try:
        socket.inet_pton(socket.AF_INET6, n)
        return True
    except socket.error:
        return False

def main():
    # Analyze CLI Args
    parser = argparse.ArgumentParser(description='v2t-dfw-export-version', add_help=False)
    parser.add_argument('--help', '-h', required=False, action='store_true', help='Display command help')
    parser.add_argument('--input', '-i', required=False, help='Path to input yaml file (Default=v2t-add-ipsets-v.yml)', default="v2t-add-ipsets-v.yml")
    args = parser.parse_args()
    if  args.help == True:
        print_help()
        quit()

    # Read input  YAML file
    with open(args.input, 'r') as file:
        input_yaml = yaml.safe_load(file)

    # Set VARS
    fqdn_nsxv = input_yaml['nsx-v']
    port = "443"
    user = input_yaml['user']
    scope = input_yaml['scope']
    port = 22
    # Ask user password
    print ("user: "+user)
    pwd = getpass()

    nb_nsg = 0
    # Get NSX-V NSGroup list
    print ("----GET NSG list----")
    url = "https://" + fqdn_nsxv + ":" + port + "/" + "api/2.0/services/securitygroup/scope/" + scope
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    auth = ("admin", pwd)
    result =  requests.get(url, auth=auth, headers=headers, verify=False)
    print ("# HTTP RETURN CODE > GET NSG list = " + str(result.status_code))

    nsg_list = result.json()
    nb_nsg = len(nsg_list)
    print ("## Number of NSG : " + str(nb_nsg))

    for i in range (nb_nsg):
        print ("------------------------------")
        print ("# NSGroupID = " + nsg_list[i]["objectId"])
        # GET IPs for each NSG actual members
        cur_nsg_id = nsg_list[i]["objectId"]
        print ("----GET IPs of current NSG----")
        url = "https://" + fqdn_nsxv + ":" + port + "/" + "api/2.0/services/securitygroup/" + cur_nsg_id + "/translation/ipaddresses"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        auth = ("admin", pwd)
        result =  requests.get(url, auth=auth, headers=headers, verify=False)
        print ("# HTTP RETURN CODE > GET NSG IPs : " + str(result.status_code))
        cur_res =result.json()
        if result.status_code != 200:
            print ("==> Error requestiong IP Addresses belonging to this NSGroup - Jump to next NSgroup")
            continue
        if len (cur_res["ipNodes"]) == 0:
            print ("==> No IP Addresses belonging to this NSGroup - Jump to next NSgroup")
            continue
        # IP Address
        tab_nsg_ips = []
        for each in cur_res["ipNodes"]:
            for val in each['ipAddresses']:
                # Do not add IP Addresses using IPv6 in the IPSet
                if not check_ipv6(val):
                    tab_nsg_ips.append (val)
        nsg_ips = ",".join(tab_nsg_ips)
        print ("## List of IPs = "+nsg_ips)


        # CREATE IPSet
        print ("----CREATE Temp IPSet----")
        url = "https://" + fqdn_nsxv + ":" + port + "/" + "api/2.0/services/ipset/" + scope
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        auth = ("admin", pwd)
        data = {
            "objectTypeName": "IPSet",
            "type": {
                "name": "IPSet"
            },
            "name": "IPSet-" + cur_nsg_id + "-v2t",
            "description" : "Temporary IPSet v2t",
            "value": nsg_ips
        }

        result =  requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
        print ("# HTTP RETURN CODE > POST new IPSet : " + str(result.status_code))
        if (result.status_code == 201):
            new_ipset_id = result.text
            print ("## IPSetID = "+result.text)
        else:
            print ("==> Error while creating new IPSet for NSGroup =  "+ cur_nsg_id)
            print (result.text)
            continue

        # ADD IPSet as static Member
        print ("----ADD IPSet in NSG----")
        url = "https://" + fqdn_nsxv + ":" + port + "/" + "api/2.0/services/securitygroup/bulk/" + cur_nsg_id
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        auth = ("admin", pwd)
        data = nsg_list[i]
        new_ipset_member = {
            "objectId": str(new_ipset_id),
            "objectTypeName": "IPSet",
            "type": {
                "name": "IPSet"
            },
            "description": "Temp. v2T"
        }
        data["revision"] = data["revision"] + 1
        data["members"].append(new_ipset_member)

        result =  requests.put(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
        print ("# HTTP RETURN CODE > PUT Add member : " + str(result.status_code))
        if (result.status_code != 200):
            print ("## Error while adding new IPSet as member for NSGroup =  "+ cur_nsg_id)
            print (result.text)
            continue

if __name__ == "__main__":
    main()

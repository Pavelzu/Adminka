import awxkit
from awxkit import api, config, utils, cli
from awxkit.api import ApiV2, job_templates, JobTemplateLaunch, base, pages, jobs
from awxkit.api.resources import resources
import os

import time
import sys
from ftplib import FTP
from ftplib import FTP_TLS
import json
from python_wireguard import Key
import re
import sys
import argparse
import getpass
import keyring
import logging

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fixed", required=True, help="Add target desctops ip only. Not subnet. Only 1 IP. ")
    parser.add_argument("-c", "--comment", required=True, help="Comment for peer")
    parser.add_argument("-d", "--desctop", required=True, help="Target desctop to connect")
    parser.add_argument("-r", "--radius", required=True, help="Target desctops ip")
    parser.add_argument("-a", "--address", required=True, help="Current notebooks ip")
    parser.add_argument("-l", "--login", required=True, help="Login to Desctop, Peers name")
    parser.add_argument("-n", "--newpass", required=False, help="Set new password", action="store_true")
    arguments = parser.parse_args()
    return arguments

def getPeersFileToDisk (address, port, login, password, filename):
    ftp = FTP()
    ftp.connect(address, port)
    ftp.login(login, password)
    with open(filename, "wb") as file:
        ftp.retrbinary(f"RETR {filename}", file.write)
    ftp.quit()

def conncttoawx(AWX_ADDRESS, AWX_USER, AWX_PASS):
    awxkit.config.base_url = os.environ.get('AWX_URL', AWX_ADDRESS)
    awxkit.config.credentials = awxkit.utils.PseudoNamespace(
        {'default':
             {'username': os.environ.get('AWX_USERNAME', AWX_USER),
              'password': os.environ.get('AWX_PASSWORD', AWX_PASS)}})
    connection = awxkit.api.Api()
    connection.load_session().get()
    client = connection.available_versions.v2.get()
    return client

def runtemplatenovars(client, templatename):
    test = client.job_templates.get(name=templatename).results[0]
    launch = job_templates.JobTemplate.launch(test)
    while True:
        time.sleep(5)
        awxjob = client.jobs.get(id=launch.id).results[0]
        #print(awxjob.status)
        if awxjob.status == "failed":
            result = False #print ("Job Failed")
            break
        if awxjob.status == "successful":
            result = True #print ("Job Successful")
            break
    #return result
    return awxjob

def runtemplatewithvars(client, templatename, newwars):
    unified_job_templates = client.unified_job_templates.get(name=templatename)
    unified_job_template = unified_job_templates.results[0]
    unified_job_template.extra_vars = json.dumps(newwars)
    unified_job_template.patch()
    return runtemplatenovars(client, templatename)

def peerFileFilterItwg(filename):
    with open(filename) as f:
        s = f.read()
    s = s.replace('\\\n', '')
    s = re.sub(r'[ ]+', ' ', s)
    slist = s.split('\n')
    clearslist = []
    for el in slist:
        if "Users_WG" in el:
            clearslist.append(el)
    with open('filteredpeerslist.txt', 'w') as f:
        f.writelines(f"{item}\n" for item in clearslist)
    os.remove(filename)
    os.renames("filteredpeerslist.txt", filename)

def ipinwgpool(filename):
    with open(filename) as f:
        s = f.read()
    slist = s.split('\n')

    iplist = []
    for el in slist:
        if el:
            iplist.append(int((re.search(r'10.30.3.\d+', el).group()).replace("10.30.3.", "")))
    iplist.sort()

    iplastoctet = 2
    for item in iplist:
        if iplastoctet != item:
            break
        iplastoctet = iplastoctet + 1
    return '10.30.3.' + str(iplastoctet)

def isPeerExists(peer, filename):
    with open(filename) as f:
        s = f.read()
    if " name=" + peer.lower() + " " in s.lower():
        return True
    else:
        return False

def changeipinnbconfigtemplate(client, newip):
    allhosts = client.hosts.get()
    for hst in allhosts.results:
        if hst.description == "Single Notebook For Remote Configuration":
            hst.name = newip
            hst.patch()
            break

def main():
    if os.path.exists("PYlogs.txt"):
        os.remove("PYlogs.txt")
    logging.basicConfig(
        level=logging.INFO,
        filename="PYlogs.txt",
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        datefmt='%H:%M:%S',
    )

    logging.info("Hello")
    systemname1 = "AWXweb"
    AWX_USER = "admin"
    AWX_ADDRESS = "http://awxaddress:port/"

    systemname2 = "FTP73"
    FTPServerAddress = '192.168.7.3'
    FTPServerPort = 1100
    FTP_USER = 'FTPAnsibleUser'
    filename = "actualpeers.txt.rsc"

    args = parse_arguments()
    logging.info("args: address - " + str(args.address) + ", login - " + str(args.login) + ", desctop - " + str(args.desctop) + ", radius - " + str(args.radius) + ", comment - " + str(args.comment) + ", fixed - " + str(args.fixed) + ", new - " + str(args.newpass))
    systemname1 = "AWX"
    systemname2 = "FTP7.3"
    if args.newpass:
        password1 = getpass.getpass(prompt="Enter secret password for AWX web:")
        password2 = getpass.getpass(prompt="Enter secret password for FTP on 192.168.7.3:")
        try:
            keyring.set_password(systemname1, AWX_USER, password1)
            keyring.set_password(systemname2, FTP_USER, password2)
        except Exception as error:
            print('Error: {}'.format(error))

    AWX_PASS = keyring.get_password(systemname1, AWX_USER)
    FTP_PASS = keyring.get_password(systemname2, FTP_USER)
    logging.info("Keyring OK")

    remotedesctop = args.desctop
    peer = args.login
    currentip = args.address
    targetsip = args.radius
    peercomment = args.comment
    fix = args.fixed
    awx = conncttoawx(AWX_ADDRESS, AWX_USER, AWX_PASS)
    logging.info("AWX Connection OK")
    logging.info("Geting peers list...")
    res = runtemplatenovars(awx, "Get Peers List")
    if res.status == "successful":
        print("Get Peers List OK")
        logging.info("Peers list OK")
        print(res.result_stdout)
    else:
        print("Get Peers List NOT OK")
        print(res.result_stdout)
        exit(9)
    getPeersFileToDisk(FTPServerAddress, FTPServerPort, FTP_USER, FTP_PASS, filename)
    logging.info("Peers list Downloaded")
    peerFileFilterItwg(filename)
    logging.info("Peers list Filtered")
    if isPeerExists(peer, filename): #("peer exists")
        logging.info("Peer " + peer + " already exists")
        res = runtemplatewithvars(awx, "Remove Peer by Username", {"peersname":peer})
        if res.status == "successful":
            print("Remove Peer by Username OK")
            logging.info("Peer " + peer + " removed")
            #print(res.result_stdout)
        else:
            print("Remove Peer by Username NOT OK")
            print(res.result_stdout)
            exit(9)
    selectedip = ipinwgpool(filename)
    logging.info("Free ip detected: " + selectedip)
    private, public = Key.key_pair()
    logging.info("The new pair private-public generated")
    changeipinnbconfigtemplate(awx, currentip)
    logging.info("AWX Inventory 'Single Notebook For Remote Configuration' changed ")

    allowedaddresses = "172.17.0.6/32," + selectedip + "/32,"
    if fix.lower() == "true":  # fixed == true only 1 ip
        allowedaddresses = allowedaddresses + targetsip + "/32"
    else:
        sub = re.search(r'\d+.\d+.\d+.', targetsip)
        allowedaddresses = allowedaddresses + sub.group() + "0/24"
    logging.info("Allowed ips: " + allowedaddresses)

    allowedaddressesMikrot = allowedaddresses
    allowedaddressesNb = allowedaddresses.replace(",", ", ")

    logging.info("Job 'Config WG notebook")
    res = runtemplatewithvars(awx, "Config WG notebook", {"pubkey": str(public), "privkey": str(private), "ip": str(selectedip), "remotedesctop": str(remotedesctop),"allowedaddressNb":str(allowedaddressesNb)})
    if res.status == "successful":
        print("Config WG notebook OK")
        logging.info("Job 'Config WG notebook' OK")
        print(res.result_stdout)
    else:
        print("Send WG Config To Notebook NOT OK")
        print(res.result_stdout)
        exit(9)
    #runtemplatewithvars(awx, "Create New Peer",{"allowedaddressWG":str(allowedaddressWG), "allowedaddressLAN":str(allowedaddressLAN), "comment": str(peercomment), "name": str(peer), "pubkey": str(public)})
    logging.info("Job 'Create New Peer' started")
    res = runtemplatewithvars(awx, "Create New Peer",{"allowedaddressMikrot":str(allowedaddressesMikrot), "comment": str(peercomment), "name": str(peer), "pubkey": str(public)})
    if res.status == "successful":
        print("Create New Peer OK")
        logging.info("Job 'Create New Peer' OK")
        print(res.result_stdout)
    else:
        print("Create New Peer NOT OK")
        print(res.result_stdout)
        exit(9)
    logging.info("Job 'Add Connection In Remmina' started")
    res = runtemplatewithvars(awx, "Add Connection In Remmina", {"login":str(peer), "host":str(remotedesctop)})
    if res.status == "successful":
        print("Add Connection In Remmina OK")
        logging.info("Job 'Add Connection In Remmina' OK")
        print(res.result_stdout)
    else:
        print("Add Connection In Remmina NOT OK")
        print(res.result_stdout)
        exit(9)
    logging.info("Everything is OK! Buy!")
    time.sleep(2)
    os.remove("PYlogs.txt")

if __name__ == "__main__":
    sys.exit(main())
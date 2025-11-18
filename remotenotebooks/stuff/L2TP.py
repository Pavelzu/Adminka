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
    parser.add_argument("-a", "--address", required=True, help="Current notebooks ip")
    parser.add_argument("-n", "--newpass", required=False, help="Set new password", action="store_true")
    arguments = parser.parse_args()
    return arguments

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

    args = parse_arguments()
    logging.info("args: address - " + str(args.address) + ", new - " + str(args.newpass))
    systemname1 = "AWX"
    if args.newpass:
        password1 = getpass.getpass(prompt="Enter secret password for AWX web:")
        try:
            keyring.set_password(systemname1, AWX_USER, password1)
        except Exception as error:
            print('Error: {}'.format(error))
    AWX_PASS = keyring.get_password(systemname1, AWX_USER)
    logging.info("Keyring OK")
    awx = conncttoawx(AWX_ADDRESS, AWX_USER, AWX_PASS)
    logging.info("AWX connection OK")

    currentip = args.address
    changeipinnbconfigtemplate(awx, currentip)
    logging.info("AWX Inventory 'Single Notebook For Remote Configuration' changed ")
    logging.info("Job 'Config L2TP notebook' started")
    res = runtemplatenovars(awx, "Config L2TP notebook")
    if res.status == "successful":
        print("Job 'Config L2TP notebook' OK")
        logging.info("Job 'Config L2TP notebook' OK")
        print(res.result_stdout)
    else:
        print("Job 'Config L2TP notebook' NOT OK")
        logging.info("Job 'Config L2TP notebook' NOT OK")
        exit (2)
        print(res.result_stdout)

    logging.info("Everything is OK! Buy!")
    time.sleep(2)
    os.remove("PYlogs.txt")








if __name__ == "__main__":
    sys.exit(main())
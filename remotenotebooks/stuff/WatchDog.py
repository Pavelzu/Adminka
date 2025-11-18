from symbol import continue_stmt

import awxkit
from awxkit import api, config, utils, cli
from awxkit.api import ApiV2, job_templates, JobTemplateLaunch, base, pages, jobs
from awxkit.api.resources import resources
import re
import sys
import argparse
import getpass
import keyring
import logging
import awxkit
import os
import time as timetosleep
from ftplib import FTP
import json
import datetime
from datetime import datetime, date, time

def getPeersFileToDisk (address, port, login, password, filename, localfilename):
    ftp = FTP()
    ftp.connect(address, port)
    ftp.login(login, password)
    with open(localfilename, "wb") as file:
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
        timetosleep.sleep(5)
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
        if "Users_WG" in el and re.search(r'sc{.*}', el):
            clearslist.append(el)
    with open('filteredpeerslistforwd.txt', 'w') as f:
        f.writelines(f"{item}\n" for item in clearslist)
    os.remove(filename)
    os.renames("filteredpeerslistforwd.txt", filename)

def getworktimelist(filename):
    with open(filename) as f:
        s = f.read()
    slist = s.split('\n')
    fullworktimelist = []
    for el in slist:
            if "sc{time:|worktime|}" in el:
                el = el.replace("name= ", "name=")
                name = re.search(r'name=[\w\.]+', el)
                name = name.group().replace("name=", "")
                fullworktimelist.append(name)
    return fullworktimelist

def definetineinterval(now):
    dateparts = now.timetuple()
    isworktimenow = False
    if now.isoweekday() == 6 or now.isoweekday() == 7:  # 0 - ponedelnik
        isworktimenow = False
    else:
        if dateparts[3] < 8 or dateparts[3] >= 20:
            isworktimenow = False
        else:
            isworktimenow = True
    return isworktimenow

def trashtosingledays(trash):
    '''
    obj = []
    summary = []
    if ";" in trash:
        obj = trash.split(';')
    else:
        obj.append(trash)
    for dt in obj:
        #print(dt)
        if "-" in dt:
            start = re.match(r"\d+-",dt).group(0).replace("-","")
            end = re.search(r"-\d+.",dt).group(0).replace("-","").replace(".","")
            month = int(re.search (r"\.\d+$",dt).group(0).replace(".",""))
            for i in range(int(start), int(end)+1):
                oneday = []
                oneday.append(i)
                oneday.append(month)
                summary.append(oneday)
        else:
            if re.search(r"^\d+\.\d+$", dt):
                d = dt.split(".")
                oneday = []
                oneday.append(int(d[0]))
                oneday.append(int(d[1]))
                summary.append(oneday)
            else:
                if "," in dt:
                    d = dt.split(".")
                    ds = d[0].split(",")
                    month = int(re.search(r"\.\d+$", dt).group(0).replace(".", ""))
                    for i in range(len(ds)):
                        oneday = []
                        oneday.append(int(ds[i]))
                        oneday.append(month)
                        summary.append(oneday)
    '''
    obj = []
    summary = []
    if ";" in trash:
        obj = trash.split(';')
    else:
        obj.append(trash)
    oneday = []
    #print(obj)
    for dt in obj:
        # print (dt)
        oneday = []
        parts = dt.split('.')  # parts[0] - days , parts[1] - mounts
        # print(parts[0])
        if "," in parts[0]:
            singleschemas = parts[0].split(",")
            for schema in singleschemas:
                if "-" in schema:
                    start = re.match(r"\d+-", schema).group(0).replace("-", "")
                    end = re.search(r"-\d+.", schema).group(0).replace("-", "").replace(".", "")
                    for i in range(int(start), int(end) + 1):
                        oneday.append(int(i))
                else:
                    if re.search(r"^\d+$", schema):
                        oneday.append(int(schema))
        else:
            if re.search(r"^\d+$", parts[0]):
                oneday.append(int(parts[0]))
            else:
                if re.search(r"^\*$", parts[0]):
                    for i in range(1, 32):
                        oneday.append(i)
                else:
                    if "-" in parts[0]:
                        start = re.match(r"\d+-", parts[0]).group(0).replace("-", "")
                        end = re.search(r"-\d+", parts[0]).group(0).replace("-", "").replace(".", "")
                        for i in range(int(start), int(end) + 1):
                            oneday.append(int(i))
        oneday.sort()
        #print(oneday)
        onemounth = []
        if "-" in parts[1]:
            start = re.match(r"\d+-", parts[1]).group(0).replace("-", "")
            end = re.search(r"-\d+", parts[1]).group(0).replace("-", "")
            for i in range(int(start), int(end) + 1):
                onemounth.append(int(i))
        else:
            if re.search(r"^\d+$", parts[1]):
                onemounth.append(int(parts[1]))

        #print(onemounth)

        for mth in onemounth:
            for dy in oneday:
                daymounth = []
                daymounth.append(dy)
                daymounth.append(mth)
                summary.append(daymounth)
    return summary

def main():
    logging.basicConfig(
        level=logging.INFO,
        filename="WDlogs.txt",
        format="%(asctime)s - %(module)s - %(message)s",
        datefmt='%d-%m-%Y %H:%M:%S',
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
    localfilename = "actualpeersforwd.txt"

    
    systemname1 = "AWX"
    systemname2 = "FTP7.3"

    AWX_PASS = keyring.get_password(systemname1, AWX_USER)
    FTP_PASS = keyring.get_password(systemname2, FTP_USER)
    logging.info("Keyring OK")
    awx = conncttoawx(AWX_ADDRESS, AWX_USER, AWX_PASS)
    logging.info("AWX Connection OK")
    logging.info("Geting peers list...")
    res = runtemplatenovars(awx, "Get Peers List")
    if res.status == "successful":
        print("Get Peers List OK")
        logging.info("Peers list OK")
        #print(res.result_stdout)
    else:
        print("Get Peers List NOT OK")
        #print(res.result_stdout)
        exit(9)
    getPeersFileToDisk(FTPServerAddress, FTPServerPort, FTP_USER, FTP_PASS, filename, localfilename)
    logging.info("Peers list Downloaded")
    peerFileFilterItwg(localfilename)
    logging.info("Peers list Filtered")

    
    #d = date(2024, 11, 2)
    #t = time(21, 0, 0)
    #curdate = datetime.combine(d, t)

    curdate = datetime.now()

    filteredpeers = open(localfilename, "r")
    isworktimenow = definetineinterval(curdate)
    todisable = []
    toenable = []
    while True:
        line = filteredpeers.readline()
        if not line:
            break
        line = line.replace("= ", "=")
        line = line.replace("| ", "|")
        line = line.replace(" |", "|")
        line = line.replace(", ", ",")

        name = re.search(r'name=[\w\.]+', line)
        name = name.group().replace("name=", "")

        if re.search(r'sc{.*date:.*}', line): # we have date option
            subf = re.search(r'date:\|.*\|', line)
            subdate = subf.group(0)
            subdate = subdate.replace("date:","")
            subdate = subdate.replace("|", "")
            dayslist = trashtosingledays(subdate)
            dateparts = curdate.timetuple()  # 0 - year; 1 - month; 2 - day; 3 - hour; 4 - minute; 5 - second; 6 - weekday (0 = Monday)
            #print(name)
            #print (dayslist)

            iter = 0
            for d in dayslist:
                iter = iter + 1
                if dateparts[2] < d[0] and dateparts[1] == d[1]: #  no chance to find in future
                    todisable.append(name)
                    break
                if dateparts[2] == d[0] and dateparts[1] == d[1]: # match day and month
                    if "time:|worktime|" in line: # we have info about work mode
                        if isworktimenow:
                            toenable.append(name)
                            break
                        else:
                            todisable.append(name)
                            break
                    else: #fulltime or no info about work mode
                        toenable.append(name)
                        break
                if iter == len(dayslist):
                    todisable.append(name)

        if re.search(r'sc{.*time:.*}', line) and not re.search(r'sc{.*date:.*}', line):  #we have only time option, and no date option
            if "time:|worktime|" in line: #variant for 8-20 workers
                if isworktimenow: #if now 8-20
                    toenable.append(name)
                else:
                    todisable.append(name)
            else: #variant for 24/7 workers
                toenable.append(name)

    print(toenable)
    print(todisable)

    if len(toenable) != 0:
        runtemplatewithvars(awx, "EnablePeer", {"names": toenable})
        logging.info("Enabled Peers: " + ' '.join(toenable))
    if len(todisable) != 0:
        runtemplatewithvars(awx, "DisablePeer", {"names": todisable})
        logging.info("Disabled Peers: " + ' '.join(todisable))












if __name__ == "__main__":
    sys.exit(main())
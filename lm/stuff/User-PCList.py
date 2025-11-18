

from selenium import webdriver
from selenium.webdriver.common.by import By
from transliterate import translit
import time
import re
import sys
import argparse
import getpass
import keyring
from pyvirtualdisplay import Display
import shutil

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--newpass", required=False, help="Set new password", action="store_true")
    arguments = parser.parse_args()
    return arguments

def main():
    display = Display(visible=0, size=(1280, 1024))
    display.start()
    args = parse_arguments()

    systemname = "glpi"
    adminlogin = "glpi"
    if args.newpass:
        # Безопасно запрашиваем ввод пароля
        passwd = getpass.getpass(prompt="Enter secret password:")
        # Пишем полученный пароль в хранилище ключей
        try:
            keyring.set_password(systemname, adminlogin, passwd)
        except Exception as error:
            print('Error: {}'.format(error))
    passwd = keyring.get_password(systemname, adminlogin)

    ##### Try to Login ###
    driver = webdriver.Chrome()
    driver.get('http://glpi.domen.ru/index.php')
    time.sleep(1)
    logintextbox = driver.find_element(By.ID, 'login_name')
    logintextbox.send_keys(adminlogin)
    page = driver.page_source
    passfildname = re.search(r'type=\"password\" class=\"form-control\" name=\"\w*', page)
    passfildnamestr = passfildname.group(0).replace('type=\"password\" class=\"form-control\" name=\"', '')
    passtextbox = driver.find_element(By.NAME, passfildnamestr)
    passtextbox.send_keys(passwd)
    driver.find_element(By.NAME, 'submit').click()
    ##### Logined ###

    ##### Get All Data ####
    pageid = 1
    f = open("/var/www/adminka/html/lm/stuff/pc-owner.tmp", "w")
    while (True):
        driver.get('http://glpi.domen.ru/front/computer.form.php?id=' + str(pageid))
        time.sleep(1)
        page = driver.page_source
        if "Объект не найден" in page:
            break
        else:
            pcname = driver.find_element(By.NAME, 'name').get_attribute("value")
            pcowner = driver.find_element(By.NAME, 'contact').get_attribute("value")
            pcowner = pcowner.replace("@CORP","")
            pcownerRU = translit(pcowner, "ru")
            pcownerRU = pcownerRU.replace("ыа","я")
            pcownerRU = pcownerRU.replace("Ыа", "Я")
            pcownerRU = pcownerRU.replace("ык", "юк")
            pcownerRU = pcownerRU.replace("Ы.", "Ю.")
            tofile = pcname + " " + pcowner + " " + pcownerRU
            f.write(pcname + " " + pcowner + " " + pcownerRU + "\n")
            #print(pcname)
            #print(pcowner)
            #print(pcownerRU)
            pageid = pageid +1

    f.close()
    shutil.copyfile("/var/www/adminka/html/lm/stuff/pc-owner.tmp","/var/www/adminka/html/lm/stuff/pc-owner.txt");
    driver.quit()
    display.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
import re
import sys
import argparse
import getpass
import keyring
from pyvirtualdisplay import Display

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", required=True, help="Email to send Galsync")
    parser.add_argument("-n", "--newpass", required=False, help="Set new password", action="store_true")
    arguments = parser.parse_args()
    return arguments

def checkEmail(driver, subj):
    driver.find_element(By.ID, '_XForm_query_display').send_keys(subj)
    driver.find_element(By.ID, '_XForm_query_display').send_keys(Keys.ENTER)
    time.sleep(1)
    page = driver.page_source
    if "No results found." in page:
        return False
    else:
        return True
def switchToPersonalBox(driver, subj):
    driver.find_element(By.ID, '_XForm_query_display').clear()
    driver.find_element(By.ID, '_XForm_query_display').send_keys(subj)
    driver.find_element(By.ID, '_XForm_query_display').send_keys(Keys.ENTER)
    time.sleep(1)
    page = driver.page_source
    subjrowid = re.search(r'zli[\w\-]*\"', page)
    subjrow = driver.find_element(By.ID, subjrowid.group(0).replace('\"', ''))
    action = ActionChains(driver)
    if subj != "galsync@domen.ru":
        action.context_click(subjrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    else:
        action.context_click(subjrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[1])  # change tab
    time.sleep(1)

def acceptGala(driver, subj):
    switchToPersonalBox(driver,subj)
    page = driver.page_source
    driver.save_screenshot('/tmp/s1.png')
    if "zli__TV-main__" in page:
        galletteridwithgarbidge = re.search(r'zli__TV-main__[\w\-=\", ]*galsync', page)
    if "zli__CLV" in page:
        galletteridwithgarbidge = re.search(r'zli__CLV[\w\-=\", ]*galsync', page)
    if not galletteridwithgarbidge:
        print("No letter from galsync")
        exit(7)
    galletterid = galletteridwithgarbidge.group(0)
    galletterid = galletterid[0:galletterid.index('\"')]
    galletter = driver.find_element(By.ID, galletterid)
    galletter.click()
    time.sleep(1)
    try:
        acceptbutton = driver.find_element(By.ID, 'zb__TV__Shr__SHARE_ACCEPT')
    except:
        acceptbutton = driver.find_element(By.ID, 'zb__CLV__Shr__SHARE_ACCEPT')
    acceptbutton.click()
    time.sleep(1)
    driver.find_element(By.ID, 'ZmAcceptShare_name').clear()
    driver.find_element(By.ID, 'ZmAcceptShare_name').send_keys("CorpBook")
    finalacceptbutton = driver.find_element(By.ID, 'ZmAcceptShare_button5')
    finalacceptbutton.click()
    time.sleep(1)
    page = driver.page_source
    if "ErrorDialog_handle" in page:
        print("Galsync book CorpBook alredy exists")
    else:
        print("Galsync book CorpBook successfully accepted!")

def sendGala(driver, subj):
    switchToPersonalBox(driver, 'galsync@domen.ru')
    driver.find_element(By.ID, 'zb__App__Contacts').click()
    time.sleep(1)
    zimbrabookrow = driver.find_element(By.ID, "zti__main_Contacts__257")
    action = ActionChains(driver)
    action.context_click(zimbrabookrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(1)
    emailtextbox = driver.find_element(By.ID, 'ShareDialog_grantee')
    emailtextbox.send_keys(subj)
    emailtextbox.send_keys(Keys.ENTER)
    driver.find_element(By.ID, 'ShareDialog_button2').click()
    time.sleep(1)
    try:
        driver.find_element(By.ID, 'ResendCancel_button2').click()
    finally:
        print("Galsync was sent to " + subj)
    
def loginMainPage(driver, adminlogin, passwd):
    driver.get('https://mail.domen.ru:7071/zimbraAdmin/')
    logintextbox = driver.find_element(By.ID, 'ZLoginUserName')
    logintextbox.send_keys(adminlogin)
    passtextbox = driver.find_element(By.ID, 'ZLoginPassword')
    passtextbox.send_keys(passwd)
    driver.find_element(By.ID, 'ZLoginButton').click()
    time.sleep(1)

def main():
    display = Display(visible=0, size=(1024, 768))
    display.start()
    if len(sys.argv) == 1:
        print ("Please add args for a script. For example, e-mail")
        exit(9)
    args = parse_arguments()

    systemname = "zimbra"
    adminlogin = "adminka@domen.ru"

    if args.newpass:
        # Безопасно запрашиваем ввод пароля
        passwd = getpass.getpass(prompt="Enter secret password:")
        # Пишем полученный пароль в хранилище ключей
        try:
            keyring.set_password(systemname, adminlogin, passwd)
        except Exception as error:
            print('Error: {}'.format(error))
    passwd = keyring.get_password(systemname, adminlogin)

    driver = webdriver.Chrome()
####### login to send
    loginMainPage(driver, adminlogin, passwd)
    if not checkEmail(driver,args.email):
        print ("Email doesn't exist")
        exit(8)
    sendGala(driver, args.email)
    driver.quit()

####### login to accept
    driver = webdriver.Chrome()
    loginMainPage(driver, adminlogin, passwd)
    acceptGala(driver, args.email)
    driver.quit()
    display.stop()


if __name__ == '__main__':
    sys.exit(main())

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
    
def loginMainPage(driver, adminlogin, passwd):
    driver.get('https://mail.domen.ru:7071/zimbraAdmin/')
    logintextbox = driver.find_element(By.ID, 'ZLoginUserName')
    logintextbox.send_keys(adminlogin)
    passtextbox = driver.find_element(By.ID, 'ZLoginPassword')
    passtextbox.send_keys(passwd)
    driver.find_element(By.ID, 'ZLoginButton').click()
    time.sleep(1)


def addtoDistribution(driver, subj, distlist):
    driver.find_element(By.ID, '_XForm_query_display').clear()
    driver.find_element(By.ID, '_XForm_query_display').send_keys(distlist)
    driver.find_element(By.ID, '_XForm_query_display').send_keys(Keys.ENTER)
    time.sleep(1)
    page = driver.page_source
    subjrowid = re.search(r'zli[\w\-]*\"', page)
    subjrow = driver.find_element(By.ID, subjrowid.group(0).replace('\"', ''))
    action = ActionChains(driver)
    action.context_click(subjrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    # driver.switch_to.window(driver.window_handles[1])  # change tab
    time.sleep(1)
    page = driver.page_source
    # findtextboxidwithgarbidge = re.findall(r'ztabv__[\w\- \"=]*query___container[\w\- \"=]*admin_xform_name_input', page)
    findtextboxidwithgarbidge = re.findall(r'ztabv__[\w\- \"=]*query___container[\w\- \"=]*xform_field_container', page)
    findtextboxidwithgarbidge2 = re.search(r'ztabv__[\w]*___', next(iter(findtextboxidwithgarbidge), None))
    findtextboxid = findtextboxidwithgarbidge2.group(0)
    findtextboxid = findtextboxid.replace("___", "")
    # time.sleep(500)
    driver.find_element(By.ID, findtextboxid).send_keys(subj)
    driver.find_element(By.ID, findtextboxid).send_keys(Keys.ENTER)
    time.sleep(1)
    page = driver.page_source
    time.sleep(1)
    subjrowidwithgarbidge = re.search(r'div class=\"Row RowEven\" id=\"zli__\w*__[a-z\d-]+', page)
    subjrowid = re.search(r'zli__\w*__[\w-]*', subjrowidwithgarbidge.group(0))
    driver.find_element(By.ID, subjrowid.group(0)).click()
    driver.find_element(By.ID, subjrowid.group(0)).send_keys(Keys.ENTER)
    page = driver.page_source
    if "Can not add the following addresses for they already are members" in page:
        print(subj + " already is a member")
        exit(5)
    else:
        driver.find_element(By.ID, 'zb__ZaCurrentAppBar__SAVE').click()
        print(subj + " successfully added!")
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
####### login to check
    loginMainPage(driver, adminlogin, passwd)
    if not checkEmail(driver,args.email):
        print ("Email doesn't exist")
        exit(8)
    driver.quit()


####### login to add in distribution
    driver = webdriver.Chrome()
    loginMainPage(driver, adminlogin, passwd)
    addtoDistribution(driver, args.email, 'goreltex_info@domen.ru')
    driver.quit()
    display.stop()


if __name__ == '__main__':
    sys.exit(main())
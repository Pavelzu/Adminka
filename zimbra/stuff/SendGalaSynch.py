from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
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
    time.sleep(2)
    page = driver.page_source
    if "No results found." in page:
        return False
    else:
        return True

def acceptGala(driver, subj):
    driver.save_screenshot('/tmp/s0.png')
    driver.find_element(By.ID, '_XForm_query_display').clear()
    driver.find_element(By.ID, '_XForm_query_display').send_keys(subj)
    driver.find_element(By.ID, '_XForm_query_display').send_keys(Keys.ENTER)
    driver.save_screenshot('/tmp/s1.png')
    time.sleep(2)
    driver.save_screenshot('/tmp/s2.png')
    page = driver.page_source
    subjrowid = re.search(r'zli[\w\-]*\"', page)
    subjrow = driver.find_element(By.ID, subjrowid.group(0).replace('\"',''))
    action = ActionChains(driver)
    action.context_click(subjrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    driver.save_screenshot('/tmp/s3.png')
    time.sleep(2)
    print(driver.current_window_handle)
    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[2])  # change tab 
    print(driver.current_window_handle)
    print(driver.window_handles)
    driver.save_screenshot('/tmp/s4.png')
    time.sleep(2)
    page = driver.page_source
    driver.save_screenshot('/tmp/s5.png')
    galletteridwithgarbidge = re.search(r'zli__TV-main__[\w\-=\", ]*galsync', page)
    if not galletteridwithgarbidge:
        print("No letter from galsync")
        exit(7)
    galletterid = galletteridwithgarbidge.group(0)
    galletterid = galletterid[0:galletterid.index('\"')]
    galletter = driver.find_element(By.ID, galletterid)
    driver.save_screenshot('/tmp/s6.png')
    galletter.click()
    time.sleep(2)
    driver.save_screenshot('/tmp/s7.png')
    acceptbutton = driver.find_element(By.ID, 'zb__TV__Shr__SHARE_ACCEPT')
    acceptbutton.click()
    time.sleep(2)
    driver.save_screenshot('/tmp/s8.png')
    driver.find_element(By.ID, 'ZmAcceptShare_name').clear()
    driver.find_element(By.ID, 'ZmAcceptShare_name').send_keys("CorpBook")
    finalacceptbutton = driver.find_element(By.ID, 'ZmAcceptShare_button5')
    finalacceptbutton.click()
    time.sleep(2)
    page = driver.page_source
    if "ErrorDialog_handle" in page:
        print("Galsync book CorpBook alredy exists")
    else:
        print("Galsync book CorpBook successfully accepted!")

def sendGala(driver, subj):
    driver.find_element(By.ID, '_XForm_query_display').clear()
    driver.find_element(By.ID, '_XForm_query_display').send_keys('galsync@domen.ru')
    driver.find_element(By.ID, '_XForm_query_display').send_keys(Keys.ENTER)
    time.sleep(2)
    page = driver.page_source
    galrowid = re.search(r'zli\w*b67c13c7-3af8-45c4-83cd-2b86b6cef5fb', page)
    galrow = driver.find_element(By.ID, galrowid.group(0))  # b67c13c7-3af8-45c4-83cd-2b86b6cef5fb
    print(driver.window_handles)
    action = ActionChains(driver)
    action.context_click(galrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[1])  # change tab
    time.sleep(2)
    print(driver.current_window_handle)
    driver.save_screenshot('/tmp/screenie.png')

    driver.find_element(By.ID, 'zb__App__Contacts').click()
    time.sleep(2)
    zimbrabookrow = driver.find_element(By.ID, "zti__main_Contacts__257")
    action.context_click(zimbrabookrow).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(2)
    emailtextbox = driver.find_element(By.ID, 'ShareDialog_grantee')
    emailtextbox.send_keys(subj)
    emailtextbox.send_keys(Keys.ENTER)
    driver.find_element(By.ID, 'ShareDialog_button2').click()
    time.sleep(2)
    try:
        driver.find_element(By.ID, 'ResendCancel_button2').click()
    finally:
        print("Galsync was sent to " + subj)
    

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

    #options = Options()
    #options.add_argument('--headless=new')
    driver = webdriver.Chrome()
    #options.add_argument('--no-sandbox')
    #options.add_argument("--no-sandbox");
    #options.add_argument("--disable-dev-shm-usage");
    #driver = webdriver.Chrome(options=options)
    #driver.set_window_size(1500, 1500)
    #driver.maximize_window()
    driver.get('https://mail.domen.ru:7071/zimbraAdmin/')
    logintextbox = driver.find_element(By.ID, 'ZLoginUserName')
    logintextbox.send_keys(adminlogin)
    passtextbox = driver.find_element(By.ID, 'ZLoginPassword')
    passtextbox.send_keys(passwd)
    driver.find_element(By.ID, 'ZLoginButton').click()
    time.sleep(2)

    if not checkEmail(driver,args.email):
        print ("Email doesn't exist")
        exit(8)

    sendGala(driver, args.email)
    driver.switch_to.window(driver.window_handles[0])  # change tab
    acceptGala(driver, args.email)
    driver.quit()
    display.stop()


if __name__ == '__main__':
    sys.exit(main())

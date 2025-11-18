from pypsexec.client import Client
import sys
import argparse
import getpass
import keyring

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True, help="Target host to connect")
    parser.add_argument("-n", "--newpass", required=False, help="Set new password", action="store_true")
    arguments = parser.parse_args()
    return arguments

def main():
    args = parse_arguments()
    if '.' in args.target:
        server = args.target
    else:
        server = args.target + ".domen.ru"
    systemname = "psexec"
    username = "adminkapsexecuser@domen.ru"
    executable = "cmd.exe"

    arguments1 = '/c rmdir /Q "C:\\Program Files (x86)\\LiteManager Pro - Server\\5185"' #c$/Program Files (x86)/LiteManager Pro - Server/5185/
    arguments4 = '/c SCHTASKS -Create /SC ONCE /RU "" /TN AdminkaLMReinstall /TR \\\\Distribs\\LM\\Server\\5185\\installscript.bat /ST 23:00 /SD 06/06/2036'
    arguments6 = "/c SCHTASKS -Run /I /TN AdminkaLMReinstall"
    arguments7 = "/c SCHTASKS -Delete /TN AdminkaLMReinstall /F"

    resultst = ""


    if args.newpass:
        # Безопасно запрашиваем ввод пароля
        password = getpass.getpass(prompt="Enter secret password:")
        # Пишем полученный пароль в хранилище ключей
        try:
            keyring.set_password(systemname, username, password)
        except Exception as error:
            print('Error: {}'.format(error))

    password = keyring.get_password(systemname, username)

    c = Client(server, username=username, password=password, encrypt=True)
    try:
        c.connect()
    except Exception as err:
        print(err)
    else:
        c.create_service()

        result = c.run_executable(executable, arguments=arguments1) #delete 5185
        if result[0]:
            resultst += result[0].decode('cp866')

        result = c.run_executable(executable, arguments=arguments4) #create task
        if result[1]:
            resultst += result[1].decode('cp866')

        result = c.run_executable(executable, arguments=arguments6) #execute task
        if result[1]:
            resultst += result[1].decode('cp866')

        result = c.run_executable(executable, arguments=arguments7) #delete task
        if result[1]:
            resultst += result[1].decode('cp866')

        c.remove_service()
        c.disconnect()
        if resultst == "":
            resultst = "Wait for a minute and try to connect"

    print(resultst)
    # print(result[0].decode('cp866') if result[0] else "")
    # print("STDERR:\n%s" % result[1].decode('cp866') if result[1] else "")


    return 0

if __name__ == '__main__':
    sys.exit(main())

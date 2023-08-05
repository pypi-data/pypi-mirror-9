#!/usr/bin/env python
# coding=utf-8

import os
import sys
from .portal import Portal

def main():
    print("\n****************************************\n")
    print("* Welcome to QDU Tearching Area Portal *\n")
    print("*             -- powered by Cole Smith *\n")
    print("****************************************\n")

    username = None
    password = None
    if not os.path.isfile('/usr/bin/userinfo.txt'):
        print("First Use This Script!!!")
        username = raw_input("UserName: ")
        password = raw_input("PassWord: ")
        print("Store info in /usr/bin/userinfo.txt")
        if not os.path.exists('/usr/bin/userinfo.txt'):
            os.system('sudo touch /usr/bin/userinfo.txt && sudo chmod 766 /usr/bin/userinfo.txt')
        with open('/usr/bin/userinfo.txt', 'w') as uif:
            uif.write(username+'\n'+password+'\n')
    else:
        # print("Make sure you UserName & PassWord in file `userinfo.txt` is Right")
        with open('/usr/bin/userinfo.txt', 'r') as uif:
            username = uif.readline().strip()
            password = uif.readline().strip()

    if username == "" or password == "":
        print("Username or Password cannot be empty.")
        print("Please Check Your Input or File `userinfo.txt` ")
        username = raw_input("UserName: ")
        password = raw_input("PassWord: ")
        with open('/usr/bin/userinfo.txt', 'w') as uif:
            uif.write(username+'\n'+password+'\n')
        sys.exit()
    
    print("Logining Now, Just Waiting a second ...\n")
    client = Portal()
    client.re_login_by_time_out(username, password)
    #client.do_heart_beat()

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests
import time
from base64 import b64encode
from bs4 import BeautifulSoup
import sys

# Constant Variable

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except :
    pass

userName = ""
userPwd = ""
serviceType = ""
isSavePwd = "on"

isQuickAuth = "false"
language = "English"
browserFinalUrl = ""
userip = "null"

cookie_hello1 = userName # document.getElementById("is_userName").value
cookie_hello2 = False # document.getElementById("id_isSavePwd").checked
cookie_hello3 = "" # encrypt(document.getElementById("id_userPwd").value)
cookie_hello4 = "" # document.getElementById("id_serviceType").value

def encrypt(password):
    ret = ""
    str = password
    for each in str:
        ret += unichr(ord(each)^0xff)
    return ret


class Portal(object):
    _VERSION = '0.0.14'

    HOST = '172.20.1.1'
    ROOT_URL = r'http://172.20.1.1/portal/'
    INDEX_URL = ROOT_URL + 'index_default.jsp'
    LOGIN_URL = ROOT_URL + 'login.jsp'
    LOGOUT_URL = ROOT_URL + 'logout.jsp'

    ONLINE_URL = ROOT_URL + 'online.jsp'
    
    ONLINE_HEARTBEAT_URL = ROOT_URL + 'online_heartBeat.jsp'
    ONLINE_SHOWTIMER_URL = ROOT_URL + 'online_showTimer.jsp'
    ONLINE_FUNCTIONBUTTON_URL = ROOT_URL + 'online_funcButton.jsp'

    TIME_OUT = 24000

    def __init__(self):
        self.__username = ''
        self.__password = ''
        self.__password_encrypt = ''

        self.__req = requests.Session()
        self.__req.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'
        # self.get_index_info()
        self.__ip = 'null'
        self.__login_success_html = ''
        # record whether is logined
        self.__is_logined = False
        #
        self.__heartBeat_data = ''
        self.__showTimer_data = ''
        self.__funcButton_data = ''
        self.__time_out = 60 # 240 # 掉线时间s
        # cookie
        self.__cookies = ''
        # headers
        self.__headers = dict()

    def get_ip(self):
        from socket import socket
        from socket import AF_INET, SOCK_DGRAM
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect((Portal.HOST, 0))
        return s.getsockname()[0]

    def checkLogin(self):
        # print BeautifulSoup(self.__req.post(Portal.ONLINE_URL).content)
        try:
            status = requests.head(r'http://www.pku.edu.cn/', timeout=15)
            if status.status_code != 200:
                return False # offline.
            return True # online
        except :
            return False

    def logout(self):
        '''
            whatever it had logined, logout
            2 results:
                1. User is offline.
                2. Logged out successfully.
        '''
        try:
            source_html = self.__req.get(Portal.LOGOUT_URL, timeout=10).content
        except :
            print("Connected to QDU Teaching Area Portal Failed...")
            sys.exit(-1)

        beautiful_html = BeautifulSoup(source_html)
        message = beautiful_html.find('div').text.strip()
        self.__is_logined = False
        print(message)
        return message
        

    def get_index_info(self):
        index_html = ''
        try:
            index_html = self.__req.get(Portal.INDEX_URL)
        except :
            try:
                index_html = self.__req.get(Portal.INDEX_URL)
            except :
                return '尝试失败'

        #print(index_html.cookies
        index_beautiful = BeautifulSoup(index_html.content)
        info = index_beautiful.findAll('input')
        return info

    def add_cookie_to_headers(self):
        JSESSIONID = self.__req.cookies.get_dict()['JSESSIONID']
        #cookie = 'hello1={0}; hello2=true; hello3={1}; hello4=; JSESSIONID={2}'.format(self.__username, self.__password_encrypt, JSESSIONID)
        cookie = 'hello1={0}; hello2=false; hello3=; hello4=; JSESSIONID={1}'.format(self.__username, JSESSIONID)
        self.__req.headers['Referer'] = 'http://172.20.1.1/portal/index_default.jsp'
        self.__req.headers['Cookie'] = cookie
        self.__req.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'
        self.__req.headers['Connection'] = 'keep-alive'
        self.__req.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

        cookies = {
            'hello1': self.__username,
            'hello2': 'false',
            'hello3': '',
            'hello4': '',
            'JSESSIONID': JSESSIONID
            }
        self.__cookies = cookies

    def online_post_after_login(self):
        '''must after login successfully.'''
        html = requests.post(Portal.ONLINE_URL, data=self.__heartBeat_data)
        return html

    def login(self, username, password, times=1):
        '''
            Before login, you had better logout.
            Fortunately, we will do logout action instead of you self.
        '''
        self.__username = username
        self.__password = password
        self.__password_encrypt = encrypt(password)

        # check online or not
        if self.checkLogin():
            print('Times %s: User Online Nowing' % times)
            return

        # whatever it had logined, logout
        # self.logout()
        self.get_index_info()
        self.add_cookie_to_headers()
        
        password = b64encode(password)

        if self.__ip == 'null':
            self.__ip = self.get_ip()
        if self.__ip == '127.0.0.1' or self.__ip == '0.0.0.0':
            self.__ip = 'null'

        payload = {
            'userName':username,
            'userPwd':password,
            'serviceType':serviceType,
            'isSavePwd':isSavePwd,
            'isQuickAuth':isQuickAuth,
            'language':language,
            'browserFinalUrl':browserFinalUrl,
            'userip':self.__ip
        }
        try :
            # html = self.__req.post(Portal.LOGIN_URL, params=payload, cookies=self.__cookies)
            self.__req.get(Portal.INDEX_URL)
            html = self.__req.post(Portal.LOGIN_URL, params=payload)
            #print('in login: ', self.__req.cookies.get_dict())
            #print('in login: ', self.__req.headers)
        except requests.exceptions.ConnectionError:
            print("Times %s: 未接入网络，请检查网线是否接好或无线是否接入" % times)
            time.sleep(10)
            self.login(username, password, times)
            # sys.exit(-1)
        
        beautiful_html = BeautifulSoup(html.content)
        login_message = beautiful_html.find('div').text.strip()
        if 'Logged in successfully.' == login_message:
            self.__is_logined = True
            self.__login_success_html = html.content
            # 获取信息
            self.get_login_info()
            # 到online界面
            print('Times %s: Logged in successfully.' % times)
            # 
            self.online_post_after_login()
        else:
            print('Times %s: Logged in failed.\nMessage: %s' % (times, login_message))
            sys.exit(-1)

        # keep login success html

        return html
        
        # with open('t.html', 'w+') as t:
        #    t.write(html.content)

    def re_login_by_time_out(self, username, password):
        '''this may be a little silly, had better not do it'''
        times = 0
        while True:
            times += 1
            self.login(username, password, times)
            # time.sleep(self.__time_out * 3)
            time.sleep(self.__time_out)

    def get_login_info(self):
        # 
        # if not self.__is_logined:
        #    username = raw_input('Username: ')
        #    password = raw_input('Password: ')
        #    self.login(username, password)
        #    time.sleep(3)
        
        html = self.__login_success_html
        beautiful_html = BeautifulSoup(html)
        info = beautiful_html.findAll('input')
        info_list = list()
        for each in info:
            tmp = dict()
            tmp[each.attrs['name']] = each.attrs['value']
            info_list.append(tmp)

        info_dict = {
            'language': info_list[0]['language'],
            'heartbeatCyc': info_list[1]['heartbeatCyc'],
            'heartBeatTimeoutMaxTime': info_list[2]['heartBeatTimeoutMaxTime'],
            'userDevPort': info_list[3]['userDevPort'],
            'userStatus': info_list[4]['userStatus'],
            'userip': self.__ip, #info_list[5]['userip'],
            'serialNo': info_list[6]['serialNo']
        }
        # keep heartbeatCyc 
        startTime = str(int(float(time.time()) * 1000))# [:13]
        # self.__time_out = int(info_list[1]['heartbeatCyc']) / 1000
        self.__heartBeat_data = info_dict
        self.__showTimer_data = {
                        'language': info_dict['language'], 
                        'startTime': startTime
                        }
        self.__funcButton_data = {
                        'language':info_dict['language'], 
                        'userip':info_dict['userip'],
                        'serialNo':info_dict['serialNo']
                        }

        return info_dict

    def do_heart_beat(self):
        if not self.__is_logined:
            username = raw_input('Username: ')
            password = raw_input('Password: ')
            self.login(username, password)
            time.sleep(3)

        #if self._heart_beat_data == '':
        #    self.get_login_info()

        while True:
            time.sleep(self.__time_out)
            self.online_heartBeat()
            # self.online_showTimer()
            # self.online_funcButton()
            #print('heart beat')
        # time.sleep(3)
        # self.logout()
        # time.sleep(3)
        # html = self.__req.post(Portal.HEART_BEAT_URL, params=self._heart_beat_data)
        # html = requests.post(Portal.HEART_BEAT_URL, params=self._heart_beat_data)
        # print(html.url)

        # return html

    def online_heartBeat(self):
        #print(self.__req.cookies.get_dict())
        #print(self.__req.headers)
        html = self.__req.post(Portal.ONLINE_HEARTBEAT_URL, data=self.__heartBeat_data)
        # print(self.__req.url)
        #print(html.url)
        #print(BeautifulSoup(html.content))
        return html

    def online_showTimer(self):
        self.__showTimer_data['startTime'] = str(int(float(time.time()) * 1000))
        html = self.__req.get(Portal.ONLINE_SHOWTIMER_URL, params=self.__showTimer_data)
        return html

    def online_funcButton(self):
        html = self.__req.get(Portal.ONLINE_FUNCTIONBUTTON_URL, params=self.__funcButton_data)
        return html


if __name__ == '__main__':
    import os

    username = None
    password = None
    if not os.path.isfile('/usr/bin/userinfo.txt'):
        print("First Use This Script!!!")
        username = raw_input("UserName: ")
        password = raw_input("PassWord: ")
        if not os.path.exists('/usr/bin/userinfo.txt'):
            os.system('sudo touch /usr/bin/userinfo.txt && sudo chmod 766 /usr/bin/userinfo.txt')
        with open('/usr/bin/userinfo.txt', 'w') as uif:
            uif.write(username+'\n'+password+'\n')
    else:
        print("Make sure you UserName & PassWord in file `userinfo.txt` is Right")
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
    
    client = Portal()
    client.re_login_by_time_out(username, password)
    #client.do_heart_beat()

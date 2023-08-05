#!/usr/bin/env python
#coding=utf-8

from StringIO import StringIO
import sys
import os
import re
import json

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import requests
from PIL import Image # install pillow
import pytesseract

class SchoolNet(object):
	'''
		Login School Net
	'''
	__index_url = r'http://192.168.3.11:7001/QDHWSingle/login.jsp'
	__login_url = r'http://192.168.3.11:7001/QDHWSingle/login.do'
	__captcha_url = r'http://192.168.3.11:7001/QDHWSingle/ValidateCodeServlet?action=ShowValidateCode1'

	def __init__(self):
		self.__logName = None
		self.__logPW = None
		self.__validatecode = None
		self.__req_session = requests.Session()

                self.__login_return_html = None
                self.__login_return_message = None

	def get_captcha(self):
		'''
			Get captcha
		'''
                try:
		    self.__req_session.get(SchoolNet.__index_url, timeout=5)
		    __captcha_img = self.__req_session.get(SchoolNet.__captcha_url, timeout=5)
                except :
                    print('获取验证码失败...')
                    print('大侠，请重新来过！')
                    sys.exit(-1)
		
		img_file = open("image.jpg", "wb")
		img_file.write(__captcha_img.content)
		img_file.close()

		return StringIO(__captcha_img.content)
        

	def convertImgToString(self):
		# import os
		# cmd = "tesseract image.jpg outputdatabase digits"
		# os.system(cmd)
		# __validatecode = open("outputdatabase.txt").readline()[:4]
		# os.system("rm -rf outputdatabase.txt")
                __validatecode = ''
                try:
                    __validatecode = pytesseract.image_to_string(\
                                        Image.open('image.jpg'))
                except :
                    __validatecode = ''
                    pass

	        if __validatecode == '':
	            if sys.platform == 'win32':
                        os.system('mspaint image.jpg')
                        try:
                            __validatecode = raw_input("Auto detect error,"\
                            " try to open image file, and input"\
                            " validatecode: ")
                        except :
                            __validatecode = input("Auto detect error,"\
                            " try to open image file, and input"\
                            " validatecode: ")

		return __validatecode

	def login(self, u, p, c):
		'''
			Login 
		'''
		self.__logName = u
		self.__logPW = p
		self.__validatecode = c
		payload = {
                        'from': 'qd',
			'logName': self.__logName,
			'logPW': self.__logPW,
			'validatecode': self.__validatecode
		}

                result = self.__req_session.post(SchoolNet.__login_url, 
                                                data=payload)
                self.__login_return_html = result.content.decode(result.encoding)\
                                                 .encode(sys.getfilesystemencoding())

                return self.resolve_info()


        def resolve_info(self):
            assert self.__login_return_html
            regSuccess = '<div class="divLoginR3_2">([^"]+)</div>'
            message = re.findall(regSuccess, self.__login_return_html)
            if len(message) <= 0:
                regFail = '<div class="divLoginR4">([^"]+)</div>'
                message = re.findall(regFail, self.__login_return_html)

            if len(message) <= 0:
                self.__login_return_message = u'登录失败'
            else:
                self.__login_return_message = message[0]
            return self.__login_return_message
            

	def already_logined(self):
		__success_url = r'http://192.168.3.11:7001/QDHWSingle/successqd.jsp'

                try:
		    __html = self.__req_session.get(__success_url,
                                                    timeout=5)
                except:
                    print('检查失败！（大概未连接校园网！）')
                    return False

                if __html.content.find('logoff.do') != -1:
                    return True
                return False

        def logout(self):
            requests.get('http://192.168.3.11:7001/QDHWSingle/logoff.do')
            print('登录状态: 退出成功!')

if __name__ == '__main__':
	

	data = SchoolNet()

        if data.already_logined():
            print('登录状态, 您已经登录,无需再次登录!')
            try:
                raw_input('任意键退出窗口')
            except:
                input('任意键退出窗口')
            sys.exit(0)

        username = ''
        password = ''
        
        if not os.path.exists('./config.json'):
            with open('config.json', 'w') as fp:
                fp.write('{\n')
                fp.write('\t"username": "用户名",\n')
                fp.write('\t"password": "密码"\n')
                fp.write('}\n')
            print('大人, 您第一次使用!!!')
            print('请修改config.json补全你的登录信息\n')
            try:
                raw_input('任意键退出')
            except:
                input('任意键退出')
            sys.exit(-1)

        try:
            dataString = open('config.json').read()
            dataJson = json.loads(dataString, encoding='utf-8')
            username = dataJson.get('username')
            password = dataJson.get('password')
        except :
            print('Error: 格式错误,请咨询维护者: Cole')
            try:
                raw_input('任意键退出')
            except:
                input('任意键退出')
            sys.exit(-1)

        if not username and not password:
            print('Error: 用户名和密码不能为空')
            try:
                raw_input('任意键退出')
            except:
                input('任意键退出')
            sys.exit(-1)

	data.get_captcha()
	cap = data.convertImgToString()
	e = data.login(username, password, cap)
	
        print("正在登录，请稍后...")
        print("登录状态: %s\n" % e)
        try:
            raw_input('任意键退出')
        except :
            input('任意键退出')


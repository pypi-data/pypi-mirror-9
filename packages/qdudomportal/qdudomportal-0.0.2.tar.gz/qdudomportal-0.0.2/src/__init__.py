#!/usr/bin/env python
# coding=utf-8

import sys
import os
import json
# import time

from .DomPortal_python import SchoolNet

def main():
    data = SchoolNet()

    if data.already_logined():
        print('登录状态, 您已经登录,无需再次登录!')
        raw_input('任意键退出窗口')
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
        raw_input('任意键退出')
        sys.exit(-1)

    try:
        dataString = open('config.json').read()
        dataJson = json.loads(dataString, encoding='utf-8')
        username = dataJson.get('username')
        password = dataJson.get('password')
    except :
        print('Error: 格式错误,请咨询维护者: Cole')
        raw_input('任意键退出')
        sys.exit(-1)

    if not username and not password:
        print('Error: 用户名和密码不能为空')
        raw_input('任意键退出')
        sys.exit(-1)

    # cap = input('Validatecode: ')
    # if sys.platform != 'linux2':
    #   cap = raw_input("Not Linux, try to open image file, and input validatecode: ")
    # else:
    data.get_captcha()
    cap = data.convertImgToString()
    e = data.login(username, password, cap)
    
    print("正在登录，请稍后...")
    print("登录状态: %s\n" % e)
    try:
        raw_input('任意键退出')
    except :
        input('任意键退出')

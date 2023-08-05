#!/usr/bin/env python
# coding=utf-8

import sys
import os
import json
# import time

from .DomPortal_python import SchoolNet

def main():
    print("\n****************************************\n")
    print("* Welcome to QDU Dormitory Area Portal *\n")
    print("*             -- powered by Cole Smith *\n")
    print("****************************************\n")

    data = SchoolNet()
    print('初始化成功.')
    print('正在检查是否已经登陆...')

    if data.already_logined():
        print('登录状态, 您已经登录,无需再次登录!')
        raw_input('任意键退出窗口')
        sys.exit(0)

    username = ''
    password = ''

    if sys.platform != 'win32':
        config_file = '/usr/bin/qdudomportal.conf'
    else:
        config_file = r'C://qdudomportal.conf'
    
    if not os.path.exists(config_file):
        print('大人, 您第一次使用!!! 正在保存基本资料。。。')
        os.system('sudo touch %s' % config_file)
        os.system('sudo chmod +666 %s' % config_file)
        with open(config_file, 'w') as fp:
            fp.write('{\n')
            fp.write('\t"username": "用户名",\n')
            fp.write('\t"password": "密码"\n')
            fp.write('}\n')
        print('请修改 %s, 补全你的登录信息\n' % config_file)
        raw_input('任意键退出')
        sys.exit(-1)

    try:
        dataString = open(config_file).read()
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
    print('正在获取验证码...')
    data.get_captcha()
    cap = data.convertImgToString()
    print('正在登陆...')
    e = data.login(username, password, cap)
    
    print("正在登录，请稍后...")
    print("登录状态: %s\n" % e)
    if e == u'登录失败':
        print('自动登陆失败，请少侠重新尝试！')
    try:
        raw_input('任意键退出')
    except :
        input('任意键退出')

if __name__ == '__main__':
    main()

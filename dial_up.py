#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: classmate lin
@contact: 406728295@qq.com
@file: dial_up.py
@time: 2018/12/17 上午11:00
@desc: 自动拨号脚本
"""

import requests
import socket
import uuid
import time
import logging


# 日志配置
logging.basicConfig(filename='dial_up.log', level=logging.INFO,
                    format='%(asctime)s  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

socket.setdefaulttimeout(5)

CMCC = 1  # 电信

TELECOM = 2  # 移动

HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Host": "10.0.0.37",
        "Referer": "http://10.0.0.37/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/70.0.3538.67 Safari/537.36"
    }

LOGIN_HOST = ('10.0.0.37', 80)

TEST_URL = "http://www.baidu.com"


def get_localhost_mac():
    """
    获取MAC地址
    :return:
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def get_localhost_ip():
    """
    获取用于访问拨号页面时的IP。
    :return:
    """
    sock = socket.socket()
    sock.connect(LOGIN_HOST)
    return sock.getsockname()[0]


def get_login_url(mac, ip):
    """
    构造登陆URL
    :param mac:
    :param ip:
    :return:
    """
    login_url = "http://10.0.0.37:801/eportal/?c=ACSetting&a=Login&protocol=http:&hostname=10.0.0.37&iTermType=1" \
                "&wlanuserip={}&wlanacip=null&wlanacname=null&mac={}&ip={}&enAdvert=0&queryACIP=0&loginMethod=1".\
                format(ip, mac, ip)
    return login_url


def get_login_data(user, pwd, login_type=TELECOM):
    """
    :param user: 用户
    :param pwd: 密码
    :param login_type: 拨号类型
    :return:
    """
    login_data = {
        "DDDDD": "",
        "upass": pwd,
        "R1": "0",
        "R2": "0",
        "R3": "0",
        "R6": "0",
        "para": "00",
        "0MKKey": "123456",
        "buttonClicked": "",
        "redirect_url": "",
        "err_flag": "",
        "username": "",
        "password": "",
        "user": "",
        "cmd": "",
        "Login": ""
    }
    if login_type == TELECOM:   # 电信
        login_data['DDDDD'] = "{}@telecom".format(user)

    elif login_type == CMCC:    # 移动
        login_data['DDDDD'] = "{}@cmcc".format(user)

    return login_data


def login(user, pwd, login_type=TELECOM):
    """
    拨号登陆
    :param user:
    :param pwd:
    :param login_type:
    :return:
    """
    msg = "login....."
    logging.info(msg)
    url = get_login_url(mac=get_localhost_mac(), ip=get_localhost_ip())
    data = get_login_data(user, pwd, login_type=login_type)
    response = requests.post(url=url, data=data, headers=HEADERS)
    if response.status_code == 200 and test_connect():
        msg = 'login success...'
        logging.info(msg=msg)
        return True
    elif response.status_code != 200 and test_connect():
        msg = 'login failed, but connect is ok.....'
        logging.info(msg)
        return False
    else:
        msg = "login failed, can't connect network."
        logging.info(msg)
        return False


def test_connect():
    """
    访问外网，测试是否已经连上网络
    :return:
    """
    msg = "test network connection at http://www.baidu.com..."
    logging.info(msg=msg)
    try:
        response = requests.get(TEST_URL)
        if response.status_code == 200:
            msg = 'connect http://www.baidu.com 200 ok...'
            logging.info(msg)
            return True
    except requests.exceptions.Timeout:
        msg = 'connect http://www.baidu.com timeout...'
        logging.info(msg)
        return False
    except:
        msg = 'service error...'
        logging.debug(msg=msg)
        return False



def login_forever(user, pwd, login_type=TELECOM, timeout=5):
    """
    登陆，以及轮询是否断线，是则重新连接
    :param user:
    :param pwd:
    :param login_type:
    :param timeout:
    :return:
    """
    while True:
        try:
            if test_connect():
                pass
            else:
                login(user, pwd, login_type=login_type)
        except:
            pass
        time.sleep(timeout)


# 允许导入的内容
__all__ = (login_forever, login)


# 允许导入的内容
__all__ = (login_forever, login)


if __name__ == '__main__':
    username = ""
    password = ""
    logging.info(msg='service start...')
    print('server running....')
    login_forever(username, password, login_type=TELECOM, timeout=3)

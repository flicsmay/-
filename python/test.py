# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from PIL import Image
import configparser

DOWNLOAD_URL = 'https://www.zhihu.com/#signin'

ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
ACCEPT_ENCODING = 'gzip, deflate, sdch'
ACCEPT_LANGUAGE = 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'

HEADER = {
    'Accept': ACCEPT,
    'Accept-Encoding': ACCEPT_ENCODING,
    'Accept-Language': ACCEPT_LANGUAGE,
    'User-Agent': USER_AGENT
}


def download_page(url):

    req = requests.get(url, headers=HEADER, verify=False)
    try:
        req.raise_for_status()
    except Exception as exc:
        print('There was a err: %s' % exc)
    data = req.content
    return data


def save_cookies(session):
    config = configparser.ConfigParser()
    config['COOKIES'] = session.cookies.get_dict()
    with open('cookie.ini', 'w') as config_file:
        config.write(config_file)


def load_cookies(session):
    config = configparser.ConfigParser()
    config.read('cookie.ini')
    for key in config['COOKIES']:
        try:
            session.cookies.set(key, config['COOKIES'][key])
        except:
            continue


def get_xsrf(html):
    """get the _xsrf which is dynamic changes over times you get in"""

    soup = BeautifulSoup(html, 'html.parser')
    _xsrf = soup.find('input', attrs={'type': 'hidden', 'name': '_xsrf'})['value']
    return _xsrf


def is_login(session):
    test_url = 'https://www.zhihu.com/settings/profile'
    login_code = session.get(test_url, allow_redirects=False, verify=False, headers=HEADER).status_code
    if int(login_code) == requests.codes.ok:
        return True
    else:
        return False


def get_captcha(session):
    t = str(int(time.time()*1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=HEADER, verify=False)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    im = Image.open('captcha.jpg')
    im.show()
    im.close()
    captcha = input('Please input the captcha:')
    return captcha


def login_in(account, password, session):

    target_url = 'http://www.zhihu.com'
    login_in_html = download_page(target_url)
    if re.match(r"^1\d{10}$", account):
        post_url = 'http://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf': get_xsrf(login_in_html),
            'password': password,
            'remember_me': 'true',
            'phone_num': account
        }
    else:
        post_url = 'http://www.zhihu.com/login/email'
        post_data = {
            '_xsrf': get_xsrf(login_in_html),
            'password': password,
            'remember_me': 'true',
            'email': account
        }
    try:
        login_page = session.post(post_url, data=post_data, headers=HEADER)
        json_return = json.loads(login_page.content.decode('utf-8'))
        print(json_return['msg'])
    except:
        post_data['captcha'] = get_captcha(session)
        login_page = session.post(post_url, data=post_data, headers=HEADER)
        json_return = json.loads(login_page.content.decode('utf-8'))
        print(json_return['msg'])
    if 'errcode' in json_return:
        print('fail to login')
        return False
    else:
        save_cookies(session)
        return True


def main():
    session = requests.session()
    people = 'https://www.zhihu.com/people/minmin.gong/activities'
    load_cookies(session)
    if is_login(session):
        print('login in successful')
    else:
        print('fail to login')
        account = input('please input your account')
        pwd = input('please input your password')
        login_in(account, pwd, session)
    session.get('https://www.zhihu.com', headers=HEADER)
    session.get('https://www.zhihu.com/people/minmin.gong', headers=HEADER)
    data = 'start=1478112898'
    html_content = session.post(people, data, headers=HEADER)
    with open('save.txt', 'wb') as fp:
        fp.write(html_content.content)


if __name__ == '__main__':
    main()

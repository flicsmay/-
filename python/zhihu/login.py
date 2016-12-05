from bs4 import BeautifulSoup
import json
import configparser
import time
from PIL import Image
import re
import requests
from download_pages import download_page

from config import COOKIE_SAVE_FILE, CONFIG_TITLE, CAPTCHA_FILE, HEADER, VERIFY


def save_cookies_to_config(session):
    """save cookie to a file with config title"""
    config = configparser.ConfigParser()
    config[CONFIG_TITLE] = session.cookies.get_dict()
    with open(COOKIE_SAVE_FILE , 'w') as config_file:
        config.write(config_file)


def load_cookies_from_config(session):
    """get cookies from cookie saved file"""
    config = configparser.ConfigParser()
    if not config.read(COOKIE_SAVE_FILE):
        return False
    for key in config[CONFIG_TITLE]:
        try:
            session.cookies.set(key, config[CONFIG_TITLE][key])
        except:
            continue


def get_xsrf(html):
    """get the _xsrf which is dynamic changes over times you get in"""
    soup = BeautifulSoup(html, 'html.parser')
    _xsrf = soup.find('input', attrs={'type': 'hidden', 'name': '_xsrf'})['value']
    # <input type="hidden" name="_xsrf" value="272521a9872250b39253957f1e6df46a"/>
    return _xsrf


def get_captcha(session):
    """get captcha if needed"""
    t = str(int(time.time()*1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=HEADER, verify=VERIFY)
    with open(CAPTCHA_FILE, 'wb') as f:
        f.write(r.content)
        f.close()
    with Image.open(CAPTCHA_FILE) as im:
        im.show()
        im.close()
    captcha = input('Please input the captcha:')
    return captcha


def is_login(session):
    """return true if is login successful"""
    test_url = 'https://www.zhihu.com/settings/profile'
    # using profile page to check login status
    login_code = session.get(test_url, allow_redirects=False, headers=HEADER, verify=VERIFY).status_code
    if int(login_code) == requests.codes.ok:
        return True
    else:
        return False


def login_in(account, password, session):
    """try to login zhihu.com"""
    target_url = 'http://www.zhihu.com'
    login_in_html = download_page(target_url)
    if re.match(r"^1\d{10}$", account):  # if using phone number account
        login_method = 'phone_num'
    else: # using email account
        login_method = 'email'
    post_url = 'https://www.zhihu.com/login/' + login_method
    post_data = {
        '_xsrf': get_xsrf(login_in_html),
        'password': password,
        'remember_me': 'true',
        login_method: account
    }
    try:
        login_return = session.post(post_url, data=post_data, headers=HEADER)
        json_return = json.loads(login_return.content.decode('utf-8'))
        print(json_return['msg'])
    except:  # else get captcha
        post_data['captcha'] = get_captcha(session)
        login_return = session.post(post_url, data=post_data, headers=HEADER)
        json_return = json.loads(login_return.content.decode('utf-8'))
        print(json_return['msg'])
    if 'errcode' in json_return:
        print('fail to login')
        return False
    else:
        save_cookies_to_config(session)
        return True


def login(session):
    load_cookies_from_config(session)
    if is_login(session):
        print('login in successful')
        return True
    else:
        print('not useful cookie found')
        account = input('please input your account')
        pwd = input('please input your password')
        return login_in(account, pwd, session)

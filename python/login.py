# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json
from PIL import Image
import configparser
import time
import codecs
from pymongo import MongoClient

PEOPLE = 'li-feng-xie'
CATCH_FORM_MID = False
RESUME_TIME = '0'
SAVE_FILE_CATCH = 'lee.txt'
SLEEP_TIME = 1


ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
ACCEPT_ENCODING = 'gzip, deflate, sdch'
ACCEPT_LANGUAGE = 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'

BASE_URL = 'https://www.zhihu.com'
PEOPLE_URL = BASE_URL + '/people/' + PEOPLE

HEADER = {
    'Accept': ACCEPT,
    'Accept-Encoding': ACCEPT_ENCODING,
    'Accept-Language': ACCEPT_LANGUAGE,
    'User-Agent': USER_AGENT
}

MONGO_CONN = MongoClient('localhost', 27017)
DATA_BASE = MONGO_CONN['time_line_DB']
DAYS_COLLECTION = DATA_BASE['days_collection']


def download_page(url):

    req = requests.get(url, headers=HEADER, verify=False)
    try:
        req.raise_for_status()
    except Exception as exc:
        print('There was a err: %s' % exc)
    data = req.content
    return data


def make_single_dict(tag_list):
    tag_to_1_dict = {}
    for tag in tag_list:
        tag_to_1_dict[tag] = 1
    return tag_to_1_dict


def add_y_dict_to_x_dict(x, y):
    for k, v in y.items():
        if k in x.keys():
            x[k] += v
        else:
            x[k] = v


def get_tag_from_question(question_url, header):
    tag_list = []
    soup = BeautifulSoup(download_page(question_url, header))
    tag_tags = soup.find_all('a', attrs={'class': 'zm-item-tag'})
    for tag in tag_tags:
        tag_list.append(tag['href'])
    return tag_list


def assemble_by_day(file_name, header):
    skip_request = ('follow_column', 'follow_favlist', 'voteup_article'
                    'join_live', 'collect_answer', 'follow_topic')

    posts = {'_id': 'first'}
    current_day = 0
    counter = 0
    with codecs.open(file_name, 'rb', encoding='utf-8') as fp:
        for each_line in fp:
            data_list = each_line.split('|')
            activity = data_list[1][7:]
            date = time.localtime(int(data_list[0]))
            formal_time = str(date.tm_year) + '/' + str(date.tm_mon) + '/' + str(date.tm_mday)
            if date.tm_yday != current_day:
                if current_day != 0:
                    posts['counter'] = counter
                    DAYS_COLLECTION.insert(posts)
                current_day = date.tm_yday
                counter = 0
                posts = {
                    '_id': formal_time,
                    'answers': {},
                    'follow': {},
                    'agrees': {},
                    'counter': 0
                }
            counter += 1
            if activity in skip_request:
                continue
            question_url = BASE_URL + data_list[2][:18]
            tag_list = get_tag_from_question(question_url, header)
            tag_dict = make_single_dict(tag_list)
            if activity == 'answer_question':
                add_in_type = 'answers'
            elif activity == 'voteup_answer':
                add_in_type = 'agrees'
            elif activity == 'follow_question':
                add_in_type = 'follow'
            else:
                raise TypeError # 随意raise了一个
            add_y_dict_to_x_dict(posts[add_in_type], tag_dict)




def save_cookies(session):
    config = configparser.ConfigParser()
    config['COOKIES'] = session.cookies.get_dict()
    with open('cookie.ini', 'w') as config_file:
        config.write(config_file)


def load_cookies(session):
    config = configparser.ConfigParser()
    if not config.read('cookie.ini'):
        return
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
        post_url = 'https://www.zhihu.com/login/email'
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


def download_page(url, header):
    req = requests.get(url, headers=header, verify=False)
    try:
        req.raise_for_status()
    except Exception as exc:
        print('There was a err: %s' % exc)
    data = req.content
    return data


def get_time_line(session, people_url, header, mid_starting, start_num):

    if mid_starting:
        mode = 'a'
    else:
        mode = 'wb'
    post_url = people_url + '/' + 'activities'
    json_request_header = header
    json_request_header['X-Xsrftoken'] = session.cookies['_xsrf']
    json_request_header['Referer'] = people_url
    json_request_header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    def has_no_class(tag):
        return not tag.has_attr('class')

    with codecs.open(SAVE_FILE_CATCH, mode, encoding='utf-8') as fp:

        if not mid_starting:
            latest_time = get_latest_activity_time(people_url, header)
        else:
            latest_time = start_num
        post_data = 'start=' + latest_time
        post_return = session.post(post_url, post_data, headers=json_request_header)
        json_return = json.loads(post_return.content.decode('utf-8'))
        while json_return['msg'][0] != 0:
            all_html = json_return['msg'][1]
            soup = BeautifulSoup(all_html, 'html.parser')
            answer_set = soup.find_all('div', attrs={'class': 'zm-profile-section-item zm-item clearfix'})
            for html in answer_set:
                date_time = html['data-time']
                detail = html['data-type-detail']
                type_list = detail.split('_')
                if type_list[2] == 'answer' or type_list[2] == 'question': # 关注问题/赞同回答
                    url_tag = html.find('a', attrs={'class': 'question_link'})
                elif type_list[2] == 'article': # 赞同文章
                    url_tag = html.find('a', attrs={'class': 'post-link'})
                elif type_list[2] == 'topic':# 关注话题
                    url_tag = html.find('a', attrs={'class': 'topic-link'})
                elif type_list[2] == 'favlist': # 关注收藏夹
                    url_tag = html.find_all(has_no_class)[0]
                elif type_list[2] == 'live': # 参加了live
                    url_tag = html.find('a', attrs={'target': '_blank'})
                elif type_list[2] == 'column' and type_list[1] == 'follow': # 关注专栏
                    url_tag = html.find('a', attrs={'class': 'column_link'})
                elif type_list[1] == 'collect': # 收藏答案
                    url_tag = html.find('a', attrs={'class': 'question-link'})
                else: # 圆桌
                    url_tag = html.find('a', attrs={'class': 'roundtable_link'})
                url = url_tag['href']
                fp.write(u'{time}|{type}|{url}\n'.format(time=date_time, type=detail, url=url))
            post_data = 'start=' + date_time
            post_return = session.post(post_url, post_data, headers=json_request_header)
            json_return = json.loads(post_return.content.decode('utf-8'))
            time.sleep(SLEEP_TIME)


def get_latest_activity_time(people_url, header):

    soup = BeautifulSoup(download_page(people_url, header), 'html.parser')
    latest_activity = soup.find('div', attrs={'class': 'zm-profile-section-item zm-item clearfix'})
    return latest_activity['data-time']


def url_text(header, session, url, post_text):
    json_request_header = header
    json_request_header['X-Xsrftoken'] = session.cookies['_xsrf']
    json_request_header['Referer'] = url
    json_request_header['Content-Type'] =  'application/x-www-form-urlencoded; charset=UTF-8'
    session.get(url, headers= header)
    post_data = 'start=' +  post_text
    post_return = session.post(url + '/activities', post_data, headers=json_request_header)
    json_return = json.loads(post_return.content.decode('utf-8'))
    print(json_return)


def main():
    session = requests.session()
    load_cookies(session)
    if is_login(session):
        print('login in successful')
    else:
        print('fail to login')
        account = input('please input your account')
        pwd = input('please input your password')
        login_in(account, pwd, session)
    assemble_by_day(SAVE_FILE_CATCH, HEADER)
    # url_text(HEADER, session, PEOPLE_URL, '1476599999')
    # get_time_line(session, PEOPLE_URL, HEADER, CATCH_FORM_MID, RESUME_TIME)


if __name__ == '__main__':
    main()

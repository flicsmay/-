# -*- coding:utf-8 -*-

"""
 抓取知乎的timeliness保存在本地，需要安装mongodb
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import codecs
from pymongo import MongoClient
from download_pages import download_page
from config import BASE_URL


PEOPLE = ''
CATCH_FORM_MID = True
RESUME_TIME = 0
SAVE_FILE_CATCH = 'save.txt'
SLEEP_TIME = 0.5
VERIFY = True
SCORE_FILE = 'score.txt'
AGREE_SCORE = 2
FOLLOW_SCORE = 5
ANSWER_SCORE = 20

QUESTION_DICT = {}

DAYS_TYPE = 'DAYS'
WEEKS_TYPE = 'WEEKS'
MONTHS_TYPE = 'MONTHS'
SEASONS_TYPE = 'SEASON'
YEARS_TYPE = 'YEARS'

MONGO_CONN = MongoClient('localhost', 27017)
DATA_BASE = MONGO_CONN['time_line_DB']
DAYS_COLLECTION = DATA_BASE['days_collection' + PEOPLE]
WEEKS_COLLECTION = DATA_BASE['weeks_collection' + PEOPLE]
MONTHS_COLLECTION = DATA_BASE['months_collection' + PEOPLE]
SEASONS_COLLECTION = DATA_BASE['season_collection' + PEOPLE]
YEARS_COLLECTION = DATA_BASE['years_collection' + PEOPLE]

TAG_CACHE = {}


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
    """从url中得到标签"""
    tag_list = []
    if question_url in QUESTION_DICT:
        tag_list = QUESTION_DICT[question_url]
        print('getting from cache')
    else:
        soup = BeautifulSoup(download_page(question_url), 'html.parser')
        tags_found = soup.find_all('a', attrs={'class': 'zm-item-tag'})
        for tag in tags_found:
            tag_list.append(tag['href'])
        QUESTION_DICT[question_url] = tag_list
    return tag_list


def assemble_by_day(file_name, header, collection, starting_from_mid, last_time):
    skip_request = ('follow_column', 'follow_favlist', 'voteup_article', 'create_article',
                    'join_live', 'collect_answer', 'follow_topic', 'collect_article', 'ask_question')

    posts = {'_id': 'first'}
    current_day = -1
    counter = 0
    with codecs.open(file_name, 'rb', encoding='utf-8') as fp:
        for each_line in fp:
            data_list = each_line.split('|')
            if starting_from_mid:
                if int(data_list[0]) > last_time:
                    print('skipping before')
                    continue
            date = time.localtime(int(data_list[0]))
            activity = data_list[1][7:]
            formal_time = str(date.tm_year) + '/' + str(date.tm_mon) + '/' + str(date.tm_mday)
            if date.tm_yday != current_day:
                if current_day != -1:
                    posts['counter'] = counter
                    collection.insert(posts)
                    print('saving %s in %s' % (posts['_id'], data_list[0]))
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
                print('skipping %s' % activity)
                continue
            question_url = BASE_URL + data_list[2][:18]
            print(question_url)
            tag_list = get_tag_from_question(question_url, header)
            tag_dict = make_single_dict(tag_list)
            if activity == 'answer_question':
                add_in_type = 'answers'
            elif activity == 'voteup_answer':
                add_in_type = 'agrees'
            elif activity == 'follow_question':
                add_in_type = 'follow'
            else:
                print(activity)
                raise TypeError # 随意raise了一个
            add_y_dict_to_x_dict(posts[add_in_type], tag_dict) # add to posts
            time.sleep(SLEEP_TIME)



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


def merge_two_days(day_one, day_two):
    day_one['counter'] += day_two['counter']
    add_y_dict_to_x_dict(day_one['answers'], day_two['answers'])
    add_y_dict_to_x_dict(day_one['follow'], day_two['follow'])
    add_y_dict_to_x_dict(day_one['agrees'], day_two['agrees'])


def is_in_the_same_week(day1, day2):
    if day1 - day2 > datetime.timedelta(0):
        day1, day2 = day2, day1
    if day2 - day1 > datetime.timedelta(6):
        return False
    if day1.weekday() - day2.weekday() > 0:
        return False
    return True


def is_in_the_same_month(day1, day2):
    return day1.month == day2.month and day1.year == day2.year


def is_in_the_same_season(day1, day2):
    return (day1.month-1) // 3 == (day2.month-1) // 3


def is_in_the_same_year(day1, day2):
    return day1.year == day2.year


def merge_day_message(check_func, get_collection, store_collection, first_day):
    date_time = first_day
    today = datetime.date.today()
    record_day = first_day
    record_msg = {}
    while date_time < today:
        find_dict_patten = {'_id': date_to_times(date_time)}
        date_msg = get_collection.find_one(find_dict_patten)
        if date_msg is None:
            date_time += datetime.timedelta(1)
            continue
        if not check_func(record_day, date_time):
            if 'agrees' in record_msg.keys():
                store_collection.insert(record_msg)
            record_msg = date_msg
            record_day = date_time
        else:
            merge_two_days(record_msg, date_msg)
        date_time += datetime.timedelta(1)

def get_topic(topic_url, header):
    if topic_url in TAG_CACHE:
        tag = TAG_CACHE[topic_url]
        print('getting from cache')
    else:
        print('catching from %s' % topic_url)
        soup = BeautifulSoup(download_page(BASE_URL + topic_url + '/hot', header), 'html.parser')
        tag = soup.find('img', attrs={'class': 'zm-avatar-editor-preview'})['alt']
        TAG_CACHE[topic_url] = tag
    return tag


def count_score(msg, types):
    score_dict = {}
    return_dict = {'date': msg['_id'], 'type': types, 'score': score_dict}
    agree_list = msg['agrees']
    for every_item in agree_list:
        agree_list[every_item] *= AGREE_SCORE
    follow_list = msg['follow']
    for every_item in follow_list:
        follow_list[every_item] *= FOLLOW_SCORE
    answer_list = msg['answers']
    for every_item in answer_list:
        answer_list[every_item] *= ANSWER_SCORE
    add_y_dict_to_x_dict(score_dict, agree_list)
    add_y_dict_to_x_dict(score_dict, follow_list)
    add_y_dict_to_x_dict(score_dict, answer_list)
    return return_dict


def save_score(score_dict, header):
    score = score_dict['score']
    with codecs.open(SCORE_FILE, 'a', encoding='utf-8') as fp:
        fp.write(u'\n{date}: {type}\n'.format(date=score_dict['date'], type=score_dict['type']))
        for each_url in score:
            name = get_topic(each_url, header)
            score_name = score[each_url]
            fp.write(u'{name}:{score}\n'.format(name=name, score=score_name))


def print_collection(collection, header, types):
    for each_msg in collection.find():
        return_dic = count_score(each_msg, types)
        save_score(return_dic, header)


def del_db_collection(collection):
    for every_msg in collection.find():
        dic = {'_id': every_msg['_id']}
        collection.remove(dic)


def print_db_collection(collection):
    for every_msg in collection.find():
        print(every_msg)



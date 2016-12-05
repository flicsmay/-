import codecs
from bs4 import BeautifulSoup
import json
import time
from download_pages import download_page
import os
from config import TIMELINESS_SAVED_FILE, INTERVAL_TIME, SAVE_FILE_FORMAT, HEADER


def get_detail(answer_html_page):

    def has_no_class(tag):
        return not tag.has_attr('class')

    date_time = answer_html_page['data-time']
    detail = answer_html_page['data-type-detail']
    type_list = detail.split('_')
    if type_list[2] == 'answer' or type_list[2] == 'question':  # 关注问题/赞同回答
        url_tag = answer_html_page.find('a', attrs={'class': 'question_link'})
    elif type_list[2] == 'article':  # 赞同文章
        url_tag = answer_html_page.find('a', attrs={'class': 'post-link'})
    elif type_list[2] == 'topic':  # 关注话题
        url_tag = answer_html_page.find('a', attrs={'class': 'topic-link'})
    elif type_list[2] == 'favlist':  # 关注收藏夹
        url_tag = answer_html_page.find_all(has_no_class)[0]
    elif type_list[2] == 'live':  # 参加了live
        url_tag = answer_html_page.find('a', attrs={'target': '_blank'})
    elif type_list[2] == 'column' and type_list[1] == 'follow':  # 关注专栏
        url_tag = answer_html_page.find('a', attrs={'class': 'column_link'})
    elif type_list[1] == 'collect':  # 收藏答案
        url_tag = answer_html_page.find('a', attrs={'class': 'question-link'})
    else:  # 圆桌
        url_tag = answer_html_page.find('a', attrs={'class': 'roundtable_link'})
    url = url_tag['href']
    return date_time, detail, url


def get_timeliness_json(session, people_url, request_header, mode, start_time, ended_time):
    """爬取一个用户的timeliness"""
    post_url = people_url + '/' + 'activities'

    latest_time = start_time
    with codecs.open(TIMELINESS_SAVED_FILE, mode, encoding='utf-8') as fp:
        post_text = 'start=' + latest_time
        post_return = session.post(post_url, post_text, headers=request_header)
        json_return = json.loads(post_return.content.decode('utf-8'))
        date_time = 0
        while json_return['msg'][0] != 0:
            all_html = json_return['msg'][1]
            answer_set = BeautifulSoup(all_html, 'html.parser').\
                find_all('div', attrs={'class': 'zm-profile-section-item zm-item clearfix'})
            for a_single_answer in answer_set:
                (date_time, activities, url) = get_detail(a_single_answer)
                if date_time < ended_time:
                    return
                fp.write(SAVE_FILE_FORMAT.format(time=date_time, type=activities, url=url))
            # just use the last date time to get json
            post_data = 'start=' + date_time
            post_return = session.post(url=post_url, data=post_data, headers=request_header)
            json_return = json.loads(post_return.content.decode('utf-8'))
            time.sleep(INTERVAL_TIME)





def get_latest_activity_time_from_page(people_url, header, verity):
    """return the time that last active"""
    soup = BeautifulSoup(download_page(people_url), 'html.parser')
    latest_activity = soup.find('div', attrs={'class': 'zm-profile-section-item zm-item clearfix'})
    return latest_activity['data-time']


def get_timeliness(people_url, session, save_file, interval_time):
    json_request_header = HEADER
    json_request_header['X-Xsrftoken'] = session.cookies['_xsrf']
    json_request_header['Referer'] = people_url
    json_request_header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

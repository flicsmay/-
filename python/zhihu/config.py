# configure file
# make global var
import os
VERIFY = True

COOKIE_SAVE_FILE = 'cookie.ini'
CONFIG_TITLE = 'COOKIES'
CAPTCHA_FILE = 'captcha.jpg'

TIMELINESS_SAVED_FILE = 'save_file.txt'
INTERVAL_TIME = 2
SAVE_FILE_SPLIT = '|'
SAVE_FILE_FORMAT = u'{time}' +  SAVE_FILE_SPLIT + '{type}' \
                   + SAVE_FILE_SPLIT + '{url}' + os.linesep

PEOPLE = ''

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
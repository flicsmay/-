# -*- coding:utf-8 -*-
# a script to get top 250 movies of douban.com

import requests
from bs4 import BeautifulSoup
import codecs
import time

DOWNLOAD_URL = 'http://movie.douban.com/top250'


def download_page(url):

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'}
    req = requests.get(url, headers=header)
    try:
        req.raise_for_status()
    except Exception as exc:
        print('There was a err: %s' % exc)
    data = req.content
    return data


def parse_html(html):

    soup = BeautifulSoup(html, 'html.parser')

    movie_list_soup = soup.find('ol', attrs={'class': 'grid_view'})

    movie_name_list = []

    for movie_li in movie_list_soup.find_all('li'):

        movie_ranking = movie_li.find('em')
        detail = movie_li.find('div', attrs={'class': 'hd'})
        movie_name = detail.find('span', attrs={'class': 'title'})
        movie_score = movie_li.find('span', attrs={'class': 'rating_num'})

        movie_name_list.append(movie_ranking.get_text() + ' ' + movie_name.get_text() + ' ' + movie_score.get_text())

    next_page = soup.find('span', attrs={'class': 'next'}).find('a')
    if next_page:
        return movie_name_list, DOWNLOAD_URL + next_page['href']
    else:
        return movie_name_list, None


def main():
    url = DOWNLOAD_URL

    with codecs.open('output.txt', 'wb', encoding='utf-8') as fp:
        while url:
            html = download_page(url)
            movies, url = parse_html(html)
            fp.write(u'{movies}\n'.format(movies='\n'.join(movies)))
            print('catching next page...')
            time.sleep(1)


if __name__ == '__main__':
    main()

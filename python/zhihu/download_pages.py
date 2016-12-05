import requests
from config import HEADER, VERIFY


def download_page(url):
    """download a http file from a given url"""
    req = requests.get(url, headers=HEADER, verify=VERIFY)
    try:
        req.raise_for_status()
    except Exception as exc:
        print('There was a err: %s' % exc)
    data = req.content
    return data

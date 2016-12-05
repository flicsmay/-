import configparser
from config import COOKIE_SAVE_FILE


def read_from_config(name):
    config = configparser.ConfigParser()
    if not config.read(COOKIE_SAVE_FILE):
        return False
    for key in config[name]:
        print(key)


def main():
    read_from_config('COOKIES')


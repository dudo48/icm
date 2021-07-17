import time

from scraper import Scraper


def main():
    scraper = Scraper(True)
    scraper.login()


if __name__ == '__main__':
    main()
    time.sleep(10)
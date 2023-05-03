from rss_parser import Parser
import requests
import time
from pprint import pprint

FEED_URL = "https://bpdnews.com/news?format=rss"
KEYWORD = 'journal'

# CHANGE THESE SETTINGS AS YOU DOWNLOAD TO AVOID REDOWNLOADING OLD STUFF

MIN_PAGE = 100
MAX_PAGE = 200
SLEEP_ON_RATELIMIT = 5

def get_filename(path):
    return path.split('/')[-1]

def download_and_save(url):
    response = requests.get(url, allow_redirects=True)
    print(url)
    if response.status_code == 429:
        print('got ratelimited')
        time.sleep(SLEEP_ON_RATELIMIT)
        return download_and_save(url)
    elif response.status_code != 200:
        print('unknown error:', response.status_code)
    with open('pdfs/'+get_filename(url), 'wb') as f:
        f.write(response.content)


def get_feed(page_number):
    url = f"{FEED_URL}&page={page_number}"
    print(url)
    response = requests.get(url)
    if response.status_code == 429:
        print('got ratelimited')
        time.sleep(SLEEP_ON_RATELIMIT)
        return get_feed(page_number)
    elif response.status_code != 200:
        print('unknown error:', response.status_code)
    parser = Parser(xml=response.content)
    return parser.parse()


if __name__ == '__main__':
    file_list = open('files.tsv', 'a')

    for page in range(MIN_PAGE, MAX_PAGE):
        print(f'\n---------\npage: {page}\n---------\n')
        feed = get_feed(page)
        for item in feed.feed:
            if KEYWORD in item.title.lower():
                print(item.title, item.publish_date, *item.description_links, sep='\t', file=file_list)
                for link in item.description_links:
                    download_and_save(link)
        file_list.flush()

    file_list.close()
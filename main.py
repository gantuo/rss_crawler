import feedparser
import urllib.request
from bs4 import BeautifulSoup
import json
import re
import traceback
from datetime import datetime
from time import mktime
import sys
import os

head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}


def from_link(source, link):
    req = urllib.request.Request(link, headers=head)  # 伪造请求头
    response = urllib.request.urlopen(req)
    html = response.read()  # 读取内容
    try:
        html = html.decode('utf-8')
    except:
        html = html.decode('gbk')
    soup = BeautifulSoup(html, 'html.parser')

    if source == '机核':
        tag, attrs = 'span', {'data-text': 'true'}
    else:
        tag, attrs = 'p', None
    text = '\n'.join([item.text for item in soup.find_all(tag, attrs)])
    return text


def from_summary(entry):
    summary = entry['summary_detail']['value']
    text = summary.replace('</p><p>', '\n')
    text = re.sub('<.+>', '', text)
    return text


def parse_entry(source, entry):
    title = entry.title
    link = entry.link

    if source == '36氪':
        text = from_summary(entry)
    else:
        text = from_link(source, link)
    text = post_process(text)
    dt = datetime.fromtimestamp(mktime(entry['published_parsed']))
    return {'title': title, 'date': dt.strftime('%Y-%m-%d %H:%M:%S'), 'text': text}


def filter_text(text):
    if len(text) < 100:
        raise Warning(f'text too short: {text}')
    m = re.findall('[^\n]+?：.+?\n', text, re.S)
    if m:
        matched_text = ''.join(m)
        if len(matched_text) / len(text) > 0.7:
            raise Warning(f'match bad pattern: {text}')


def parse(source, url):
    # 解析RSS源
    rss = feedparser.parse(url, request_headers=head)

    # 获取RSS源的标题、链接、摘要等信息
    items = []
    print(f'feed {source} has {len(rss.entries)} articles')
    for entry in rss.entries:
        try:
            item = parse_entry(source, entry)
            filter_text(item['text'])
            items.append(item)
        except:
            print(traceback.format_exc())
    return items


def post_process(text):
    text = text.replace(u'\xa0', '')
    return re.sub('(\n)+', '\n', text)


def process(input):
    source, url = input
    print(f'processing rss feed: {source}, url: {url}')
    try:
        texts = parse(source, url)
        if len(texts) == 0:
            return
        date = datetime.now().strftime('%Y%m%d')
        path = f'output/{date}/'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(f'{path}/{source}.json', 'w', encoding='utf-8') as f:
            for text in texts:
                try:
                    f.write(json.dumps(text, ensure_ascii=False) + '\n')
                except Exception:
                    print(traceback.format_exc())
    except Exception:
        print(traceback.format_exc())
        print(url)
    print(f'rss feed done: {source}')


def run_par():
    urls = {
        # entertainment
        # 'Variety':'https://variety.com/feed/',
        'The Hollywood Reporter': 'https://www.hollywoodreporter.com/feed/',
        'Screen Rant': 'https://screenrant.com/feed/',
        # fashion
        'Elle Magazine': 'https://www.elle.com/rss/all.xml/',
        # science
        'Scientific American': 'http://rss.sciam.com/ScientificAmerican-Global',

        # 'Nature':'https://www.nature.com/nature.rss',
        'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml?edition=uk',
        'TechCrunch': 'http://feeds.feedburner.com/TechCrunch/',
        'ESPN': 'http://www.espn.com/espn/rss/news',
        'WebMD': 'https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC',
        'The Economist': 'https://www.economist.com/finance-and-economics/rss.xml',
        # 'Edutopia': 'http://www.edutopia.org/rss.xml',
        'Lonely Planet': 'http://www.lonelyplanet.com/rss/feeds.blogs.xml',
    }
    urls_cn = {
        # tech
        "极客公园": "https://www.geekpark.net/rss",
        "爱范儿": "https://www.ifanr.com/feed",
        "36氪": "https://36kr.com/feed-article",
        "虎嗅": "https://rss.huxiu.com/",

        # authority
        "人民网时政新闻": "http://www.people.com.cn/rss/politics.xml",

        # game
        "机核": "https://www.gcores.com/rss",
        "研游社": "https://www.yystv.cn/rss/feed",
        # "触乐": "https://rsshub.app/chuapp/index/daily",
        # animation
        # "005tv": "https://rsshub.app/005tv/zx/latest",
    }

    from multiprocessing import Pool

    # urls.update(urls_cn)
    urls = urls_cn
    # 进程数
    num_workers = len(urls)

    with Pool(num_workers) as p:
        p.map(process, urls.items())


def test():
    # url = ("人民网时政新闻","http://www.people.com.cn/rss/politics.xml")
    url = ("机核", "https://www.gcores.com/rss")
    # url = ("36氪", "https://36kr.com/feed-article")
    # url =("触乐", "https://rsshub.app/chuapp/index/daily")

    process(url)


if __name__ == '__main__':
    run_par()
    # test()

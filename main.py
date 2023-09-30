import feedparser
import urllib.request
from bs4 import BeautifulSoup
import json
import re
import traceback

head = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0..'}


def parse_entry(source, entry):
    title = entry.title
    link = entry.link
    req = urllib.request.Request(link, headers=head)  # 伪造请求头
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')  # 读取内容
    soup = BeautifulSoup(html, 'html.parser')
    text = '\n'.join([item.text for item in soup.find_all('p')])

    return {'title': title, 'date': '', 'text': text}


def parse(source, url):
    # 解析RSS源
    rss = feedparser.parse(url, request_headers=head)

    # 获取RSS源的标题、链接、摘要等信息
    texts = []
    for entry in rss.entries:
        try:
            text = parse_entry(source, entry)
            texts.append(text)
        except:
            traceback.format_exc()
    return texts


def post_process(text):
    return re.sub('(\n.?)+', '\n', text).replace(u'\xa0', '')


if __name__ == '__main__':
    urls = {
        'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml?edition=uk',
        'TechCrunch': 'http://feeds.feedburner.com/TechCrunch/',
        'Scientific American': 'http://rss.sciam.com/ScientificAmerican-Global',
        # 'Vogue': 'http://www.vogue.com/rss',
        'ESPN': 'http://www.espn.com/espn/rss/news',
        # 'Entertainment Weekly': 'https://feeds.feedburner.com/entertainmentweekly',
        'WebMD': 'https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC',
        'The Economist': 'https://www.economist.com/finance-and-economics/rss.xml',
        'Edutopia': 'http://www.edutopia.org/rss.xml',
        'Lonely Planet': 'http://www.lonelyplanet.com/rss/feeds.blogs.xml',
    }

    for source, url in urls.items():
        try:
            texts = parse(source, url)
            if len(texts) == 0:
                continue
            with open(f'output/{source}.json', 'w', encoding='utf-8') as f:
                for text in texts:
                    try:
                        f.write(json.dumps(text, ensure_ascii=False) + '\n')
                    except Exception:
                        print(traceback.format_exc())


        except Exception:
            print(traceback.format_exc())
            print(url)
        print('#####################################################\n')

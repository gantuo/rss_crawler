import re

import requests
from bs4 import BeautifulSoup
from utils import *
import json
import traceback
from multiprocessing import Pool

head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}

# 定义要爬取的网站主页URL
base_url = 'https://www.gcores.com'  # 替换为你要爬取的网站的URL


# 创建一个函数来获取每一页的文章链接
def get_article_links(page_url):
    response = requests.get(page_url, headers=head)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 通过分析网页结构来找到文章链接的HTML元素
        article_links = soup.find_all('a', href=re.compile('^/articles/\d+'))  # 请根据实际情况进行调整
        # 提取每篇文章的URL
        article_links = list(filter(lambda x: not 'class' in x.attrs, article_links))
        article_urls = [link['href'] for link in article_links]
        return article_urls
    else:
        print("请求失败，状态码:", response.status_code)
        return []


# 创建一个函数来获取每篇文章的内容
def get_article_content(article_url):
    full_url = base_url + article_url
    response = requests.get(full_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 通过分析网页结构来找到文章内容的HTML元素
        # title:  <h1 class="originalPage_title">《往日之影》游戏摄影——狗镇及支线：All the Pieces Matter</h1>
        title = soup.find('h1', {'class': 'originalPage_title'}).text
        # date:  <span class="me-2 u_color-gray-info" title="2023-10-14 11:00:00">1 小时前</span>
        date_info = soup.find('span', {"class": "me-2 u_color-gray-info"},
                              title=re.compile('\d{4}-\d+-\d+ \d{2}:\d{2}:\d{2}'))
        date = date_info.attrs['title']
        # text
        article_pieces = soup.find_all('span', {'data-text': 'true'})  # 请根据实际情况进行调整
        if article_pieces:
            article_content = '\n'.join([piece.text for piece in article_pieces])
            return title, date, article_content
        else:
            print("未找到文章内容")
            return None
    else:
        print("请求失败，状态码:", response.status_code)
        return None


def process(page):
    print(f'getting page: {page}')
    page_url = f'{base_url}/articles?page={page}'  # 替换为你的网站分页URL
    article_urls = get_article_links(page_url)
    articles = []

    if not article_urls:
        return
    for article_url in article_urls:
        result = get_article_content(article_url)
        if result:
            title, date, text = result
            print(f'get article: {title}')
            articles.append((title, date, text))
    return articles


# 主函数，用于获取所有文章
def scrape_all_articles(start_page=1, end_page=10):
    all_article_content = []

    page_index = [i for i in range(start_page, end_page)]
    num_workers = max(10, len(page_index))
    with Pool(num_workers) as p:
        results = p.map(process, page_index)
    for result in results:
        all_article_content += result
    return all_article_content


if __name__ == '__main__':
    # 调用主函数来获取所有文章内容
    all_articles = scrape_all_articles(start_page=1, end_page=20)

    # 现在，all_articles 变量包含了所有文章的内容
    path = create_output_dir()
    source = '机核'
    with open(f'{path}/{source}.json', 'w', encoding='utf-8') as f:
        for title, date, text in all_articles:
            try:
                filter_text(text)
                obj = {'title': title, 'date': date, 'text': text}
                f.write(json.dumps(obj, ensure_ascii=False) + '\n')
            except Exception:
                print(traceback.format_exc())

import json
import os
from collections import defaultdict
# import pandas as pd
from datetime import datetime
def read(root,paths,result:defaultdict):
    for path in paths:
        feed = path.split('/')[-1].replace('.json','')
        p = f'{root}/{path}'
        with open(p,'r',encoding='utf-8') as f:
            print(f'reading file: {p}')
            items=[json.loads(line) for line in f.readlines()]
            result[feed] += items
def get_docs():
    result = defaultdict(list)
    for root, dirs, files in os.walk('output/'):
        read(root,files,result)
        for dir in dirs:
            for r,ds,fs in os.walk(dir):
                read(r,fs, result)
    return(result)

def deduplicate(input:defaultdict):
    for feed,items in input.items():
        result = {}
        for item in items:
            result[item['title']] = item
        dedup_items = list(result.values())
        input[feed] = sort_docs(dedup_items)
    return input
def sort_docs(docs):
    """
    sort docs by date
    :param docs: doc: {'title':'...', 'date':'xxxx','text':'xxx'}
    :return:
    """
    def sort_key(doc):
        date = datetime.strptime(doc['date'],'%Y-%m-%d %H:%M:%S')
        return date.timestamp()
    return sorted(docs,key=sort_key)

if __name__ == '__main__':
    docs = get_docs()
    dedup_docs = deduplicate(docs)
    for feed, docs in dedup_docs.items():
        with open(f'output/merged/{feed}.json','w',encoding='utf-8') as f:
            for doc in docs:
                f.write(json.dumps(doc,ensure_ascii=False)+'\n')
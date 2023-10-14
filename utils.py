from datetime import datetime
import os
import re

def create_output_dir():
    date = datetime.now().strftime('%Y%m%d %H:%M:%S')
    path = f'output/{date}/'
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def filter_text(text):
    if len(text) < 100:
        raise Warning(f'text too short: {text}')
    m = re.findall('[^\n\.,。，]{1,10}：.{1,10}\n', text, re.S)
    if m:
        matched_text = ''.join(m)
        if len(matched_text) / len(text) > 0.7:
            raise Warning(f'match bad pattern: {text}')


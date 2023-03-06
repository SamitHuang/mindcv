'''
This script is to detect invalid urls in markdown files quickly.
Usage:
    1. Detect all invalid urls in each markdown file recursively found in a directory
       python check_urls.py --dir ./
    2. Detect all invalid urls in each markdown files under a directory
       python check_urls.py --dir /path/to/dir --recur 0
    3. Only detect invalid urls for one file
       python check_urls.py --path /path/to/markdown_file

Note: 1. In the follow cases, this script may fail to detect some urls:
        a) urls in a table, without '.yaml' or '.ckpt' postfix
        b) other urls embedded in unknown complex html structures.
      2. It cannot check the correctness of the correspondence between the linked text and url.
      2. It's not perfect, so please also review the links manually to ensure everything is right.
'''
import requests
import markdown
from lxml import etree
import re
import argparse

parser = argparse.ArgumentParser(description='na', add_help=False)
parser.add_argument('-p', '--path', type=str, default='./README.md',
                           help='markdown file path')
parser.add_argument('-f', '--filter_relative', type=int, default=1,
                           help='filter relative path and not check it')
parser.add_argument('-d', '--dir', type=str, default='',
                           help='search markdown files (recursively) and check all urls if not empty')
parser.add_argument('-r', '--recur', type=int, default=1,
                           help='search markdown files recursively in dir if 1')

LARGE_POSTFIX = ['.ckpt', '.pth', '.zip', '.rar']

def check_url_valid(url, use_get=False):
    try:
        if use_get:
            request = requests.get(url, timeout=5)
        else:
            request = requests.head(url, timeout=5)
        if request.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print('Error: ', e)
        return False

def extract_table_urls(file_path):
    with open(file_path) as file:
        ret = []
        for line in file:
            #urls1 = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+.ckpt', line)
            #urls2 = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+.yaml', line)
            yamls = re.findall("(?P<url>https?://[^\s]+.yaml)", line)
            ckpts = re.findall("(?P<url>https?://[^\s]+.ckpt)", line)
            ret += yamls
            ret += ckpts

        return ret

#body_markdown = "This is an [inline link](http://google.com). This is a [non inline link][1]\r\n\r\n  [1]: http://yahoo.com"
def extract(file_path, filter_relative_path=False):
    def getlinks(string):
        """return a list with markdown links"""
        html = markdown.markdown(string, output_format='html')
        links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
        links = list(filter(lambda l: l[0] != "{", links))
        return links
    with open(file_path) as file:
        md = file.read()

    links = getlinks(md)
    ret = links
    if filter_relative_path:
        ret = []
        for link in links:
            if link[:4] == 'http':
                ret.append(link)
    return ret

from pathlib import Path
import os
def find_md(dir_path, recur=True):
    ret = []
    search_func = Path(dir_path).rglob if recur else Path(dir_path).glob
    for path in search_func('*.md'):
        if path.name[0] != '.': ## exclude .git
            ret.append(path)
    for path in search_func('*.MD'):
        if path.name[0] != '.':
            ret.append(path)

    return sorted(ret)

def is_large_file(url):
    for postfix in LARGE_POSTFIX:
        if postfix in url:
            return True
    return False


if __name__ == '__main__':
    args = parser.parse_args()
    if args.dir != '':
        md_list = find_md(args.dir, recur=args.recur)
    else:
        md_list = [args.path]
    print(md_list)

    report = []
    for md_path in md_list:
        print('\n--> ', 'Parsing markdown: ', md_path)
        #urls = extract('./mindcv/README.md')
        urls = extract(md_path, filter_relative_path=args.filter_relative)
        urls_in_table = extract_table_urls(md_path)
        print('Extract urls: ')
        print(urls)
        print(urls_in_table)
        for url in urls + urls_in_table:
            print(url)
            if check_url_valid(url)==False:
                print('==> INVALID!')
                report.append((md_path, url))
            else:
                print('VALID')

    print(f'\nFound invalid URLs:')
    for (md, url) in report:
        print(f"{md}\t\t{url}")


    print('\nNote: Some of the found urls can be valid if they just do not support requests.head() or timeout. Please check manually.')

    # double check using request.get()
    final = []
    print('\n -> Final check with requests.get()')
    for (md, url) in report:
        if not is_large_file(url):
            if not check_url_valid(url, use_get=True):
                print(f"Invalid\t{md}\t\t{url}")
                final.append(md, url)
            else:
                print(f"Valid\t{md}\t\t{url}")

    print('\nFinal invalid URLs in {len(md_list)} markdown files:')
    for (md, url) in final:
        print(f"Invalid\t{md}\t\t{url}")

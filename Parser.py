import requests
import html2text
import re
from bs4 import BeautifulSoup
import bs4
import json
"""
main_func returns data in JSON format.
main_func takes two arguments: request (text of request) and number (number of sites)
requests[socks] was installed
"""
def get_hrefs(url):
    """

    :param url: url of search query
    :return: urls of sites in search page
    """

    try:
        proxies = {'http': "socks5://myproxy:9191"}
        s=requests.get(url, proxies=proxies)
    except:
        print('Ошибка поискового запроса')
        return []
    hrefs = []
    soup = BeautifulSoup(s.text, 'html.parser')
    finds = soup.findAll('a', re.compile(r'[^\'\"]*organic__url[^\'\"]*'))
    for f in finds:
        if len(finds) == 0:
            continue
        s = re.search(r'href[\s]*=[\s]*[\'\"]([^\'\"]*)[\'\"]', str(f))
        noabs = re.search(r'yabs.yandex', s.group(1))
        noyandex = re.search(r'yandex.ru', s.group(1))
        http = re.search(r'^http', s.group(1))
        if noabs == None and http!=None and noyandex==None:
            hrefs.append(s.group(1))
    return hrefs


def extract_articles(soup, mass):
    """

    :param soup: html in beautifulsoup format
    :param mass: link to list of data
    :return: nothing
    """
    wrong_types = [bs4.element.NavigableString, bs4.element.CData, bs4.element.Comment, bs4.element.Declaration,
                   bs4.element.ProcessingInstruction]

    if type(soup) not in wrong_types:
        for i in range(len(soup.contents)):
            extract_articles(soup.contents[i], mass)
    else:
        if soup != '\n':
            mass.append(soup)


def get_text(href):
    """

    :param href: url of requested site
    :return: text of site
    if there are tags article, then we extract text from them
    else we use html2text
    """
    try:
        s = requests.get(href)
    except:
        print('ошибка доступа к', href)
        return ''
    soup = BeautifulSoup(s.text, 'html.parser')
    captcha = soup.findAll('div', 'g-recaptcha')
    if len(captcha)>0:
        print('There is captcha on ', href)
    article = soup.findAll('article')
    text = ''
    if len(article)>0:
        mass = []
        for a in article:
            extract_articles(a,mass)
        for m in mass:
            text+=m+'\n'
    else:
        text = html2text.HTML2Text().handle(s.text)
    return text


def main_func(request, number):
    pages = 0
    hrefs = []
    while len(hrefs) < number:
        url = f'https://yandex.ru/search/?text={request}&clid=2270455&win=351&lr=213&p={pages}'
        h= get_hrefs(url)
        if len(h)==0:
            print('There is captcha on Yandex Search')
            break
        for i in h:
            if i not in hrefs:
                hrefs.append(i)
        pages+=1

    diction_of_webs = dict()
    hrefs = hrefs[0:number]
    for href in hrefs:
        text = get_text(href)
        if href in diction_of_webs:
            print('repeat', href)
        diction_of_webs[href] = text
    diction_json = json.dumps(diction_of_webs)
    return diction_json


if __name__=='__main__':
    # pass
    json_diction = main_func('request', 5)      #return json object
    diction = json.loads(json_diction)          #return dict
    for d in diction:
        print(d)


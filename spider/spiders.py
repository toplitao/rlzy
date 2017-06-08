'''
spiders
'''

import requests, time, json, threading, os

from bs4 import BeautifulSoup

domian = 'http://www.cqhrss.gov.cn'
global COOKIE

def start():
    """docstring for get_cookies"""
    create_save_path(['./results/sydw','./results/sydw/item'])
    global COOKIE
    session = requests.Session()
    response = session.get(domian)
    COOKIE = session.cookies.get_dict()
    print(COOKIE)
    if not COOKIE:
        time.sleep(5)
        start()
    else:
        body = get_body(domian+'/zwxx/ywfl/rsrc/sydw/sydwzp/','./results/sydw','index.html')
        analysis_index(body)

def get_body(link,save_path,filename,delay = 2):
    file_path = save_path+'/'+filename
    if not os.path.isfile(file_path):
        get_html(link, file_path, delay)
    while check_503(file_path)[0] >=  0:
        get_html(link, file_path, delay)
    return check_503(file_path)[1]

def get_html(link, file_path, delay):
    time.sleep(delay)
    global COOKIE
    cookie_str = ''
    for k in COOKIE:
        cookie_str = cookie_str+k+' = '+COOKIE[k]+'; '
    cookie_str = cookie_str+'Hm_lvt_c9e4dff6b2fa46bedb23549177e34ee9 = 1496737822,1496800937,1496814246,1496814251; Hm_lpvt_c9e4dff6b2fa46bedb23549177e34ee9 = 1496818908; _gscu_322517208 = 93974348qyf4tm17; _gscs_322517208 = t96818907eelh3f11|pv:1; _gscbrs_322517208 = 1; 129_vq = 391'
    headers = {
        # 'Accept':'text/html,application/xhtml+xml,application/xml;q = 0.9,image/webp,*/*;q = 0.8',
        # 'Accept-Encoding':'gzip, deflate, sdch',
        # 'Accept-Language':'zh-CN,zh;q = 0.8',
        # 'Cache-Control':'max-age = 0',
        # 'Connection':'keep-alive',
        'COOKIE':cookie_str,
        # 'Host':'www.cqhrss.gov.cn',
        # 'If-Modified-Since':'Tue, 06 Jun 2017 03:30:59 GMT',
        # 'If-None-Match':"2d7c-551423f8622c0",
        # 'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    }
    r = requests.get(link,headers = headers)
    print('get>>> '+link+' to '+file_path)
    with open(file_path, 'wb') as fd:
        for chunk in r.iter_content(100000):
            fd.write(chunk)

def check_503(file_path):
    body = open(file_path, 'rb').read()
    soup = BeautifulSoup(body)
    title = soup.html.head.title.get_text()
    return [title.find('503 Service Temporarily Unavailable'),body]

def analysis_index(html_doc):
    soup = BeautifulSoup(html_doc)
    lis = soup.select(".article_list > ul > li")
    data =  []
    threads = []
    for index, li in enumerate(lis):
        header = li.a.pp.get_text()
        time = li.a.span.get_text()
        href = li.a.get('href')
        if(href.find("http")  ==  -1):
            child = domian+li.a.get('href')
        json_data = {
            'header' : header,
            'time' : time,
            'child' : child,
            'thread' : myThread(child,'./results/sydw/item', time+header + '.html', index*2)
        }
        #thread = myThread(child,'./results/sydw/item', time+header + '.html', index*2)
        json_data['thread'].start()
        #threads.append(thread)
        data.append(json_data)
        print(header,child)
    # print('-----------------------------index data-------------------------------------')
    # print('-----------------------------index data-------------------------------------')
    # print(data)
    deal_child(data)
    
def deal_child(data):
    for item in data:
        item['thread'].join()
        soup = BeautifulSoup(item['thread'].get_thread_body())
        for p in soup.select(".information > .article > p"):
            row=p.get_text()
            get_feld(item,row,['报名时间','报名地址','报名方式'])
        del item['thread']
    # with open('./data.json', 'wb') as fd:
    #     # for json_data in data:
    #     #     print(json_data)
    #     fd.writelines((data))
    print('-----------------------------index data-------------------------------------')
    print(data)
    print('---------------------------------over--------------------------------------')

def get_feld(item,row,istrs):
    for istr in istrs:
        if(row.find(istr) >= 0):
            item[''+istr+'']=row


def danalysis_child(html_doc):
    print(1)

class myThread (threading.Thread):
    def __init__(self, link, save_path, filename,delay):
        threading.Thread.__init__(self)
        self.link = link
        self.save_path = save_path
        self.filename = filename
        self.delay = delay
        self.body = ''
    def run(self):
        self.body = get_body(self.link,self.save_path,self.filename)
    def get_thread_body(self):
        return self.body

def create_save_path(save_paths):
    for save_path in save_paths:
        if not os.path.exists(save_path):
            os.makedirs(save_path)

start()
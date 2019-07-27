# !/usr/bin/python3
# -*- coding:utf-8 -*-
# 
#    Date: 2019/05/02
#    Author: Shieber, Henry
#
#                             APACHE LICENSE
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#                            Function Description
#    一键下载Bilibili弹幕网的视频。
#
#    Copyright 2019 
#    All Rights Reserved!

import re, os, sys, time
import hashlib, json
from bs4 import BeautifulSoup as Soup
from os.path import join,exists,splitext
from requests import get
from selenium import webdriver
from moviepy.editor import *
from multiprocessing import Pool
import urllib.request as request

def get_play_list(url, cid, q):
    '''访问B站API地址'''
    headers = {
                'Referer': url, 
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
              }
    entropy  = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appk,sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params   = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type='%(appk,cid,q,q)
    chksum   = hashlib.md5(bytes(params+sec,'utf8')).hexdigest()
    url_api  = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s'%(params,chksum)
    html_res = get(url_api, headers=headers).json()
    videos   = [html_res['durl'][0]['url']]
    return videos

def Schedule_cmd(blocknum, blocksize, totalsize):
    '''设置下载进度条'''
    recv_sz,fildes = blocknum * blocksize, sys.stdout
    pervent = recv_sz / totalsize
    percent = "%.2f%%" % (pervent * 100)
    string  = ('*' * round(pervent * 50)).ljust(50, '-')
    fildes.write(percent.ljust(8, ' ') + '[' + string + ']')
    fildes.flush()
    fildes.write('\r')

def down_video(videos, title, url, page):
    opener = request.build_opener()
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) \
                Gecko/20100101 Firefox/56.0'),
        ('Accept', '*/*'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Range', 'bytes=0-'),   
        ('Referer', url), 
        ('Origin', 'https://www.bilibili.com'),
        ('Connection', 'keep-alive'),
    ]

    print('[正在下载P{}段视频,.....]:'.format(page) + title)
    num = 1
    VideoPath = join(sys.path[0], 'videos', title) 
    for url in videos:
        request.install_opener(opener)
        if not exists(VideoPath):
            os.makedirs(VideoPath)

        if len(videos) > 1:
            request.urlretrieve(url=url,filename=join(VideoPath,
                r'{}-{}.mp4'.format(title, num)),reporthook=Schedule_cmd)  
        else:
            request.urlretrieve(url=url,filename=join(VideoPath,
                r'{}.mp4'.format(title)),reporthook=Schedule_cmd)  
        num += 1

def combine_video(videos, title):
    '''合并视频'''
    VideoPath = join(sys.path[0], 'bilibili_video', title)
    if len(videos) > 1:
        print("[下载:%s完成,正在合并...]:"%title)
        VideoL = []
        rt     = VideoPath
        for f in sorted(os.listdir(rt),key=lambda x: int(x[x.rindex("-")+1:x.rindex(".")])):
            if splitext(f)[1] == '.flv':
                flPath = join(rt, f)
                video  = VideoFileClip(flPath)
                VideoL.append(video)
        clip = concatenate_videoclips(VideoL)
        clip.to_videofile(join(rt, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
        print("[视频:%s合并完成...]"%title)
    else:
        print("[视频:%s合并完成...]"%title)

def download_control(av):
    '''视频下载调度函数'''
    quality = '80'              
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
              }
    if av.isdigit():   
        st = av 
    else:
        st = re.search(r'/av(\d+)/*', av).group(1)
    url = 'https://api.bilibili.com/x/web-interface/view?aid='+st
    
    html = get(url, headers=headers).json()
    data = html['data']
    cid_list = []             
    if '?p=' in av:
        P = re.search(r'\?p=(\d+)',av).group(1)
        cid_list.append(data['pages'][int(P) - 1])
    else:
        cid_list = data['pages']

    for item in cid_list:
        cid, title= str(item['cid']), item['part']
        title  = re.sub(r'[\/\\:*?"<>|]', '', title)  
        print('[cid]:%s\n[标题]:%s' %(cid, title))

        page   = str(item['page'])
        url   +=  "/?p=" + page
        videos = get_play_list(url, cid, quality)
        down_video(videos, title, url, page)
        combine_video(videos, title)

    VideoPath = join(sys.path[0], 'bilibili_video')
    if sys.platform.startswith('win'):
        os.startfile(VideoPath)

class AvSpider():
    '''
        输入B站Up主av号
        实现下载其所有视频投稿
    '''
    def __init__(self,avnum):
        self.headers = {
                        'User-Agent':'Mozilla/5.0 (compatible; MSTE 5.5; Windows NT)',
                        'Connection':'close'
                       }
        self.avnum   = avnum
        self.url     = 'https://space.bilibili.com/%s/video'%avnum

    def get_urls(self,driver):
        driver.get(self.url)
        time.sleep(5)
        html_cont = driver.page_source

        urls = []
        soup = Soup(html_cont,'html.parser') 
        if not soup:
            return urls
        resp = soup.find('span',class_='be-pager-total')
        if not resp:
            urls.append(self.url)
            return urls

        resp = resp.getText().split()
        last = int(resp[1])
        for num in range(1,last+1):
            url = 'https://space.bilibili.com/%s/video?tid=0&\
                   page=%d&keyword=&order=pubdate'%(self.avnum,num)
            urls.append(url)

        return urls

    def get_avs(self,urls,driver):
        avs = []
        if not urls:
            return avs

        aim = input('一页有30个视频，只获取第一页？(yes/no): ')
        print('...............................................')
        if aim == 'yes' or aim == 'YES': 
            urls = urls[:1]
        for url in urls: 
            video_avs = self.get_video_avs(url,driver)
            if not video_avs:
                continue
            avs += video_avs 

        return len(avs), avs

    def get_video_avs(self,url,driver):
        driver.get(url)
        time.sleep(5)

        html_cont = driver.page_source
        soup = Soup(html_cont,'html.parser') 
        if not soup:
            return None

        video_avs = []
        video_url = soup.find('ul',class_='list-list')
        video_new = video_url.find_all('li',class_='list-item clearfix fakeDanmu-item new')
        if video_new:
            for new in video_new:
                video_avs.append(new['data-aid'])
        video_li  = video_url.find_all('li',class_='list-item clearfix fakeDanmu-item')
        for video in video_li:
            video_avs.append(video['data-aid'])

        return video_avs

def download_multi(video_avs):
    '''多进程下载'''
    if not video_avs:
        return None

    pool = Pool(10)
    for av in video_avs:
        pool.apply_async(download_control,(av,))
    pool.close()
    pool.join()

def get_first_last(video_num):
    '''获取下载起止视频数'''
    print('...............................................')
    opt = input('指定一个范围内的视频下载吗？(yes/no): ')
    print('...............................................')
    if opt == 'yes' or opt == 'YES':
        try: 
            first = int(input('请输入要下载视频的起始数字(1): '))
            if first < 1 or first > video_num:
                first = 0
            else:
                first -= 1
        except ValueError:
            first = 0
        try: 
            last  = int(input('请输入要下载视频的结尾数字(%d): '%video_num))
            if last <0 or last > video_num:
                last = video_num
        except ValueError:
            last = video_num

        return first, last

    opt = input('请指定若干独立的视频(2,5): ')
    print('...............................................')
    opt = opt.replace(',',' ').split()
    opt = [int(op) for op in opt]
    return None, opt
        
if __name__== "__main__":
    # 先单进程下载所有视频av号，在多进程下载视频
    # 测试Up主av号 415479453
    
    #Step I：获取所有视频的av号
    print('...............................................')
    avnum  = input('请输入B站视频Up主的UID号: ')
    print('...............................................')
    driver = webdriver.Firefox()
    spider = AvSpider(avnum)
    urls   = spider.get_urls(driver)
    v_num, avs = spider.get_avs(urls,driver)
    driver.close()

    #Step II：设定下载url
    print('视频参数：质量-1080P，格式-mp4, 共%d个'%v_num)
    first, last = get_first_last(v_num)
    if first == None:
        video_avs = [avs[i-1] for i in last] 
    else:
        video_avs = avs[first:last]

    #Step III：多进程下载视频
    print('开始下载指定的%d个视频'%len(video_avs))
    download_multi(video_avs)

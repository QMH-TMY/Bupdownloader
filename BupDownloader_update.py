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

'''
项目: B站视频下载
加密API版,不需要加入cookie,直接即可下载1080p视频
20190422 - 增加多P视频单独下载其中一集的功能
'''

import re, os, sys, time
from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from moviepy.editor import *
from multiprocessing import Pool
import requests, hashlib, urllib.request, json

# 访问API地址
def get_play_list(start_url, cid, quality):
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey,sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params  = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum  = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    headers = {
                'Referer': start_url, 
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36  \
                (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
              }

    html = requests.get(url_api, headers=headers).json()
    video_list = [html['durl'][0]['url']]
    return video_list

def Schedule_cmd(blocknum, blocksize, totalsize):
    recv_size = blocknum * blocksize
    fd = sys.stdout                         #设置下载进度条
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    num = round(pervent * 50)
    string = ('*' * num).ljust(50, '-')
    fd.write(percent_str.ljust(8, ' ') + '[' + string + ']')
    fd.flush()
    fd.write('\r')

def down_video(video_list, title, start_url, page):
    num = 1
    print('[正在下载P{}段视频...]:'.format(page) + title)
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title) 
    for i in video_list:
        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Range', 'bytes=0-'),   # Range 的值要为 bytes=0- 才能下载完整视频
            ('Referer', start_url),  # 注意修改referer,必须要加的!
            ('Origin', 'https://www.bilibili.com'),
            ('Connection', 'keep-alive'),
        ]
        urllib.request.install_opener(opener)

        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)

        #开始下载
        if len(video_list) > 1:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}-{}.mp4'.format(title, num)),reporthook=Schedule_cmd)  #写成flv也行
        else:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}.mp4'.format(title)),reporthook=Schedule_cmd) 
        num += 1

def combine_video(video_list, title):
    '''合并视频'''
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title) #下载目录
    if len(video_list) > 1:   #视频大于一段才要合并
        print('[下载完成,正在合并视频......]:' + title)
        L = []                #定义数组存放视频
        root_dir = currentVideoPath #访问video 文件夹
        for fil in sorted(os.listdir(root_dir), key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
            
            if os.path.splitext(fil)[1] == '.flv' #后缀名为 .mp4/.flv:
                filePath = os.path.join(root_dir, fil)
                video = VideoFileClip(filePath)
                L.append(video)
        final_clip = concatenate_videoclips(L)
        final_clip.to_videofile(os.path.join(root_dir, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
        print("[视频'%s'合并完成...]"%title)

    else:
        print("[视频'%s'合并完成...]"%title)

def download_control(start):
    '''视频下载调度函数'''
    quality = '80'                 # 视频质量1080P
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    if start.isdigit() == True: 
        # 获取cid的api, 传入aid即可
        start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + start
    else:
        start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + re.search(r'/av(\d+)/*', start).group(1)
    
    html = requests.get(start_url, headers=headers).json()
    data = html['data']
    cid_list = []                  # 获取视频的cid,title
    if '?p=' in start:             #多P单独下载分P视频
        p = re.search(r'\?p=(\d+)',start).group(1)
        cid_list.append(data['pages'][int(p) - 1])
    else:
        cid_list = data['pages']

    for item in cid_list:
        title, cid, page = item['part'],str(item['cid']),str(item['page'])
        title = re.sub(r'[\/\\:*?"<>|]', '', title)
        print('[cid]:%s\n[标题]:%s'%(cid,title))
        start_url  = ''.join([start_url,"/?p=", page])
        video_list = get_play_list(start_url, cid, quality)
        down_video(video_list, title, start_url, page)
        combine_video(video_list, title)

    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video')#当前目录作存储目录
    if (sys.platform.startswith('win')):
        os.startfile(currentVideoPath)

class AvSpider():
    '''
        输入B站Up主av号(如：290526283，注意不是视频av号)
        实现下载其所有视频投稿
    '''
    def __init__(self,avnum):
        self.avnum     = avnum
        self.start_url = 'https://space.bilibili.com/%s/video'%avnum
        self.headers   = {
                           'User-Agent':'Mozilla/5.0 (compatible; MSTE 5.5; Windows NT)',\
                           'Connection':'close'
                         }

    def get_all_page_urls(self,driver):
        driver.get(self.start_url)
        time.sleep(10)
        html_cont = driver.page_source

        page_urls = []
        soup = Soup(html_cont,'html.parser') 
        if not soup:
            return page_urls

        last_res  = soup.find('span',class_='be-pager-total')
        if not last_res:
            page_urls.append(self.start_url)
            return page_urls

        last_page = int(last_res.getText()[2])
        for num in range(1,last_page+1):
            new_page_url = 'https://space.bilibili.com/%s/video?tid=0&page=%d&keyword=&order=pubdate'%(self.avnum,num)
            page_urls.append(new_page_url)

        return page_urls

    def get_all_avs(self,page_urls,driver):
        all_video_avs = []
        if not page_urls:
            return all_video_avs

        for page_url in page_urls:
            video_avs = self.get_video_avs(page_url,driver)
            if not video_avs:
                continue
            all_video_avs += video_avs 

        return len(all_video_avs), all_video_avs

    def get_video_avs(self,url,driver):
        driver.get(url)
        time.sleep(5)

        html_cont = driver.page_source
        soup = Soup(html_cont,'html.parser') 
        if not soup:
            return []

        video_avs = []
        video_ul  = soup.find('ul',class_='list-list')

        #第一页的第一个视频模式不同，单独处理
        video_new = video_ul.find_all('li',class_='list-item clearfix fakeDanmu-item new')
        assert len(video_new) != 0
        for new in video_new:
            video_avs.append(new['data-aid'])
        #其余视频模式相同，集中处理
        video_li  = video_ul.find_all('li',class_='list-item clearfix fakeDanmu-item')
        for video in video_li:
            video_avs.append(video['data-aid'])
        return video_avs

def download_multi(video_avs):
    '''多进程下载'''
    assert len(video_avs) != 0

    pool = Pool(5)
    for av in video_avs:
        pool.apply_async(download_control,(av,))
    pool.close()
    pool.join()

    return True

def get_first_last(video_num):
    '''获取下载起止视频数或指定视频下载个数'''
    options = input('指定一个范围内的视频下载吗？(yes/no): ')
    if options == 'yes' or options == 'YES':
        try: 
            first_num = int(input('请输入要下载视频的起始数字(1): '))
            if first_num < 1 or first_num > video_num:
                first_num = 0
            else:
                first_num -= 1
        except ValueError:
            first_num = 0

        try: 
            last_num  = int(input('请输入要下载视频的结尾数字(%d): '%video_num))
            if last_num <0 or video_num > video_num:
                last_num = video_num
        except ValueError:
            last_num = video_num

        return first_num, last_num

    options = input('请指定若干独立视频(4,8,32): ')
    options = options.replace(',',' ').split()
    options = [int(i) for i in options]
    return None, options
        
if __name__== "__main__":
    # 先单进程下载所有视频av号，在多进程下载视频
    # 测试Up主UID号 17416518
    
    #Step I：获取所有视频的av号
    avnum     = input('请输入Up主的UID号: ')
    driver    = webdriver.Firefox()
    avspider  = AvSpider(avnum)
    page_urls = avspider.get_all_page_urls(driver)
    video_num, all_video_avs = avspider.get_all_avs(page_urls,driver)
    driver.close()

    #Step II：设定下载数目
    print('开始下载B站Up主%s的投稿视频'%avnum)
    print('视频质量：1080P，格式：mp4, 共%d个'%video_num)
    first_num, last_num = get_first_last(video_num)
    if first_num == None:
        download_list = [all_video_avs[i-1] for i in last_num] 
    else:
        download_list = all_video_avs[first_num:last_num]

    #Step III：多进程下载视频
    print('开始下载指定的%d个视频'%len(download_list))
    download_multi(download_list)

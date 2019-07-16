# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Date: 2019/05/02
# Author: Shieber, Henry
# 
# 说明，本程序一半由我写，另一半是借用的Henry的代码，
# 并行下载函数download_multi，选择函数get_first_last，类AvSpider还有最后__name__下面是我写的，
# 解析视频地址下载存储是Henry的代码，我只把他的flv改成了mp4，并删了些代码。
# 

'''
项目: B站视频下载
加密API版,不需要加入cookie,直接即可下载1080p视频
20190422 - 增加多P视频单独下载其中一集的功能
'''

import re, os, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
import requests, hashlib, urllib.request, json
from multiprocessing import Pool
from moviepy.editor import *

# 访问API地址
def get_play_list(start_url, cid, quality):
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    headers = {
        'Referer': start_url,  # 注意加上referer
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }

    html = requests.get(url_api, headers=headers).json()
    video_list = [html['durl'][0]['url']]
    return video_list

'''
 urllib.urlretrieve 的回调函数：
def callbackfunc(blocknum, blocksize, totalsize):
    @blocknum:  已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
'''

def Schedule_cmd(blocknum, blocksize, totalsize):
    recv_size = blocknum * blocksize
    # 设置下载进度条
    fd = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('*' * n).ljust(50, '-')
    fd.write(percent_str.ljust(8, ' ') + '[' + s + ']')
    fd.flush()
    fd.write('\r')

def down_video(video_list, title, start_url, page):
    num = 1
    print('[正在下载P{}段视频,请稍等...]:'.format(page) + title)
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title) 
    for i in video_list:
        opener = urllib.request.build_opener()
        # 请求头
        opener.addheaders = [
            # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
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

        # 创建文件夹存放视频
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)

        # 开始下载
        if len(video_list) > 1:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}-{}.mp4'.format(title, num)),reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        else:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}.mp4'.format(title)),reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        num += 1

# 合并视频
def combine_video(video_list, title):
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title)  # 当前目录作为下载目录
    if len(video_list) >= 2:
        # 视频大于一段才要合并
        print('[下载完成,正在合并视频...]:' + title)
        # 定义一个数组
        L = []
        # 访问 video 文件夹 (假设视频都放在这里面)
        root_dir = currentVideoPath
        # 遍历所有文件
        for file in sorted(os.listdir(root_dir), key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
            # 如果后缀名为 .mp4/.flv
            if os.path.splitext(file)[1] == '.flv':
                # 拼接成完整路径
                filePath = os.path.join(root_dir, file)
                # 载入视频
                video = VideoFileClip(filePath)
                # 添加到数组
                L.append(video)
        # 拼接视频
        final_clip = concatenate_videoclips(L)
        # 生成目标视频文件
        final_clip.to_videofile(os.path.join(root_dir, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
        print('[视频合并完成...]' + title)

    else:
        # 视频只有一段则直接打印下载完成
        print('[视频合并完成...]:' + title)

def download_control(start):
    '''视频下载调度函数'''
    if start.isdigit() == True:    #输入的是av号
        # 获取cid的api, 传入aid即可
        start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + start
    else:
        start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + re.search(r'/av(\d+)/*', start).group(1)
    
    quality = '80'                 # 视频质量1080P
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    html = requests.get(start_url, headers=headers).json()
    data = html['data']
    cid_list = []                  # 获取视频的cid,title
    if '?p=' in start:
        # 单独下载分P视频
        p = re.search(r'\?p=(\d+)',start).group(1)
        cid_list.append(data['pages'][int(p) - 1])
    else:
        # 只有一P，直接下载
        cid_list = data['pages']

    for item in cid_list:
        cid = str(item['cid'])
        title = item['part']
        title = re.sub(r'[\/\\:*?"<>|]', '', title)               # 替换为空的
        print('[cid]:' + cid)
        print('[标题]:' + title)
        page = str(item['page'])
        start_url = start_url + "/?p=" + page
        video_list = get_play_list(start_url, cid, quality)
        #start_time = time.time()
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
        self.start_url = 'https://space.bilibili.com/%s/video'%avnum
        self.headers = {'User-Agent':'Mozilla/5.0 (compatible; MSTE 5.5; Windows NT)', 'Connection':'close'}
        self.avnum = avnum

    def get_all_page_urls(self,driver):
        driver.get(self.start_url)
        time.sleep(10)
        html_cont = driver.page_source

        page_urls = []
        soup = Soup(html_cont,'html.parser') 
        if not soup:
            return page_urls

        last_res  = soup.find('span',class_='be-pager-total')
        if last_res is None:
            page_urls.append(self.start_url)
            return page_urls

        last_page = int(last_res.getText()[2])
        for num in range(1,last_page+1):
            new_page_url = 'https://space.bilibili.com/%s/video?tid=0&page=%d&keyword=&order=pubdate'%(self.avnum,num)
            page_urls.append(new_page_url)

        return page_urls

    def get_all_avs(self,page_urls,driver):
        all_video_avs = []
        if page_urls is None:
            return all_video_avs

        for page_url in page_urls:
            video_avs = self.get_video_avs(page_url,driver)
            if video_avs is None:
                continue
            all_video_avs += video_avs 

        return len(all_video_avs), all_video_avs

    def get_video_avs(self,url,driver):
        driver.get(url)
        time.sleep(5)

        html_cont = driver.page_source
        soup = Soup(html_cont,'html.parser') 
        if not soup:
            return None

        video_avs = []
        video_ul  = soup.find('ul',class_='list-list')

        #第一页的第一个视频模式不同，单独处理
        video_new = video_ul.find_all('li',class_='list-item clearfix fakeDanmu-item new')
        if video_new != []:
            for new in video_new:
                video_avs.append(new['data-aid'])

        for new in video_new:
            video_avs.append(new['data-aid'])

        #其余视频模式相同，集中处理
        video_li  = video_ul.find_all('li',class_='list-item clearfix fakeDanmu-item')
        for video in video_li:
            video_avs.append(video['data-aid'])

        return video_avs

def download_multi(video_avs):
    '''多进程下载'''
    if video_avs == []:
        return None

    pool = Pool(5)
    for av in video_avs:
        pool.apply_async(download_control,(av,))

    pool.close()
    pool.join()

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
    
    ############# 第一阶段：获取所有视频的av号#########################
    avnum     = input('请输入Up主的UID号: ')
    driver    = webdriver.Firefox()
    avspider  = AvSpider(avnum)
    page_urls = avspider.get_all_page_urls(driver)
    video_num, all_video_avs = avspider.get_all_avs(page_urls,driver)
    driver.close()

    #############第二阶段：设定下载数目，多进程下载视频###################
    print('开始下载B站Up主%s的投稿视频'%avnum)
    print('视频质量：1080P，格式：mp4, 共%d个'%video_num)

    first_num, last_num = get_first_last(video_num)
    if first_num is None:
        download_list = [all_video_avs[i-1] for i in last_num] 
    else:
        download_list = all_video_avs[first_num:last_num]

    print('开始下载指定的%d个视频'%len(download_list))
    download_multi(download_list)

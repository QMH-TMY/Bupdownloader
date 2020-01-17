### 兼容系统 
- Linux
- Mac OS
- Windows

### 描述 
输入Up主的UID号，从[哔哩哔哩弹幕网](https://www.bilibili.com/)下载Up主的所有视频(mp4格式，可指定下载个数)并将所有的文件存储在脚本运行的目录下。

### 使用 
	$ python3 BupDownloader.py
	$ 请输入Up主av号: 190526283 
	$ 请输入下载视频质量(60,80): 80

### 注意 
> av号是Up主的UID号，不是视频的av号。UID，就是一个数字字符串。  
> 60对应60P，80对应80P的质量。请勿大量使用，避免给B站服务器带来压力。  


### 依赖 
> 使用python3且安装依赖包  
> $ sudo pip3 install -r requirement.txt  

由于B站的反爬虫措施，直接爬取B站Up主视频目录是爬不到东西的，所以要用selenium。要驱动浏览器就要下载对应的驱动器补丁，不同浏览器补丁不同。  
> Firefox，Chrome，Edge浏览器请分别到这三处下载对应的版本并解压。  
<a href="https://github.com/mozilla/geckodriver/releases/tag/v0.24.0">geckodriver</a>，<a href="https://sites.google.com/a/chromium.org/chromedriver/">Chromedriver</a>，<a href="https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/">Webdriver</a>

解压后，将对应的driver的绝对路径加入环境变量。如果报错说缺少哪个包，就对照着自己安装吧。

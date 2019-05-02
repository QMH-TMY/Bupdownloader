--------
# 描述 #
-------

输入Up主的av号，从[哔哩哔哩弹幕网](https://www.bilibili.com/)下载Up主的所有视频(mp4格式，可指定下载个数)并将所有的文件存储在脚本运行的目录下。

# 使用 #
	$ python3 BupDownloader.py
	$ 请输入Up主av号: 190526283 
	# 注意：是自己喜欢的Up主的av号，不是她的某个视频的av号
	# 上面的那个是我自己随便写的，就是一个9位的数字字符串。

# 依赖 #
1.请使用python3

2.由于B站的反爬虫措施，直接爬取B站Up主视频目录是爬不到东西的，所以要用selenium。

  自然，要驱动浏览器就要下载对应的驱动器补丁，不同浏览器补丁不同。

3.Firfox浏览器请到[此处](https://github.com/mozilla/geckodriver/releases/tag/v0.24.0)下载对应的版本并解压。

4.Chrome浏览器请到[此处](https://sites.google.com/a/chromium.org/chromedriver/)下载对应的版本并解压。

5.Edge浏览器请到[此处](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)下载对应的版本并解压。

6.解压后，将对应的driver的绝对路径加入环境变量。

7.现在你可以有一个大胆的想法了。

8.如果报错说缺少哪个包，就对照着自己安装吧。

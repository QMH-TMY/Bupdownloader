--------
# 描述 #
-------

输入Up主的UID号，从[哔哩哔哩弹幕网](https://www.bilibili.com/)下载Up主的所有视频(mp4格式，可指定下载个数)并将所有的文件存储在脚本运行的目录下。

# 使用 #
	$ python3 BupDownloader.py
	$ 请输入Up主av号: 190526283 
	# 注意：是自己喜欢的Up主的UID号，不是她的某个视频的av号
	# 上面的那个是我自己随便写的，就是一个数字字符串。

# 依赖 #
<li>请使用python3</li>
<li>由于B站的反爬虫措施，直接爬取B站Up主视频目录是爬不到东西的，所以要用selenium。</br>
自然，要驱动浏览器就要下载对应的驱动器补丁，不同浏览器补丁不同。</li>
<li> Firefox浏览器请到<a href="https://github.com/mozilla/geckodriver/releases/tag/v0.24.0">此处</a>下载对应的版本并解压。</li>
<li>Chrome浏览器请到<a href="https://sites.google.com/a/chromium.org/chromedriver/">此处</a>下载对应的版本并解压。</li>
<li>Edge浏览器请到<a href="https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/">此处</a>下载对应的版本并解压。</li>
<li>解压后，将对应的driver的绝对路径加入环境变量。</li>
<li>如果报错说缺少哪个包，就对照着自己安装吧。</li>
<li>请保持低调，不要大规模使用，避免给B站服务器带来压力，避免他们更改反爬策略，不然，这个程序就不能用了。</li>
<li>现在你可以有一个大胆的想法了。</li>
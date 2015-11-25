#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
from lxml import etree
def get_nodes(_url, _xpath):
  #headers = {'User-Agent':'Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'}  
  #req = urllib2.Request(url=_url,headers=headers)
  resp = urllib2.urlopen(_url)
  import time
  #print resp
  res = resp.read()
  #ret = res.find("22c9.png")
  #if ret:
  #  ret = ret - 200
  #  print res[ret:ret+250]
  f = open("test.html", "w")
  f.write(res)
  f.close()
  tree = etree.HTML(res)
  return tree.xpath(_xpath)
  
#print len(get_nodes("http://tech.163.com/latest", '//*[@id="instantPanel"]/div[1]/ul/li[1]/a[2]'))
#nodes = get_nodes("http://tech.163.com/", '//h2[@class="color-link"]/a')
#nodes = get_nodes("http://tech.qq.com/", '//div[@class="Q-tpList"]/div/h3/a')
#nodes = get_nodes("http://tech.sina.com.cn/", '//a[@target="_blank"]')
def check_img(url,xpaths,expect):
	count = 0
	for xpath in xpaths:
		nodes = get_nodes(url,xpath)
		for node in nodes:
			try:
				#print node.get("src")
				count = count + 1
			except:
				print "exception."
	if expect != count:
		print url, "expect:%d, actual:%d "%(expect, count)



xpaths=[]
#check_img("", xpaths, 2)

#img
if False:
	# 3g.news.cn cases. 
	xpaths=['//p/img']
	check_img("http://3g.news.cn//html/947/201651.html", xpaths, 1)
	check_img("http://3g.news.cn/html/694/201398.html", xpaths, 0)
	#check_img("http://3g.news.cn/html/113/201841.html", xpaths, 1)
	check_img("http://3g.news.cn/html/158/201886.html", xpaths, 3)
	check_img("http://3g.news.cn/html/122/201850.html", xpaths, 3)

	#http://inews.ifeng.com/
	xpaths=["//p/img"]
	check_img("http://inews.ifeng.com/46385628/news.shtml", xpaths, 2)
	check_img("http://inews.ifeng.com/46384592/news.shtml", xpaths, 1)
	check_img("http://inews.ifeng.com/46385131/news.shtml", xpaths, 1)
	check_img("http://inews.ifeng.com/46385131/news.shtml", xpaths, 1)
	check_img("http://inews.ifeng.com/46385628/news.shtml", xpaths, 2)

	# http://news.qq.com/  cannot

	xpaths=["//div/img[@class='j_fullppt']","//div/img[@class='j_fullppt_cover']"]
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkwuwv3597971.d.html?vt=4&pos=8&cid=56261", xpaths, 2)
	check_img("http://news.sina.cn/gn/2015-11-25/detail-ifxkwuwy7112185.d.html?vt=4&pos=8&cid=56261", xpaths, 2)
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkxfvn9008810.d.html?vt=4&pos=11&cid=56264", xpaths, 2)
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkwuwv3601067.d.html?vt=4&pos=11&cid=56264", xpaths, 1)
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkwuwy7117086.d.html?vt=4&pos=11&cid=56264", xpaths, 1)


	print "test fin."



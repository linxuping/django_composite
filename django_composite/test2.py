#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
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
  #f = open("test.html", "w")
  #f.write(res)
  #f.close()
  tree = etree.HTML(res)
  return tree.xpath(_xpath)


def get_href(node):
	href = None
	for i in range(6):
		href = node.get("href")
		if href != None:
			return href
		node = node.getparent()
		if node == None:
			return None
  
#print len(get_nodes("http://tech.163.com/latest", '//*[@id="instantPanel"]/div[1]/ul/li[1]/a[2]'))
#nodes = get_nodes("http://tech.163.com/", '//h2[@class="color-link"]/a')
#nodes = get_nodes("http://tech.qq.com/", '//div[@class="Q-tpList"]/div/h3/a')
#nodes = get_nodes("http://tech.sina.com.cn/", '//a[@target="_blank"]')
def analyze_new(url,xpaths):
	count = 0
	for xpath in xpaths:
		_print = True
		nodes = get_nodes(url,xpath)
		for node in nodes:
			try:
				_text = node.text
				_href = get_href(node)
				#print _href
				if not _text or not _href:
					continue
				if True or _print:
					print xpath,_text,_href
					_print = False
				count = count + 1
			except:
				print "exception.",node, sys.exc_info()
	print url, "count: %d"%count




xpaths=["//h2"]
analyze_new("http://xw.qq.com/m/news", xpaths)

#img
if False:
	xpaths=["//div[@class='newlist']/ul/li/a"]
	analyze_new("http://3g.news.cn/html/", xpaths)

	xpaths=["//div[@class='list-item']/a"]
	analyze_new("http://m.baidu.com/news", xpaths)

	xpaths=["//p"]
	analyze_new("http://inews.ifeng.com/", xpaths)

	xpaths=["//section/p/a","//h4/a/strong","//div/div/a"]
	analyze_new("http://m.sohu.com/", xpaths)

	xpaths=["//h3[@class='carditems_list_h3']"]
	analyze_new("http://news.sina.cn/", xpaths)

	xpaths=["//li/h4/a"]
	analyze_new("http://news.163.com/mobile/", xpaths)

	xpaths=["//h2"]
	analyze_new("http://xw.qq.com/m/news", xpaths)

	xpaths=["//div/div/h3/a","//div/div/p/a","//ul[@class='first-child-no-top last-child-no-bottom']/li/a","//ul[@class='first-child-no-top']/li/a"]
	analyze_new("http://m.cctv.com/", xpaths)


	print "test fin."



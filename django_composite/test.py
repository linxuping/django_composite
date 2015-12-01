#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import urllib2
from lxml import etree
from base import *

'''
def get_nodes(_url, _xpath):
  headers = {'User-Agent':'Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'}  
  req = urllib2.Request(url=_url,headers=headers)
  resp = urllib2.urlopen(req)
  #print resp
  res = resp.read()

  #ret = res.find("22c9.png")
  #if ret:
  #  ret = ret - 200
  #  print res[ret:ret+250]

  #import commands
  #ret,res = commands.getstatusoutput("wget -O - %s 2>/dev/null"%_url)
  f = open("test.html", "w")
  f.write(res)
  f.close()
  tree = etree.HTML(res)
  rets = tree.xpath(_xpath)
  return rets
'''
  
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
				print node.get("src"),node.get("alt"),node.get("class")
				count = count + 1
			except:
				print "exception."
	if expect != count:
		print url, "expect:%d, actual:%d "%(expect, count)



#xpaths=["//li/a/img","//img"]
#check_img("http://fashion.163.com/photoview/25A20026/89975.html#p=B9E1UBPM25A20026", xpaths, 1)

#check_img("http://ent.163.com/15/1129/23/B9KH19UG00031H2L.html", xpaths, 1)
#check_img("", xpaths, 1)
#xpaths=["//div[@class='finPicImg']/i/img"]
#check_img("http://m.sohu.com/n/428445902/?wscrid=46653_7", xpaths, 4)

xpaths=["//div[@class='image split']/img"]
check_img("http://xw.qq.com/news/20151201062793/NEW2015120106279303", xpaths, 1)

#xpaths=["//div[@class='text_area']/p/img"]
#check_img("http://m.cctv.com/dc/n/index.shtml?articalID=ARTI1448001002177758&code=860010-1145020000", xpaths, 1)

#img
import sys
if len(sys.argv) == 2:
	#xpaths=["//img"]
	#check_img("http://m.baidu.com./ssid=0/from=0/bd_page_type=1/uid=94A95CF79EB83D4797E3ADE1AC66F7C9/t=news_top/tc?order=1&pfr=3-11-bdindex-top-6--&m=0&src=http%3A%2F%2Fnews.cqnews.net%2Fhtml%2F2015-11%2F27%2Fcontent_35862507.htm", xpaths, 0)
	#check_img("http://m.baidu.com/news?fr=mohome&ssid=0&from=&uid=&pu=sz%401320_1001%2Cta%40iphone_2_4.0_3_534&bd_page_type=1#page/chosen/http%3A%2F%2Fsports.163.com%2F15%2F1127%2F19%2FB9EVVNVG00051C89.html/%E6%9B%9D%E7%94%B3%E8%8A%B1%E5%AF%BB%E9%94%8B%E6%AC%B2%E8%B4%AD%E5%9F%83%E6%89%98%E5%A5%A5/%E7%BD%91%E6%98%93%E4%BD%93%E8%82%B2/1448626604000/10828169368740776447", xpaths, 1)

	xpaths=["//p[@class='f_center']/img"]
	check_img("http://tech.163.com/15/1127/08/B9DPDEJK000915BD.html", xpaths, 1)
	check_img("http://tech.163.com/15/1127/07/B9DL7PCK00094P0U.html", xpaths, 0)
	check_img("http://news.163.com/15/1127/19/B9EVS1GK000155IV.html#163interesting?xstt", xpaths, 2)
	check_img("http://news.163.com/15/1127/18/B9ETI31G00014TUH.html#163interesting?xstt", xpaths, 8)
	check_img("http://news.163.com/15/1127/14/B9EEDIVQ0001121M.html", xpaths, 1)

	xpaths=["//div/div/p[@class='a3']/img"]
	check_img("http://m.sohu.com/n/428445902/?wscrid=46653_7", xpaths, 4)
	check_img("http://m.sohu.com/n/428381716/?wscrid=1137_20", xpaths, 1)

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

	xpaths=["//div/img[@class='j_fullppt']","//div/img[@class='j_fullppt_cover']","//img[@data-role='img-slide']","//div[@class='img_wrapper']/img"]
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkwuwv3597971.d.html?vt=4&pos=8&cid=56261", xpaths, 2)
	check_img("http://news.sina.cn/gn/2015-11-25/detail-ifxkwuwy7112185.d.html?vt=4&pos=8&cid=56261", xpaths, 2)
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkxfvn9008810.d.html?vt=4&pos=11&cid=56264", xpaths, 2)
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkwuwv3601067.d.html?vt=4&pos=11&cid=56264", xpaths, 1)
	check_img("http://news.sina.cn/sh/2015-11-25/detail-ifxkwuwy7117086.d.html?vt=4&pos=11&cid=56264", xpaths, 1)
	check_img("http://blog.sina.cn/dpool/blog/s/blog_5160b89b0102w16o.html?mtch=sports&pos=10&vt=4", xpaths, 2)
	check_img("http://blog.sina.cn/dpool/blog/s/blog_683c082b0102w2zb.html?mtch=sports&pos=10&vt=4", xpaths, 1)
	check_img("http://tech.sina.com.cn/i/2015-11-29/doc-ifxmazmy2228740.shtml", xpaths, 1)
	check_img("http://tech.sina.com.cn/it/2015-11-29/doc-ifxmazmz8983876.shtml", xpaths, 1)

	xpaths=['//div/div/img']
	check_img("http://xw.qq.com/news/20151126055197/NEW2015112605519702", xpaths, 3)
	check_img("http://xw.qq.com/news/20151127054496/NEW2015112705449602", xpaths, 7)

	print "test fin."



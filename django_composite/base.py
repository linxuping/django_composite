#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
import datetime
import sys
import traceback
import sqlite3
from lxml import etree
import smtplib
from email.mime.text import MIMEText
import logging
import random
logger = logging.getLogger('news') # 这里用__name__通用,自动检测.
import yaml
g_config = yaml.load(file("django_composite/conf.yaml"))
import threading
g_db_lock = threading.Lock()

import jieba.posseg as pseg
word_types = ["n", "ns", "nr", "eng"]

g_key_weights = {}
#debug.
is_debug = True

def get_days_ago(days):
  import datetime
  nowt = datetime.datetime.now()
  days_ago = nowt + datetime.timedelta(days=-2)
  return days_ago.strftime("%Y-%m-%d")
def get_current_min():
  return int(time.localtime()[4])


def get_img_xpath(_url,xpath):
	nodes = get_nodes(_url, xpath)
	if len(nodes) > 0: 
		try:
			for _n in nodes:
				_src = _n.get("src")
				if _src == None:
					continue
				if (_src.find(".png")!=-1 or _src.find(".jpg")!=-1 or _src.find(".jpeg")!=-1) and _src.find("http")==0 and _src.find("default")==-1:
					return _src
		except:
			print "exception. nodes empty. ",nodes
			pass
	return ""


def get_nodes2(_url,_xpath):
	rets = get_nodes(_url,_xpath)
	if False and len(rets) ==0:
		try:
			import commands
			ret,res = commands.getstatusoutput("wget -O - %s 2>/dev/null"%_url)
			#print "wget %s -O -"%_url,ret,res[:100]
			#f = open("test.html", "w")
			#f.write(res)
			#f.close()
			tree = etree.HTML(res)
			rets = tree.xpath(_xpath)
		except:
			rets = []
	return rets


def add_imgs(imgs, url):
	if url=="" or url==None or len(imgs)>=3:
		return
	#ignores = ["d.ifengimg.com","rcode","default","blank","load"]
	ignores = g_config["ignoreurls"]
	_tmp = url.split("/")[-1]
	if _tmp.find(".") != -1:
		for img in imgs:
			if img.find(_tmp) != -1:
				return
	hit = False
	for ig in ignores:
		if url.find(ig) != -1:
			hit = True
			break
	if not hit:
		imgs.add(url)


def get_net_img_size(url):
		#!/usr/bin/env python
	#encoding=utf-8
	try:
		import cStringIO, urllib2, Image
		file = urllib2.urlopen(url)
		tmpIm = cStringIO.StringIO(file.read())
		im = Image.open(tmpIm)
		#print im.format, im.size, im.mode
		return im.size
	except:
		return (0,0)

def get_imgs(_title,_url):
	imgs = set()
	postfixs = [".png",".jpg",".jpeg"]
	host = _url.split("http://")[1].split("/")[0]
	xpath_dic = g_config["xp_imgs"]
	for _k in xpath_dic.keys():
		if host.find(_k) == -1:
			continue
		for xpath in xpath_dic[_k]:
			nodes = get_nodes2(_url,xpath)
			for node in nodes:
				try:
					_src = node.get("src")
					if _src == None:
						continue
					_latest = _src.rsplit("/")[1]
					for postfix in postfixs:
						if _latest.find(".")!=-1 and _latest.find(postfix)==-1:
							continue
						#print "hit>>> ",_src
						add_imgs(imgs,_src)
						break
				except:
					print "exception."

	if len(imgs) == 0:
		#try get.
		words = pseg.cut(_title)
		words = [ w.word for w in words ]
		ymd = time.strftime("%d_%m_%Y").split("_")
		nodes = get_nodes2(_url,"//img")
		for node in nodes:
			_src = node.get("src")
			_h = None
			_w = None
			if node.get("height")!=None and node.get("height").isdigit() and node.get("width")!=None and node.get("width").isdigit():
				_h = int(node.get("height"))
				_w = int(node.get("width"))
			else:
				_h,_w = get_net_img_size(_src)
			if (_h>int(g_config["nimg_size_limit"][0]) and _w>int(g_config["nimg_size_limit"][1])) or \
					(_h>int(g_config["nimg_size_limit"][2]) and _w>int(g_config["nimg_size_limit"][3])):
				add_imgs(imgs,_src)
				continue

			if _src==None or (_src.find(".")!=-1 and _src.rsplit(".")[1] not in postfixs):
				continue
			if _src.find(ymd[1])!=-1 and _src.find(ymd[2])!=-1:# and _src.find(ymd[0])!=-1:
				add_imgs(imgs,_src)

			_alt = node.get("alt")
			if _alt == None:
				continue
			ws = pseg.cut(_alt)
			_count2 = 0
			for w in [ w.word for w in ws ]:
				if w in words:
					_count2 = _count2+1
				if _count2 > 3:
					add_imgs(imgs,_src)
					break

	#3.default
	icon = ""
	logos = g_config["logos"]
	for _k,_v in logos.items():
		if host.find(_k) != -1:
			icon = "/static/logo/%s"%_v
	if icon == "":
		icon = "/static/news.png"
	#print "fin. "
	#logger.info("get_imgs: %s %s %d"%(_title,icon,len(imgs)))
	return icon,imgs


class attr:
	def __init__(self, key, value):
		self.key = key
		self.value = value
		if False and isinstance(self.value, list):
			for item in self.value:
				if isinstance(item,news_item):
					#print "START. ", item.text,item.href
					item.icon,item.imgs = get_imgs(item.text,item.href)
					#print "END. ", self.key,item.imgs
					#logger.info("Imgs: %s:%s:%s."%(self.key,item.href,str(item.imgs)) )

class news_item:
  def __init__(self, text, href):
    self.text = text
    self.href = href
    self.icon,self.imgs = get_imgs(text,href)
class news:
  def __init__(self, topic="", news_items=None, navbar_key=None):
    self.topic = topic
    self.news_items = news_items
    self.offical_link = ""
    if navbar_key != None:
      global navbar_infos
      self.offical_link = navbar_infos[navbar_key]["url_infos"][topic][2]
  def filter(self, searchcontent):
    tmp_new_items = []
    for tmp_item in self.news_items:
      #print tmp_item,tmp_item.text,searchcontent
      if tmp_item.text.find(searchcontent) != -1:
        tmp_new_items.append(tmp_item)
    return news(self.topic, tmp_new_items)

tag_tech = u"互联网"
tag_soci = u"今日头条"
tag_phys = u"体育"
tag_amus = u"娱乐"
tag_cont = u"联系我"

#-------------------- common part ------------------#
hotkeys_black_list = [u"问题",u"能力",u"图片",u"图",u"内衣",u"内裤",u"模式",u"手机",u"平台",u"全球",u"企业",u"CEO",u"科技",u"领域",u"全面",u"",u"",u""]
#-------------------- tech part ------------------#
tech_tag=u"_"+tag_tech
url_infos_tech = {
  #topic: [tech link, xpath, offical link]
  u"凤凰网"+tech_tag: ["http://tech.ifeng.com/", ['//a'], "http://www.ifeng.com/", time.strftime('%Y%m%d',time.localtime(time.time())) ],#2014_07/24
  "36kr": ["http://www.36kr.com/", ['//a[@target="_blank"]'], "http://www.36kr.com/", "/p/"],#
  "cnbeta": ["http://m.cnbeta.com/", ['//li/div/a'], "http://m.cnbeta.com/", ""],#
  #u"新浪"+tech_tag: ["http://tech.sina.com.cn/internet/", ['//a'], "http://www.sina.com.cn/", "" ],#2014-07-24
  #u"腾讯"+tech_tag: ["http://tech.qq.com/", ['//a'], "http://www.qq.com/", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  #u"百度"+tech_tag: ["http://m.baidu.com/news?from=844c&vit=fns#index/info:%E4%BA%92%E8%81%94%E7%BD%91", ['//a'], "http://www.baidu.com/", "http"],#'//div[@class="feeds-item"]/h3/a'
  #u"网易"+tech_tag: ["http://tech.163.com/", ['//a'], "http://www.163.com/", time.strftime('%Y/%m%d',time.localtime(time.time()))[2:] ],#"14/0724"
  #"google.com": ["https://news.google.com.hk/news/section?pz=1&cf=all&ned=cn&topic=t", '//span[@class="titletext"]', "https://news.google.com.hk/news/", "http"],#
} 
#go to config.py 
hotkeys_tech = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
hotkeys_tech_white_list = [u"车", u"移动", u"生活", u"路由器", u"腕带", u"手表", u"谷歌", u"微软", u"百度", u"阿里", u"腾讯", u"BAT", u"锤子", u"雷军"]
hotkeys_tech_black_list = [u"中国", u"技术", u"行业", u"公司", u"传", u"美", u"用户", u"市场", u"版", u"产品", u"功能",u"全部"]
words_stat_tech = {} #{"word":count}
all_news_tech = [news( url_infos_tech.keys()[0] )]*len(url_infos_tech) #initial
#-------------------------------------------------#
#------------------- social part -----------------#
url_infos_soci = {
  #topic: [tech link, xpath, offical link]
  ##u"新华社": ["http://3g.news.cn/html/", ["//div[@class='newlist']/ul/li/a"], "http://3g.news.cn", ""],#
  #u"凤凰网": ["http://inews.ifeng.com/", ['//p'], "http://inews.ifeng.com/", "news"],#
  #u"搜狐": ["http://m.sohu.com/", ["//section/p/a","//h4/a/strong","//div/div/a"], "http://m.sohu.com", "/?wscrid="],
  u"新浪": ["http://news.sina.cn/", ["//h3[@class='carditems_list_h3']"], "http://news.sina.cn", ""],
  #u"网易": ["http://news.163.com/mobile/", ['//li/h4/a'], "http://www.163.com/", "" ],
  #u"腾讯": ["http://xw.qq.com/m/news", ['//h2'], "http://news.qq.com", "" ],#20140724 - 201407
  ##u"百度": ["http://m.baidu.com/news", ["//div[@class='list-item']/a"], "http://m.baidu.com", "" ],#
  #u"CCTV": ["http://m.cctv.com/", ["//div/div/h3/a","//div/div/p/a","//ul[@class='first-child-no-top last-child-no-bottom']/li/a","//ul[@class='first-child-no-top']/li/a"], "http://m.cctv.com/", "index.shtml"],#
  #u"people": ["http://m.people.cn", ["//ul/li/a"], "http://m.people.cn", ""],#

} 
hotkeys_soci = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
hotkeys_soci_white_list = [u"车", u"房", u"球", u"涨", u"跌", u"天气", u"足球", u"移动", u"手机", u"大妈", u"游戏", u"恒大", u"淘宝", u"电影", u"双十一"]
hotkeys_soci_black_list = [u"男人", u"女人", u"男子", u"女子", u"男孩", u"女孩", u"人", 
							u"公司", u"全国", u"头条", u"我", u"我们", u"直播", u"视频直播", 
							u"图", u"中国", u"思客", u"网友", u"社会",u"官方",u"先生",u"企业",u"家庭",u"全部",u"",u"",u"",u""]
words_stat_soci = {} #{"word":count}
all_news_soci = [news( url_infos_soci.keys()[0] )]*len(url_infos_soci) #initial
#-------------------------------------------------#
#------------------- physical part -----------------#
phys_tag=u"_"+tag_phys
url_infos_phys = {
  #u"新浪"+phys_tag: ["http://sports.sina.cn/?from=wap", ['//h3'], "http://sports.sina.cn/?from=wap", "" ],#2014_07/24
  u"搜狐"+phys_tag: ["http://m.sohu.com/c/27/", ['//a'], "http://m.sohu.com", ""],#
  #u"腾讯"+phys_tag: ["http://xw.qq.com/m/sports/index.htm", ['//h2'], "http://xw.qq.com/m/sports/index.htm", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  #u"21cn"+phys_tag: ["http://3g.21cn.com/zy/sports/cbs/", ['//a'], "http://3g.21cn.com/zy/sports/cbs/", time.strftime('%Y/%m%d',time.localtime(time.time())) ],#20140724
  #u"百度"+phys_tag: ["http://internet.baidu.com/", ['//a'], "http://www.baidu.com/", ""],#'//div[@class="feeds-item"]/h3/a'
  u"网易"+phys_tag: ["http://3g.163.com/touch/sports/", ['//p'], "http://3g.163.com/touch/sports/", "" ],#"14/0724"
} 
hotkeys_phys = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
hotkeys_phys_white_list = [u"车", u"房", u"球", u"涨", u"跌", u"天气", u"足球", u"移动", u"手机", u"大妈", u"游戏", u"恒大", u"淘宝", u"电影", u"双十一"]
hotkeys_phys_black_list = [u"男人", u"女人", u"男子", u"女子", u"男孩", u"女孩", u"人", 
							u"公司", u"全国", u"头条", u"我", u"我们", u"直播", u"视频直播", 
							u"图", u"中国", u"思客", u"网友", u"社会",u"官方",u"先生",u"企业",u"家庭",u"全部",u"视频",u"",u"",u""]
words_stat_phys = {} #{"word":count}
all_news_phys = [news( url_infos_phys.keys()[0] )]*len(url_infos_phys) #initial
#-------------------------------------------------#
#------------------- amuse part -----------------#
_tag=u"_"+tag_amus
url_infos_amus = {
  #u"新浪"+_tag: ["http://sports.sina.cn/?from=wap", ['//h3'], "http://sports.sina.cn/?from=wap", "" ],#2014_07/24
  #u"搜狐"+_tag: ["http://m.sohu.com/c/27/", ['//a'], "http://m.sohu.com", ""],#
  #u"腾讯"+_tag: ["http://xw.qq.com/m/sports/index.htm", ['//h2'], "http://xw.qq.com/m/sports/index.htm", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  #u"21cn"+_tag: ["http://3g.21cn.com/zy/sports/cbs/", ['//a'], "http://3g.21cn.com/zy/sports/cbs/", time.strftime('%Y/%m%d',time.localtime(time.time())) ],#20140724
  #u"百度"+_tag: ["http://internet.baidu.com/", ['//a'], "http://www.baidu.com/", ""],#'//div[@class="feeds-item"]/h3/a'
  u"网易"+_tag: ["http://3g.163.com/touch/sports/", ['//p'], "http://3g.163.com/touch/sports/", "" ],#"14/0724"
} 
hotkeys_amus = ["", "", "", "", "", "", "", "", ""] 
hotkeys_amus_white_list = []
hotkeys_amus_black_list = [u"",u"",u""]
words_stat_amus = {} #{"word":count}
all_news_amus = [news( url_infos_amus.keys()[0] )]*len(url_infos_amus) #initial
#-------------------------------------------------#

navbar_infos = {
  tag_tech: {"url_infos":url_infos_tech, "white_list":hotkeys_tech_white_list, "black_list":hotkeys_tech_black_list+hotkeys_black_list, \
           "hot_keys":hotkeys_tech, "words_stat":words_stat_tech, "all_news":all_news_tech},
  tag_soci: {"url_infos":url_infos_soci, "white_list":hotkeys_soci_white_list, "black_list":hotkeys_soci_black_list+hotkeys_black_list, \
           "hot_keys":hotkeys_soci, "words_stat":words_stat_soci, "all_news":all_news_soci},
  tag_phys: {"url_infos":url_infos_phys, "white_list":hotkeys_phys_white_list, "black_list":hotkeys_phys_black_list+hotkeys_black_list, \
           "hot_keys":hotkeys_phys, "words_stat":words_stat_phys, "all_news":all_news_phys},
  tag_amus: {"url_infos":url_infos_amus, "white_list":hotkeys_amus_white_list, "black_list":hotkeys_amus_black_list+hotkeys_black_list, \
           "hot_keys":hotkeys_amus, "words_stat":words_stat_amus, "all_news":all_news_amus},
}
is_first_load = True


def convert_unicode(s):
  if isinstance(s, unicode):
    return s
  code_types = ["utf-8", "gbk", "ASCII", "Latin-1", "ISO8859—1", "UTF-16", "cp936", "gb2312", "MBCS", "DBCS"]
  for _type in code_types:
    try:
      return unicode(s, _type)
    except:
      pass
  return unicode(s, "utf-8")

def try_get_nodes2(_url, _xpath):
  import commands
  ret,res = commands.getstatusoutput("wget -O - %s 2>/dev/null"%_url)
  res = convert_unicode(res)
  tree = etree.HTML(res)
  return tree.xpath(_xpath)

def try_get_nodes(_url, _xpath):
  headers = {"User-Agent":"Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"}
  req = urllib2.Request(url=_url,headers=headers)
  resp = urllib2.urlopen(req, timeout=3)
  #resp = urllib2.urlopen(_url, timeout=8)
  res = resp.read()
  res = convert_unicode(res)
  tree = etree.HTML(res)
  rets = tree.xpath(_xpath)
  #if rets == []:
  #  return try_get_nodes2(_url,_xpath)
  return rets
def get_nodes(_url, _xpath):
  rets = []
  for i in range(3):
    try:
      #print "try: ",i,_url
      rets = try_get_nodes(_url, _xpath)
      break
    except:
      #print "get_nodes exception. ",_url
      continue
  if len(rets) == 0:
    pass#logger.error("get_nodes fail. %s:%s"%(_url,_xpath) )
  return rets


def get_href(node):
	href = None
	for i in range(6):
		href = node.get("href")
		if href != None:
			return href
		node = node.getparent()
		if node == None:
			return None
 

tmpset=set()
def get_news(topic, navbar_key, old_new_items):
  global word_types, navbar_infos, topic_hit, tmpset
  url_infos = navbar_infos[navbar_key]["url_infos"]
  hotkeys_tech_black_list = navbar_infos[navbar_key]["black_list"]
  #words_stat = navbar_infos[navbar_key]["words_stat"]
  news_list = []
  new_keys = set()#ignore the multi keys
  nodes3 = []
  for xpath in url_infos[topic][1]:
    nodes3 += get_nodes(url_infos[topic][0], xpath)
  tmp_words_hit = [] 
  tmpset2=set()
  #print "topic_hit ",topic_hit
  
  for node in nodes3:
    if None!=node.text and len(node.text)>10 and len(node.text)<48 \
        and not node.text in new_keys:
      node.text = node.text.strip("\r\n ")
      '''
      _href = node.get("href")
      #special deal with    <a href=***><span>text</span></a>
      #if topic=="google.com" and None!=node.getparent().get("href"):
      #  _href = node.getparent().get("href")
      if topic==u"新浪" or topic==u"新浪"+phys_tag:
        _href = node.getparent().getparent().getparent().get("href")
      elif topic==u"网易"+phys_tag:
        _href = node.getparent().getparent().get("href")
      elif topic==u"腾讯"+phys_tag:
        _href = node.getparent().get("href")
      elif topic == "36kr":
        if node.text.find(u"氪")!=-1 and node.text.find("KrTV")!=-1:
          continue
      elif topic == u"凤凰网": 
        _href = node.getparent().getparent().get("href")
      '''
      #if None!=_href and _href.find("javascript:void")!=-1:
      #  continue
      if topic == "36kr":
        if node.text.find(u"氪")!=-1 or node.text.find("KrTV")!=-1:
          continue

      _href = get_href(node)
      #print topic,node.text,_href

      if _href==None or _href.find("javascript:void")!=-1 or \
          _href.find(url_infos[topic][3])==-1 or _href.find("http://yd.sina.cn/")!=-1:
        continue
      if _href.find("http://") == -1:
         _href = url_infos[topic][2] + _href
      #end special.
      #print "[LOG add text.] ",navbar_key,topic,node.text
      if (node.text.find("[")!=-1 and node.text.find("]")!=-1) or\
         (node.text.find(u"【")!=-1 and node.text.find(u"】")):# _href.find("default")!=-1 or _href.find("rcode")!=-1:
        continue
      if (_href not in tmpset and _href not in tmpset2) and (node.text[:10] not in tmpset and node.text[:10] not in tmpset2):
        tmpset2.add(node.text[:10])
        tmpset2.add(_href)
        news_list.append(news_item(node.text, _href))
        #print "10 words ahead check existed! ",node.text[:10]  for log
      else:
        continue
      new_keys.add(node.text)

  for node in old_new_items:
    if (node.href not in tmpset and node.href not in tmpset2) and (node.text[:10] not in tmpset and node.text[:10] not in tmpset2):
      tmpset2.add(node.text[:10])
      tmpset2.add(node.href)
      news_list.append(node)
      #print "10 words ahead check existed! ",node.text[:10]  for log

  for node in news_list:
    try:
      #print "[LOG (jieba)] cutting."
      words =pseg.cut(node.text)
      tmp_words_hit2=[]
      for w in words:
        if w.flag in word_types and len(w.word)>1 and \
            not w.word in hotkeys_tech_black_list:
          #global words_stat
          if w.word in tmp_words_hit2:
            continue
          tmp_words_hit2.append(w.word)
          if not navbar_infos[navbar_key]["words_stat"].has_key(w.word):
            navbar_infos[navbar_key]["words_stat"][w.word] = 1
          else:
            navbar_infos[navbar_key]["words_stat"][w.word] = int(navbar_infos[navbar_key]["words_stat"][w.word])+1
          if w.word not in tmp_words_hit:
            tmp_words_hit.append(w.word)
            navbar_infos[navbar_key]["words_stat"][w.word] = int(navbar_infos[navbar_key]["words_stat"][w.word])+3 #不同topic都提到，说明更热门，在一个topic内频率高不表示对外热门
    except:
      logger.error("[Error Msg(jieba)] %s"%str(sys.exc_info()) )
      pass
  #print topic, "all:%d"%len(nodes3), "get:%d"%len(news_list)
  return nodes3,news_list,tmpset2


def _tofloat(_count, _key):
  #the last one '1' is used for num like 1000   3.1000 -> 3.10001 保持住后面的3个0
  return float("%s.%s1"%(_count,_key))


def get_hot_keys(dic, hot_topic_count=10, topic="None", savedb=True):
  global g_key_weights
  #dic: {"aa":2, "bb":1999, "cc":88, "dd":45, "ee":10, "ff":13}
  #max_count = 1000 #如果统计表示已经超过1000次，这么高频，不用统计了，直接放到max_topic_list
 
  if hot_topic_count > len(dic):
    hot_topic_count = len(dic)
  max_topic_list = []
  tmp_dict = {} #{1:"aa", 2:"bb", 3:"cc", 4:"dd", 5:"ee", 6:"ff"}
  tmp_list = [] #[2.11, 88.31, 45.41, 10.51, 13.61]
  count = 1
  for _k,_v in dic.items():
    #if _v > max_count:
    #  max_topic_list.append(_k)
    #  continue
    tmp_dict[count] = _k
    tmp_list.append(_tofloat(_v,count))
    count += 1
  #left_count = hot_topic_count - len(max_topic_list)
  #if left_count < 0:#need optimze,if ["aa"->1111,"bb"->2222,"cc"->9999], maybe return [aa,bb] 
  #  return max_topic_list[:hot_topic_count]
  tmp_list = sorted(tmp_list, reverse=True)
  #print tmp_list
  max_topic_counts = []
  for ii in range(hot_topic_count):
    countstr = str(tmp_list[ii]).split(".")[0]
    #if "11" == countstr:  #1 + 10(title weight)
    #  break
    max_topic_counts.append(countstr)
    tmp_dict_k = int(str(tmp_list[ii]).split(".")[1][:-1])#'88.31' -> '31' -> '3' -> 3
    max_topic_list.append(tmp_dict[tmp_dict_k])
    #debug
    g_key_weights[ tmp_dict[tmp_dict_k] ] = int(countstr)
     
    #if ii < 3:
    #  print tmp_dict[tmp_dict_k],countstr
    #save_hoykey_count(tmp_dict[tmp_dict_k], int(countstr), topic)
    if savedb:
      save_hoykey_count2(tmp_dict[tmp_dict_k], int(countstr), topic)
  #print "max_topic_counts: ",max_topic_counts
  return max_topic_list,max_topic_counts

def sort_hot_keys(dic, topic, hot_keys):
  #compare with yesterday. if lager, have higher priority
  tmp_list1 = []
  tmp_list2 = []
  for _k in hot_keys:
    count_yesterday = get_db_hotkey_count(_k, topic, yesterday())
    if dic[_k] > count_yesterday:
      tmp_list1.append(_k)
    else:
      tmp_list2.append(_k)
  return tmp_list1 + tmp_list2

 
#------------- for sqlite ---------------# 
def create_table(create_str):
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  try:
    c.execute(create_str)
    cx.commit()
  except:
    print "[Error Msg(create_table)] ",sys.exc_info()
  c.close()
def create_tables():
  create_table("create table hotkeys(name nvarchar(20), count int, topic nvarchar(100), day datetime)")
def save_hoykey_count(key, count, topic, day=None):
  #only keep two days - yesterday & today
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  if None == day:
    day = today()
  #print "save to db ",key,count,topic,day
  c.execute("delete from hotkeys where name='%s' and topic='%s' and day='%s'"%(key,topic,day))
  c.execute("insert into hotkeys values('%s', %d, '%s', '%s')"%(key,count,topic,day))
  cx.commit()
  c.close()
def get_db_hotkey_count(key, topic, day):
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  c.execute("select count from hotkeys where name='%s' and topic='%s' and day='%s'"%(key,topic,day))
  cx.commit()
  ret = c.fetchone()
  if None == ret:
    return 0
  count = ret[0]
  c.close()
  return int(count)
def del_hotkeys_expired(day=None, expired_days=1):
  if None == day:
    day = today()
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  #delete day < datetime-n
  c.execute("delete from hotkeys where day < %s-%d"%(day, expired_days))
  cx.commit()
  c.close()
#----------------------------------------#
def today():
  return datetime.date.today().strftime('%Y%m%d')
def yesterday():
  return (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y%m%d')
  
#-------------- send mail ---------------#
import base64
def send_mail(to_list,sub,content):
    #设置服务器，用户名、口令以及邮箱的后缀
    mail_host="smtp.sohu.com"
    mail_user="ma201401"
    mail_pass="abcd1234"
    mail_postfix="sohu.com"
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content)
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = to_list
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        print '[LOG] send mail ok.'
        return True
    except Exception, e:
        print '[LOG] send mail fail.'
        print str(e)
        return False
#----------------------------------------#
 
#------------------- init_news2 ------------------#
#new algorithm of hot keys:   except column day
'''
name topic count_old count_avg count_new weight     date
                     co+cn/2             gen_weight  
up_hour:
  if init:
    co=ca=cn  weight=0
  else:
    ca = ca+cn / 2
    gen_weight
	up_day: 
	  clear 2 days ago
	  co=ca weight=0 
	  gen_weight
'''
     
def gen_weight(c_old, c_new):
  #1\count  *  2\rate up
  if c_new >= c_old:
    tmp = (c_new-c_old)*(c_new-c_old)*(c_new-c_old)*(c_new-c_old)+c_old #main page change.
    if c_new > 5:
      tmp = 100 + c_new
    if tmp < c_old:
      tmp = c_old
    return tmp
  else:
    return c_new

def create_tables2():
  create_table("create table hotkeys2(name nvarchar(20), count int, count_avg int, count_new int, weight int, topic nvarchar(100), createdate date not null)")
def save_hoykey_count2(key, count_new, topic):
  #和上一次对比，如果更热门了，增加weight，如果冷门些了，降低weight
  #key = str(key)
  #topic = str(topic)
  g_db_lock.acquire()
  try:
    cx = sqlite3.connect("test.db")
    c = cx.cursor()
    #print "save to db ",key,count,topic
    c.execute("select count,count_avg from hotkeys2 where name='%s' and topic='%s'"%(key,topic))
    oldcount = c.fetchone()
    if None == oldcount:
      c.execute("insert into hotkeys2 values('%s', %d, %d, %d, %d, '%s', datetime('now','localtime'))"%(key,count_new,count_new,count_new,count_new,topic))
    else:
      count_avg = (int(oldcount[1]) + count_new)/2
      weight= gen_weight(int(oldcount[0]), count_new)
      global g_key_weights
      g_key_weights[key] = weight 
      c.execute("update hotkeys2 set count_avg=%d,count_new=%d,weight=%d where name='%s' and topic='%s'"%(count_avg,count_new,weight,key,topic))
    cx.commit()
    c.close()
  except:
    logger.error( "Exception(%s): %s, %s"%(str(sys._getframe().f_code.co_name), str(sys.exc_info()),str(traceback.format_exc()) ))
  g_db_lock.release()
def update_base():
  #build when 00:00 and then save hotkey
	g_db_lock.acquire()
	try:
	  cx = sqlite3.connect("test.db")
	  c = cx.cursor()
	  _sql = "select name,topic,count_avg from hotkeys2"
	  c.execute(_sql)
	  items = c.fetchall()
	  if None == items:
	    print "ERROR: %s"%_sql
	  else:
	    for i in range(len(items)):
	      key = items[i][0]
	      topic = items[i][1]
	      count_avg = int(items[i][2])
	      #c.execute("update hotkeys2 set count=%d,weight=0 where name='%s' and topic='%s'"%(count_avg,key,topic))
	      c.execute("update hotkeys2 set count=%d,weight=%d where name='%s' and topic='%s'"%(count_avg,count_avg,key,topic))
	  cx.commit()
	  c.close()
	except:
		logger.error( "Exception(%s): %s, %s"%(str(sys._getframe().f_code.co_name), str(sys.exc_info()),str(traceback.format_exc()) ))
		return
	logger.info("%s OK."%(str(sys._getframe().f_code.co_name)))
	g_db_lock.release()
	

def del_hotkeys_expired2():
	g_db_lock.acquire()
	try:
		cx = sqlite3.connect("test.db")
		c = cx.cursor()
		#delete day < datetime-n
		#c.execute("delete from hotkeys2 where createdate < date_sub(now(),interval 2 day)")
		c.execute("delete from hotkeys2 where createdate < '%s'"%get_days_ago(2))
		cx.commit()
		c.close()
	except:
		logger.error( "Exception(%s): %s, %s"%(str(sys._getframe().f_code.co_name), str(sys.exc_info()),str(traceback.format_exc()) ))
	g_db_lock.release()
def sort_hot_keys2(topic):
  #topic = str(topic)
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  #print "save to db ",key,count,topic
  c.execute("select name from hotkeys2 where topic='%s' and weight>0 and (weight>count or count>10) ORDER BY weight DESC"%topic)
  keyarrs = c.fetchall()
  if None == keyarrs:
    return []
  #cx.commit()
  c.close()
  tmplist = []
  #print tmplist
  for i in range(len(keyarrs)):
    tmplist.append(keyarrs[i][0])
  return tmplist
def print_db_me():
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  c.execute("select * from hotkeys2")
  keyarrs = c.fetchall()
  if None == keyarrs:
    print "ERROR: db empty."
  c.close()
  tmplist = []
  for i in range(len(keyarrs)):
    print "line: ",keyarrs[i]
#-------------------------------------------------#
 
#-------------------------- UNIT TEST ----------------------------#
unittest = False
def ut_get_hot_keys():
  tmp_dict = {"aa":2, "bb":1999, "cc":88, "dd":45, "oo":1, "ee":10, "ff":13}
  print get_hot_keys(tmp_dict, 1)," answer: bb"
  print get_hot_keys(tmp_dict, 2)," answer: bb,cc"
  print get_hot_keys(tmp_dict, 3)," answer: bb,cc,dd"
  print get_hot_keys(tmp_dict, 4)," answer: bb,cc,dd,ff"
  print get_hot_keys(tmp_dict, 5)," answer: bb,cc,dd,ff,ee"
  print get_hot_keys(tmp_dict, 6)," answer: bb,cc,dd,ff,ee,aa"
  print get_hot_keys(tmp_dict, 7)," answer: bb,cc,dd,ff,ee,aa"
  print get_hot_keys(tmp_dict, 8)," answer: bb,cc,dd,ff,ee,aa"
def ut_save_hoykey_count():
  create_tables()
  save_hoykey_count("aaa", 12, tag_tech, "20140730")
  save_hoykey_count("bbb", 17, tag_soci, "20140729")
  print get_db_hotkey_count("bbb", tag_soci, "20140729")
  print get_db_hotkey_count("bbb", tag_soci, "20140720")
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  c.execute("select * from hotkeys") 
  print c.fetchall()
  c.close()
def ut_show_hoykeys():
  cx = sqlite3.connect("test.db")
  c = cx.cursor()
  c.execute("select * from hotkeys") 
  print c.fetchall()
  c.close()
def ut_send_mail():
  if send_mail("417306303@qq.com","hello","this is python sent"):
    print "send successful"
  else:
    print "send fail"
def ut_gen_weight():
  print "44 66",gen_weight(44,66)
  print "5 17",gen_weight(5,17)
  print "44 33",gen_weight(44,33)
  print "5 7",gen_weight(5,7)
  print "7 5",gen_weight(7,5)
  print "101 101",gen_weight(101,101)
def ut_test_new_db():
  create_tables2()
  save_hoykey_count2("testkey", 5, "topic")
  save_hoykey_count2("testkey2", 5, "topic")
  save_hoykey_count2("testkey", 7, "topic")
  print_db_me()
  print "run del_hotkeys_expired2."
  del_hotkeys_expired2()
  print_db_me()
  print "run sort_hot_keys2.",sort_hot_keys2("topic")
  update_base()
  print_db_me()

if unittest:
  #ut_get_hot_keys()
  #ut_save_hoykey_count()
  #ut_test_db_day()
  #print today()
  #print yesterday()
  #ut_show_hoykeys()

  #print get_days_ago(2)
  #print "hour: ",get_current_hour()
  #ut_gen_weight()
  #ut_test_new_db()

  ut_send_mail()

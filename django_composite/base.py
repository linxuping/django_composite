#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
from lxml import etree

def get_nodes(_url, _xpath):
  try:
    resp = urllib2.urlopen(_url)
    res = resp.read()
    tree = etree.HTML(res)
    return tree.xpath(_xpath)
  except:
    return []
  
url_infos = {
  #topic: [tech link, xpath, offical link]
  "163.com": ["http://tech.163.com/", '//a', "http://www.163.com/", time.strftime('%Y/%m%d',time.localtime(time.time()))[2:] ],#"14/0724"
  "qq.com": ["http://tech.qq.com/", '//a', "http://www.qq.com/", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  "sina.com": ["http://tech.qq.com/", '//a', "http://www.sina.com.cn/", time.strftime('%Y-%m-%d',time.localtime(time.time())) ],#2014-07-24
  "ifeng.com": ["http://tech.ifeng.com/", '//a', "http://www.ifeng.com/", time.strftime('%Y_%m/%d',time.localtime(time.time())) ],#2014_07/24
  "baidu.com": ["http://internet.baidu.com/", '//div[@class="feeds-item"]/h3/a', "http://www.baidu.com/", "http"],#
  "cnbeta.com": ["http://m.cnbeta.com/", '//li/div/a', "http://m.cnbeta.com/", "http"],#
} #go to config.py 
hot_keys = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
all_news = []
  
class news_item:
  def __init__(self, text, href):
    self.text = text
    self.href = href
class news:
  def __init__(self, topic, news_items):
    self.topic = topic
    self.news_items = news_items
    global url_infos
    self.offical_link = url_infos[topic][2]

def get_news(topic, searchcontent):
  global url_infos
  news_list = []
  nodes3 = get_nodes(url_infos[topic][0], url_infos[topic][1])
  for node in nodes3:
    if None!=node.get("href") and node.get("href").find(url_infos[topic][3])!=-1 \
	   and None!=node.text and len(node.text)>10 and len(node.text)<28 and node.text.find(searchcontent)!=-1:
      news_list.append(news_item(node.text,node.get("href")))
  return news_list
  

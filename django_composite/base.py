#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
from lxml import etree

def get_nodes(_url, _xpath):
  resp = urllib2.urlopen(_url)
  res = resp.read()
  tree = etree.HTML(res)
  return tree.xpath(_xpath)
  
url_infos = {
  #topic: [tech link, xpath, offical link]
  "163.com": ["http://tech.163.com/", '//a', "http://www.163.com/", time.strftime('%Y/%m%d',time.localtime(time.time()))[2:] ],#"14/0724"
  "qq.com": ["http://tech.qq.com/", '//a', "http://www.qq.com/", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  "sina.com": ["http://tech.qq.com/", '//a', "http://www.sina.com.cn/", time.strftime('%Y-%m-%d',time.localtime(time.time())) ],#2014-07-24
} #go to config.py
  
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

    
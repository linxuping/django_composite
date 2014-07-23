#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
from lxml import etree

def get_nodes(_url, _xpath):
  resp = urllib2.urlopen(_url)
  res = resp.read()
  tree = etree.HTML(res)
  return tree.xpath(_xpath)
  
offical_links = {
  #topic: [tech link, xpath, offical link]
  "163.com": ["http://tech.163.com/", '//h2[@class="color-link"]/a', "http://www.163.com/"],
  "qq.com": ["http://tech.qq.com/", '//div[@class="Q-tpList"]/div/h3/a', "http://www.qq.com/"],
  "sina.com": ["http://tech.qq.com/", '//div[@class="Q-tpList"]/div/h3/a', "http://www.sina.com.cn/"],
} #go to config.py
  
class news_item:
  def __init__(self, text, href):
    self.text = text
    self.href = href
class news:
  def __init__(self, topic, news_items):
    self.topic = topic
    self.news_items = news_items
    global offical_links
    self.offical_link = offical_links[topic][2]

    
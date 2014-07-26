#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
import sys
from lxml import etree

url_infos = {
  #topic: [tech link, xpath, offical link]
  "163.com": ["http://tech.163.com/", '//a', "http://www.163.com/", time.strftime('%Y/%m%d',time.localtime(time.time()))[2:] ],#"14/0724"
  "qq.com": ["http://tech.qq.com/", '//a', "http://www.qq.com/", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  "sina.com": ["http://tech.sina.com.cn/internet/", '//a', "http://www.sina.com.cn/", time.strftime('%Y-%m-%d',time.localtime(time.time())) ],#2014-07-24
  "ifeng.com": ["http://tech.ifeng.com/", '//a', "http://www.ifeng.com/", time.strftime('%Y_%m/%d',time.localtime(time.time())) ],#2014_07/24
  "baidu.com": ["http://internet.baidu.com/", '//div[@class="feeds-item"]/h3/a', "http://www.baidu.com/", "http"],#
  "cnbeta.com": ["http://m.cnbeta.com/", '//li/div/a', "http://m.cnbeta.com/", "http"],#
} #go to config.py 
hot_keys = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
hot_key_white_list = [u"车", u"谷歌", u"百度", u"阿里", u"腾讯", u"锤子"]
hot_key_black_list = [u"中国", u"技术", u"行业", u"公司"]
is_first_load = False

def get_nodes(_url, _xpath):
  try:
    resp = urllib2.urlopen(_url)
    res = resp.read()
    tree = etree.HTML(res)
    return tree.xpath(_xpath)
  except: 
    print "[Error Msg] ",sys.exc_info()
    return []
  
class news_item:
  def __init__(self, text, href):
    self.text = text
    self.href = href
class news:
  def __init__(self, topic="", news_items=None):
    self.topic = topic
    self.news_items = news_items
    global url_infos
    self.offical_link = url_infos[topic][2]
  def filter(self, searchcontent):
    tmp_new_items = []
    for tmp_item in self.news_items:
      if tmp_item.text.find(searchcontent) != -1:
        tmp_new_items.append(tmp_item)
    return news(self.topic, tmp_new_items)
all_news = [news("qq.com")]*len(url_infos) #initial

import jieba.posseg as pseg
word_types = ["n", "ns", "nr", "eng"]
new_words_stat = {} #{"word":count}
def get_news(topic):
  global url_infos, word_types, hot_key_black_list
  news_list = []
  new_keys = []#ignore the multi keys
  nodes3 = get_nodes(url_infos[topic][0], url_infos[topic][1])
  for node in nodes3:
    if None!=node.get("href") and node.get("href").find(url_infos[topic][3])!=-1 \
	   and None!=node.text and len(node.text)>10 and len(node.text)<28  \
	   and not node.text in new_keys:
	  #and node.text.find(searchcontent)!=-1
      news_list.append(news_item(node.text,node.get("href")))
      new_keys.append(node.text)
      try:
        #print "[LOG (jieba)] cutting."
        words =pseg.cut(node.text)
        for w in words:
          if w.flag in word_types and not w.word in hot_key_black_list:
            global new_words_stat
            if not new_words_stat.has_key(w.word):
              new_words_stat[w.word] = 1
            else:
              new_words_stat[w.word] = new_words_stat[w.word]+1
            #print "[LOG (jieba word)]", w.word
      except:
        print "[Error Msg(jieba)] ",sys.exc_info()
        pass
  return news_list

def get_hot_keys(dic, hot_topic_count=10):
  #dic: {"aa":2, "bb":1999, "cc":88, "dd":45, "ee":10, "ff":13}
  max_count = 1000 #如果统计表示已经超过1000次，这么高频，不用统计了，直接放到max_topic_list
 
  if hot_topic_count > len(dic):
    hot_topic_count = len(dic)
  max_topic_list = []
  tmp_dict = {} #{1:"aa", 2:"bb", 3:"cc", 4:"dd", 5:"ee", 6:"ff"}
  tmp_list = [] #[2.11, 88.31, 45.41, 10.51, 13.61]
  def _tofloat(_count, _key):
    #the last one '1' is used for num like 1000   3.1000 -> 3.10001 保持住后面的3个0
    return float("%s.%s1"%(_count,_key))
  count = 1
  for _k,_v in dic.items():
    if _v > max_count:
      max_topic_list.append(_k)
      continue
    tmp_dict[count] = _k
    tmp_list.append(_tofloat(_v,count))
    count += 1
  left_count = hot_topic_count - len(max_topic_list)
  if left_count < 0:#need optimze,if ["aa"->1111,"bb"->2222,"cc"->9999], maybe return [aa,bb] 
    return max_topic_list[:hot_topic_count]
  tmp_list = sorted(tmp_list, reverse=True)
  #print tmp_list
  for ii in range(left_count):
    tmp_dict_k = int(str(tmp_list[ii]).split(".")[1][:-1])#'88.31' -> '31' -> '3' -> 3
    max_topic_list.append(tmp_dict[tmp_dict_k])
  return max_topic_list
 
#-------------------------- UNIT TEST ----------------------------#
unittest = False
def ut_get_hot_keys():
  tmp_dict = {"aa":2, "bb":1999, "cc":88, "dd":45, "ee":10, "ff":13}
  print get_hot_keys(tmp_dict, 1)," answer: bb"
  print get_hot_keys(tmp_dict, 2)," answer: bb,cc"
  print get_hot_keys(tmp_dict, 3)," answer: bb,cc,dd"
  print get_hot_keys(tmp_dict, 4)," answer: bb,cc,dd,ff"
  print get_hot_keys(tmp_dict, 5)," answer: bb,cc,dd,ff,ee"
  print get_hot_keys(tmp_dict, 6)," answer: bb,cc,dd,ff,ee,aa"
  print get_hot_keys(tmp_dict, 7)," answer: bb,cc,dd,ff,ee,aa"
  print get_hot_keys(tmp_dict, 8)," answer: bb,cc,dd,ff,ee,aa"
if unittest:
  ut_get_hot_keys()
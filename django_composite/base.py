#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
import datetime
import sys
import sqlite3
from lxml import etree

class news_item:
  def __init__(self, text, href):
    self.text = text
    self.href = href
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
      if tmp_item.text.find(searchcontent) != -1:
        tmp_new_items.append(tmp_item)
    return news(self.topic, tmp_new_items)
	
#-------------------- tech part ------------------#
url_infos_tech = {
  #topic: [tech link, xpath, offical link]
  "163.com": ["http://tech.163.com/", '//a', "http://www.163.com/", time.strftime('%Y/%m%d',time.localtime(time.time()))[2:] ],#"14/0724"
  "qq.com": ["http://tech.qq.com/", '//a', "http://www.qq.com/", time.strftime('%Y%m%d',time.localtime(time.time())) ],#20140724
  "sina.com": ["http://tech.sina.com.cn/internet/", '//a', "http://www.sina.com.cn/", time.strftime('%Y-%m-%d',time.localtime(time.time())) ],#2014-07-24
  "ifeng.com": ["http://tech.ifeng.com/", '//a', "http://www.ifeng.com/", time.strftime('%Y_%m/%d',time.localtime(time.time())) ],#2014_07/24
  "baidu.com": ["http://internet.baidu.com/", '//div[@class="feeds-item"]/h3/a', "http://www.baidu.com/", "http"],#
  "cnbeta.com": ["http://m.cnbeta.com/", '//li/div/a', "http://m.cnbeta.com/", "http"],#
  #"google.com": ["https://news.google.com.hk/news/section?pz=1&cf=all&ned=cn&topic=t", '//span[@class="titletext"]', "https://news.google.com.hk/news/", "http"],#
  "36kr.com": ["http://www.36kr.com/", '//a[@target="_blank"]', "http://www.36kr.com/", "/p/"],#
} 
#go to config.py 
hotkeys_tech = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
hotkeys_tech_white_list = [u"车", u"移动", u"生活", u"路由器", u"腕带", u"手表", u"谷歌", u"微软", u"百度", u"阿里", u"腾讯", u"BAT", u"锤子", u"雷军"]
hotkeys_tech_black_list = [u"中国", u"技术", u"行业", u"公司", u"传", u"美", u"用户", u"市场", u"版", u"产品", u"功能"]
words_stat_tech = {} #{"word":count}
all_news_tech = [news("sina.com")]*len(url_infos_tech) #initial
#-------------------------------------------------#
#------------------- social part -----------------#
url_infos_soci = {
  #topic: [tech link, xpath, offical link]
  "163.social": ["http://news.163.com/shehui/", '//a', "http://www.163.com/", time.strftime('%Y/%m%d',time.localtime(time.time()))[2:][:-2] ],#"14/0724" - 14/07
  "qq.social": ["http://news.qq.com/society_index.shtml", '//a', "http://www.qq.com/", time.strftime('%Y%m%d',time.localtime(time.time()))[:-2] ],#20140724 - 201407
  "baidu.social": ["http://shehui.news.baidu.com/", '//li/a', "http://www.baidu.com/", time.strftime('%d',time.localtime(time.time()))],#
} 
hotkeys_soci = ["车", "4G", "小米", "手机", "平板", "谷歌", "阿里", "百度", "腾讯"] 
hotkeys_soci_white_list = [u"车", u"移动", u"生活", u"路由器", u"腕带", u"手表", u"谷歌", u"微软", u"百度", u"阿里", u"腾讯", u"BAT", u"锤子", u"雷军"]
hotkeys_soci_black_list = [u"男人", u"女人", u"人", u"公司", u"全国", u"头条", u"我", u"我们"]
words_stat_soci = {} #{"word":count}
all_news_soci = [news("163.social")]*len(url_infos_soci) #initial
#-------------------------------------------------#

navbar_infos = {
  "tech": {"url_infos":url_infos_tech, "white_list":hotkeys_tech_white_list, "black_list":hotkeys_tech_black_list, \
           "hot_keys":hotkeys_tech, "words_stat":words_stat_tech, "all_news":all_news_tech},
  "soci": {"url_infos":url_infos_soci, "white_list":hotkeys_soci_white_list, "black_list":hotkeys_soci_black_list, \
           "hot_keys":hotkeys_soci, "words_stat":words_stat_soci, "all_news":all_news_soci},
}
is_first_load = False

def try_get_nodes(_url, _xpath):
  resp = urllib2.urlopen(_url)
  res = resp.read()
  tree = etree.HTML(res)
  return tree.xpath(_xpath)
def get_nodes(_url, _xpath):
  try:
    return try_get_nodes(_url, _xpath)
  except: 
    try:
	  return try_get_nodes(_url, _xpath)
    except:
      print "[Error Msg] ",sys.exc_info()
  return []

import jieba.posseg as pseg
word_types = ["n", "ns", "nr", "eng"]
def get_news(topic, navbar_key):
  global word_types, navbar_infos
  url_infos = navbar_infos[navbar_key]["url_infos"]
  hotkeys_tech_black_list = navbar_infos[navbar_key]["black_list"]
  words_stat_tech = navbar_infos[navbar_key]["words_stat"]
  news_list = []
  new_keys = []#ignore the multi keys
  nodes3 = get_nodes(url_infos[topic][0], url_infos[topic][1])
  for node in nodes3:
    #print "[LOG nodeinfo] ",node.text,node.get("href")
    if ((None!=node.get("href") and node.get("href").find(url_infos[topic][3])!=-1) or topic=="google.com")\
	   and None!=node.text and len(node.text)>10 and len(node.text)<48  \
	   and not node.text in new_keys:
      _href = node.get("href")
      #special deal with    <a href=***><span>text</span></a>
      if topic=="google.com" and None!=node.getparent().get("href"):
        _href = node.getparent().get("href")
      elif topic == "36kr.com":
        if node.text.find(u"氪") != -1:
          continue
        #_href = "http://www.36kr.com" + _href
      if _href.find("http://") == -1:
         _href = url_infos[topic][2] + _href
      #end special.
      #print "[LOG add text.] ",navbar_key,topic,node.text
      news_list.append(news_item(node.text, _href))
      new_keys.append(node.text)
      try:
        #print "[LOG (jieba)] cutting."
        words =pseg.cut(node.text)
        for w in words:
          if w.flag in word_types and not w.word in hotkeys_tech_black_list:
            #global words_stat_tech
            if not words_stat_tech.has_key(w.word):
              words_stat_tech[w.word] = 1
            else:
              #if w.word == u"社交" or w.word == "社交":
                #print "---> ", node.text			  
              words_stat_tech[w.word] = words_stat_tech[w.word]+1
            #print "[LOG (jieba word)]", w.word
      except:
        print "[Error Msg(jieba)] ",sys.exc_info()
        pass
  return news_list

def get_hot_keys(dic, hot_topic_count=10, topic="None"):
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
    countstr = str(tmp_list[ii]).split(".")[0]
    if "1" == countstr:
      break
    tmp_dict_k = int(str(tmp_list[ii]).split(".")[1][:-1])#'88.31' -> '31' -> '3' -> 3
    max_topic_list.append(tmp_dict[tmp_dict_k])
    save_hoykey_count(tmp_dict[tmp_dict_k], int(countstr), topic)
  return max_topic_list
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
  c.execute("select name from hotkeys where day < %s-%d"%(day, expired_days))
  cx.commit()
  c.close()
#----------------------------------------#

def today():
  return datetime.date.today().strftime('%Y%m%d')
def yesterday():
  return (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y%m%d')
 
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
  save_hoykey_count("aaa", 12, "tech", "20140730")
  save_hoykey_count("bbb", 17, "soci", "20140729")
  print get_db_hotkey_count("bbb", "soci", "20140729")
  print get_db_hotkey_count("bbb", "soci", "20140720")
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
if unittest:
  ut_get_hot_keys()
  ut_save_hoykey_count()
  ut_test_db_day()
  print today()
  print yesterday()
  ut_show_hoykeys()


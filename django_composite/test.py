#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
from lxml import etree
def get_nodes(_url, _xpath):
  resp = urllib2.urlopen(_url)
  res = resp.read()
  tree = etree.HTML(res)
  return tree.xpath(_xpath)
  
#print len(get_nodes("http://tech.163.com/latest", '//*[@id="instantPanel"]/div[1]/ul/li[1]/a[2]'))
#nodes = get_nodes("http://tech.163.com/", '//h2[@class="color-link"]/a')
#nodes = get_nodes("http://tech.qq.com/", '//div[@class="Q-tpList"]/div/h3/a')
nodes = get_nodes("http://tech.sina.com.cn/", '//div')
print len(nodes)
for node in nodes:
  print node.text,node.get("class")
# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Template,Context,RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from books.models import Publisher
from base import *
from copy import deepcopy
import thread
import threading
import time
import sys
import traceback
import random

mutex_update_news = threading.Lock()

#mock memcache
mock_mc = {"mock_key", "mock_value"}

from django import forms
class UserForm(forms.Form):
    username = forms.CharField()
#用户登录
@csrf_exempt 
def login(req):
    if req.method == "POST":
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            #把获取表单的用户名传递给session对象
            req.session['username'] = username
            return HttpResponseRedirect('/index')        #HttpResponseRedirect -> /index       but  not    index.html
    else:
        uf = UserForm()
    return render_to_response('login.html',{'uf':uf})    #render_to_response -> login.html    but not    /login 
#登录之后跳转页
@csrf_exempt 
def index(req):
    username = req.session.get('username','anybody')
    return render_to_response('index.html',{'username':username})
#注销动作
@csrf_exempt 
def logout(req):
    del req.session['username']  #删除session
    return HttpResponse('logout ok!')

@csrf_exempt  
def visit_bootstrap(request):
  fp = open('django_composite/bootstrap.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context({"id":1}))  
  return HttpResponse(html) 
  
@csrf_exempt  
def visit_blog(request):
  print request.session.items()
  fp = open('django_composite/blog.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context({"id":1}))  
  return HttpResponse(html) 



g_hotkeys = {}
def build_list_config():
  global hotkeys_tech_black_list,hotkeys_soci_black_list,g_hotkeys
  f = open("django_composite/list.conf")
  g_hotkeys = {}
  for line in f.readlines():
    line = line.decode("utf-8").strip(" \r\n")
    #print line
    if line.find("bls=") != -1:
      hotkeys_tech_black_list += line.split("bls=")[1].split(",")
      hotkeys_soci_black_list += line.split("bls=")[1].split(",")
    elif line.find("blstech=") != -1:
      hotkeys_tech_black_list += line.split("blstech=")[1].split(",")
    elif line.find("blssoci=") != -1:
      hotkeys_tech_black_list += line.split("blssoci=")[1].split(",")
    elif line.find("hktech=")!=-1 and line.split("hktech=")[1]!="":
      g_hotkeys[tag_tech] = line.split("hktech=")[1]
    elif line.find("hksoci=")!=-1 and line.split("hksoci=")[1]!="":
      g_hotkeys[tag_soci] = line.split("hksoci=")[1]
  f.close()



def init_news2(_init=True):
  global url_infos_tech, navbar_infos, is_first_load, tmpset
  build_list_config()
  if is_first_load:
    create_tables2()
  import time
  uptime = time.strftime("%m%d%H%M", time.localtime())
  for _k, _v in navbar_infos.items():
    count = 0
    tmpset.clear() #avoid repeated
    for topic,infos in _v["url_infos"].items():
      #global all_news_tech
      _all_news = []
      _get_news = []
      _tmpset2 = set()
      for i in range(15):    #retries
        #if navbar_infos[_k]["all_news"][count].news_items != None:
        #  print _init,"old len: ",len(navbar_infos[_k]["all_news"][count].news_items)
        if _init:
          _all_news,_get_news,_tmpset2 = get_news(topic, _k, [])
        else:
          _all_news,_get_news,_tmpset2 = get_news(topic, _k, navbar_infos[_k]["all_news"][count].news_items)
        if len(_get_news) > 0:
          break
      for setitem in _tmpset2:
        tmpset.add(setitem)
      #print "[LOG %s] fetch %s. all:%d, get:%d"%(time.strftime("%Y-%m-%d %X",time.localtime()),topic,len(_all_news),len(_get_news))
      logger.info( "fetch %s. all:%d, get:%d"%(topic,len(_all_news),len(_get_news)) )
      #if not _init:
      #  _tmplists = [ _new.href for _new in _get_news]
      #  for _item in navbar_infos[_k]["all_news"][count].news_items:
      #    if _item.href not in _tmplists:
      #      _get_news.append(_item)
      #  _get_news = list( set(_get_news + navbar_infos[_k]["all_news"][count].news_items) )
      navbar_infos[_k]["all_news"][count] = news(topic, _get_news, _k)
      count += 1
    words_stat = navbar_infos[_k]["words_stat"]

    _hotkeys,max_topic_counts = get_hot_keys(words_stat, 1000, _k, uptime)
    #print "max_topic_counts::  ",max_topic_counts
    navbar_infos[_k]["words_stat"] = {} #old data
    navbar_infos[_k]["hot_keys"] = _hotkeys[:150] 
    #print_db_me()
    _hotkeys2 = sort_hot_keys2(_k)
    navbar_infos[_k]["hot_keys_up"] = _hotkeys2[:80] 
	#build cache.
    logger.info("building cache.")
    get_jsondata({"helpkey":_k, "helpkey2":"", "quickkey":u"全部"}, False)
    for _hotkey in set(_hotkeys+_hotkeys2):
      get_jsondata({"helpkey":_k, "helpkey2":"", "quickkey":_hotkey}, False)
    for _hotkey in navbar_infos[_k]["white_list"]:
      get_jsondata({"helpkey":_k, "helpkey2":"", "quickkey":_hotkey}, False)
  
def thread_update_news(searchcontent):
  #sleeptime = 15*60 #debug
  sleeptime = 1*60*60 #release
  while True:
    _init = False
    time.sleep(sleeptime)
    logger.info("update news.")
    try:
      if get_current_hour() < 1: #00: 00
        update_base()
        _init = True
      init_news2(_init)
      del_hotkeys_expired2()
    except:
      logger.error(str(sys.exc_info()) )
#print "[LOG %s] Global Run."%(time.strftime("%Y-%m-%d %X", time.localtime()))

def filter_news(quickkey, all_news):
  _news = []
  for news_item in all_news:
    _news.append( news_item.filter(quickkey) )
  return _news
  

import codecs
config_headers = ["hktech=","hksoci=","bls=","blstech=","blssoci=",
                  "wlstech=","wlssoci="]
def admin_update_configs(cont):
  cont = cont.strip("\r\n ")
  ret = False
  header = None
  for _header in config_headers:
    if cont.find(_header) != -1:
      header = _header
      ret = True
      break
  if not ret:
    return False
  
  logger.info("[admin_update_configs]type:  %s"%cont)
  f = open("django_composite/list.conf")
  lines = f.readlines()
  print lines
  f.close()


  for i in range(len(lines)):
    lines[i] = lines[i].strip("\r\n ").decode("utf-8")
    if lines[i].find(header) != -1:
      if header=="blstech=" or header=="blssoci=" or \
        header=="wlstech=" or header=="wlssoci=" or \
        header=="bls=":
        if lines[i] == header: #tag=
          lines[i] = cont
          break
        cont = cont.split(header)[1]
        if lines[i].find(cont) == -1:
          lines[i] = lines[i] + u"," + cont
      else:
        lines[i] = cont
      break

  #f = open("django_composite/list.conf","w")
  f = codecs.open("django_composite/list.conf","w","utf-8")
  #lines = [ line.strip("\r\n ").encode("utf-8") for line in lines ]
  for line in lines:
    line=line.strip("\r\n ")
    try:
      f.write(line+"\n")
    except:
      logger.error( "Exception: %s, %s"%(str(sys.exc_info()),str(traceback.format_exc()) ))
  f.close()
  return False

  
g_news_cache = {}    #helpkey_helpkey2_quickey: obj

def get_jsondata(args, from_request=True):
  global is_first_load, navbar_infos
  #print request.session.items()
  searchcontent = args.get("searchcontent", None)
  quickkey = args.get("quickkey", searchcontent)
  helpkey = args.get("helpkey", None)

  if from_request:
    #print "[LOG %s] request.POST: "%(time.strftime("%Y-%m-%d %X", time.localtime())), args
    if tag_soci==helpkey or None==helpkey:
      helpkey = tag_soci
    if (quickkey=="" or None==quickkey) and not helpkey==tag_cont:
      if g_hotkeys.get(helpkey,"") != "":
        quickkey = g_hotkeys[helpkey]
      elif len(navbar_infos[helpkey]["hot_keys"])>0: #first key
        quickkey = navbar_infos[helpkey]["hot_keys"][0]
  
  cache_key = u"%s_%s_%s"%(args.get("helpkey", ''),args.get("helpkey2", ''),quickkey)
  if from_request and cache_key in g_news_cache:
    logger.info("hit cache: %s."%cache_key)
    #print g_news_cache[cache_key]
    return g_news_cache[cache_key]
  
  disp_content = "block"
  disp_contact = "none"
  status_tech = "active"
  status_soci = ""
  status_contact = ""
  navbar_tab = tag_tech
  if tag_soci == helpkey:
    #helpkey = tag_soci
    status_tech = ""
    status_soci = "active"
    status_contact = ""	
    navbar_tab = tag_soci
  elif tag_cont == helpkey:
    status_tech = ""
    status_soci = ""
    status_contact = "active"
    disp_content = "none"
    disp_contact = "block"
    navbar_tab = tag_soci
    contactdesc = args.get("helpkey2", '')
    if '' != contactdesc:
      admin_update_configs(contactdesc)
      send_mail("417306303@qq.com", "from 360 views.", str(contactdesc))

  jsondata = None
  raw_news = []
  all_news = []
  if quickkey == u"全部":
    raw_news = navbar_infos[navbar_tab]["all_news"]
  else:
    raw_news = filter_news(quickkey,navbar_infos[navbar_tab]["all_news"])
  #for k,v in raw_news.items(): 
  #  all_news += [ item.topic=k for item in v ]
  #make magic list.
  _count = 0
  for _newsobj in raw_news: 
    for _new in _newsobj.news_items:
      _new.topic = _newsobj.topic
      _count = _count+1
      all_news.insert(random.randint(0,_count),_new)
  jsondata = {
                 "news":all_news, 
                 "hot_keys":navbar_infos[navbar_tab]["hot_keys"],\
                 "hot_keys_up":navbar_infos[navbar_tab]["hot_keys_up"], \
                 "disp_content":disp_content, "disp_contact":disp_contact,"helpkey":helpkey,\
                 "hot_keys_anual":navbar_infos[navbar_tab]["white_list"], "stat_tech":status_tech, \
                 "stat_soci":status_soci, "stat_cont":status_contact, "quickkey":quickkey 
             }
  if tag_cont!=helpkey and len(g_news_cache)<1000:
    g_news_cache[cache_key] = deepcopy(jsondata)
    if from_request:
      logger.info("build cache: %s."%cache_key)
  return jsondata 
  

@csrf_exempt
def visit_offcanvas(request):
  #bug: 同个客户端同时刷新好几次，可能同时返回导致内容混合
  ip = None
  if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
    ip =  request.META['HTTP_X_FORWARDED_FOR']  
  else:  
    ip = request.META['REMOTE_ADDR'] 
  logger.info("%s BEGIN. %s"%(ip,str(request.POST)))

  global is_first_load
  mutex_update_news.acquire()
  if is_first_load:
    #print "[LOG %s] init news."%(time.strftime("%Y-%m-%d %X", time.localtime()))
    logger.info("init news.")
    update_base()
    init_news2()
    thread.start_new_thread(thread_update_news, ("",))
    is_first_load = False
  mutex_update_news.release()

  jsondata = get_jsondata(request.POST)
  fp = open('django_composite/offcanvas.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context(jsondata))  
  logger.info("%s END."%ip)
  return HttpResponse(html) 
  '''
  respdict = {}
  if None == quickkey:
    respdict = {"news":all_news_tech, "hot_keys":hotkeys_tech}
  else:
    respdict = {"news":filter_news(quickkey), "hot_keys":hotkeys_tech}
  return render_to_response('django_composite/offcanvas.html', respdict, context_instance=RequestContext(request))
  '''

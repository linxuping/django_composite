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


def init_news2():
  global url_infos_tech, navbar_infos, is_first_load
  if is_first_load:
    create_tables2()
  import time
  uptime = time.strftime("%m%d%H%M", time.localtime())
  for _k, _v in navbar_infos.items():
    count = 0
    for topic,infos in _v["url_infos"].items():
      #global all_news_tech
      _all_news = []
      _get_news = []
      for i in range(15):    #retries
        _all_news,_get_news = get_news(topic, _k)
        if len(_get_news) > 0:
          break
      print "[LOG %s] fetch %s. all:%d, get:%d"%(time.strftime("%Y-%m-%d %X",time.localtime()),topic,len(_all_news),len(_get_news))
      navbar_infos[_k]["all_news"][count] = news(topic, _get_news, _k)
      count += 1
    words_stat = navbar_infos[_k]["words_stat"]

    _hotkeys,max_topic_counts = get_hot_keys(words_stat, 1000, _k, uptime)
    #print "max_topic_counts::  ",max_topic_counts
    navbar_infos[_k]["words_stat"] = {} #old data
    navbar_infos[_k]["hot_keys"] = _hotkeys[:150] 
    _hotkeys2 = sort_hot_keys2(_k, uptime)
    navbar_infos[_k]["hot_keys_up"] = _hotkeys2[:80] 
	#build cache.
    print "building cache."
    get_jsondata({"helpkey":_k, "helpkey2":"", "quickkey":u"全部"}, False)
    for _hotkey in set(_hotkeys+_hotkeys2):
      get_jsondata({"helpkey":_k, "helpkey2":"", "quickkey":_hotkey}, False)
    for _hotkey in navbar_infos[_k]["white_list"]:
      get_jsondata({"helpkey":_k, "helpkey2":"", "quickkey":_hotkey}, False)
  del_hotkeys_expired2(uptime)
  
def thread_update_news(searchcontent):
  sleeptime = 15*60 #debug
  #sleeptime = 1*60*60 #release
  while True:
    time.sleep(sleeptime)
    print "[THREAD] update news. ",time.strftime("%Y-%m-%d %X", time.localtime())
    try:
      init_news2()
    except:
      print "[Error Msg(thread_update_news)] ",sys.exc_info()
print "[LOG %s] Global Run."%(time.strftime("%Y-%m-%d %X", time.localtime()))

def filter_news(quickkey, all_news):
  _news = []
  for news_item in all_news:
    _news.append( news_item.filter(quickkey) )
  return _news
  
  
g_news_cache = {}    #helpkey_helpkey2_quickey: obj
  

def get_jsondata(args, from_request=True):
  global is_first_load, navbar_infos
  #print request.session.items()
  searchcontent = args.get("searchcontent", None)
  quickkey = args.get("quickkey", searchcontent)
  helpkey = args.get("helpkey", None)

  if from_request:
    print "[LOG %s] request.POST: "%(time.strftime("%Y-%m-%d %X", time.localtime())), args
    if tag_soci==helpkey or None==helpkey:
      helpkey = tag_soci
    if quickkey=="" or None==quickkey:
      if len(navbar_infos[helpkey]["hot_keys"])>0: #first key
        quickkey = navbar_infos[helpkey]["hot_keys"][0]
  
  cache_key = u"%s_%s_%s"%(args.get("helpkey", ''),args.get("helpkey2", ''),quickkey)
  if from_request and cache_key in g_news_cache:
    print "hit cache: ",cache_key
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
      send_mail("417306303@qq.com", "from 360 views.", str(contactdesc))


  jsondata = None
  if quickkey == u"全部":
    jsondata = {"news":navbar_infos[navbar_tab]["all_news"], "hot_keys":navbar_infos[navbar_tab]["hot_keys"], \
                    "hot_keys_up":navbar_infos[navbar_tab]["hot_keys_up"], \
                    "disp_content":disp_content, "disp_contact":disp_contact,"helpkey":helpkey,\
	                "hot_keys_anual":navbar_infos[navbar_tab]["white_list"], "stat_tech":status_tech, \
					"stat_soci":status_soci ,"stat_cont":status_contact, "quickkey":quickkey}
  else:
    jsondata = {"news":filter_news(quickkey,navbar_infos[navbar_tab]["all_news"]), "hot_keys":navbar_infos[navbar_tab]["hot_keys"],\
                    "hot_keys_up":navbar_infos[navbar_tab]["hot_keys_up"], \
                    "disp_content":disp_content, "disp_contact":disp_contact,"helpkey":helpkey,\
                    "hot_keys_anual":navbar_infos[navbar_tab]["white_list"], "stat_tech":status_tech, \
					"stat_soci":status_soci, "stat_cont":status_contact, "quickkey":quickkey}
  if len(g_news_cache) < 1000:
    g_news_cache[cache_key] = deepcopy(jsondata)
    if from_request:
      print "build cache: ",cache_key
  return jsondata 
  

@csrf_exempt
def visit_offcanvas(request):
  #bug: 同个客户端同时刷新好几次，可能同时返回导致内容混合
  global is_first_load
  mutex_update_news.acquire()
  if is_first_load:
    print "[LOG %s] init news."%(time.strftime("%Y-%m-%d %X", time.localtime()))
    init_news2()
    thread.start_new_thread(thread_update_news, ("",))
    is_first_load = False
  mutex_update_news.release()

  jsondata = get_jsondata(request.POST)
  fp = open('django_composite/offcanvas.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context(jsondata))  
  return HttpResponse(html) 
  '''
  respdict = {}
  if None == quickkey:
    respdict = {"news":all_news_tech, "hot_keys":hotkeys_tech}
  else:
    respdict = {"news":filter_news(quickkey), "hot_keys":hotkeys_tech}
  return render_to_response('django_composite/offcanvas.html', respdict, context_instance=RequestContext(request))
  '''

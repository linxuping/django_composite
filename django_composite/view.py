# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Template,Context,RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from books.models import Publisher
from base import *
import thread
import threading
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

def init_news():
  global url_infos_tech, navbar_infos
  create_tables()
  for _k, _v in navbar_infos.items():
    count = 0
    for topic,infos in _v["url_infos"].items():
      print "[LOG] fetch %s."%topic
      #global all_news_tech
      navbar_infos[_k]["all_news"][count] = news(topic, get_news(topic, _k), _k)
      count += 1
    words_stat = navbar_infos[_k]["words_stat"]
    #hotkeys_tech = navbar_infos["tech"]["hot_keys"]  #为什么直接用hotkeys_tech操作，不是一个引用？所以只能下面覆盖数据.
    #hotkeys_tech_white_list = navbar_infos["tech"]["white_list"]
    #print "[LOG (hot keys stat)] ",words_stat_tech
    _hotkeys = get_hot_keys(words_stat, 50, _k)
    #for _key in hotkeys_tech_white_list:
    #  if not _key in _hotkeys_tech:
    #    _hotkeys_tech.append(_key)
    navbar_infos[_k]["hot_keys"] = _hotkeys
  del_hotkeys_expired()
  
import time
def thread_update_news(searchcontent):
  while True:
    time.sleep(1440)
    print "[THREAD] update news. ",time.strftime("%Y-%m-%d %X", time.localtime())
    init_news()
print "[LOG] Global Run."

def filter_news(quickkey, all_news):
  _news = []
  for news_item in all_news:
    _news.append( news_item.filter(quickkey) )
  return _news
  
@csrf_exempt
def visit_offcanvas(request):
  global is_first_load, navbar_infos
  #print request.session.items()
  print "[LOG] request.POST: ", request.POST
  searchcontent = request.POST.get("searchcontent", None)
  quickkey = request.POST.get("quickkey", searchcontent)
  status_tech = "active"
  status_soci = ""
  navbar_tab = "tech"
  if "social" == request.POST.get("helpkey", None):
    status_tech = ""
    status_soci = "active"
    navbar_tab = "soci"

  mutex_update_news.acquire()
  if not is_first_load:
    print "[LOG] init news."
    init_news()
    thread.start_new_thread(thread_update_news, ("",))
    is_first_load = True
  mutex_update_news.release()
  
  fp = open('django_composite/offcanvas.html')  
  t = Template(fp.read())  
  fp.close()  
  html = None
  if None==quickkey or ""==quickkey:
    #print "===>", navbar_infos["soci"]["all_news"],navbar_tab
    html = t.render(Context({"news":navbar_infos[navbar_tab]["all_news"], "hot_keys":navbar_infos[navbar_tab]["hot_keys"], \
	                         "hot_keys_anual":navbar_infos[navbar_tab]["white_list"], "stat_tech":status_tech, "stat_soci":status_soci }))  
  else:
    html = t.render(Context({"news":filter_news(quickkey,navbar_infos[navbar_tab]["all_news"]), "hot_keys":navbar_infos[navbar_tab]["hot_keys"],\
                            "hot_keys_anual":navbar_infos[navbar_tab]["white_list"], "stat_tech":status_tech, "stat_soci":status_soci	}))
  return HttpResponse(html) 
  '''
  respdict = {}
  if None == quickkey:
    respdict = {"news":all_news_tech, "hot_keys":hotkeys_tech}
  else:
    respdict = {"news":filter_news(quickkey), "hot_keys":hotkeys_tech}
  return render_to_response('django_composite/offcanvas.html', respdict, context_instance=RequestContext(request))
  '''
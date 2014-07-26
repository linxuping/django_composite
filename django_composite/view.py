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
  global url_infos
  '''
  #get 126 news
  news_163 = []
  nodes = get_nodes("http://tech.163.com/", '//a')
  for node in nodes:
    if None!=node.get("href") and node.get("href").find(url_infos["163.com"][3])!=-1 and None!=node.text and len(node.text)>10 and len(node.text)<28 and node.text.find(searchcontent)!=-1:
      news_163.append(news_item(node.text,node.get("href")))
  '''
  count = 0
  for topic,infos in url_infos.items():
    print "[LOG] fetch %s."%topic
    global all_news
    all_news[count] = news(topic, get_news(topic))
    count += 1
  '''
  news_163 = get_news("163.com")
  news_qq = get_news("qq.com")
  news_sina = get_news("sina.com")
  news_ifeng = get_news("ifeng.com")
  news_baidu = get_news("baidu.com")
  news_cnbeta = get_news("cnbeta.com")
  #all_news = [news("163.com", news_163)]
  all_news = [news("cnbeta.com", news_cnbeta),news("163.com", news_163),news("qq.com", news_qq),news("ifeng.com", news_ifeng),news("baidu.com", news_baidu)  ] #news("sina.com", news_sina)
  ''' 
  global new_words_stat,hot_keys,hot_key_white_list
  #print "[LOG (hot keys stat)] ",new_words_stat
  hot_keys = get_hot_keys(new_words_stat, 20)
  for _key in hot_key_white_list:
    if not _key in hot_keys:
      hot_keys.append(_key)
  
import time
def thread_update_news(searchcontent):
  while True:
    time.sleep(1440)
    print "[THREAD] update news. ",time.strftime("%Y-%m-%d %X", time.localtime())
    init_news()
print "[LOG] Global Run."

def filter_news(quickkey):
  _news = []
  for news_item in all_news:
    _news.append( news_item.filter(quickkey) )
  return _news
  
@csrf_exempt
def visit_offcanvas(request):
  global is_first_load
  #print request.session.items()
  print "[LOG] request.POST: ", request.POST
  searchcontent = request.POST.get("searchcontent", None)
  quickkey = request.POST.get("quickkey", searchcontent)

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
  if None == quickkey:
    html = t.render(Context({"news":all_news, "hot_keys":hot_keys}))  
  else:
    html = t.render(Context({"news":filter_news(quickkey), "hot_keys":hot_keys}))
  return HttpResponse(html) 
  '''
  respdict = {}
  if None == quickkey:
    respdict = {"news":all_news, "hot_keys":hot_keys}
  else:
    respdict = {"news":filter_news(quickkey), "hot_keys":hot_keys}
  return render_to_response('django_composite/offcanvas.html', respdict, context_instance=RequestContext(request))
  '''
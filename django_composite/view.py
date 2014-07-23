# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Template,Context,RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from books.models import Publisher
from base import *

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
  
@csrf_exempt  
def visit_offcanvas(request):
  print request.session.items()
  
  #get 126 news
  news_163 = []
  nodes = get_nodes("http://tech.163.com/", '//h2[@class="color-link"]/a')
  for node in nodes:
    news_163.append(news_item(node.text,node.get("href")))
  news_qq = []
  nodes2 = get_nodes("http://tech.qq.com/", '//div[@class="Q-tpList"]/div/h3/a')
  for node in nodes2:
    news_qq.append(news_item(node.text,node.get("href")))
  news_sina = []
  nodes3 = get_nodes("http://tech.sina.com.cn/", '//div[@class="feed-card-item"]/h2/a')
  for node in nodes3:
    news_sina.append(news_item(node.text,node.get("href")))
    
  _news = [news("163.com", news_163),news("qq.com", news_qq),news("sina.com", news_sina)]
  
  fp = open('django_composite/offcanvas.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context({"news":_news}))  
  return HttpResponse(html) 
  
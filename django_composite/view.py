# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import Template,Context,RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  
def visit_bootstrap(request):
  fp = open('django_composite/bootstrap.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context({"id":1}))  
  return HttpResponse(html) 
  
@csrf_exempt  
def visit_blog(request):
  fp = open('django_composite/blog.html')  
  t = Template(fp.read())  
  fp.close()  
  html = t.render(Context({"id":1}))  
  return HttpResponse(html) 
  
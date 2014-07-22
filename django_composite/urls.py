from django.conf.urls import patterns, include, url

from django.contrib import admin
import view
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_composite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^bootstrap/', view.visit_bootstrap),
	url(r'^blog/', view.visit_blog),
    url(r'^news/', view.visit_offcanvas),
    url(r'^login/$', view.login),
    url(r'^index/$', view.index),
    url(r'^logout/$', view.logout),
)

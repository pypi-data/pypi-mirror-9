from django.conf.urls import patterns, include, url

from django.contrib import admin
#from pug.dj.miner import views

# admin autodiscovery in Django 1.7 and here will override the custom admin_site work of call_center.admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', views.home, name='crawlnmine-home'),
    url(r'^', include('pug.dj.miner.urls'), name='miner'),
    url(r'^invest/', include('pug.invest.urls')),
    #url(r'^crawler/', include('pug.crawler.urls', namespace='crawler')),

    url(r'^admin/', include(admin.site.urls)),
)

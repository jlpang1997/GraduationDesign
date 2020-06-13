
from django.contrib import admin

# from django.contrib import admin

from django.urls import path
 
from django.conf.urls import *

from . import response


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('index',response.index),
    url('shuimu',response.show),
    url('zhihu',response.show),
    url('weibo',response.show),
    url('tieba',response.show),

    url('search-shuimu',response.search),
    url('search-tieba',response.search),
    url('search-zhihu',response.search),
    url('search-weibo',response.search),
    
    url('login',response.login),
    url('register',response.register),
    url('out',response.out),
    # url('',response.index),
]

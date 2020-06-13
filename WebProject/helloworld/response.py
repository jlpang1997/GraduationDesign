from django.http import HttpResponse

from django.shortcuts import render,redirect

from TestModel.models import Test,User
from .flush import *
import re

##为什么直接运行和和被调用运行时不一样的呢
import os


from hashlib import md5

# shuimu=Spider_shuimu.Spider_shuimu()
# zhihu=Spider_zhihu.Spider_zhihu()
# tieba=Spider_baidutieba.Spider_baidutieba()
# weibo=Spider_weibo.Spider_weibo()
spider_dict={
    '/shuimu':shuimu,
    '/zhihu':zhihu,
    '/tieba':tieba,
    '/weibo':weibo,

    '/search-shuimu':shuimu,
    '/search-zhihu':zhihu,
    '/search-tieba':tieba,
    '/search-weibo':weibo,
}




def index(request):  #首页展示
    return render(request,'index.html')


def show(request):
    path=request.path
    spider=spider_dict[path]
    params={
        'topics':[],
        'site_name':spider.site_name,
        'site_url':spider.site_url,
        'search_sample':spider.search_sample,
        'search_action':spider.search_action,
    }
    if(request.method=='GET'): #从首页跳转过来
        flush(spider)
        params['topics']=hots_analysis_result[spider.id]
        return render(request,'show_template.html',params)


    elif request.method=='POST':
        link=request.POST['search']
        if path=='/search-weibo':
            link='https://s.weibo.com/weibo?q='+link+'&Refer=top'
        comments=spider.get_comments(link)
        result_dict=get_sentiment(comments)
        title=spider.title

        params['topic']={
        'title'        :title,
        'link'         :link,
        "positive_rate":result_dict['positive_rate'],
        'negative_rate':result_dict['negative_rate'],
        'pos_count'    :result_dict['pos_count'],
        'neg_count'    :result_dict['neg_count'],
        'total_count'  :result_dict['total_count']
        }
        
        return render(request,'search_template.html',params)
    else:
        return redirect('https://www.ustc.edu.cn/')


def search(request):
    path=request.path
    spider=spider_dict[path]
    params={
        'topics':[],
        'site_name':spider.site_name,
        'site_url':spider.site_url,
        'search_sample':spider.search_sample,
        'search_action':spider.search_action,
    }
    if request.method=='POST':
        link=request.POST['search']
        if path=='/search-weibo':
            link='https://s.weibo.com/weibo?q='+link+'&Refer=top'
        comments=spider.get_comments(link)
        result_dict=get_sentiment(comments)
        title=spider.title

        params['topic']={
        'title'        :title,
        'link'         :link,
        "positive_rate":result_dict['positive_rate'],
        'negative_rate':result_dict['negative_rate'],
        'pos_count'    :result_dict['pos_count'],
        'neg_count'    :result_dict['neg_count'],
        'total_count'  :result_dict['total_count']
        }

        return render(request,'search_template.html',params)



def login(request):
    params={
        "error":False
    }
    if request.method=='GET':
        return render(request,'login.html')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']

        q=User.objects.get(email=email)
        if not q or q.password!=password :
            params['error']=True
            return render(request,'login.html',params)
        
        else:
            return render(request,'index.html')




def register(request):
    params={
        "err_meg":None
    }
    err_meg=None
    if request.method=='GET':
        return render(request,'register.html')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        q=User.objects.filter(email=email)
        if q:
            err_meg="邮箱已经被注册"
            return render(request,'register.html',{"err_meg":err_meg})
        elif password!=confirm_password or password=="":
            err_meg="两个密码不一致，请重新输入"
            return render(request,'register.html',{"err_meg":err_meg})
        
        else:
            user=User(email=email,password=password)
            user.save()
            request.path='/login'
            return render(request,'login.html',{"from_register":True})




def out(request):
    return render(request,'login.html')

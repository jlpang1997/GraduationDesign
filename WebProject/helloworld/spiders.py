import requests
from pyquery import PyQuery as pq
import re
import time
import datetime
import json
import sys
import os
from hashlib import md5
from math import ceil
import asyncio
import urllib.parse
import logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
from time import time


class Spider_shuimu(object):
    def __init__(self):
        self.comment_count=0  #作为一个帖子的base_info
        self.page_count=0
        self.title=None
        
        self.comment_index=0  #初始化
        self.page_index=1  #网页page索引从1开始
        self.fp=None

        self.id='shuimu'
        self.site_name='清华水木社区'
        self.site_url='http://www.newsmth.net'
        self.search_sample="http://www.newsmth.net/nForum/#!article/ComicPlaza/168753"
        self.search_action='/search-shuimu'
        self.comments_per_page=10
        self.max_comments=1000
        self.max_hots=1 #限定爬虫获取的最大热点数
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
        }

    def reset(self): #跑完一个主题帖之后就reset
        self.comment_index=0
        self.page_index=1
        self.fp=None
        self.title=None

    def get_base_info(self,url):
        '''
        输入：检索贴url
        过程：获取帖子的基本信息：页数、发言数、标题
        输出：无
        '''
        html=self.get_one_page(url)
        doc=pq(html)
        
        title=doc('.n-right span')
        if title:
            self.title=title.attr('_c')

        comment_count=doc('.page-pre i').html()
        if comment_count: 
            self.comment_count=min(int(comment_count),self.max_comments)
        else:
            self.comment_count=1  #只有一页的话

        self.page_count=ceil(self.comment_count/self.comments_per_page)

        if(self.title==None):
            logging.debug('cannot get base_info:%s'%(url))

        logging.debug('base_info:comment_count=%d,page_count=%d,title=%s,url=%s'%(self.comment_count,self.page_count,self.title,url))

    def get_one_page(self,url):
        if(url):
            try:
                logging.debug('get url content from %s:url=%s'%(self.id,url))
                response=requests.get(url,headers=self.headers)
                if(response.status_code==200):
                    content_type=response.headers['Content-Type'].split(';')[0].strip()
                    if content_type=='application/json':
                        return response.json()
                    elif content_type=='text/html':
                        return response.text

            except requests.ConnectionError as e:
                logging.error('cannot connect to %s'%(url))

    def parse_one_page(self,html):
        doc=pq(html)
        items=doc('.article').items()
        for item in items:
            result_item={}
            result_item['name']=item('.a-u-name').text()

            t=item('.a-content p').remove('font').remove('a').remove('br').text()
            tmp=re.search('站内.*--',t,re.S)
            if(tmp):
                t=tmp.group()[2:-2]
            t=re.sub('【.*】','',t,re.S).strip()
            t=re.sub('--.*','',t,re.S)
            t=re.sub('发自.*','',t,re.S)
            t=re.sub('来自.*','',t,re.S).replace('\xa0',' ').strip().replace('\n','')

            result_item['comment']=t
            self.comment_index+=1
            logging.debug('get a comment from %s:title=%s,progress=(%d/%d)'%(self.id,self.title,self.comment_index,self.comment_count))
            yield result_item

    def get_comments(self,url):
        self.reset()
        url_prefix=url.replace('#!','')+'?ajax'
        self.get_base_info(url_prefix)
        if(self.title==None):#如果该网页无法爬取就跳过
            return []

        while(self.comment_index<self.comment_count and self.page_index<=self.page_count):
            url=url_prefix+"&p="+str(self.page_index)
            html=self.get_one_page(url)
            item_count=0
            for item in self.parse_one_page(html):
                yield item['comment']
                item_count+=1
            if item_count==0: #水木清华简直太多bug了 有可能base_info 没问题 但真正爬的时候就有问题了
                break
            self.page_index+=1

    def save_comments(self,item):  
        '''
        输入：发言item {'name': ,'comment':  ,}
        过程：保存一个发言到文件或者数据库
        输出：无
        '''
        # self.fp.write(item['comment'].replace('\n','')+'\n')
        pass

    
    def get_hots(self):
        url='http://www.newsmth.net/nForum/mainpage?ajax'
        base_url='http://www.newsmth.net'
        html=self.get_one_page(url)
        doc=pq(html)
        top10=doc('#top10 ul li div').items()
        for top in top10:
            titles=list(top('a').items())
            target_node=titles[1]
            hot={
                'url':base_url+target_node.attr('href'),
                'title':target_node.text()
            }
            logging.debug('get a hot from %s:url=%s,title=%s'%(self.id,hot['url'],hot['title']))
            if hot['url'].split('/')[-2]=='Stock':
                continue
            yield hot
    
    def test(self):
        '''
        测试两个功能：get_hots,run_one_hot
        '''
        total_time=0
        total_count=0
        # for hot in spider.get_hots():
        #     print(hot)
        # for c in spider.get_comments('http://www.newsmth.net/nForum/article/ITExpress/2135626'):
        #     print(c)
        for hot in self.get_hots():
            # start=time()
            # count=0
            for c in self.get_comments(hot['url']):
                print(c)
        #         count+=1
        #     if(count==0):
        #         continue
        #     use_time=time()-start
        #     total_time+=use_time
        #     total_count+=count



class Spider_baidutieba(object):
    def __init__(self):
        self.comment_count=0  #作为一个帖子的base_info
        self.page_count=0
        self.title=None
        
        self.comment_index=0  #初始化
        self.page_index=1
        self.fp=None

        self.id='tieba'
        self.site_name='百度贴吧'
        self.site_url='https://tieba.baidu.com/'
        self.search_sample="https://tieba.baidu.com/p/6709826506"
        self.search_action='/search-tieba'
        self.comments_per_page=10
        self.max_comments=1 #限定一个帖子的最大发言数
        self.max_hots=10 #限定爬虫获取的最大热点数
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
        }


    def reset(self): #跑完一个主题帖之后就reset
        self.comment_index=0
        self.page_index=1
        self.fp=None
        self.title=None

    def get_base_info(self,url):
        '''
        输入：检索贴url
        过程：获取帖子的基本信息：页数、发言数、标题
        输出：无
        '''
        html=self.get_one_page(url)
        doc=pq(html)

        comment_count=doc('.pb_footer .red[style]')
        if comment_count:
            self.comment_count=min(int(comment_count.text()),self.max_comments)

        max_page=doc('.pb_footer .jump_input_bright').attr('max-page')
        if max_page:
            self.page_count=int(max_page) 
        else:
            self.page_count=1    

        title=doc('.core_title_txt')
        if title:
            self.title=title.text()

        if(self.title==None):
            logging.debug('cannot get base_info:%s'%(url))

        logging.debug('base_info:comment_count=%d,page_count=%d,title=%s,url=%s'%(self.comment_count,self.page_count,self.title,url))

    def get_one_page(self,url):
        '''
        输入：url
        过程：
        输出：html文本
        '''
        if(url):
            try:
                logging.debug('get url content from %s:url=%s'%(self.id,url))
                response=requests.get(url,headers=self.headers)
                if(response.status_code==200):
                    content_type=response.headers['Content-Type'].split(';')[0].strip()
                    if content_type=='application/json':
                        return response.json()
                    elif content_type=='text/html':
                        return response.text

            except requests.ConnectionError as e:
                logging.error('cannot connect to %s'%(url))

    def parse_one_page(self,html):  
        '''
        输入：html文本
        过程：解析页面 第一次：页数、发言数  ，每一次：该页的所有发言
        输出：所有发言
        '''
        doc=pq(html)
            
        items=doc('.p_postlist>div').remove('a').remove('img').items()
        for item in items: #获取item
            result_item={}
            result_item['name']=item('.d_name').attr('data-field')

            result_item['comment']=item('.d_post_content.j_d_post_content').text().replace('\n','')

            self.comment_index+=1 # 发言索引+1
            logging.debug('get a comment from %s:title=%s,progress=(%d/%d)'%(self.id,self.title,self.comment_index,self.comment_count))
            yield result_item

    def get_comments(self,url):
        self.reset()
        init_url=url
        self.get_base_info(url)
        while(self.page_index<=self.page_count and self.comment_index<self.comment_count):
            url=init_url+'?pn='+str(self.page_index)
            html=self.get_one_page(url)
            for item in self.parse_one_page(html):
                yield item['comment']
            self.page_index+=1

    def save_one_item(self,item):  
        '''
        输入：发言item {'name': ,'comment':  ,}
        过程：保存一个发言到文件fp
        输出：无
        '''
        self.fp.write(item['comment'].replace('\n','')+'\n')

    def get_hots(self):  
        '''
        输入：无
        过程：获取实时热门话题自身的url，title，如果是贴吧或者微博，就要获取selected_urls
        输出：hots ,hots的结构里面必须有一个或多个精选url
        '''
        url='http://tieba.baidu.com/hottopic/browse/topicList'
        # response=requests.get(url,headers=headers)
        j=self.get_one_page(url)
        topic_list=j['data']['bang_topic']['topic_list']
        hot_count=0
        for topic in topic_list:
            hot={
                'url':topic['topic_url'].replace('amp;',''),
                'title':topic['topic_name']
                }
            hot['selected_urls']=self.get_all_selected_urls(hot['url'])

            logging.debug('get a hot from %s:url=%s,title=%s'%(self.id,hot['url'],hot['title']))
            yield hot
            hot_count+=1
            if hot_count>=self.max_hots: #只收集十条
                break

    def get_all_selected_urls(self,url):  
        '''
        输入: hot对应的精选贴
        过程：只针对微博和贴吧获取对应的精选贴url
        输出：selected_urls
        '''
        selected_urls=[]
        html=self.get_one_page(url)
        doc=pq(html)
        items=doc('#selected-feed .thread-item').items()
        base_url='https://tieba.baidu.com'
        for item in items:
            selected_urls.append(
                {
                    "title":item('.center>a').text(),
                    "url":base_url+item('.center a').attr('href')
                })
        return selected_urls
    
    def test(self):
        # hots=self.get_hots()
        # for hot in hots:
        #     for url in hot['selected_urls']:
        #         for c in (self.get_comments(url['url'])):
        #             print(c)
        #         print(self.title)
        for c in self.get_comments('https://tieba.baidu.com/p/6709826506'):
            print(c)
        print(self.title)

        #   
        # total_time=0
        # total_count=0
        # for i in range(0,1):
        #     for hot in hots:
        #         for url in hot['selected_urls']:
        #             start=time()
        #             count=0
        #             for c in (spider.get_comments(url['url'])):
        #                 count+=1
        #             use_time=time()-start
        #             total_time+=use_time
        #             total_count+=count

        # logging.debug("%f ms/comment.%d seconds.%d comments"%(1000*total_time/total_count,total_time,total_count))      
       



class Spider_zhihu(object):
    def __init__(self):
        self.comment_count=0  #作为一个帖子的base_info
        self.page_count=0
        self.title=None
        
        self.comment_index=0  #初始化
        self.page_index=1
        self.fp=None

        self.id='zhihu'
        self.site_name='知乎社区'
        self.site_url='http://www.zhihu.com'
        self.search_sample="https://www.zhihu.com/question/339879487"
        self.search_action='/search-zhihu'
        self.comments_per_page=10
        self.max_comments=1 #限定一个帖子的最大发言数
        self.max_hots=10 #限定爬虫获取的最大热点数
        self.headers={
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'cookie':'SESSIONID=kq4VvgmXE1UTqCN6nxLndrzgqPM1Na40uFQmhjy9NAZ; JOID=V1wWAEMJuD8yW5R6Cg9kqCPpcygdMOxTbyH7PkBy6F1ZPqw1QTJi42pXkn0B3OHLSkqO4ePakdKQIO79usOyR94=; osd=VVgRC04LvDg5VpZ-DQRpqifueCUfNOtYYiP_OUt_6lleNaE3RTVp7mhTlXYM3uXMQUeM5eTRnNCUJ-XwuMe1TNM=; _zap=3fbfc45f-a767-49be-809c-f3eed482e64d; _xsrf=5GXNVuSdt1Ew96dGoW8LczLBxvYVMgRS; ISSW=1; d_c0="AJAZBRCwNxGPTid2JXHXqAcu8cfriHACVXw=|1588574917"; _ga=GA1.2.1231512065.1588574918; tshl=; q_c1=bf6082127e49481787d0fe81ab87f107|1588586954000|1588586954000; tst=h; _gid=GA1.2.956732698.1591174453; SESSIONID=8SlVwnCJvQekn5NLMVaLLdGyVfX77GSq2ksIFQ6MwIv; JOID=UVkcBEzpGZnOHhvTN-1_yQ3Fy4ss00L7mG13mHObSvSrcCqfc-nPQJQYEdU5GRfTfpIvzw5y0OQ9QHlqVTlBPXE=; osd=VlAQCkLuEJXAEBzaO-NxzgTJxYUr2k71lmp-lH2VTf2nfiSYeuXBTpMRHds3Hh7fcJwoxgJ83uM0THdkUjBNM38=; anc_cap_id=0ead5886a889443b858a5c54cd0e2d97; capsion_ticket="2|1:0|10:1591211260|14:capsion_ticket|44:YjhjNWNlMzgyYzhjNGU4MWIyMTkzMGQ0ZTY5NTAyMzc=|0a2c6348c7ac8a0be659ec71a8a708a1af2f86f014c48e5b9200455eb8d783ba"; z_c0="2|1:0|10:1591211299|4:z_c0|92:Mi4xZzhOVkF3QUFBQUFBa0JrRkVMQTNFU1lBQUFCZ0FsVk5JMFBGWHdEaUR3ZHJ5YlR5T2ZUbmt5WHlyOEVIa2czZ0lR|7e236945a1c85494da58581b4cc6b609ec2c41eb4577e3e246ab1f21bd81b152"; unlock_ticket="AGAAJxAwWgomAAAAYAJVTSv8116ZnZOCHuvx8SPXlUDDPHJ7XkUihA=="; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1591211194,1591211219,1591211241,1591211327; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1591211327; KLBRSID=fb3eda1aa35a9ed9f88f346a7a3ebe83|1591211328|1591201793'
        }
    
    def reset(self): #跑完一个主题帖之后就reset
        self.comment_index=0
        self.page_index=1
        self.fp=None
        self.title=None

    def get_one_page(self,url):
        if(url):
            try:
                response=requests.get(url,headers=self.headers)
                if(response.status_code==200):
                    content_type=response.headers['Content-Type'].split(';')[0].strip()
                    if content_type=='application/json':
                        return response.json()
                    elif content_type=='text/html':
                        return response.text
                    else:
                        return None
                else:
                    return None
            except requests.ConnectionError as e:
                print('Connect failed.')
                return None

    def get_base_info(self,url):
        '''
        输入：检索贴url
        过程：获取帖子的基本信息：页数、发言数、标题
        输出：无
        '''
        question_id=url.split('/')[-1]
        url='https://www.zhihu.com/api/v4/questions/'+question_id+'/answers?platform=desktop&sort_by=default&limit=1&offset=0'
        json=self.get_one_page(url)
        self.title=json['data'][0]['question']['title']
        self.comment_count=json['paging']['totals']

    def parse_one_page(self,json):
        items=json['data']
        for item in items:
            result_item={'name':item['author']['name']}

            comment=item['content']

            doc=pq(comment).remove('a')# 这里直接删除外部链接 图片视频什么的
            comment=doc.text()         #这里只保留文字
            # comment=re.sub('\s','',comment) # 取出多余的空格

            result_item['comment']=comment
            self.comment_index+=1
            yield result_item

    def get_comments(self,url):
        self.reset()
        question_id=url.split('/')[-1]
        filename=md5(url.encode(encoding='UTF-8')).hexdigest() 

        self.get_base_info(url)
    
        init_url='https://www.zhihu.com/api/v4/questions/'+question_id+'/answers?include=data%2Ccontent&platform=desktop&sort_by=default&limit=20&offset='
        
        self.fp=open(filename,'w')
        while self.comment_index<self.comment_count and self.comment_index<self.max_comments:
            url=init_url+str(self.comment_index)
            j=self.get_one_page(url)
            for item in self.parse_one_page(j):
                yield item['comment']

    def save_one_item(self,item):  
        '''
        输入：发言item {'name': ,'comment':  ,}
        过程：保存一个发言到文件fp
        输出：无
        '''
        self.fp.write(item['comment'].replace('\n',' ')+'\n')

    def get_hots(self):
        url='https://www.zhihu.com/hot'
        html=self.get_one_page(url)
        doc=pq(html)
        hots=[]
        items=doc('.HotList-list .HotItem-content>a').items()
        hot_count=0
        for item in items:
            hot={
                    'url':item.attr('href'),
                    'title':item.attr('title')
                }
            if hot['url'].split('/')[-2]!='question':
                continue
            yield hot
            hot_count+=1
            if hot_count>=self.max_hots: #只收集十条
                break

    def test(self):
        hots=self.get_hots()
        for hot in hots:
            print(hot)
            for c in self.get_comments(hot['url']):
                print(c)
                print('*'*10) 



class Spider_weibo(object):
    def __init__(self):
        self.comment_count=0  #作为一个帖子的base_info
        self.page_count=0
        self.title=None
        
        self.comment_index=0  #初始化
        self.page_index=1
        self.fp=None

        self.id='weibo'
        self.site_name='新浪微博'
        self.site_url='https://s.weibo.com/top/summary?cate=realtimehot'
        self.search_sample="火影忍者完结"
        self.search_action='/search-weibo'
        self.comments_per_page=10
        self.max_comments=1 #限定一个帖子的最大发言数
        self.max_hots=10 #限定爬虫获取的最大热点数
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
            'Cookie': 'SINAGLOBAL=4273708395035.425.1588792035255; UOR=,,login.sina.com.cn; SSOLoginState=1591856563; _s_tentry=login.sina.com.cn; Apache=5541324434634.329.1591856564386; ULV=1591856565067:5:3:1:5541324434634.329.1591856564386:1591432444485; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhUyPVR4C.BTNdluvdSHMd35JpX5KMhUgL.Foq7S0241hqceoM2dJLoIEnLxK-LBK-L1hnLxKnL1h.LB-qLxK.LBo.LB.qLxKBLBonLBonp1K.N; ALF=1623485019; SCF=AkmlWxzAzsOY8zc01Ul0HvC5W4GjKyv0uDFCX6nlC32ils5eIyiVUoIKgmmPiQq8_LlUznXXREVDY5Zq3Ev9bsY.; SUB=_2A25z50aNDeRhGeBO7FMY-CjKyTuIHXVQlT9FrDV8PUNbmtANLVDDkW9NRdrMH5qcQeVfPWznSxhA8i9bwwHkatQd; SUHB=0nlu9YmHMt98Mu; WBStorage=42212210b087ca50|undefined; secsys_id=ae70b92afaaaf1647d30af2cad16c475',
            'Host': 's.weibo.com',

        }
    
    def reset(self): #跑完一个主题帖之后就reset
        self.comment_index=0
        self.page_index=1
        self.fp=None
        self.title=None

    def get_base_info(self,url):
        '''
        输入：检索贴url
        过程：获取帖子的基本信息：页数、发言数、标题
        输出：无
        '''
        html=self.get_one_page(url)
        doc=pq(html)
        m_error=doc('.m-error').text()
        if m_error =='':
            self.comment_count=self.max_comments
            self.page_count=1
        else:
            self.comment_count=min(self.max_comments,int(re.search(r'\d+',doc('.m-error').text()).group()))
            self.page_count=50 ##最多50页好了
  
        self.title=doc('.search-input>input').attr('value')

    def get_one_page(self,url):
        '''
        输入：url
        过程：
        输出：html文本
        '''
        if(url):
            try:
                response=requests.get(url,headers=self.headers)
                if(response.status_code==200):
                    content_type=response.headers['Content-Type'].split(';')[0].strip()
                    if content_type=='application/json':
                        return response.json()
                    elif content_type=='text/html':
                        return response.text
                    else:
                        return None
                else:
                    return None
            except requests.ConnectionError as e:
                print('Connect failed.')
                return None

    def parse_one_page(self,html):  
        '''
        输入：html文本
        过程：解析页面 第一次：页数、发言数  ，每一次：该页的所有发言
        输出：所有发言
        '''
        doc=pq(html)
 
        items=doc('.card-feed .content').items()
        for item in items: #获取item
            result_item={}
            result_item['name']=item('.info [nick-name]').attr('nick-name')

            result_item['comment']=item('.txt').remove('a').text().replace('\n','')

            self.comment_index+=1 # 发言索引+1
            yield result_item

    def save_one_item(self,item):  
        '''
        输入：发言item {'name': ,'comment':  ,}
        过程：保存一个发言到文件fp
        输出：无
        '''
        self.fp.write(item['comment'].replace('\n','')+'\n')


    def get_hots(self):  
        '''
        输入：无
        过程：获取实时热门话题自身的url，title，如果是贴吧或者微博，就要获取selected_urls
        输出：hots ,hots的结构里面必须有一个或多个精选url
        '''
        url='https://s.weibo.com/top/summary?cate=realtimehot'
        html=self.get_one_page(url)
        doc=pq(html)
        items=doc('.td-02>a').items()
        hot_count=0
        for item in items:
            href=item.attr('href')
            if(href[-1]==';'):
                continue
            hot={
                'url':'https://s.weibo.com'+href,
                'title':item.text()
                }
            yield hot
            hot_count+=1
            if hot_count>=self.max_hots: #只收集十条
                break

    def get_comments(self,url): 
        '''
        输入：帖子url
        过程：获取html->解析html->保存items
        输出: 保存帖子的filename和帖子的title
        '''
        self.reset()
        self.get_base_info(url)
        init_url=url+'&page='
        while self.page_index<=self.page_count and self.comment_index<self.comment_count and self.page_index<self.page_count:
            url=init_url+str(self.page_index)
            html=self.get_one_page(url)
            for item in self.parse_one_page(html):
                yield item['comment']
                if self.comment_index>=self.max_comments:
                    break
            self.page_index+=1

    def test(self):
        for hot in self.get_hots():
            print(hot)
            for c in self.get_comments(hot['url']):
                print(c)


if __name__ == '__main__':
    shuimu=Spider_shuimu()
    tieba=Spider_baidutieba()
    zhihu=Spider_zhihu()
    weibo=Spider_weibo()
    tieba.test()


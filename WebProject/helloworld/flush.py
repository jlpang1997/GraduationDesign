from importlib import import_module

# from spiders import Spider_shuimu,Spider_baidutieba,Spider_zhihu,Spider_weibo
from .spiders import Spider_shuimu,Spider_baidutieba,Spider_zhihu,Spider_weibo
# from Classification_Based_on_Sentiment_Dict.sentiment_classifier import get_sentiment
# from .Classification_Based_on_Sentiment_Dict.sentiment_classifier import get_sentiment
from .Classification_Based_on_Networks.sentiment_api import get_sentiment

import time
import logging

'''
spider_id:topics
'''
hots_analysis_result={

    'shuimu':[],
    'zhihu':[],
    'tieba':[],
    'weibo':[],
}
# shuimu=Spider_shuimu.Spider_shuimu()
# zhihu=Spider_zhihu.Spider_zhihu()
# tieba=Spider_baidutieba.Spider_baidutieba()
# weibo=Spider_weibo.Spider_weibo()

shuimu=Spider_shuimu()
zhihu=Spider_zhihu()
tieba=Spider_baidutieba()
weibo=Spider_weibo()

def flush(spider):
    '''
    输入：spider
    过程：
    '''
    logging.debug('%s is flushing.'%(spider.id))
    topics=[]
    def sort_key(elem):
        return elem['total_count'] 

    if spider.id=='tieba':
        hots=spider.get_hots()
        for hot in hots:
            print(hots)
            pos_count,neg_count,total_count=0,0,0

            for topic in hot['selected_urls']:
                comments=spider.get_comments(topic['url'])

                result_dict=get_sentiment(comments)
                pos_count+=result_dict['pos_count']
                neg_count+=result_dict['neg_count']
                total_count+=result_dict['total_count']

            pos_number_ratio=100*pos_count//total_count if total_count!=0 else 56
            neg_number_ratio=100*neg_count//total_count if total_count!=0 else 56

            topics.append(
                {
                'title':hot['title'],
                'link':hot['url'],
                "positive_rate":str(pos_number_ratio)+'%',
                'negative_rate':str(neg_number_ratio)+'%',
                'pos_count': pos_count,
                'neg_count': neg_count,
                'total_count':total_count
                }
            )

    else:
        hots=spider.get_hots()
        for hot in hots:
            comments=spider.get_comments(hot['url'])
            result_dict=get_sentiment(comments)
            topics.append(
                {
                    'title':hot['title'],
                    'link':hot['url'],
                    "positive_rate":result_dict['positive_rate'],
                    'negative_rate':result_dict['negative_rate'],
                    'pos_count':result_dict['pos_count'],
                    'neg_count':result_dict['neg_count'],
                    'total_count':result_dict['total_count']
                }
            )

    topics.sort(key=sort_key,reverse=True)
    hots_analysis_result[spider.id]=topics
    logging.debug('get topics:%s'%(str(topics)))
    logging.debug('%s finish flush.'%(spider.id))

def run():
    for s in [shuimu,tieba,zhihu,weibo]:
        flush(s)
    print(hots_analysis_result)


if __name__=='__main__':
    # sentiment_classifier.test()
    # pass
    run()
    

__author__ = 'Pang Jinlin'
from importlib import import_module
import sys
import os

# import utils
from . import utils

import logging

current_work_dir = os.path.dirname(__file__)
# 1.读取情感词典和待处理文件

# 情感词典
posdict = utils.read_lines(current_work_dir+"\emotion_dict/pos_all_dict.txt")
negdict = utils.read_lines(current_work_dir+"\emotion_dict/neg_all_dict.txt")
# 程度副词词典
mostdict = utils.read_lines(current_work_dir+'\degree_dict/most.txt')   # 权值为2
verydict = utils.read_lines(current_work_dir+'\degree_dict/very.txt')   # 权值为1.5
moredict = utils.read_lines(current_work_dir+'\degree_dict/more.txt')   # 权值为1.25
ishdict = utils.read_lines(current_work_dir+'\degree_dict/ish.txt')   # 权值为0.5
insufficientdict = utils.read_lines(current_work_dir+'\degree_dict/insufficiently.txt')  # 权值为0.25
inversedict = utils.read_lines(current_work_dir+'\degree_dict/inverse.txt')  # 权值为-1



# 2.程度副词处理，根据程度副词的种类不同乘以不同的权值
def match(word, sentiment_value):
	if word in mostdict:
		sentiment_value *= 2.0
	elif word in verydict:
		sentiment_value *= 1.75
	elif word in moredict:
		sentiment_value *= 1.5
	elif word in ishdict:
		sentiment_value *= 1.2
	elif word in insufficientdict:
		sentiment_value *= 0.5
	elif word in inversedict:  ##否定词处理
		#print "inversedict", word
		sentiment_value *= -1
	return sentiment_value


# 3.情感得分的最后处理，防止出现负数
# Example: [5, -2] →  [7, 0]; [-4, 8] →  [0, 12]
def transform_to_positive_num(poscount, negcount):
	pos_count = 0
	neg_count = 0
	if poscount < 0 and negcount >= 0:
		neg_count += negcount - poscount
		pos_count = 0
	elif negcount < 0 and poscount >= 0:
		pos_count = poscount - negcount
		neg_count = 0
	elif poscount < 0 and negcount < 0:
		neg_count = -poscount
		pos_count = -negcount
	else:
		pos_count = poscount
		neg_count = negcount
	return (pos_count, neg_count)


# 求单条微博语句的情感倾向总得分
def single_review_sentiment_score(weibo_sent):
	single_review_senti_score = []
	cuted_review = utils.cut_sentence(weibo_sent)  # 句子切分，单独对每个句子进行分析

	for sent in cuted_review:  ##对每一个句子
		seg_sent = utils.segmentation(sent)   # 分词
		seg_sent = utils.del_stopwords(seg_sent)[:]
		i = 0    # 记录扫描到的词的位置
		s = 0    # 记录情感词的位置
		poscount = 0    # 记录该分句中的积极情感得分
		negcount = 0    # 记录该分句中的消极情感得分

		for word in seg_sent:   # 对句子里面的每一个单词
			#print word
			if word in posdict:  # 如果是积极情感词
				#print "posword:", word
				poscount += 1   # 积极得分+1
				for w in seg_sent[s:i]:
					poscount = match(w, poscount)  ##找到一个积极词汇，然后判断前面是否有程度词或者否定词
				s = i + 1  # 记录情感词的位置变化

			elif word in negdict:  # 如果是消极情感词
				negcount += 1
				for w in seg_sent[s:i]:
					negcount = match(w, negcount)
				s = i + 1
			i += 1
		single_review_senti_score.append(transform_to_positive_num(poscount, negcount))   # 对得分做最后处理

	pos_result, neg_result = 0, 0   # 分别记录积极情感总得分和消极情感总得分
	for res1, res2 in single_review_senti_score:  # 每个分句循环累加
		pos_result += res1
		neg_result += res2

	result = pos_result - neg_result   # 该条微博情感的最终得分
	result = round(result, 1)
	return result


# 分析test_data.txt 中的所有微博，返回一个列表，列表中元素为（分值，微博）元组

def run_score(comments):
	for content in comments:
		score = single_review_sentiment_score(content)  # 对每条微博调用函数求得打分
		yield score



# 求取测试文件中的正负极性的微博比，正负极性分值的平均值比，正负分数分别的方差
def handel_result(results):  ##分别统计正向、负向的数量
	pos_count,neg_count=0,0
	for result in results:
		if result >= 0:
			pos_count+=1
		elif result < 0:
			neg_count+=1

	total_number=pos_count+neg_count
	pos_number_ratio = 100*pos_count//total_number if total_number!=0 else 56
	neg_number_ratio = 100*neg_count//total_number if total_number!=0 else 56

	result_dict = {
		'positive_rate':str(pos_number_ratio)+'%',
		'negative_rate':str(neg_number_ratio)+'%',
		'pos_count':pos_count,
		'neg_count':neg_count,
		'total_count':total_number
	}

	return result_dict

#我需要的就是这个接口
def get_sentiment(comments):
	logging.debug('start analysing......')
	results = run_score(comments)
	result_dict = handel_result(results)
	logging.debug('start analysing......')
	return result_dict

# if __name__ == '__main__':
def test():
	# results = run_score("test_data.txt")     # 计算每句话的极性得分，返回list，元素是（得分，微博）
	# result_dict = handel_result(results)   # 计算结果的各种参数，返回字典
	comments=['''贾乃亮曾与李小璐一起陪甜馨打羽毛球''','我好','大家好','伤心难过']
	print(get_semtiment(comments))



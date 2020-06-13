
import jieba
import jieba.posseg as pseg
# print ("加载用户词典...")
import sys
import os


current_work_dir = os.path.dirname(__file__)
jieba.load_userdict(current_work_dir+'/emotion_dict/pos_all_dict.txt')
jieba.load_userdict(current_work_dir+'/emotion_dict/neg_all_dict.txt')

def read_lines(filename):
	fp = open(filename, 'r')
	lines = []
	for line in fp.readlines():
		line = line.strip()
		line = line.encode("utf-8").decode("utf-8")
		lines.append(line)
	fp.close()
	return lines
stopwords = read_lines(current_work_dir+"/emotion_dict/stop_words.txt")  # 读取停用词表


# 分词，返回List
def segmentation(sentence):
	return jieba.lcut(sentence)

# 句子切分
def cut_sentence(words):
	words = words.encode("utf-8").decode('utf8')
	start = 0
	i = 0
	token = 'meaningless'
	sents = []
	punt_list = ',.!?;~，。！？；～… '.encode("utf-8").decode('utf8')
	#print "punc_list", punt_list
	for word in words:
		#print "word", word
		if word not in punt_list:   # 如果不是标点符号
			#print "word1", word
			i += 1
			token = list(words[start:i+2]).pop()
			#print "token:", token
		elif word in punt_list and token in punt_list:  # 处理省略号
			#print "word2", word
			i += 1
			token = list(words[start:i+2]).pop()
			#print "token:", token
		else:
			#print "word3", word
			sents.append(words[start:i+1])   # 断句
			start = i + 1
			i += 1
	if start < len(words):   # 处理最后的部分
		sents.append(words[start:])
	return sents



# 去除停用词
def del_stopwords(seg_sent):
	new_sent = []   # 去除停用词后的句子
	for word in seg_sent:
		if word in stopwords:
			continue
		else:
			new_sent.append(word)
	return new_sent


if __name__ == '__main__':
	test_sentence1 = "这款手机大小合适。"
	test_sentence2 = "这款手机大小合适，配置也还可以，很好用，只是屏幕有点小。。。总之，戴妃+是一款值得购买的智能手机。"
	test_sentence3 = "这手机的画面挺好，操作也比较流畅。不过拍照真的太烂了！系统也不好。"
	

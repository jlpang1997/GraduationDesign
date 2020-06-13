# coding: UTF-8
import os
import torch
import numpy as np
import pickle as pkl
from tqdm import tqdm
import time
import jieba
import sys
import os
from datetime import timedelta
import pandas as pd
from math import ceil

MAX_VOCAB_SIZE = 100000  # 词典长度限制
UNK, PAD = '<UNK>', '<PAD>'  # 未知字，padding符号

stopwords=set()
cur_dir=os.path.abspath(os.path.dirname(__file__))
with open(cur_dir+"/static/data/stop_words.txt","r") as fp:
    for line in fp.readlines():
        stopwords.add(line.strip())

def strip_sent(sent):
    '''
    把一个原始的句子分词成一个词序列，并去除停用词，返回最终的词序列
    '''
    words_it=jieba.cut(sent)
    words=[]
    for word in words_it:
        if word not in stopwords:
            words.append(word)
    return words

def build_vocab(file_path, tokenizer, max_size, min_freq):
    '''
    从12万条微博中生成一个词汇表
    '''
    vocab_dic = {}
    data = pd.read_csv(file_path)
    for idx, row in tqdm(data.iterrows()):
        content=row['review']
        for word in tokenizer(content):
            vocab_dic[word] = vocab_dic.get(word, 0) + 1

    vocab_list = sorted([_ for _ in vocab_dic.items() if _[1] >= min_freq], key=lambda x: x[1], reverse=True)[:max_size]##根据词频排序从大到小排序

    vocab_dic = {word_count[0]: idx for idx, word_count in enumerate(vocab_list)}

    vocab_dic.update({UNK: len(vocab_dic), PAD: len(vocab_dic) + 1})  ##这里把未知字符和占位符分别给一个index
    return vocab_dic


def build_dataset(config, ues_word):
    if ues_word:
        tokenizer = strip_sent  # 以空格隔开，word-level
    else:
        tokenizer = lambda x: [y for y in x]  # char-level
    if os.path.exists(config.vocab_path):
        vocab = pkl.load(open(config.vocab_path, 'rb'))
    else:
        vocab = build_vocab(config.vocab_init_path, tokenizer=tokenizer, max_size=MAX_VOCAB_SIZE, min_freq=3)
        pkl.dump(vocab, open(config.vocab_path, 'wb'))  
    print(f"Vocab size: {len(vocab)}")

    def load_dataset(path, pad_size=32):
        contents = []
        data = pd.read_csv(path)
        for idx, row in tqdm(data.iterrows()):
            content,label=row['review'].strip(),row['label']
            words_line = []
            token = tokenizer(content)
            seq_len = len(token)
            if pad_size:
                if len(token) < pad_size: #seq_len 不包含PAD
                    token.extend([PAD] * (pad_size - len(token)))##句子太短的话会在后面填充PAD
                else:
                    token = token[:pad_size]
                    seq_len = pad_size
            # word to id
            for word in token:
                words_line.append(vocab.get(word, vocab.get(UNK)))
            contents.append((words_line, int(label), seq_len))
        return contents  # [([...], 0,10), ([...], 1,21), ...]
    train = load_dataset(config.train_path, config.pad_size)
    dev = load_dataset(config.dev_path, config.pad_size)
    test = load_dataset(config.test_path, config.pad_size)
    return vocab, train, dev, test

def mybuild_dataset(config, ues_word,comments):
    if ues_word:
        tokenizer = strip_sent  # 以空格隔开，word-level
    else:
        tokenizer = lambda x: [y for y in x]  # char-level
    if os.path.exists(config.vocab_path):
        vocab = pkl.load(open(config.vocab_path, 'rb'))
    else:
        vocab = build_vocab(config.vocab_init_path, tokenizer=tokenizer, max_size=MAX_VOCAB_SIZE, min_freq=3)
        pkl.dump(vocab, open(config.vocab_path, 'wb'))  
    print(f"Vocab size: {len(vocab)}")

    def load_dataset(path, pad_size=32):
        contents = []
        for comment in tqdm(comments):
            content,label=comment.strip(),0
            words_line = []
            token = tokenizer(content)
            seq_len = len(token)
            if pad_size:
                if len(token) < pad_size: #seq_len 不包含PAD
                    token.extend([PAD] * (pad_size - len(token)))##句子太短的话会在后面填充PAD
                else:
                    token = token[:pad_size]
                    seq_len = pad_size
            # word to id
            for word in token:
                words_line.append(vocab.get(word, vocab.get(UNK)))
            contents.append((words_line, int(label), seq_len))
        return contents  # [([...], 0,10), ([...], 1,21), ...]

    test = load_dataset(config.test_path, config.pad_size)
    return vocab, test

class DatasetIterater(object):
    def __init__(self, batches, batch_size, device):
        '''
        batches 就是用build_dataset得到的train_data,dev_data,test_data  [([...], 0，10), ([...], 1,24), ...]
        '''
        self.batch_size = batch_size
        self.batches = batches
        self.n_batches = ceil(len(batches) / batch_size)
        self.index = 0
        self.device = device

    def _to_tensor(self, datas):
        x = torch.LongTensor([_[0] for _ in datas]).to(self.device)
        y = torch.LongTensor([_[1] for _ in datas]).to(self.device)

        # pad前的长度(超过pad_size的设为pad_size)
        seq_len = torch.LongTensor([_[2] for _ in datas]).to(self.device)
        return (x, seq_len), y

    def __next__(self):
        if self.index >= self.n_batches:
            self.index = 0
            raise StopIteration
        else:
            batches = self.batches[self.index * self.batch_size: (self.index + 1) * self.batch_size]
            self.index += 1
            batches = self._to_tensor(batches)
            return batches

    def __iter__(self):  ##__iter__ 和 __next__ 是一个迭代器必须的方法
        return self

    def __len__(self):
        return self.n_batches


def build_iterator(dataset, config):
    iter = DatasetIterater(dataset, config.batch_size, config.device)
    return iter


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))


if __name__ == "__main__":
    print(stopwords)
    pass


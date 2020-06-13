# -*- coding: utf-8 -*-
 
import random
 
"""
随机按比例拆分数据
"""
 
def split(all_list, shuffle=False, ratio1=0.7,ratio2=0.2,ratio3=0.1):
    num = len(all_list)-1
    offset1 = int(num * ratio1)
    offset2 = int(num * (ratio1+ratio2))
    if num == 0 or offset1 < 1:
        return [], all_list
    if shuffle:
        random.shuffle(all_list)  # 列表随机排序
    train = all_list[1:7001]
    dev=all_list[7001:8001]
    test = all_list[8001:10001]
    return train,dev, test
 
 
def write_split(film, train, dev,test):
    infilm = open(film, 'r', encoding='utf-8')
    tainfilm = open(train, 'w', encoding='utf-8')
    devfilm = open(dev, 'w', encoding='utf-8')
    testfilm = open(test, 'w', encoding='utf-8')
    li = []
    for datas in infilm.readlines():
        li.append(datas.strip())
    traindatas,devdatas, testdatas = split(li, shuffle=True)
    
    tainfilm.write("label,review" + '\n')
    devfilm.write("label,review" + '\n')
    testfilm.write("label,review" + '\n')

    for traindata in traindatas:
        tainfilm.write(traindata + '\n')
    for devdata in devdatas:
        devfilm.write(devdata + '\n')

    for testdata in testdatas:
        testfilm.write(testdata + '\n')

    infilm.close()
    tainfilm.close()
    devfilm.close()
    testfilm.close()
 
 
if __name__ == "__main__":
    write_split('./static/data/weibo_senti_100k.csv', './static/data/train.csv', './static/data/dev.csv','./static/data/test.csv')
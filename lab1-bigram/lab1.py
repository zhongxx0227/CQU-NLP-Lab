'''
Author: XiangxinZhong
Date: 2021-10-29 16:18:04
LastEditors: XiangxinZhong
LastEditTime: 2021-10-29 23:14:02
Description: NPL Lab1 Bigram
'''

from sys import _current_frames
from threading import currentThread
import jieba
import numpy as np
import pandas as pd
import re


# 待替代符号
punc = "\n ！？｡＂＃《》＄％＆＇（）＊＋－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏#$%&'()*+-/;<=>?@[\]^_`{|}~“”？！【】（）。’‘……￥"


'''
description: 对语料的预处理
param {*} file_path
return {*}
'''


def Pretreatment(file_path):
    intab = "０１２３４５６７８９"
    outtab = "0123456789"
    trantab = str.maketrans(intab, outtab)  # 将所有的in字符与对应的out字符建立映射
    f1 = open("F:/IDE/Python/NLP/Lab1_Bigram/lab1/filter.txt",
              "w", encoding='utf-8')  # 构造过滤后的文件
    for line in open(file_path, encoding='gbk'):
        new_line = re.sub(
            r" |/t|/n|/m|/v|/u|/a|/w|/q|r|t|/k|/f|/p|n|/c|s|/|d|i|b|l|j|e|v|g|N|V|R|T|y|o|A|D|h|z|x|A|B|M|a|Y|\d{8}-\d{2}-\d{3}-\d{3}", "", line)
        new_line = new_line.translate(trantab)  # 将所有的in字符用对应的out字符替代
        f1.write(new_line)
    f1.close()


'''
description: 提取头条语料库每一行的句子主干
param {*} sen
return {*} sen[s:e]
'''


def sep(sen):
    s = 0  # 开始
    e = 0  # 结束
    length = len(sen)
    for i in range(length, 0, -1):
        if sen[i-3:i] == "_!_" and e == 0:
            e = i-3
            break
    for i in range(e, 0, -1):
        if sen[i-3:i] == "_!_" and s == 0:
            s = i
            break
    return sen[s:e]


'''
description: 语料库预处理，每个句子添加BOS和EOS
param {*} filename
return {*} list
'''


def preDiv(filename):
    listSen = []
    with open(filename, 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            # line = sep(line)
            listTmp = list(jieba.cut(line))
            listSen.append("BOS")
            listSen.extend(listTmp)
            listSen.append("EOS")
    f.close()
    return listSen


'''
description: 统计词频
param {*} lists
return {*} dictSen, dictLen
'''


def statistic(lists):
    dictSen = {}
    for word in lists:
        if word not in punc:
            if word not in dictSen:
                dictSen[word] = 1
            else:
                dictSen[word] += 1
    dictSen = sorted(dictSen.items(), key=lambda x: x[1], reverse=False)
    dictSen = dict(dictSen)
    dictLen = len(dictSen)
    return dictSen, dictLen


'''
description: 输入例句分词
param {*} sen
return {*} cutResult
'''


def cutWord(sen):
    cutResult = list(jieba.cut(sen))
    tmp = []
    for word in cutResult:
        if word not in punc:
            tmp.append(word)
    cutResult = tmp
    cutResult.insert(0, "BOS")
    cutResult.append("EOS")
    print("分词结果为：{}\n".format(cutResult))
    return cutResult


'''
description: bi-gram算法，计算概率，平滑
param {*} listSen
param {*} dicSen
param {*} dicLen
param {*} cutResult
return {*}
'''


def biGram(listSen, dicSen, dicLen, cutResult):
    fenzi = [0]*(len(cutResult)-1)
    fenmu = []
    for i in range(1, len(cutResult)):
        # 计算分母
        if cutResult[i-1] in dicSen:
            fenmu.append(dicSen[cutResult[i-1]])
        else:
            fenmu.append(0)
        # 计算分子
        for j in range(len(listSen)):
            if (listSen[j] == cutResult[i-1]) and listSen[j+1] == cutResult[i]:
                fenzi[i-1] += 1
    print("二元语法在语料库中的频数为：{}\n".format(fenzi))
    print("一元语法在语料库中的频数为：{}\n".format(fenmu))
    # 使用加法数据平滑
    k = 1
    b = k*dicLen
    fenzi = [i + k for i in fenzi]
    fenmu = [i + b for i in fenmu]
    result = 1
    for i in range(len(fenzi)):
        if fenmu[i] != 0:
            tmp = fenzi[i]/fenmu[i]
            result *= tmp
    return result


if __name__ == "__main__":
    Pretreatment("F:/IDE/Python/NLP/Lab1_Bigram/lab1/训练语料.txt")
    filename = "F:/IDE/Python/NLP/Lab1_Bigram/lab1/filter.txt"
    listSen = preDiv(filename)
    sen1 = "让党旗在基层一线高高飘扬，必须进一步发挥党员先锋模范作用。"
    sen2 = "我爱我的祖国"
    sen3 = "我们伟大祖国在新的一年，将是充满生机、充满希望的一年。"
    sen4 = "坚持中国共产党的领导"
    testData = [sen1, sen2, sen3, sen4]
    cnt = 0  # 计数
    for ss in testData:
        print("Sentence {}: \n".format(ss))
        cnt += 1
        cutResult = cutWord(ss)
        dictSen, dictLen = statistic(listSen)
        result = biGram(listSen, dictSen, dictLen, cutResult)
        print("Sentence {} 的概率为 {}\n".format(cnt, result))

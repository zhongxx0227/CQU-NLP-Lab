'''
Author: XiangxinZhong
Date: 2021-11-05 21:50:02
LastEditors: XiangxinZhong
LastEditTime: 2021-11-07 11:05:00
Description: NLP Lab2 HMM Pinyin2Hanzi 数据处理部分
'''


import re
import string

'''
description: 头条数据预处理，生成拼音-汉字 字典，统计每个拼音对应的汉字序列
param {*} None
return {*} wordDictD,wordDictS,pinyinDict,wordList,wordIndex,wordNum
'''


def getWordDict():
    content = []
    punctuation = r"[^a-zA-Z0-9\u4e00-\u9fa5]"  # 使用正则表达式去除所有的中文标点
    # 头条数据预处理，去除包含的标点符号
    with open('toutiao_cat_data.txt', 'r', encoding='UTF-8') as f:
        while 1:
            example = f.readline()
            if not example:
                break
            example = example.replace('\n', '').replace(' ', '')
            example = example.split('_!_')
            del example[0:3]
            temp = []
            for word in example:
                word = re.sub(punctuation, ' ', word)
                word = word.split(' ')
                if word != '':
                    temp.extend(word)
            while '' in temp:
                temp.remove('')
            content.extend(temp)
    f.close()

    #生成拼音-汉字字典
    pinyinDict = {}
    with open('pinyin2hanzi.txt', 'r', encoding='UTF-8') as f:
        while 1:
            example = f.readline()
            if not example:
                break
            example = example.replace('\n', '')
            example = example.split(' ')
            pinyinDict[example[0]] = example[1]

    wordDictS = {} # 单字出现的次数
    wordIndex = {} # 单字索引
    wordList = [] # 单字列表
    i = 0
    for item in pinyinDict:
        for word in pinyinDict[item]:
            if word not in wordDictS.keys():
                wordDictS[word] = 0
                wordList.append(word)
                wordIndex[word] = i
                i += 1
    # 加入句子标签
    wordDictS['E'] = 0
    wordIndex['E'] = i + 1

    wordNum = 0 # 统计字数
    wordDictD = {} # 双字出现的次数
    # 统计单字出现的频率   过滤掉了字典中没有的字
    for sentence in content:
        sentence = sentence + 'E'
        for word in sentence:
            if word in wordDictS.keys():
                wordDictS[word] += 1
                wordNum += 1
    # 统计状态转移中双字出现的概率
    for sentence in content:
        for i in range(len(sentence) - 1):
            if sentence[i] in wordDictS.keys() and sentence[i+1] in wordDictS.keys():
                word = sentence[i] + sentence[i + 1]
                if word not in wordDictD.keys():
                    wordDictD[word] = 1
                else:
                    wordDictD[word] += 1
    # print(wordDictD)
    return wordDictD, wordDictS, pinyinDict, wordList, wordIndex, wordNum




'''
description: 生成转移概率，即字与字(状态间)的转移概率
param {*} wordDictD
param {*} wordDictS
param {*} wordListS
param {*} wordIndex
return {*} transferList 转移概率矩阵
'''
def getTransferProb(wordDictD, wordDictS, wordListS, wordIndex):
    wordListD = list(wordDictD.keys())
    singleWordNum = len(wordListS)
    doubleWordNum = len(wordListD)

    # 假设有N个字，生成的转移概率矩阵为N*N的
    transferList = [[0] * len(wordListS) for i in range(len(wordListS))]
    # 计算转移概率
    for i in range(singleWordNum):
        index1 = wordIndex[wordListS[i]]
        num1 = wordDictS[wordListS[index1]]
        wordPre = wordListS[index1]
        if num1 == 0:
            for j in range(singleWordNum):
                transferList[index1][j] = 1 / singleWordNum
        else:
            for j in range(singleWordNum):
                index2 = wordIndex[wordListS[j]]
                wordLast = wordListS[index2]
                word = wordPre + wordLast
                if word in wordDictD.keys():
                    num2 = wordDictD[word]  # 采用加一平滑方法
                    transferList[index1][index2] = num2 / \
                        (singleWordNum + num1)
                else:
                    transferList[index1][index2] = (1 / singleWordNum)
    return transferList



'''
description: 构造初始状态概率分布，假设每个状态的概率等于其频率
param {*} wordDictS
param {*} pinyinDict
param {*} wordNum
return {*} initialProb
'''
def getIniStatusProb(wordDictS, pinyinDict, wordNum):
    wordUnique = len(wordDictS)
    initialProb = {}
    for pinyin in pinyinDict.keys():
        for word in pinyinDict[pinyin]:  # 如果在词典里面有这个词
            if wordDictS[word] != 0:
                initialProb[word] = (
                    float(wordDictS[word]) + 1) / (wordNum + wordUnique)
            else:  # 如果在词典中的词没有出现在训练语料    保证统计的词只包含词典中的词
                initialProb[word] = 1 / wordUnique
    return initialProb



'''
description: 构造发射概率
param {*} pinyinDict
return {*}
'''
def getLanchProb(pinyinDict):
    lanchProb = {}
    # 先计算发射频率，要解决多音字问题
    with open('lexicon1.txt', 'r', encoding='UTF-8') as f:
        while 1:
            example = f.readline()
            example = example.strip('\n')
            if not example:
                break
            wordList = []
            pinyinList = []
            [wordString, pinyinString] = example.split('\t')
            # 获取拼音和汉字列表
            for word in wordString:
                wordList.append(word)
            pinyinTemp = pinyinString.split(' ')
            for pinyin in pinyinTemp:
                pinyin = pinyin[:len(pinyin) - 1]
                pinyinList.append(pinyin)
            for i in range(len(wordList)):
                word = wordList[i]
                pinyin = pinyinList[i]
                if word not in lanchProb.keys():  # 如果此时字典中没有这个字，肯定也就没有它的拼音
                    lanchProb[word] = {}  # 创建嵌套的字典
                    lanchProb[word][pinyin] = 1
                else:  # 如果字典中已经有了这个字
                    if pinyinList[i] not in lanchProb[word].keys():  # 有了这个字，但无拼音
                        lanchProb[word][pinyin] = 1
                    else:  # 有字有拼音
                        lanchProb[word][pinyin] += 1

    f.close()

    #计算发射概率
    for word in lanchProb:
        sumCount = 0
        for pinyin in lanchProb[word]:
            sumCount += lanchProb[word][pinyin]
        for pinyin in lanchProb[word]:
            lanchProb[word][pinyin] = float(lanchProb[word][pinyin]) / sumCount

    for pinyin in pinyinDict.keys():
        for word in pinyinDict[pinyin]:
            if word not in lanchProb.keys():
                lanchProb[word] = {}
                lanchProb[word][pinyin] = 2
            else:
                for key in lanchProb[word].keys():
                    if lanchProb[word][key] == 2:
                        lanchProb[word][pinyin] = 2
                        break

    for word in lanchProb.keys():
        sum = 0
        for pinyin in lanchProb[word].keys():
            if lanchProb[word][pinyin] == 2:
                sum += 2
        for pinyin in lanchProb[word].keys():
            if lanchProb[word][pinyin] == 2:
                lanchProb[word][pinyin] = float(lanchProb[word][pinyin]) / sum
    return lanchProb

'''
description: 调用前面的函数，获取参数
param {*}
return {*}
'''
def getParameter():
    wordDictD, wordDictS, pinyinDict, wordListS, wordIndex, wordNum = getWordDict()
    print('字典统计完成！')
    transferList = getTransferProb(wordDictD, wordDictS, wordListS, wordIndex)
    print('转移概率统计完成')
    IniStatusProb = getIniStatusProb(wordDictS, pinyinDict, wordNum)
    print('初始状态概率统计完成')
    LanchProb = getLanchProb(pinyinDict)
    print('发射概率统计完成')
    return transferList, LanchProb, IniStatusProb, pinyinDict, wordIndex, wordListS

'''
Author: XiangxinZhong
Date: 2021-11-05 21:50:02
LastEditors: XiangxinZhong
LastEditTime: 2021-11-07 11:51:13
Description: NLP Lab2 HMM Pinyin2Hanzi 维特比算法实现拼音到汉字的转换 
'''

'''
description: 维特比算法部分
param {*} t
param {*} ObserveList
param {*} transferList
param {*} LanchProb
param {*} IniStatusProb
param {*} pinyinDict
param {*} wordIndex
param {*} delta
param {*} recordPre
return {*} delta 维特比变量
return {*} recordPre 转移路径
'''
def Viterbi(t, ObserveList, transferList, LanchProb, IniStatusProb, pinyinDict, wordIndex, delta, recordPre):
    if t == 0:  # 初始状态时：
        pinyin = ObserveList[t]  # 获取拼音
        wordList = pinyinDict[pinyin]
        for word in wordList:
            index = wordIndex[word]  # 获取字的顺序位置
            prob = 1
            for pinyinTemp in LanchProb[word].keys():
                if pinyinTemp == ObserveList[t]:
                    prob = LanchProb[word][pinyinTemp]  # 获取发射概率
            delta[t][index] = IniStatusProb[word] * prob  # 初始状态概率乘发射概率
            recordPre[t][index] = 0
    else:  # 正常情况进行递归
        prePinyin = ObserveList[t - 1]  # 上个观察值对应的状态序列
        preStatus = pinyinDict[prePinyin]
        currentPinyin = ObserveList[t]  # 现在的状态序列
        currentStatus = pinyinDict[currentPinyin]

        # 当前
        for i in range(len(currentStatus)):
            indexCur = wordIndex[currentStatus[i]]
            maxTransferProb = -1
            maxValueIndex = -1
            # 上一个
            for j in range(len(preStatus)):
                indexPre = wordIndex[preStatus[j]]
                # 寻找转移到现在状态的最大可能的前置状态
                if delta[t - 1][indexPre] * transferList[indexPre][indexCur] > maxTransferProb:
                    maxTransferProb = delta[t - 1][indexPre] * \
                        transferList[indexPre][indexCur]
                    maxValueIndex = indexPre
            # 寻找到最大概率的路径后乘以转移概率
            prob = 1
            for pinyinTemp in LanchProb[currentStatus[i]].keys():
                if pinyinTemp == ObserveList[t]:
                    prob = LanchProb[currentStatus[i]][pinyinTemp]
            delta[t][indexCur] = maxTransferProb * prob
            recordPre[t][indexCur] = maxValueIndex  # 路径

    if t == len(ObserveList) - 1:
        return delta, recordPre
    else:
        return Viterbi(t + 1, ObserveList, transferList, LanchProb, IniStatusProb, pinyinDict, wordIndex, delta, recordPre)


'''
description: 回溯
param {*} delta
param {*} recordPre
param {*} wordListS
return {*}
'''
def recall(delta, recordPre, wordListS):
    result = []
    t = len(delta) - 1
    lastWordIndex = delta[t].index(max(delta[t]))  # 寻找到最后一个字
    result.append(wordListS[lastWordIndex])

    preIndex = -1
    for i in range(t, -1, -1):

        if i == t:
            preIndex = recordPre[i][lastWordIndex]
        else:
            result.append(wordListS[preIndex])
            preIndex = recordPre[i][preIndex]
    return result


'''
description: 拼音转汉字主函数
param {*} transferList
param {*} LanchProb
param {*} IniStatusProb
param {*} pinyinDict
param {*} wordIndex
param {*} wordListS
return {*}
'''
def predHanzi(transferList, LanchProb, IniStatusProb, pinyinDict, wordIndex, wordListS):
    pinyinList = []
    trueHanziList = []
    with open('测试集.txt', 'r', encoding='gbk') as f:
        while 1:
            pinyin = f.readline()
            if not pinyin:
                break

            # 获取拼音序列
            pinyin = pinyin.strip('\n')
            pinyin = pinyin.strip()
            pinyin = pinyin.lower()  # 将所有的大写字母转换为小写
            pinyin = pinyin.split(' ')
            pinyinList.append(pinyin)
            # 获取真实汉字
            hanzi = f.readline()
            hanzi = hanzi.replace('\n', '').replace(' ', '')
            temp = []
            for word in hanzi:
                temp.append(word)
            # print(temp)
            trueHanziList.append(temp)
    rightSentence = 0
    sentenceNum = len(pinyinList)
    rightWordNum = 0
    testWordNum = 0
    wordNum = len(wordListS)
    with open("result.txt", "w") as f:
        for i in range(sentenceNum):
            print('输入的拼音为：', pinyinList[i])
            f.write('输入的拼音为：{}\n'.format(pinyinList[i]))
            print('真实的结果为：', trueHanziList[i])
            f.write('真实的结果为：{}\n'.format(trueHanziList[i]))
            delta = [[-1 for t in range(wordNum)]
                     for k in range(len(pinyinList[i]))]
            recordPre = [[-1 for t in range(wordNum)]
                         for k in range(len(pinyinList[i]))]
            delta, recordPre = Viterbi(
                0, pinyinList[i], transferList, LanchProb, IniStatusProb, pinyinDict, wordIndex, delta, recordPre)
            temp = recall(delta, recordPre, wordListS)
            result = temp[::-1]  # 将回溯结果反转

            rightNum = 0
            # 利用严格标准看待句子是否完全正确
            flag = 1
            for j in range(len(trueHanziList[i])):
                testWordNum += 1
                if trueHanziList[i][j] != result[j]:
                    flag = 0
                if trueHanziList[i][j] == result[j]:
                    rightNum += 1
                    rightWordNum += 1
            if flag == 1:
                rightSentence += 1

            print('预测的结果为：', result)
            f.write('预测的结果为：{}\n'.format(result))
            print('该句子的单字正确率为：', rightNum / len(trueHanziList[i]), '\n')
            f.write('该句子的单字正确率为：{}\n'.format(rightNum / len(trueHanziList[i])))

        print('完全正确的句子个数：', rightSentence)
        print('字的正确率为：', rightWordNum / testWordNum)
        print('句子的正确率：', rightSentence / sentenceNum)
        f.write('完全正确的句子个数：{}\n'.format(rightSentence))
        f.write('字的正确率为：{}\n'.format(rightWordNum / testWordNum))
        f.write('句子的正确率：{}\n'.format(rightSentence / sentenceNum))

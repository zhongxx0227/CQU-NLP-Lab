'''
Author: XiangxinZhong
Date: 2021-11-05 21:50:02
LastEditors: XiangxinZhong
LastEditTime: 2021-11-07 14:24:48
Description: 主函数
'''
import PreocessData
import Compute
if __name__ == '__main__':
    PreocessData.getWordDict()
    transferList,LanchProb,IniStatusProb,pinyinDict,wordIndex,wordListS = PreocessData.getParameter()

    Compute.predHanzi(transferList,LanchProb,IniStatusProb,pinyinDict,wordIndex,wordListS)



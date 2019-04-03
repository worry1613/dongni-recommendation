# -*- coding: utf-8 -*-
# @创建时间 : 26/3/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

# 用户协同过滤算法类实现
# 经典版本,进化版本
# 参考网上内容以及《推荐系统实践》书内代码
import random

import math
import json
import pickle
from operator import itemgetter
import numpy as np
import pandas as pd
import datetime
import time
from copy import deepcopy, copy

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class userCF(object):
    def __init__(self, f,sep='::'):
        self.file = f
        self.df = pd.read_csv(self.file, sep=sep, header=None, usecols=[0, 1], names=['userid', 'itemid'],
                              engine='python')
        # alluserids 所有用户的id集合
        self.alluserids = pd.Series(self.df['userid']).unique()
        # allitemids 所有物品的id集合
        self.allitemids = pd.Series(self.df['itemid']).unique()
        self.W = dict()
        self.calOK = False
        # uanduitem  用户和用户的关系集合
        self.uanduitem = dict()
        # item_users 物品id对应的用户id集合表关系
        self.item_users = dict()
        # user_items 用户id对应的物品id集合表关系
        self.user_items = dict()

        # 每个用户的访问总量
        self.useritemcount = dict()
        self.test = dict()
        self.train = dict()

    def loaddat(self):
        logging.info('loaddat 开始')
        try:
            f = open(self.file+'.'+self.__class__.__name__+".train.dat", "rb")
            self.train = pickle.load(f)
            f.close()
            self.calOK = True
            self.user_items = deepcopy(self.train)
        except Exception as e:
            self.calOK = False
            logging.error(self.file+'.'+self.__class__.__name__+'.train.dat文件不存在')
            return self.calOK
        try:
            f = open(self.file+'.'+self.__class__.__name__+".test.dat", "rb")
            self.test = pickle.load(f)
            f.close()
            self.calOK = True
        except Exception as e:
            self.calOK = False
            logging.error(self.file+'.'+self.__class__.__name__+'.test.dat文件不存在')
            return self.calOK
        try:
            f = open(self.file+'.'+self.__class__.__name__+".item_users.dat", "rb")
            self.item_users = pickle.load(f)
            f.close()
            self.calOK = True
        except Exception as e:
            self.calOK = False
            logging.error(self.file+'.'+self.__class__.__name__+'.item_users.dat文件不存在')
            return self.calOK
        try:
            f = open(self.file+'.'+self.__class__.__name__+".useritemcount.dat", "rb")
            self.useritemcount = pickle.load(f)
            f.close()
            self.calOK = True
        except Exception as e:
            self.calOK = False
            logging.error(self.file+'.'+self.__class__.__name__+'.useritemcount.dat文件不存在')
            return self.calOK

        try:
            f = open(self.file+'.'+self.__class__.__name__+".W.dat", "rb")
            self.W = pickle.load(f)
            f.close()
            self.calOK = True
        except Exception as e:
            self.calOK = False
            logging.error(self.file+'.'+self.__class__.__name__+".W.dat")
            return self.calOK
        try:
            f = open(self.file+'.'+self.__class__.__name__+".uanduitem.dat" , "rb")
            self.uanduitem = pickle.load(f)
            f.close()
            self.calOK = True
        except Exception as e:
            self.calOK = False
            logging.error(self.file+'.'+self.__class__.__name__+".uanduitem.dat")
            return self.calOK
        return self.calOK

    def savedat(self):
        logging.info('savedat 开始')
        try:
            f = open(self.file + '.' + self.__class__.__name__ + ".train.dat", "wb")
            pickle.dump(self.train, f)
            f.close()
        except Exception as e:
            logging.error(self.file + '.' + self.__class__.__name__ + '.train.dat保存文件出错')

        try:
            f = open(self.file + '.' + self.__class__.__name__ + ".test.dat", "wb")
            pickle.dump(self.test, f)
            f.close()
        except Exception as e:
            logging.error(self.file + '.' + self.__class__.__name__ + '.test.dat保存文件出错')
        try:
            f = open(self.file + '.' + self.__class__.__name__ + ".item_users.dat", "wb")
            pickle.dump(self.item_users, f)
            f.close()
        except Exception as e:
            logging.error(self.file + '.' + self.__class__.__name__ + '.item_users.dat保存文件出错')
        try:
            f = open(self.file + '.' + self.__class__.__name__ + ".useritemcount.dat", "wb")
            pickle.dump(self.useritemcount, f)
            f.close()
        except Exception as e:
            logging.error(self.file + '.' + self.__class__.__name__ + '.useritemcount.dat保存文件出错')
        try:
            f = open(self.file + '.' + self.__class__.__name__ + ".W.dat", "wb")
            pickle.dump(self.W, f)
            f.close()
        except Exception as e:
            logging.error(self.file + '.' + self.__class__.__name__ + '.W.dat文件不存在')
        try:
            f = open(self.file + '.' + self.__class__.__name__ + ".uanduitem.dat", "wb")
            pickle.dump(self.uanduitem, f)
            f.close()
        except Exception as e:
            logging.error(self.file + '.' + self.__class__.__name__ + ".uanduitem.dat")

    def splitdata(self, M, key):
        """把数据切成训练集和测试集
        :param M:  数据将分成M份
        :param key:  选取第key份数据做为测试数据
        :return:
        """
        logging.info('开始切分训练，测试数据集 %d:%d' % (M-key, key))
        if self.calOK is False:
            random.seed(int(time.time()))
            for row in self.df.itertuples():
                if random.randint(0, M) == key:
                    self.test.setdefault(row[1], set())
                    self.test[row[1]].add(row[2])
                else:
                    self.train.setdefault(row[1], set())
                    self.train[row[1]].add(row[2])
                    self.item_users.setdefault(row[2], set())
                    self.item_users[row[2]].add(row[1])

            for k, v in self.train.items():
                self.useritemcount.setdefault(k, len(v))
            self.user_items = deepcopy(self.train)
        logging.info('切分训练，测试数据集完毕 ')

    # t  算法种类
    # 1 -- 传统算法  2 -- 改进算法，性能提高10%-15%
    def fit(self, t=2):
        # 算法分拆成2个函数，方便复用
        if self.calOK is False:
            logging.info('算法开始 %s ' % (str(datetime.datetime.now()),))
            self._fit(t)
            self._fitW()
            logging.info('算法结束 %s ' % (str(datetime.datetime.now()),))

    def _fit(self, t):
        '''
        计算 用户与用户矩阵
        :param t:    1 -- 传统算法  2 -- 改进算法，性能提高10%-15%
        :return:
        '''
        # ic=0
        if t == 1:
            # 最传统的算法
            for i, users in self.item_users.items():
                for u in users:
                    for v in users:
                        if u == v:
                            continue
                        self.uanduitem.setdefault(u, {})
                        self.uanduitem[u].setdefault(v, 0)
                        self.uanduitem[u][v] += 1
                        # ic+=1
                # print(ic,datetime.datetime.now())
        else:
            # 改进的算法，性能提高10%-15%
            for i, users in self.item_users.items():
                vs = copy(users)
                for u in users:
                    vs.remove(u)
                    for v in vs:
                        # ic += 1
                        self.uanduitem.setdefault(u, {})
                        self.uanduitem[u].setdefault(v, 0)
                        self.uanduitem[u][v] += 1
                        self.uanduitem.setdefault(v, {})
                        self.uanduitem[v].setdefault(u, 0)
                        self.uanduitem[v][u] += 1
                # print(ic,datetime.datetime.now())
        # print('last',ic)

    def _fitW(self):
        '''
        计算W矩阵
        :return:
        '''
        for u, ru in self.uanduitem.items():
            for v, cuv in ru.items():
                self.W.setdefault(u, {})
                self.W[u].setdefault(v, cuv / math.sqrt(self.useritemcount[u] * self.useritemcount[v]))

    def recommend(self, user, n=20, k=10):
        '''
        推荐
        :param user:  用户
        :param k:     取近邻数
        :param n:     推荐结果数
        :return:
        '''
        rank = dict()
        rvi = 1.0
        interacted_items = self.user_items[user]
        if user in self.W.keys():
            for v, wuv in sorted(self.W[user].items(), key=itemgetter(1), reverse=True)[0:k]:
                for i in self.user_items[v]:
                    if i in interacted_items:
                        # we should filter items user interacted before
                        continue
                    rank.setdefault(i, 0)
                    rank[i] += wuv * rvi

            ret = sorted(rank.items(), key=itemgetter(1), reverse=True)
            return ret[:n]
        else:
            return []

    '''
    评测函数
    '''
    def RecallandPrecision(self, N, K):
        """ 计算推荐结果的召回率,准确率
            @param N     推荐结果的数目
            @param K     选取近邻的数目
        """
        hit = 0
        n_recall = 0
        n_precision = 0
        for user in self.train.keys():
            if user in self.test:
                tu = self.test[user]
                rank = self.recommend(user, N, K)
                for item, pui in rank:
                    if item in tu:
                        hit += 1
                n_recall += len(tu)
                n_precision += N
        # print(hit)
        # print(n_recall, n_precision)
        return hit / (n_recall * 1.0), hit / (n_precision * 1.0)

    def Coverage(self, N, K):
        """ 计算推荐结果的覆盖率
            @param N     推荐结果的数目
            @param K     选取近邻的数目
        """
        recommned_items = set()
        all_items = set()

        for user in self.train.keys():
            for item in self.train[user]:
                all_items.add(item)

            rank = self.recommend(user, N, K)
            for item, pui in rank:
                recommned_items.add(item)

        # print('len: ', len(recommned_items), 'all_items:', len(all_items))
        return len(recommned_items) / (len(all_items) * 1.0)

    def Popularity(self, N, K):
        """ 计算推荐结果的新颖度(流行度)
            @param N     推荐结果的数目
            @param K     选取近邻的数目
        """
        item_popularity = dict()
        for user, items in self.train.items():
            for item in items:
                if item not in item_popularity:
                    item_popularity[item] = 0
                item_popularity[item] += 1

        ret = 0
        n = 0
        for user in self.train.keys():
            rank = self.recommend(user, N, K)
            for item, pui in rank:
                ret += math.log(1 + item_popularity[item])
                n += 1
        ret /= n * 1.0
        return ret


# 用户协同过滤进化版，对热门产品进入惩罚
class userCFIIF(userCF):
    #
    def _fit(self, t):
        # ic=0
        if t == 1:
            # 最传统的算法
            for i, users in self.item_users.items():
                userc = len(users)
                for u in users:
                    for v in users:
                        if u == v:
                            continue
                        self.uanduitem.setdefault(u, {})
                        self.uanduitem[u].setdefault(v, 0)
                        self.uanduitem[u][v] += 1 / math.log(1 + userc)
                        # ic+=1
                # print(ic,datetime.datetime.now())
        else:
            # 改进的算法，性能提高10%-15%
            for i, users in self.item_users.items():
                userc = len(users)
                vs = copy(users)
                for u in users:
                    vs.remove(u)
                    for v in vs:
                        # ic += 1
                        self.uanduitem.setdefault(u, {})
                        self.uanduitem[u].setdefault(v, 0)
                        self.uanduitem[u][v] += 1 / math.log(1 + userc)
                        self.uanduitem.setdefault(v, {})
                        self.uanduitem[v].setdefault(u, 0)
                        self.uanduitem[v][u] += 1 / math.log(1 + userc)
                # print(ic,datetime.datetime.now())
        # print('last',ic)


if __name__ == '__main__':
    """
2019-04-03 23:56:18,379 : INFO : loaddat 开始
2019-04-03 23:57:15,043 : INFO : userCF: K:   5, 召回率: 12.1880% ,准确率: 20.5700% ,流行度: 4.4797, 覆盖率: 95.1891% 
2019-04-03 23:57:25,511 : INFO : userCF: K:  10, 召回率: 12.0073% ,准确率: 20.2650% ,流行度: 4.4887, 覆盖率: 90.5218% 
2019-04-03 23:57:41,661 : INFO : userCF: K:  20, 召回率: 12.0858% ,准确率: 20.3975% ,流行度: 4.4957, 覆盖率: 83.0780% 
2019-04-03 23:58:04,359 : INFO : userCF: K:  30, 召回率: 12.2384% ,准确率: 20.6550% ,流行度: 4.5028, 覆盖率: 76.9986% 
2019-04-03 23:58:32,676 : INFO : userCF: K:  40, 召回率: 12.1332% ,准确率: 20.4775% ,流行度: 4.5105, 覆盖率: 71.7808% 
2019-04-03 23:59:24,328 : INFO : userCF: K:  80, 召回率: 12.3065% ,准确率: 20.7700% ,流行度: 4.5339, 覆盖率: 54.5476% 
2019-04-04 00:01:11,291 : INFO : userCF: K: 160, 召回率: 12.1924% ,准确率: 20.5775% ,流行度: 4.6945, 覆盖率: 44.9258% 
2019-04-04 00:01:16,453 : INFO : loaddat 开始
2019-04-04 00:02:24,677 : INFO : userCFIIF: K:   5, 召回率: 11.9846% ,准确率: 20.0975% ,流行度: 4.4748, 覆盖率: 95.4752% 
2019-04-04 00:02:35,687 : INFO : userCFIIF: K:  10, 召回率: 12.0457% ,准确率: 20.2000% ,流行度: 4.4816, 覆盖率: 91.3096% 
2019-04-04 00:02:53,590 : INFO : userCFIIF: K:  20, 召回率: 12.0889% ,准确率: 20.2725% ,流行度: 4.4924, 覆盖率: 83.6964% 
2019-04-04 00:03:16,974 : INFO : userCFIIF: K:  30, 召回率: 11.9890% ,准确率: 20.1050% ,流行度: 4.5043, 覆盖率: 76.2748% 
2019-04-04 00:03:45,327 : INFO : userCFIIF: K:  40, 召回率: 11.9950% ,准确率: 20.1150% ,流行度: 4.5121, 覆盖率: 70.0742% 
2019-04-04 00:04:35,538 : INFO : userCFIIF: K:  80, 召回率: 11.9175% ,准确率: 19.9850% ,流行度: 4.5362, 覆盖率: 54.0101% 
2019-04-04 00:06:31,769 : INFO : userCFIIF: K: 160, 召回率: 12.0993% ,准确率: 20.2900% ,流行度: 4.6929, 覆盖率: 44.7450% 
2019-04-04 00:06:33,101 : INFO : loaddat 开始
2019-04-04 00:07:06,764 : INFO : userCF: K:   5, 召回率: 14.7879% ,准确率: 12.3445% ,流行度: 4.4152, 覆盖率: 12.5477% 
2019-04-04 00:07:11,261 : INFO : userCF: K:  10, 召回率: 16.5775% ,准确率: 13.8384% ,流行度: 4.6904, 覆盖率: 8.5434% 
2019-04-04 00:07:17,653 : INFO : userCF: K:  20, 召回率: 17.2207% ,准确率: 14.3753% ,流行度: 4.8990, 覆盖率: 5.8251% 
2019-04-04 00:07:25,828 : INFO : userCF: K:  30, 召回率: 17.1825% ,准确率: 14.3434% ,流行度: 4.9947, 覆盖率: 4.7619% 
2019-04-04 00:07:34,989 : INFO : userCF: K:  40, 召回率: 17.1252% ,准确率: 14.2956% ,流行度: 5.0580, 覆盖率: 4.0871% 
2019-04-04 00:07:50,470 : INFO : userCF: K:  80, 召回率: 16.4310% ,准确率: 13.7161% ,流行度: 5.1890, 覆盖率: 3.0876% 
2019-04-04 00:08:18,304 : INFO : userCF: K: 160, 召回率: 15.5139% ,准确率: 12.9506% ,流行度: 5.3063, 覆盖率: 2.4064% 
    """
    M = 5
    key = 1
    N = 10
    K = [5,10,20,30,40,80,160]

    ucf = userCF('./data/views.dat')
    lt = ucf.loaddat()
    if not lt:
        ucf.splitdata(M, key)
        ucf.fit()
        ucf.savedat()
    for k in K:
        recall, precision = ucf.RecallandPrecision(N, k)
        popularity = ucf.Popularity(N, k)
        coverage = ucf.Coverage(N, k)

        logging.info('userCF: K: %3d, 召回率: %2.4f%% ,准确率: %2.4f%% ,流行度: %2.4f, 覆盖率: %2.4f%% ' %
              (k, recall*100, precision*100, popularity, coverage*100))

    ucfiif = userCFIIF('./data/views.dat')
    if not ucfiif.loaddat():
        ucfiif.splitdata(M, key)
        ucfiif.fit()
        ucfiif.savedat()
    for k in K:
        recall, precision = ucfiif.RecallandPrecision(N, k)
        popularity = ucfiif.Popularity(N, k)
        coverage = ucfiif.Coverage(N, k)

        logging.info('userCFIIF: K: %3d, 召回率: %2.4f%% ,准确率: %2.4f%% ,流行度: %2.4f, 覆盖率: %2.4f%% ' %
              (k, recall*100, precision*100, popularity, coverage*100))

    ucfartist = userCF('./data/user_artists.dat',sep='\t')
    if not ucfartist.loaddat():
        ucfartist.splitdata(M, key)
        ucfartist.fit()
        ucfartist.savedat()
    for k in K:
        recall, precision = ucfartist.RecallandPrecision(N, k)
        popularity = ucfartist.Popularity(N, k)
        coverage = ucfartist.Coverage(N, k)

        logging.info('userCF: K: %3d, 召回率: %2.4f%% ,准确率: %2.4f%% ,流行度: %2.4f, 覆盖率: %2.4f%% ' %
              (k, recall * 100, precision * 100, popularity, coverage * 100))

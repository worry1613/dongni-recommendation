# -*- coding: utf-8 -*-
# @创建时间 : 26/3/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

# 参考网上内容以及《推荐系统实践》书内代码
import random
from optparse import OptionParser

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

# 兴趣因子数，降维后的特征数
F = 10

class SVD(object):
    # Funk-SVD
    def __init__(self, fi, sep='::', f=F):
        """
        :param fi: 日志文件
        :param sep: 分隔符
        :param f: 兴趣因子数，降维的特征数，默认10
        """
        self.P = {}     #P矩阵
        self.Q = {}     #Q矩阵
        self.F = f
        self.file = fi
        self.df = pd.read_csv(self.file, sep=sep, header=None, usecols=[0, 1, 2, 3], names=['userid', 'itemid','rating','timestamp'],
                              engine='python')
        # users 所有用户的id集合
        self.users = pd.Series(self.df['userid']).unique()
        # items 所有物品的id集合
        self.items = pd.Series(self.df['itemid']).unique()
        for user in self.users:
            self.P[user] = [random.random() for i in range(F)]
        for item in self.items:
            self.Q[item] = [random.random() for i in range(F)]

    def predict(self,u,i):
        """

        :param u: user id
        :param i: item id
        :return:
        """
        return sum(self.P[u][f] * self.Q[i][f] for f in range(self.F))

    def recommend(self,u,i):
        return self.predict(u,i)

    # def loaddat(self):
    #     logging.info('loaddat 开始')
    #     try:
    #         f = open(self.file+'.'+self.__class__.__name__+".train.dat", "rb")
    #         self.train = pickle.load(f)
    #         f.close()
    #         self.calOK = True
    #         self.user_items = deepcopy(self.train)
    #     except Exception as e:
    #         self.calOK = False
    #         logging.error(self.file+'.'+self.__class__.__name__+'.train.dat文件不存在')
    #         return self.calOK
    #     try:
    #         f = open(self.file+'.'+self.__class__.__name__+".test.dat", "rb")
    #         self.test = pickle.load(f)
    #         f.close()
    #         self.calOK = True
    #     except Exception as e:
    #         self.calOK = False
    #         logging.error(self.file+'.'+self.__class__.__name__+'.test.dat文件不存在')
    #         return self.calOK
    #     try:
    #         f = open(self.file+'.'+self.__class__.__name__+".item_users.dat", "rb")
    #         self.item_users = pickle.load(f)
    #         f.close()
    #         self.calOK = True
    #     except Exception as e:
    #         self.calOK = False
    #         logging.error(self.file+'.'+self.__class__.__name__+'.item_users.dat文件不存在')
    #         return self.calOK
    #     try:
    #         f = open(self.file+'.'+self.__class__.__name__+".useritemcount.dat", "rb")
    #         self.useritemcount = pickle.load(f)
    #         f.close()
    #         self.calOK = True
    #     except Exception as e:
    #         self.calOK = False
    #         logging.error(self.file+'.'+self.__class__.__name__+'.useritemcount.dat文件不存在')
    #         return self.calOK
    #
    #     try:
    #         f = open(self.file+'.'+self.__class__.__name__+".W.dat", "rb")
    #         self.W = pickle.load(f)
    #         f.close()
    #         self.calOK = True
    #     except Exception as e:
    #         self.calOK = False
    #         logging.error(self.file+'.'+self.__class__.__name__+".W.dat")
    #         return self.calOK
    #     try:
    #         f = open(self.file+'.'+self.__class__.__name__+".uanduitem.dat" , "rb")
    #         self.uanduitem = pickle.load(f)
    #         f.close()
    #         self.calOK = True
    #     except Exception as e:
    #         self.calOK = False
    #         logging.error(self.file+'.'+self.__class__.__name__+".uanduitem.dat")
    #         return self.calOK
    #     return self.calOK

    # def savedat(self):
    #     logging.info('savedat 开始')
    #     try:
    #         f = open(self.file + '.' + self.__class__.__name__ + ".train.dat", "wb")
    #         pickle.dump(self.train, f)
    #         f.close()
    #     except Exception as e:
    #         logging.error(self.file + '.' + self.__class__.__name__ + '.train.dat保存文件出错')
    #
    #     try:
    #         f = open(self.file + '.' + self.__class__.__name__ + ".test.dat", "wb")
    #         pickle.dump(self.test, f)
    #         f.close()
    #     except Exception as e:
    #         logging.error(self.file + '.' + self.__class__.__name__ + '.test.dat保存文件出错')
    #     try:
    #         f = open(self.file + '.' + self.__class__.__name__ + ".item_users.dat", "wb")
    #         pickle.dump(self.item_users, f)
    #         f.close()
    #     except Exception as e:
    #         logging.error(self.file + '.' + self.__class__.__name__ + '.item_users.dat保存文件出错')
    #     try:
    #         f = open(self.file + '.' + self.__class__.__name__ + ".useritemcount.dat", "wb")
    #         pickle.dump(self.useritemcount, f)
    #         f.close()
    #     except Exception as e:
    #         logging.error(self.file + '.' + self.__class__.__name__ + '.useritemcount.dat保存文件出错')
    #     try:
    #         f = open(self.file + '.' + self.__class__.__name__ + ".W.dat", "wb")
    #         pickle.dump(self.W, f)
    #         f.close()
    #     except Exception as e:
    #         logging.error(self.file + '.' + self.__class__.__name__ + '.W.dat文件不存在')
    #     try:
    #         f = open(self.file + '.' + self.__class__.__name__ + ".uanduitem.dat", "wb")
    #         pickle.dump(self.uanduitem, f)
    #         f.close()
    #     except Exception as e:
    #         logging.error(self.file + '.' + self.__class__.__name__ + ".uanduitem.dat")

    # def splitdata(self,M,key):
    #     """把数据切成训练集和测试集
    #     :param M:  数据将分成M份
    #     :param key:  选取第key份数据做为测试数据
    #     :return:
    #     """
    #     logging.info('开始切分训练，测试数据集 %d:%d' % (M-key, key))
    #     if self.calOK is False:
    #         random.seed(int(time.time()))
    #         for row in self.df.itertuples():
    #             if random.randint(0, M) == key:
    #                 self.test.setdefault(row[1], set())
    #                 self.test[row[1]].add(row[2])
    #             else:
    #                 self.train.setdefault(row[1], set())
    #                 self.train[row[1]].add(row[2])
    #                 self.item_users.setdefault(row[2], set())
    #                 self.item_users[row[2]].add(row[1])
    #
    #         for k, v in self.train.items():
    #             self.useritemcount.setdefault(k, len(v))
    #         self.user_items = deepcopy(self.train)
    #     logging.info('切分训练，测试数据集完毕 ')

    def fit(self,t=2):
        # t  算法种类
        # 1 -- 传统算法  2 -- 改进算法，性能提高10%-15%
        # 算法分拆成2个函数，方便复用
        if self.calOK is False:
            logging.info('算法开始 %s ' % (str(datetime.datetime.now()),))
            self._fit(t)
            self._fitW()
            logging.info('算法结束 %s ' % (str(datetime.datetime.now()),))

    def _fit(self,t):
        pass

    def _fitW(self):
        pass

    def recommend(self,user,n=20,k=10):
        pass
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


# class userCF(CF):
#     def _fit(self, t):
#         '''
#         计算 用户与用户矩阵
#         :param t:    1 -- 传统算法  2 -- 改进算法，性能提高10%-15%
#         :return:
#         '''
#         # ic=0
#         if t == 1:
#             # 最传统的算法
#             for i, users in self.item_users.items():
#                 for u in users:
#                     for v in users:
#                         if u == v:
#                             continue
#                         self.uanduitem.setdefault(u, {})
#                         self.uanduitem[u].setdefault(v, 0)
#                         self.uanduitem[u][v] += 1
#                         # ic+=1
#                 # print(ic,datetime.datetime.now())
#         else:
#             # 改进的算法，性能提高10%-15%
#             for i, users in self.item_users.items():
#                 vs = copy(users)
#                 for u in users:
#                     vs.remove(u)
#                     for v in vs:
#                         # ic += 1
#                         self.uanduitem.setdefault(u, {})
#                         self.uanduitem[u].setdefault(v, 0)
#                         self.uanduitem[u][v] += 1
#                         self.uanduitem.setdefault(v, {})
#                         self.uanduitem[v].setdefault(u, 0)
#                         self.uanduitem[v][u] += 1
#                 # print(ic,datetime.datetime.now())
#         # print('last',ic)
#
#     def _fitW(self):
#         '''
#         计算W矩阵
#         :return:
#         '''
#         for u, ru in self.uanduitem.items():
#             for v, cuv in ru.items():
#                 self.W.setdefault(u, {})
#                 self.W[u].setdefault(v, cuv / math.sqrt(self.useritemcount[u] * self.useritemcount[v]))
#
#     def recommend(self, user, n=20, k=10):
#         '''
#         推荐
#         :param user:  用户
#         :param k:     取近邻数
#         :param n:     推荐结果数
#         :return:
#         '''
#         rank = dict()
#         rvi = 1.0
#         interacted_items = self.user_items[user]
#         if user in self.W.keys():
#             for v, wuv in sorted(self.W[user].items(), key=itemgetter(1), reverse=True)[0:k]:
#                 for i in self.user_items[v]:
#                     if i in interacted_items:
#                         # we should filter items user interacted before
#                         continue
#                     rank.setdefault(i, 0)
#                     rank[i] += wuv * rvi
#
#             ret = sorted(rank.items(), key=itemgetter(1), reverse=True)
#             return ret[:n]
#         else:
#             return []
#
# # 用户协同过滤进化版，对热门产品进入惩罚
# class userCFIIF(userCF):
#     #
#     def _fit(self, t):
#         # ic=0
#         if t == 1:
#             # 最传统的算法
#             for i, users in self.item_users.items():
#                 userc = len(users)
#                 for u in users:
#                     for v in users:
#                         if u == v:
#                             continue
#                         self.uanduitem.setdefault(u, {})
#                         self.uanduitem[u].setdefault(v, 0)
#                         self.uanduitem[u][v] += 1 / math.log(1 + userc)
#                         # ic+=1
#                 # print(ic,datetime.datetime.now())
#         else:
#             # 改进的算法，性能提高10%-15%
#             for i, users in self.item_users.items():
#                 userc = len(users)
#                 vs = copy(users)
#                 for u in users:
#                     vs.remove(u)
#                     for v in vs:
#                         # ic += 1
#                         self.uanduitem.setdefault(u, {})
#                         self.uanduitem[u].setdefault(v, 0)
#                         self.uanduitem[u][v] += 1 / math.log(1 + userc)
#                         self.uanduitem.setdefault(v, {})
#                         self.uanduitem[v].setdefault(u, 0)
#                         self.uanduitem[v][u] += 1 / math.log(1 + userc)
#                 # print(ic,datetime.datetime.now())
#         # print('last',ic)
#

if __name__ == '__main__':
    f = '..//..//dataset//movielens//ml-1m//ratings.dat'
    m = SVD(f)
    """
    """

    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='用户访问日志文件', dest='file')
    parser.add_option(      '--train', type=int, default=0.8,help='训练数据占比,默认0.8', dest='train')
    parser.add_option(      '--sep', type=str, default='::',help='日志文件分隔符,默认 ::', dest='sep')
    parser.add_option('-n',  type=int, default=10, help='推荐结果的数目,默认10', dest='n')
    parser.add_option('-k',  type=str, default='10',help='选取近邻的数目', dest='k')

    options, args = parser.parse_args()
    if not options.file:
        parser.print_help()
        exit()

    M = int(options.train//(1-options.train))
    key = 1
    N = options.n
    K = [int(kk) for kk in options.k.split(',')]
    sep = options.sep

    ucf = userCF(options.file,sep=sep)
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

    ucfiif = userCFIIF(options.file,sep=sep)
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
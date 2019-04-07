# -*- coding: utf-8 -*-
# @创建时间 : 17/10/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

# dimsum2算法，具体见下链接
# https://blog.twitter.com/engineering/en_us/a/2014/all-pairs-similarity-via-dimsum.html
#
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


class userCFv2(object):
    def __init__(self, f,threshold=0.1,sep='::'):
        self.threshold = threshold
        self.file = f
        self.df = pd.read_csv(self.file, sep=sep, header=None, usecols=[0, 1], names=['userid', 'itemid'],
                              engine='python')
        # alluserids 所有用户的id集合
        self.alluserids = pd.Series(self.df['userid']).unique()
        self.userdict = dict(zip(self.alluserids,range(len(self.alluserids))))
        # allitemids 所有物品的id集合
        self.allitemids = pd.Series(self.df['itemid']).unique()
        self.itemdict = dict(zip(self.allitemids,range(len(self.allitemids))))
        self.matrix_u2i = np.zeros((len(self.alluserids),len(self.allitemids)),dtype=np.int8)
        self.gama = math.sqrt(4 * math.log(len(self.allitemids)) / threshold)
        # 用户相似度矩阵
        self.W = np.zeros((len(self.alluserids),len(self.alluserids)),dtype=np.int8)

        # uanduitem  用户和用户的关系集合
        # self.uanduitem = dict()
        # item_users 物品id对应的用户id集合表关系
        # self.item_users = dict()
        # user_items 用户id对应的物品id集合表关系
        # self.user_items = dict()

        # 每个用户的访问总量
        self.useritemcount = dict()
        self.test = np.zeros((len(self.alluserids),len(self.allitemids)),dtype=np.int8)
        self.train = np.zeros((len(self.alluserids),len(self.allitemids)),dtype=np.int8)
        self.calOK = False

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
                    self.test[self.userdict[row[1]], self.itemdict[row[2]]] = 1
                else:
                    self.train[self.userdict[row[1]],self.itemdict[row[2]]] = 1
                    # self.item_users.setdefault(row[2], set())
                    # self.item_users[row[2]].add(row[1])

            # for k, v in self.train.items():
            #     self.useritemcount.setdefault(k, len(v))
            # self.user_items = deepcopy(self.train)
        logging.info('切分训练，测试数据集完毕 ')

    # t  算法种类
    # 1 -- 传统算法  2 -- 改进算法，性能提高10%-15%
    def fit(self):
        # 算法分拆成2个函数，方便复用
        if self.calOK is False:
            logging.info('算法开始 %s ' % (str(datetime.datetime.now()),))
            self._fit()
            self._fitW()
            logging.info('算法结束 %s ' % (str(datetime.datetime.now()),))

    def _fit(self):
        '''
        # 填充 用户与物品矩阵
        # :return:
        # '''
        # # ic=0
        # if t == 1:
        #     # 最传统的算法
        #     for i, users in self.item_users.items():
        #         for u in users:
        #             for v in users:
        #                 if u == v:
        #                     continue
        #                 self.uanduitem.setdefault(u, {})
        #                 self.uanduitem[u].setdefault(v, 0)
        #                 self.uanduitem[u][v] += 1
        #                 # ic+=1
        #         # print(ic,datetime.datetime.now())
        # else:
        #     # 改进的算法，性能提高10%-15%
        #     for i, users in self.item_users.items():
        #         vs = copy(users)
        #         for u in users:
        #             vs.remove(u)
        #             for v in vs:
        #                 # ic += 1
        #                 self.uanduitem.setdefault(u, {})
        #                 self.uanduitem[u].setdefault(v, 0)
        #                 self.uanduitem[u][v] += 1
        #                 self.uanduitem.setdefault(v, {})
        #                 self.uanduitem[v].setdefault(u, 0)
        #                 self.uanduitem[v][u] += 1
        #         # print(ic,datetime.datetime.now())
        # # print('last',ic)

    def _fitW(self):
        """
        计算用户相似矩阵,DIMSUMv2算法
        https://blog.twitter.com/engineering/en_us/a/2014/all-pairs-similarity-via-dimsum.html
        :return:
        """
        for r in range(self.train.shape[0]):
            logging.info('%d行 ' % (r,))
            for cj in range(self.train.shape[1]):
                alist = np.nonzero(self.train[:,cj])[0].tolist()
                ll = len(alist)
                # logging.info('%d行 %d列 %d个元素' % (r,cj,ll))
                lcj = min(1, self.gama / np.linalg.norm(self.train[:,cj]))
                tp = random.random()
                if tp < lcj:
                    for ck in range(cj+1,ll):
                        lck = min(1, self.gama / np.linalg.norm(self.train[:, ck]))
                        tp = random.random()
                        if tp < lck:
                            self.W[alist[cj],alist[ck]] += 0 \
                                if self.train[r,[alist[cj]]][0] ==0 or self.train[r,[alist[ck]]][0] ==0  \
                                else (self.train[r,[alist[cj]]][0]*self.train[r,[alist[ck]]][0]/
                                      (min(self.gama,lcj)*min(self.gama,lck)))
                            # logging.info('%d %d %d >> %f' %(r, alist[cj],alist[ck],self.W[alist[cj],alist[ck]]))
                        # logging.info('%d行 %d列 %d列' % (r, cj, ck))
        print('fitW end!!')
        # for u, ru in self.uanduitem.items():
        #     for v, cuv in ru.items():
        #         self.W.setdefault(u, {})
        #         self.W[u].setdefault(v, cuv / math.sqrt(self.useritemcount[u] * self.useritemcount[v]))

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
class userCFIIFv2(userCFv2):
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
    """
    M = 5
    key = 1
    N = 10
    K = [5,10,20,30,40,80,160]

    ucf = userCFv2('./data/views.dat')
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

    ucfiif = userCFIIFv2('./data/views.dat')
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

    ucfartist = userCFv2('./data/user_artists.dat',sep='\t')
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

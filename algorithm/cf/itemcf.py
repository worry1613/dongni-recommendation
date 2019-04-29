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
import pickle
import json
from operator import itemgetter
import numpy as np
import pandas as pd
import datetime
import time
from copy import deepcopy, copy

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class itemCF(object):
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
        # iandiuser  item和item的关系集合
        self.iandiuser = dict()
        # item_users 物品id对应的用户id集合表关系
        self.item_users = dict()
        # user_items 用户id对应的物品id集合表关系
        self.user_items = dict()
        # 每个item的访问用户总量
        self.itemusercount = dict()
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
        logging.info('开始切分训练，测试数据集 %d:%d' % (M - key, key))
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

            for k, v in self.item_users.items():
                self.itemusercount.setdefault(k, len(v))
            self.user_items = deepcopy(self.train)

        logging.info('切分训练，测试数据集完毕 ')

    # t  算法种类
    # 1 -- 传统算法  2 -- 改进算法，性能提高10%-15%
    def fit(self, t=2):
        # 算法分拆成2个函数，方便复用
        if self.calOK is False:
            logging.info('算法开始 %s ' % (str(datetime.datetime.now()),))
            self.__fit(t)
            self.__fitW()
            logging.info('算法结束 %s ' % (str(datetime.datetime.now()),))

    def __fit(self, t):
        if t == 1:
            # 最传统的算法
            for u, items in self.user_items.items():
                for i in items:
                    for j in items:
                        if i == j:
                            continue
                        self.iandiuser.setdefault(i, {})
                        self.iandiuser[i].setdefault(j, 0)
                        self.iandiuser[i][j] += 1
                        # ic+=1
                # print(ic,datetime.datetime.now())
        else:
            # 改进的算法，性能提高10%-15%
            for u, items in self.user_items.items():
                ii = copy(items)
                for i in items:
                    ii.remove(i)
                    for j in ii:
                        # ic += 1
                        self.iandiuser.setdefault(i, {})
                        self.iandiuser[i].setdefault(j, 0)
                        self.iandiuser[i][j] += 1
                        self.iandiuser.setdefault(j, {})
                        self.iandiuser[j].setdefault(i, 0)
                        self.iandiuser[j][i] += 1
                # print(ic,datetime.datetime.now())
        # print('last',ic)

    def __fitW(self):
        for i, ri in self.iandiuser.items():
            for j, cij in ri.items():
                self.W.setdefault(i, {})
                self.W[i].setdefault(j, cij / math.sqrt(self.itemusercount[i] * self.itemusercount[j]))

    # 数据归一化
    def __normalization(self):
        Wret = self.W.copy()
        for k, v in self.W.items():
            maxW = max([tv for tk, tv in v.items()])
            # print(v)
            for kk, vv in v.items():
                self.W[k][kk] = vv / maxW
            # print(self.W[k])

    def recommend(self, user, k=10, n=20):
        '''
        推荐
        :param user:  用户
        :param k:     取近邻数
        :param n:     推荐结果数
        :return:
        '''
        rank = dict()
        rui = 1.0
        ru = self.user_items[user]
        for i in ru:
            for j, wj in sorted(self.W[i].items(), key=itemgetter(1), reverse=True)[0:k]:
                if j in ru:
                    # we should filter items user interacted before
                    continue
                rank.setdefault(j, {})
                rank[j].setdefault('weight', 0)
                rank[j].setdefault('reason', {})
                rank[j]['reason'].setdefault(i, 0)
                rank[j]['weight'] += wj * rui
                rank[j]['reason'][i] = wj * rui

            ret = sorted(rank.items(), key=lambda d: d[1]['weight'], reverse=True)
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

# item协同过滤进化版，对热门产品进入惩罚
class itemCFIUF(itemCF):
    #
    def __fit(self, t):
        # ic=0
        if t == 1:
            # 最传统的算法
            for u, items in self.user_items.items():
                itemc = len(items)
                for i in items:
                    for j in items:
                        if i == j:
                            continue
                        self.iandiuser.setdefault(i, {})
                        self.iandiuser[i].setdefault(j, 0)
                        self.iandiuser[i][j] += 1 / math.log(1 + itemc)
                        # ic+=1
                # print(ic,datetime.datetime.now())
        else:
            # 改进的算法，性能提高10%-15%
            for u, items in self.user_items.items():
                itemc = len(items)
                ii = copy(items)
                for i in items:
                    ii.remove(i)
                    for j in ii:
                        # ic += 1
                        self.iandiuser.setdefault(i, {})
                        self.iandiuser[i].setdefault(j, 0)
                        self.iandiuser[i][j] += 1 / math.log(1 + itemc)
                        self.iandiuser.setdefault(j, {})
                        self.iandiuser[j].setdefault(i, 0)
                        self.iandiuser[j][i] += 1 / math.log(1 + itemc)
                # print(ic,datetime.datetime.now())


if __name__ == '__main__':
    M = 5
    key = 1
    N = 10
    K = [5, 10, 20, 30, 40, 80, 160]

    icf = itemCF('./data/views.dat')
    lt = icf.loaddat()
    if not lt:
        icf.splitdata(M, key)
        icf.fit()
        icf.savedat()
    for k in K:
        recall, precision = icf.RecallandPrecision(N, k)
        popularity = icf.Popularity(N, k)
        coverage = icf.Coverage(N, k)

        logging.info('userCF: K: %3d, 召回率: %2.4f%% ,准确率: %2.4f%% ,流行度: %2.4f, 覆盖率: %2.4f%% ' %
                     (k, recall * 100, precision * 100, popularity, coverage * 100))

    icfiuf = itemCFIUF('./data/views.dat')
    if not icfiuf.loaddat():
        icfiuf.splitdata(M, key)
        icfiuf.fit()
        icfiuf.savedat()
    for k in K:
        recall, precision = icfiuf.RecallandPrecision(N, k)
        popularity = icfiuf.Popularity(N, k)
        coverage = icfiuf.Coverage(N, k)

        logging.info('userCFIIF: K: %3d, 召回率: %2.4f%% ,准确率: %2.4f%% ,流行度: %2.4f, 覆盖率: %2.4f%% ' %
                     (k, recall * 100, precision * 100, popularity, coverage * 100))

    icfartist = itemCF('./data/user_artists.dat', sep='\t')
    if not icfartist.loaddat():
        icfartist.splitdata(M, key)
        icfartist.fit()
        icfartist.savedat()
    for k in K:
        recall, precision = icfartist.RecallandPrecision(N, k)
        popularity = icfartist.Popularity(N, k)
        coverage = icfartist.Coverage(N, k)

        logging.info('userCF: K: %3d, 召回率: %2.4f%% ,准确率: %2.4f%% ,流行度: %2.4f, 覆盖率: %2.4f%% ' %
                     (k, recall * 100, precision * 100, popularity, coverage * 100))


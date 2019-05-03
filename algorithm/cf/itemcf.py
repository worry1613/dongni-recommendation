# -*- coding: utf-8 -*-
# @创建时间 : 26/3/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

# 用户协同过滤算法类实现
# 经典版本,进化版本
# 参考网上内容以及《推荐系统实践》书内代码
import random
import time
from optparse import OptionParser

import math
from operator import itemgetter
from copy import deepcopy, copy

import logging

from usercf import CF

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class itemCF(CF):
    def __init__(self, f,sep='::'):
        CF.__init__(self,f,sep)
        # iandiuser  item和item的关系集合
        self.iandiuser = dict()
        # 每个item的访问用户总量
        self.itemusercount = dict()

    def _fit(self, t):
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
    def splitdata(self,M,key):
        # CF.splitdata(self,M,key)
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

    def _fitW(self):
        for i, ri in self.iandiuser.items():
            for j, cij in ri.items():
                self.W.setdefault(i, {})
                self.W[i].setdefault(j, cij / math.sqrt(self.itemusercount[i] * self.itemusercount[j]))

    # 数据归一化
    def _normalization(self):
        # Wret = self.W.copy()
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

# item协同过滤进化版，对热门产品进入惩罚
class itemCFIUF(itemCF):
    #
    def _fit(self, t):
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
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='用户访问日志文件', dest='file')
    parser.add_option('--train', type=int, default=0.8, help='训练数据占比,默认0.8', dest='train')
    parser.add_option('--sep', type=str, default='::', help='日志文件分隔符,默认 ::', dest='sep')
    parser.add_option('-n', type=int, default=10, help='推荐结果的数目,默认10', dest='n')
    parser.add_option('-k', type=str, default='10', help='选取近邻的数目', dest='k')

    options, args = parser.parse_args()
    if not options.file:
        parser.print_help()
        exit()

    M = int(options.train // (1 - options.train))
    key = 1
    N = options.n
    K = [int(kk) for kk in options.k.split(',')]
    sep = options.sep

    icf = itemCF(options.file,sep=sep)
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

    icfiuf = itemCFIUF(options.file,sep=sep)
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
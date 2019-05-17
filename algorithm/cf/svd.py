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
    """
    Funk-SVD
    """
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
        logging.info('开始读取日志文件，%s ' % (fi,))
        self.df = pd.read_csv(self.file, sep=sep, header=None, usecols=[0, 1, 2, 3], names=['userid', 'itemid','rating','timestamp'],
                              engine='python')
        logging.info('日志文件读取完成')
        # users 所有用户的id集合
        self.users = []
        # items 所有物品的id集合
        self.items = []
        self.test = {}
        self.train = {}

    def predict(self,u,i):
        """
        预测
        :param u: user id
        :param i: item id
        :return:
        """
        return sum(self.P[u][f] * self.Q[i][f] for f in range(self.F))

    def recommend(self,u,i):
        """
        推荐
        :param u:
        :param i:
        :return:
        """
        return self.predict(u,i)

    def loaddat(self,tr,te,P,Q):
        logging.info('loaddat 开始')
        calOK = 0
        try:
            f = open(tr, "rb")
            self.train = pickle.load(f)
            f.close()
            calOK = 1
        except Exception as e:
            calOK = 0
            logging.error('%s文件不存在' % (tr,))
            return calOK
        try:
            f = open(te, "rb")
            self.test = pickle.load(f)
            f.close()
            calOK = 1
        except Exception as e:
            calOK = 0
            logging.error('%s文件不存在' % (te,))
            return calOK
        try:
            f = open(P, "rb")
            self.P = pickle.load(f)
            f.close()
            calOK = 1
        except Exception as e:
            calOK = 0
            logging.error('%s文件不存在' % (P,))
            return calOK
        try:
            f = open(Q, "rb")
            self.Q = pickle.load(f)
            f.close()
            calOK = 0
        except Exception as e:
            calOK = 0
            logging.error('%s文件不存在' % (Q,))
            return calOK
        return calOK

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

    def splitdata(self,M=10,key=1):
        """把数据切成训练集和测试集
        :param M:  数据将分成M份
        :param key:  选取第key份数据做为测试数据
        :return:
        """
        logging.info('开始切分训练，测试数据集 %d:%d' % (M-key, key))
        testids = random.sample(list(self.df.index), len(self.df.index) * key // M)
        trainids = set(self.df.index) - set(testids)
        self.test = self.df.loc[testids]
        self.train = self.df.loc[trainids]
        logging.info('切分训练，测试数据集完毕,训练数据%d条，测试数据%d条。' % (len(trainids), len(testids)))

        self.users = pd.Series(self.train['userid']).unique()
        # items 所有物品的id集合
        self.items = pd.Series(self.train['itemid']).unique()
        logging.info('共%d条评分记录，用户共%d个，物品共%d个。' % (self.train.shape[0], len(self.users), len(self.items)))
        for user in self.users:
            self.P[user] = [random.random() / math.sqrt(F) for i in range(F)]
        for item in self.items:
            self.Q[item] = [random.random() / math.sqrt(F) for i in range(F)]


    def fit(self, N=10, alpha=.1, _lambda=.1, out=1):
        """
        训练
        :param N:    迭代次数，默认10
        :param alpha:   a 参数，默认
        :param _lambda: "入"参数 ,默认
        :param out: 是否保存模型文件 ,默认1，输出
        :return:
        """
        start = time.time()
        logging.info('开始训练，F: %d ,N:%d ,alpha:%.4f ,lambda:%.4f。' % (self.F, N, alpha,_lambda))
        for step in range(0, N):
            logging.info('=====N:%d' % (step,))
            for row in self.train.itertuples():
                u, i, rui = row[1],row[2],row[3]
                pui = self.predict(u, i)
                eui = rui - pui
                # logging.info('%d,%d,%f' % (u, i, rui))
                for f in range(0, self.F):
                    # logging.info('P[%d][%d]=%f,Q[%d][%d]=%f,rui=%1.1f,pui=%f,eui=%f ' % (u, f, self.P[u][f],
                    #                                                                        i, f, self.Q[i][f],
                    #                                                                        rui,pui,eui))
                    self.P[u][f] += alpha * (self.Q[i][f] * eui - _lambda * self.P[u][f])
                    self.Q[i][f] += alpha * (self.P[u][f] * eui - _lambda * self.Q[i][f])
            alpha *= 0.9
        logging.info('训练结束，共耗时%d秒。' % (time.time()-start))
        if out:
            #保存模型文件
            fpname = '%s.%s.P.%d_%d_%f_%f.dat' % (self.file, self.__class__.__name__, self.F, N, alpha, _lambda)
            fqname = '%s.%s.Q.%d_%d_%f_%f.dat' % (self.file, self.__class__.__name__, self.F, N, alpha, _lambda)
            ftrname = '%s.%s.Q.%d_%d_%f_%f.train.dat' % (self.file, self.__class__.__name__, self.F, N, alpha, _lambda)
            ftename = '%s.%s.Q.%d_%d_%f_%f.test.dat' % (self.file, self.__class__.__name__, self.F, N, alpha, _lambda)
            try:
                f = open(fpname, "wb")
                pickle.dump(self.P, f)
                f.close()
            except Exception as e:
                logging.error('%s 保存文件出错' % (fpname, ))
            try:
                f = open(fqname, "wb")
                pickle.dump(self.Q, f)
                f.close()
            except Exception as e:
                logging.error('%s 保存文件出错' % (fpname, ))
            try:
                f = open(ftrname, "wb")
                pickle.dump(self.train, f)
                f.close()
            except Exception as e:
                logging.error('%s 保存文件出错' % (ftrname, ))
            try:
                f = open(ftename, "wb")
                pickle.dump(self.test, f)
                f.close()
            except Exception as e:
                logging.error('%s 保存文件出错' % (ftename, ))
        # return list(self.P, self.Q)

    '''
    评测函数
    '''
    def rmse(self):
        """ 均方根误差RMSE
        """
        scores = []
        for row in self.test.itertuples():
            user,item,rating = row[1],row[2],row[3]
            scores.append(
                math.pow(rating - sum(self.P[user][f] * self.Q[item][f] for f in range(self.F)),
                         2))
        return math.sqrt(sum(scores)/len(scores))

if __name__ == '__main__':
    clsmap = {1:SVD,2:SVD,3:SVD,4:SVD,}
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='用户访问日志文件', dest='file')
    parser.add_option('--train', type=int, default=0.9, help='训练数据占比,默认0.9', dest='train')
    parser.add_option('--sep', type=str, default='::', help='日志文件分隔符,默认 ::', dest='sep')
    parser.add_option('-n', type=int, default=10, help='迭代次数，默认10', dest='n')
    parser.add_option('-a', type=float, default=.1, help='alpha参数默认.1', dest='a')
    parser.add_option('-l', type=float, default=.1, help='lambda参数默认.1', dest='l')
    parser.add_option('-m', type=int, default=1, help='模型类型，1-svd,2-biassvd,3-svd++,4-tsvd++,默认1', dest='m')
    parser.add_option('-f', type=int, default=10, help='兴趣因子数，降维后的特征数,默认10', dest='f')

    options, args = parser.parse_args()
    if not options.file:
        parser.print_help()
        exit()

    M = int(options.train // (1 - options.train))
    key = 1
    N = options.n
    alpha = options.a
    _lambda = options.l
    sep = options.sep
    fname = options.file
    f = options.f
    m = options.m

    # clsmap[m]
    svd = SVD(fname,sep,f)
    svd.splitdata(M+key,key=key)
    svd.fit(N=N,alpha=alpha,_lambda=_lambda)
    rmse = svd.rmse()
    logging.info('SVD: F: %3d, N: %2.4f ,alpha: %2.4f ,lambda: %2.4f, RMSE: %2.4f' %
                 (f, N, alpha, _lambda, rmse))
    exit()

    """
    """
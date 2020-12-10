# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

from optparse import OptionParser
from gensim import models
import logging
import numpy as np
from sklearn.cluster import KMeans

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Cluster(object):
    """
    聚类，用Kmeans算法实现
    数据模型现在只支持word2vector一种，用 numpy.mean实现文档向量
    """

    def __init__(self, fin=None, fmodel=None, clusters=300):
        self.clusters = clusters
        self.file = fin
        self.filemodel = fmodel
        self.result = None
        if (fin and fmodel) is not None:
            self.__process()

    def __process(self):
        mw2v = models.Word2Vec.load(self.filemodel)
        vsize = mw2v.vector_size

        # noinspection PyBroadException
        def wv(wvord):
            try:
                return mw2v.wv[wvord]
            except Exception:
                return np.zeros(vsize, dtype=int)

        lines = open(self.file).readlines()
        w2vm = [np.mean([wv(w) for w in line.split(' ')], axis=0) for line in lines]
        self.result = KMeans(n_clusters=self.clusters, random_state=0).fit(w2vm)

    def save(self, fout=None):
        try:
            f = open(fout, 'w')
            f.write(','.join(str(x) for x in self.result.labels_.tolist()))
            f.close()
        except IOError:
            logging.error(f'{fout}聚类结果文件保存错误请检查!')
            exit(0)
        logging.info(f'{fout}聚类结果文件保存成功!')


if __name__ == '__main__':
    '''
    python cluster.py -i ../../../data/新闻min_cw.txt 
                        -o ../../../data/新闻min_cluser5.txt 
                        -m ../../../model/w2v.300.新闻min.model
                        -n 200
    '''
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='分完词的语料库文件', dest='wordsfile')
    parser.add_option('-m', '--model', type=str, help='模型文件,只能是word2vector模型', dest='modelfile')
    parser.add_option('-o', '--out', type=str, help='存放聚类后结果的文件', dest='kmeansfile')
    parser.add_option('-n', '--clusters', type=int, default=20, help='聚类的簇数,默认20', dest='clusters')

    options, args = parser.parse_args()
    if not (options.wordsfile and options.modelfile and options.kmeansfile):
        parser.print_help()
        exit()

    logging.info(f'wordsfile={options.wordsfile}')
    logging.info(f'modelfile={options.modelfile}')
    logging.info(f'kmeansfile={options.kmeansfile}')
    logging.info(f'clusters={options.clusters}')
    kmean = Cluster(options.wordsfile, options.modelfile, options.clusters)
    kmean.save(options.kmeansfile)

# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

import os, sys

import gensim
from gensim import corpora, models

from NLP import nlp

reload(sys)
sys.setdefaultencoding('utf8')
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Topics(nlp):
    """
    话题模型实现
    """
    def __init__(self, fin=None, t=None, topcis=10):
        self.type = t
        self.model = None
        self.file = fin
        self.corpora_documents = []
        self.dictionary = None
        self.corpus = []
        self.corpus_result = []
        self.corpus_tfidf = None
        self.topics=topcis
        if fin is not None:
            self.__process()

    # @property
    # def dictionary(self):
    #     return self.__dictionary
    #
    # @dictionary.setter
    # def dictionary(self,d):
    #     self.__dictionary = d
    #
    # @property
    # def model(self):
    #     return self.__model
    #
    # @model.setter
    # def model(self,m):
    #     self.__model = m
    #
    # @property
    # def corpus(self):
    #     return self.__corpus
    #
    # @corpus.setter
    # def corpus(self,c):
    #     self.__corpus = c

    def load(self, fdict=None, fcorpus=None, fmodel=None):
        """
        装载保存好的模型文件
        :param fdict:   dictionary文件
        :param fcorpus: corpus文件
        :param fmodel:  model文件
        :return:
        """
        if fdict is not None:
            try:
                self.dictionary = corpora.Dictionary.load(fdict)
            except IOError:
                logging.error('dictionary %s 文件load错误!' % (fdict,))
                exit(0)
            logging.info('dictionary %s 文件load成功!' % (fdict,))

        if fcorpus is not None:
            try:
                self.corpus = corpora.MmCorpus(fcorpus)
            except IOError:
                logging.error('dictionary %s 文件load错误!' % (fcorpus,))
                exit(0)
            logging.info('dictionary %s 文件load成功!' % (fcorpus,))

    def __process(self):

        for line in open(self.file).readlines():
            self.corpora_documents.append(line.split(' '))

        logging.info('corpora is %d ' % (len(self.corpora_documents)))

        self.dictionary = corpora.Dictionary(self.corpora_documents)

        self.corpus = [self.dictionary.doc2bow(text) for text in self.corpora_documents]
        tfidf = models.TfidfModel(self.corpus)
        self.corpus_tfidf = tfidf[self.corpus]
        self.fit(topics=self.topics)

    def save(self, fdict=None, fcorpus=None, fmodel=None):
        if fdict is not None:
            try:
                self.dictionary.save(fdict)
            except IOError:
                logging.error('dictionary %s 写文件取错误请检查!' % (fdict,))
                exit(0)
            logging.info('dictionary %s 文件保存成功!' % (fdict,))
        if fcorpus is not None:
            try:
                corpora.MmCorpus.serialize(fcorpus, self.corpus)
            except IOError:
                logging.error('corpus %s 写文件取错误请检查!' % (fcorpus,))
                exit(0)
            logging.info('corpus %s 文件保存成功!' % (fcorpus,))
        if fmodel is not None:
            try:
                self.model.save(fmodel)
            except IOError:
                logging.error('model %s 写文件取错误请检查!' % (fmodel,))
                exit(0)
            logging.info('model %s 文件保存成功!' % (fmodel,))

    def fit(self, topics=10):
        pass


class Topics_lsi(Topics):
    """
    LSI话题模型实现
    """
    __type = 'LSI'

    def __init__(self, fin=None):
        super(Topics_lsi, self).__init__(fin=fin, t=self.__type)

    def load(self, fdict=None, fcorpus=None, fmodel=None):
        super(Topics_lsi, self).load(fdict=fdict, fcorpus=fcorpus, fmodel=None)

        if fmodel is not None:
            try:
                self.model = models.LsiModel.load(fmodel)
            except IOError:
                logging.error('model %s 文件load错误!' % (fmodel,))
                exit(0)
            logging.info('model %s 文件load成功!' % (fmodel,))

    def fit(self, topics=10):
        self.model = gensim.models.lsimodel.LsiModel(corpus=self.corpus,  id2word=self.dictionary, num_topics=topics)


class Topics_lda(Topics):
    """
    LDA话题模型实现
    """
    __type = 'LDA'

    def __init__(self,fin=None):
        super(Topics_lda, self).__init__(fin=fin, t=self.__type)

    def load(self,fdict=None, fcorpus=None, fmodel=None):
        super(Topics_lda, self).load(fdict=fdict, fcorpus=fcorpus, fmodel=None)

        if fmodel is not None:
            try:
                self.model = models.LdaModel.load(fmodel)
            except IOError:
                logging.error('model %s 文件load错误!' % (fmodel,))
                exit(0)
            logging.info('model %s 文件load成功!' % (fmodel,))

    def fit(self, topics=200):
        self.model = gensim.models.ldamodel.LdaModel(corpus=self.corpus,  id2word=self.dictionary, num_topics=topics)


if __name__ == '__main__':
    file_txt = '../../中文语料库/THUCNews/last_THUCNews_w2v.txt'

    # lsi = Topics_lsi(file_txt)
    lsi = Topics_lsi()
    fd = 'last_THUCNews.dict'
    fc = 'last_THUCNews.mm'
    fmlsi = 'last_THUCNews-' + lsi.type + '.model'

    bfd = os.path.exists(fd)
    bfc = os.path.exists(fc)
    bfm = os.path.exists(fmlsi)
    if bfd is True:
        if bfm is True:
            lsi.load(fdict=fd, fcorpus=fc, fmodel=fmlsi)
        else:
            lsi.load(fdict=fd, fcorpus=fc)
    else:
        lsi = Topics_lsi(file_txt)

    lsi.fit()

    if bfd is True:
        lsi.save(fdict=None,fcorpus=None,fmodel=fm)
    else:
        lsi.save(fd, fc, fm)

    lda = Topics_lda()
    fmlda = 'last_THUCNews-' + lda.type + '.model'
    bfmlda = os.path.exists(fmlda)
    if bfd is True:
        if bfmlda is True:
            lda.load(fdict=fd, fcorpus=fc, fmodel=fmlda)
        else:
            lda.load(fdict=fd, fcorpus=fc)
    else:
        lda = Topics_lda(file_txt)
    lda.fit()
    if bfd is True:
        lda.save(fdict=None,fcorpus=None,fmodel=fmlda)
    else:
        lda.save(fd, fc, fmlda)
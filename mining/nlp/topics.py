# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

import os, sys
from optparse import OptionParser

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
    最基础的tfidf
    """
    __type = 'TFIDF'

    def __init__(self, fin=None, t=None, topcis=10):
        self.type = t
        self.model = None
        self.file = fin
        self.corpora_documents = []
        self.dictionary = None
        self.corpus = []
        self.corpus_result = []
        self.corpus_tfidf = None
        self.topics = topcis
        if fin is not None:
            self.__process()

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

        self.corpora_documents = [line.strip().split(' ') for line in open(self.file).readlines()]

        logging.info('corpora is %d ' % (len(self.corpora_documents)))

        self.dictionary = corpora.Dictionary(self.corpora_documents)

        self.corpus = [self.dictionary.doc2bow(text) for text in self.corpora_documents]
        self.model = models.TfidfModel(self.corpus)
        self.corpus_tfidf = self.model[self.corpus]
        self.fit(topics=self.topics)

    def save(self, fdict=None, fcorpus=None, fmodel=None):
        if not fdict:
            fdict = self.file + '.dict'
        if not fcorpus:
            fcorpus = self.file + '.mm'
        if not fmodel:
            fmodel = self.file + '.' + self.__type
        try:
            self.dictionary.save(fdict)
        except IOError:
            logging.error('dictionary %s 写文件取错误请检查!' % (fdict,))
            exit(0)
        logging.info('dictionary %s 文件保存成功!' % (fdict,))
        try:
            corpora.MmCorpus.serialize(fcorpus, self.corpus)
        except IOError:
            logging.error('corpus %s 写文件取错误请检查!' % (fcorpus,))
            exit(0)
        logging.info('corpus %s 文件保存成功!' % (fcorpus,))
        try:
            self.model.save(fmodel)
        except IOError:
            logging.error('model %s 写文件取错误请检查!' % (fmodel,))
            exit(0)
        logging.info('model %s 文件保存成功!' % (fmodel,))

    def fit(self, topics=200):
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

    def fit(self, topics=200):
        self.model = gensim.models.lsimodel.LsiModel(corpus=self.corpus, id2word=self.dictionary, num_topics=topics)

    def save(self, fmodel=None):
        if not fmodel:
            fmodel = self.file + '.' + self.__type
        try:
            self.model.save(fmodel)
        except IOError:
            logging.error('model %s 写文件取错误请检查!' % (fmodel,))
            exit(0)
        logging.info('model %s 文件保存成功!' % (fmodel,))


class Topics_lda(Topics):
    """
    LDA话题模型实现
    """
    __type = 'LDA'

    def __init__(self, fin=None):
        super(Topics_lda, self).__init__(fin=fin, t=self.__type)

    def load(self, fdict=None, fcorpus=None, fmodel=None):
        super(Topics_lda, self).load(fdict=fdict, fcorpus=fcorpus, fmodel=None)

        if fmodel is not None:
            try:
                self.model = models.LdaModel.load(fmodel)
            except IOError:
                logging.error('model %s 文件load错误!' % (fmodel,))
                exit(0)
            logging.info('model %s 文件load成功!' % (fmodel,))

    def fit(self, topics=200):
        self.model = gensim.models.ldamodel.LdaModel(corpus=self.corpus, id2word=self.dictionary, num_topics=topics)

    def save(self, fmodel=None):
        if not fmodel:
            fmodel = self.file + '.' + self.__type
        try:
            self.model.save(fmodel)
        except IOError:
            logging.error('model %s 写文件取错误请检查!' % (fmodel,))
            exit(0)
        logging.info('model %s 文件保存成功!' % (fmodel,))


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='分完词的语料库文件', dest='wordsfile')
    parser.add_option('-t', '--type', type=int, help='模型种类,1-tfidf,2-lsi,3-lda', dest='modetype')
    parser.add_option('-d', '--modeldir', type=str, default='./', help='存放模型文件的目录,默认当前目录', dest='modeldir')
    parser.add_option('-l', '--loadmodetype', type=str, help='加载的模型种类,1-tfidf,2-lsi,3-lda', dest='loadmodeltype')

    options, args = parser.parse_args()
    if not (options.wordsfile or options.modetype):
        parser.print_help()
        exit()


    def tfidf():
        tfidf = Topics(options.wordsfile)
        tfidf.save()


    def lsi():
        lsi = Topics_lsi(options.wordsfile)
        lsi.save()


    def lda():
        lda = Topics_lda(options.wordsfile)
        lda.save()


    types = {1: tfidf, 2: lsi, 3: lda}
    operation = types[options.modetype]
    operation()

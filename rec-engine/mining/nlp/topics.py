# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

from optparse import OptionParser
import gensim
from gensim import corpora, models
import logging
import os.path

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Topics(object):
    """
    话题模型实现
    最基础的tfidf
    """
    __type = 'TFIDF'

    def __init__(self, fin=None, t=None, topcis=300):
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

    def save(self, path=None, fdict=None, fcorpus=None, fmodel=None):
        p,f =os.path.split(self.file)
        if not fdict:
            fdict = (path + f if path else self.file) + '.dict'
        if not fcorpus:
            fcorpus = (path + f if path else self.file) + '.mm'
        if not fmodel:
            fmodel = (path + f if path else self.file) + '.' + self.__type
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

    def fit(self, topics=300):
        self.model = gensim.models.lsimodel.LsiModel(corpus=self.corpus, id2word=self.dictionary, num_topics=topics)

    def save(self, path=None, fmodel=None):
        p, f = os.path.split(self.file)
        if not fmodel:
            fmodel = (path + f if path else self.file) + '.' + self.__type
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

    def fit(self, topics=300):
        self.model = gensim.models.ldamodel.LdaModel(corpus=self.corpus, id2word=self.dictionary, num_topics=topics)

    def save(self, path=None, fmodel=None):
        p, f = os.path.split(self.file)
        if not fmodel:
            fmodel = (path + f if path else self.file) + '.' + self.__type
        try:
            self.model.save(fmodel)
        except IOError:
            logging.error('model %s 写文件取错误请检查!' % (fmodel,))
            exit(0)
        logging.info('model %s 文件保存成功!' % (fmodel,))


if __name__ == '__main__':
    '''
    python topics.py -i ../../../data/新闻min_cw.txt -t 2 -d ../../../model
    '''
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='分完词的语料库文件', dest='wordsfile')
    parser.add_option('-t', '--type', type=int, help='模型种类,1-tfidf,2-lsi,3-lda', dest='modetype')
    parser.add_option('-d', '--modeldir', type=str, default='./', help='存放模型文件的目录,默认当前目录', dest='modeldir')

    options, args = parser.parse_args()
    if not (options.wordsfile or options.modetype):
        parser.print_help()
        exit()
    if options.modeldir[-1] is not '/':
        options.modeldir+='/'

    def tfidf():
        tfidf = Topics(options.wordsfile)
        tfidf.save(options.modeldir)

    def lsi():
        lsi = Topics_lsi(options.wordsfile)
        lsi.save(options.modeldir)

    def lda():
        lda = Topics_lda(options.wordsfile)
        lda.save(options.modeldir)

    types = {1: tfidf, 2: lsi, 3: lda}
    operation = types[options.modetype]
    logging.info(f'wordsfile={options.wordsfile}')
    logging.info(f'modetype={options.modetype}')
    logging.info(f'modeldir={options.modeldir}')
    operation()

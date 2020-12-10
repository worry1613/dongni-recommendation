# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

from optparse import OptionParser
import jieba
import jieba.analyse
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# stopd = './/stop.dict'
TFIDF = 1
TEXTRANK = 2

class Keywords():
    """
    提取关键词类，提取语料库的文本关键词
    用textrank算法提取
    """
    def __init__(self, fin, fout, keytype, keynum=5, userdict=None, stopdict=None):
        """
        :param fin: 语料库文件
        :param userdict: 自定义词典
        :param stopdict: 停用词典
        """
        self.fin = fin
        self.fout = fout
        self.keytype = keytype
        self.keynum = keynum
        self.result = []

        if userdict is not None:
            jieba.load_userdict(userdict)
        if stopdict is not None:
            jieba.analyse.set_stop_words(stopdict)

    def gen(self):
        """
        生成关键词
        :param fout:
        :return:
        """
        try:
            docs = open(self.fin)
        except IOError:
            print(self.fin, "文件读取错误请检查!")
            exit(0)

        lines = docs.readlines()
        logging.info('%d lines ======' % (len(lines),))
        if self.keytype == TFIDF:
            self.result = [jieba.analyse.extract_tags(line, topK=self.keynum, allowPOS=('ns', 'n'), withWeight=False) for
                           line in lines]
        else:
            self.result = [jieba.analyse.textrank(line, topK=self.keynum, allowPOS=('ns', 'n'), withWeight=False) for
                           line in lines]
        docs.close()
        logging.info('>>>>>>>>>>>>>')
        if fout:
            self.save(fout=fout)

    def save(self, fout):
        """
        生成的关键词的结果保存文件
        :param fout:
        :return:
        """
        try:
            f = open(fout, "w")
            f.write(''.join([" ".join(words) + "\n" for words in self.result]))
            f.close()
        except IOError:
            print(self.fout, "写文件取错误请检查!")
            exit(0)


if __name__ == '__main__':
    '''
    python keywords.py -i ../../../data/新闻min.txt -o ../../../data/新闻min_keywords.txt -s ../../../data/stop.dict -t 1 -n 5
    '''
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='语料库文件,每行一个doc', dest='corpusfile')
    parser.add_option('-o', '--out', type=str, help='关键词文件', dest='keywordsfile')
    parser.add_option('-w', '--word', type=str, help='自定义词典文件', dest='wordsdict')
    parser.add_option('-s', '--stop', type=str, help='停用词词典文件', dest='stopwords')
    parser.add_option('-t', '--type', type=int, default=1,help='生成关键词方法，1，TFIDF,2，TEXTRANK', dest='type')
    parser.add_option('-n', '--keynum', type=int, default=5,help='生成关键词个数', dest='keynumber')

    options, args = parser.parse_args()
    if not (options.corpusfile or options.keywordsfile):
        parser.print_help()
        exit()

    fin = options.corpusfile
    fout = options.keywordsfile
    fwordsdict = options.wordsdict if options.wordsdict is not None else None
    fstopwords = options.stopwords
    keynum = options.keynumber
    keytype = options.type

    logging.info(f'corpusfile={fin}')
    logging.info(f'keywordsfile={fout}')
    logging.info(f'wordsdict={fwordsdict}')
    logging.info(f'stopwords={fstopwords}')
    logging.info(f'type={keytype}')
    logging.info(f'keynumber={keynum}')

    t = Keywords(fin,fout,keytype,keynum=keynum,userdict=fwordsdict,stopdict=fstopwords)
    t.gen()

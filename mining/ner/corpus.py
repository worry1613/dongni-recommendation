# -*- coding: utf-8 -*-
# @创建时间 : 15/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
import getopt
import random

from config import get_config
from util import q_to_b
import os, sys

reload(sys)
sys.setdefaultencoding('utf8')
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Corpus:
    _maps = {u't': u'TIME',  # 时间
             u'nr': u'PER',  # 人
             u'ns': u'ORG',  # 组织
             u'nt': u'LOC'}  # 地点

    def __init__(self):
        self.lines = []

    def pre_process(self, fin):
        lines = self.load_corpus(fin)
        self.lines = []
        for line in lines:
            words = [word for word in q_to_b(line.decode('utf-8').strip()).split(' ')[1:] if word] # 全角转半角
            if len(words) <=0:
                continue
            new_words = self.process_time(words)  # 处理时间
            new_words = self.process_person(new_words)  # 处理人名
            new_words = self.process_org(new_words)                     #处理组织机构
            self.lines.append(new_words)
            # self.lines.append('  '.join(new_words))

        # self.save_corpus(data='\n'.join(self.lines).encode('utf-8'), file_path=fout)

    def save_corpus(self, file_path, data=None):
        """
        写语料
        """
        d = ''
        if data is None:
            d = '\n'.join(['  '.join(line) for line in self.lines]).encode('utf-8')

        f = open(file_path, 'w')
        f.write(d)
        f.close()

    def load_corpus(self, file_path):
        """
        读取语料
        """
        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def load_corpus_processed(self, file_path):
        """
        读取已经处理完毕语料
        """
        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        self.lines = [line.strip().decode('utf-8').split('  ') for line in lines]
        return

    def process_time(self, words):
        """
        处理时间
        """
        new_words = []
        temp = ''
        for k, word in enumerate(words):
            if '/t' in word:
                temp = temp[:-2] + word
            elif temp:
                new_words.append(temp)
                temp = ''
                new_words.append(word)
            else:
                new_words.append(word)
        if temp:
            new_words.append(temp)
        return new_words

    def process_person(self, words):
        """
        处理人名
        """
        new_words = []
        temp = ''
        lw = len(words)
        index = 0
        while index < lw:
            word = words[index]
            if '/nr' in word and index + 1 < lw and '/nr' in words[index + 1]:
                temp = word[:-3] + words[index + 1]
                new_words.append(temp)
                temp = ''
                index = index + 1
            else:
                new_words.append(word)
            index = index + 1
        return new_words

    def process_org(self, words):
        """
        处理组织机构名，[XX XX]
        """
        new_words = []
        temp = ''
        for k, word in enumerate(words):
            if '[' in word:
                temp = word.split('/')[0][1:]
            elif ']' in word and temp:
                w = word.split('/')[0]
                pos = word.split(']')[1]
                temp += w + '/' + pos
                new_words.append(temp)
                temp = ''
            elif temp:
                temp += word.split('/')[0]
            else:
                new_words.append(word)

        return new_words

    def process_seq(self, words=None,keyfunc=None):
        """
        标注数据
        """
        if words is None:
            words = self.lines
        words_seq =[[word.split('/')[0] for word in line] for line in words ]       #词
        pos_seq =[[word.split('/')[1] for word in line] for line in words ]        #词性
        tags_seq =[[self._maps.get(p) if p in self._maps else 'O' for p in pos] for pos in pos_seq ]        #词标签  ns,nt,t,nr

        return keyfunc(words_seq,pos_seq,tags_seq)
        # return self.tag_BIO_pos(words_seq,pos_seq,tags_seq)

    def split_train(self,ra=.7):
        """
        切分训练测试数据集
        :param ra: 训练数据比例 默认0.7
        :return:
        """
        l = len(self.lines)
        a = [i for i in range(l)]
        testl = random.sample(a,int(l*(1-ra)))
        train = []
        test = []
        for n in a:
            if n in testl:
                test.append(self.lines[n])
            else:
                train.append(self.lines[n])
        return train,test

    def tag_BIO_pos(self,wordsq,posq,tagsq):
        posq = [[[posq[index][i] for _ in range(len(wordsq[index][i]))]
                    for i in range(len(posq[index]))]
                   for index in range(len(posq))]
        tagsq = [[[self.tag_perform_bio(tagsq[index][i], w) for w in range(len(wordsq[index][i]))]
                     for i in range(len(tagsq[index]))] for index in range(len(tagsq))]
        wq = []
        tq = []
        pq = []
        posq = [[t for p in pos for t in p] for pos in posq]
        for pos in posq:
            pq.extend(pos+[''])
        tagsq = [[t for tag in tags for t in tag] for tags in tagsq]
        for tags in tagsq:
            tq.extend(tags+[''])
        wordsq = [[t for word in words for t in word] for words in wordsq]
        for words in wordsq:
            wq.extend(words+[''])
        lines = ['' if w==p==t=='' else '%s %s %s' % (w,p,t) for w,p,t in zip(wq,pq,tq)]
        return lines

    def tag_BIO(self,wordsq,posq,tagsq):
        tagsq = [[[self.tag_perform_bio(tagsq[index][i], w) for w in range(len(wordsq[index][i]))]
                     for i in range(len(tagsq[index]))] for index in range(len(tagsq))]
        wq = []
        tq = []
        tagsq = [[t for tag in tags for t in tag] for tags in tagsq]
        for tags in tagsq:
            tq.extend(tags+[''])
        wordsq = [[t for word in words for t in word] for words in wordsq]
        for words in wordsq:
            wq.extend(words+[''])
        lines = ['' if w==t=='' else '%s %s' % (w,t) for w,t in zip(wq,tq)]
        return lines

    def tag_perform_bio(self, tag, index):
        """
        标签使用BIO模式
        """
        if index == 0 and tag != u'O':
            return u'B-{}'.format(tag)
        elif tag != u'O':
            return u'I-{}'.format(tag)
        else:
            return tag

    def build_test(self,wordsq,keyfunc):
        return self.process_seq(words=wordsq,keyfunc=keyfunc)


if __name__ == '__main__':
    usage = """  
                corpus.py -r 训练数据集文件名 -t 测试数据集文件名 -m 模型文件名

                -i file        原始已经标注语料库文件名
                -o file        保存合成后处理完成语料库文件名
                -l file        合成后处理完成语料库文件名, 与i ,o 选项互斥
                -c num         循环生成训练测试数据集次数，用于交叉验证，默认1,最大10
                -r ratio       训练数据占比，默认0.7
                -f dataformat  训练数据集成生格式，默认bio,bio,bio_pos,bmewo,bmewo_pos

                生成已经标注后的语料库rmrb.txt, 生成一个训练测试数据集，测试数据占比0.7，数据集格式bio
                corpus.py  -i rmrb199801.txt  -o rmrb.txt 
                生成已经标注后的语料库rmrb.txt, 生成3个训练测试数据集，测试数据占比0.8，数据集格式bio
                corpus.py  -i rmrb199801.txt  -o rmrb.txt -c 3 -r 0.8  
                载入已经标注后的语料库rmrb.txt, 生成3个训练测试数据集，测试数据占比0.8，数据集格式bio
                corpus.py  -l rmrb.txt -c 3 -r 0.8  
                生成已经标注后的语料库rmrb.txt, 生成4个训练测试数据集，测试数据占比0.75，数据集格式bio_pos
                corpus.py  -i rmrb199801.txt  -o rmrb.txt -c 4 -r 0.75 -f bio_pos  
                生成已经标注后的语料库rmrb.txt, 生成2个训练测试数据集，测试数据占比0.85，数据集格式bmewo_pos
                corpus.py  -i rmrb199801.txt  -o rmrb.txt -c 2 -r 0.85 -f bmewo_pos  
                """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:l:c:r:f:h", ["input=", "output=", "load=", "ci=", "ratio=", "dataformat=","help="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()

    fin = None
    fout = None
    fload_formated = None
    tms = 1
    ratio = 0.7
    dformat = 'bio'
    for k, v in opts:
        if k in ('-i', '--input'):
            if v != '':
                fin = v
        elif k in ('-o', '--output'):
            fout = v
        elif k in ('-l', '--load'):
            fload_formated = v
        elif k in ('-c', '--ci'):
            tms = int(v)
        elif k in ('-r', '--ratio'):
            ratio = float(v)
        elif k in ('-f', '--dataformat'):
            dformat = v
        elif k in ('-h', '--help'):
            print(usage)
            exit()
    if fin and fload_formated:
        print(usage)
        exit()
    corpus = Corpus()
    fmap = {'bio': corpus.tag_BIO,
            'bio_pos': corpus.tag_BIO_pos,
            # 'bmewo': corpus.tag_BMEWO,
            # 'bmewo_pos': corpus.tag_BMEWO_pos
            }

    if fload_formated:
        corpus.load_corpus_processed(file_path=fload_formated)
    else:
        corpus.pre_process(fin)
        if fout:
            corpus.save_corpus(file_path=fout)

    def save(f, d):
        fin = open(f, 'w')
        fin.write('\n'.join(d))
        fin.close()

    ra = ratio
    for i in range(tms):
        tr,te = corpus.split_train(ra)
        tr_text = corpus.process_seq(tr,fmap.get(dformat))
        te_text = corpus.build_test(te,fmap.get(dformat))
        tr_file = 'model/train_%s_%s_%s.txt' % (dformat,str(ra),i)
        te_file = 'model/test_%s_%s_%s.txt' % (dformat,str(1-ra),i)
        save(tr_file,tr_text)
        save(te_file,te_text)

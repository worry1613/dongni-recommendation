# -*- coding: utf-8 -*-
# @创建时间 : 15/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
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
            words = q_to_b(line.decode('utf-8').strip()).split('  ')[1:]  # 全角转半角
            if len(words) <=0:
                continue
            new_words = self.process_time(words)  # 处理时间
            new_words = self.process_person(new_words)  # 处理人名
            new_words = self.process_org(new_words)                     #处理组织机构
            self.lines.append(new_words)
            # self.lines.append('  '.join(new_words))

        # self.save_corpus(data='\n'.join(self.lines).encode('utf-8'), file_path=fout)

    def save_corpus(self, data, file_path):
        """
        写语料
        """
        if data is None:
            data = '\n'.join(self.lines).encode('utf-8')
        f = open(file_path, 'w')
        f.write(data)
        f.close()

    def load_corpus(self, file_path):
        """
        读取语料
        """
        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        return lines

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

    def process_seq(self, words=None):
        """
        标注数据
        """
        new_words = []
        temp = ''
        words_seq =[[word.split('/')[0] for word in line] for line in self.lines ]       #词
        pos_seq =[[word.split('/')[1] for word in line] for line in self.lines ]        #词性
        tags_seq =[[ self._maps.get(p) if p in self._maps else 'O' for p in pos] for pos in pos_seq ]        #词标签  ns,nt,t,nr

        self.tag_BIO_pos(words_seq,pos_seq,tags_seq)

    def split_train(self,ra=.7):
        pass

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
            pq.extend(pos+[' '])
        tagsq = [[t for tag in tags for t in tag] for tags in tagsq]
        for tags in tagsq:
            tq.extend(tags+[' '])
        wordsq = [[t for word in words for t in word] for words in wordsq]
        for words in wordsq:
            wq.extend(words+[' '])
        lines = ['%s\t%s\t%s' % (w,p,t) for w,p,t in zip(wq,pq,tq)]
        return lines

    def tag_perform_bio(self, tag, index):
        """
        标签使用BIO模式
        """
        if index == 0 and tag != u'O':
            return u'B_{}'.format(tag)
        elif tag != u'O':
            return u'I_{}'.format(tag)
        else:
            return tag



if __name__ == '__main__':
    corpus = Corpus()
    corpus.pre_process('data/rmrb199801.txt')
    # corpus.save_corpus(file_path='data/rmrb.txt')
    corpus.process_seq()

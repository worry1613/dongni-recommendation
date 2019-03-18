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
        pass

    def pre_process(self, fin, fout):
        lines = self.load_corpus(fin)
        lines_new = []
        for line in lines:
            words = q_to_b(line.decode('utf-8').strip()).split('  ')[1:]  # 全角转半角
            new_words = self.process_time(words)  # 处理时间
            new_words = self.process_person(new_words)  # 处理人名
            new_words = self.process_org(new_words)                     #处理组织机构
            lines_new.append('  '.join(new_words))
        self.save_corpus(data='\n'.join(lines_new).encode('utf-8'), file_path=fout)

    def save_corpus(self, data, file_path):
        """
        写语料
        """
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


if __name__ == '__main__':
    corpus = Corpus()
    corpus.pre_process('data/rmrb199801.txt', 'data/rmrb.txt')

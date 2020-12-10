# -*- coding: utf-8 -*-
# @创建时间 : 15/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
from optparse import OptionParser
from time import time
from util import q_to_b
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

'''
处理人民日报1998年1月已标注数据集格式
'''


class RmrbReprogress():
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
            words = [word for word in q_to_b(line.strip()).split(' ')[1:] if word]  # 全角转半角
            if len(words) <= 0:
                continue
            new_words = self.process_time(words)  # 处理时间
            new_words = self.process_person(new_words)  # 处理人名
            new_words = self.process_org(new_words)  # 处理组织机构
            self.lines.append(new_words)

    def save_corpus(self, file_path):
        """
        写语料
        """
        d = '\n'.join(['  '.join(line) for line in self.lines])

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

    def process_time(self, words):
        """
        处理时间
        一九九八年/t  新年/t  =======  一九九八年新年/t
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
        江/nr  泽民/nr  =====  江泽民/nr
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
        [中国/ns  政府/n]nt  ===== 中国政府/nt
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
    '''
        python rmrbreprogress.py -i 词性标注@人民日报199801.txt  -o rmrb.test.txt 
        '''
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='原始已经标注语料库文件名,人民日报1998年1月已标注数据格式集', dest='infile')
    parser.add_option('-o', '--out', type=str, help='保存合成后处理完成语料库文件名', dest='outfile')

    options, args = parser.parse_args()
    if not (options.infile and options.outfile):
        parser.print_help()
        exit()

    fin = options.infile
    fout = options.outfile
    logging.info(f'infile={fin}')
    logging.info(f'outfile={fout}')
    start = time()
    logging.info(f'任务开始')
    Rmrb = RmrbReprogress()
    Rmrb.pre_process(fin)
    Rmrb.save_corpus(file_path=fout)
    logging.info(f'任务完成，耗时 {time() - start} 秒')

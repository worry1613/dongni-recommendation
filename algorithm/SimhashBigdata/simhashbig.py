# -*- coding: utf-8 -*-
# @创建时间 : 26/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
import getopt
import os
import pickle

from simhash import Simhash
import sys


class SimhashBig(object):
    def __init__(self):
        self.hm = 3
        self.values = [{}, {}, {}, {}]
        self.valuesC = 0
        self.mask = 0b1111111111111111

    def turn(self, v):
        r = [None, None, None, None]
        for i in range(4, 0, -1):
            r[i - 1] = v & self.mask
            v >>= 16
        r.reverse()
        return r

    def save(self, v):
        """
        保存simhash值v
        :param v:    数值
        :return:
        """
        value =v
        for i in range(4,0,-1):
            a = v & self.mask
            if a in self.values[i-1].keys():
                self.values[i-1][a].add(value)
            else:
                self.values[i-1][a] = {value}
            v >>= 16

    def find(self, v):
        """
        查找v，找到海明距离小于3的，true,没有找到false
        :param v:
        :return:   找到海明距离小于3的true,没有找到false
        """
        hm = 0
        vm = self.turn(v)
        rm = [None, None, None, None]
        for k, m in enumerate(vm):
            if m in self.values[k].keys():
                rm[k] = m
        hm_max = 0
        if rm.count(None) == len(rm):
            return False

        for kr, r in enumerate(rm):
            if r:
                for key in self.values[kr].keys():
                    hm_t = self.hamming_distance(vm[kr], key)
                    if hm_max <= hm_t:
                        hm_max = hm_t
                        if hm_max > self.hm:
                            return False
                hm += hm_max
                if hm > self.hm:
                    return False
        if hm <= self.hm:
            return True
        else:
            return False

    def hamming_distance(self, o, v):
        """
        计算o和v之间的海明距离
        :param o:
        :param v:
        :return:
        """
        x = (o ^ v) & ((1 << 128) - 1)
        tot = 0;
        while x:
            tot += 1
            x &= x - 1
        return tot

    def imports(self, fout):
        """
        装载values文件
        :param f:
        :return:
        """
        with open(fout, 'w') as f:
            pickle.dump(self.values, f)

    def exports(self, fin):
        """
        保存values到文件
        :param f:
        :return:
        """
        with open(fin) as f:
            self.values = pickle.load(f)


if __name__ == '__main__':
    usage = """  
                    simhashbig.py [-i 语料库文件 -d 语料库目录] [-o 海量数据simhash文件名 -m 海量数据simhash文件名 -a 海量数据simhash文件名]  

                    -i file       语料库文件,优先级高于语料库目录
                    -d dir        语料库目录
                    -o file       输出语料库文件数据simhash保存文件
                    -m file       语料库文件数据simhash保存文件，用于验证
                    -a file       语料库文件数据simhash保存文件，增量保存

                    语料库通用完simhash处理，输出simhashs.dat
                    simhashbig.py  -i rmrb199801.txt  -o simhashs.dat
                    使用simhashs.dat数据，验证语料库内容是否重复
                    simhashbig.py  -i rmrb199801.txt  -m simhashs.dat 
                    库料库目录输入，追加保存simhashs.dat
                    simhashbig.py  -d ../..  -a simhashs.dat 
                    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:d:o:m:a:h",
                                   ["input=", "dir=", "output=", "model=", "append=", "help="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()

    fin = None
    fout = None
    fmodel = None
    famodel = None
    dir = None
    for k, v in opts:
        if k in ('-i', '--input'):
            if v != '':
                fin = v
        elif k in ('-o', '--output'):
            fout = v
        elif k in ('-d', '--dir'):
            dir = v
        elif k in ('-m', '--model'):
            fmodel = v
        elif k in ('-a', '--append'):
            famodel = v
        elif k in ('-h', '--help'):
            print(usage)
            exit()
    if (fin or dir) is None and (fout or fmodel or famodel) is None:
        print(usage)
        exit()
    shb = SimhashBig()
    if fin:
        f = open(fin)
        lines = f.readlines()
        f.close()

        for l in range(len(lines)):
            s = Simhash(lines[l].decode('utf8'))
            if not shb.find(s.value):
                shb.save(s.value)
        shb.exports(fout)
    elif dir:
        files = os.listdir(dir)
        for file in files:
            f = open(file)
            lines = f.readlines()
            f.close()

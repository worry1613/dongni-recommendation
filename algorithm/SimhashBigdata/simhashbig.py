# -*- coding: utf-8 -*-
# @创建时间 : 26/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
import datetime
import getopt
import os
import pickle

from simhash import Simhash
import sys

# reload(sys)
# sys.setdefaultencoding('utf8')

class SimhashBig(object):
    def __init__(self):
        self.hm = 3
        self.values = [{}, {}, {}, {}, set()]
        # self.valuesC = 0
        self.mask = 0b1111111111111111

    def turn(self, v):
        r = [None, None, None, None]
        for i in range(4, 0, -1):
            r[i - 1] = v & self.mask
            v >>= 16
        # r.reverse()
        return r

    def save(self, v):
        """
        保存simhash值v
        :param v:    数值
        :return:
        """
        value = v
        for i in range(4, 0, -1):
            a = v & self.mask
            if a in self.values[i - 1].keys():
                self.values[i - 1][a].add(value)
            else:
                self.values[i - 1][a] = {value}
            v >>= 16
        self.values[-1].add(value)

    def delete(self, v):
        """
        删除simhash值v
        :param v:    数值
        :return:
        """
        vm = self.turn(v)
        rm = [None, None, None, None]
        # vl = set()
        for k, m in enumerate(vm):
            if m :
                self.values[k].remove(v)
        self.values[-1].remove(v)

    def find(self, v):
        """
        查找v，找到海明距离小于3的，true,没有找到false
        :param v:
        :return:   找到海明距离小于3的true,没有找到false
        """
        hm_t = 0
        vm = self.turn(v)
        keyspass = set()
        for k, m in enumerate(vm):
            if m in self.values[k].keys():
                values = self.values[k][m]
                if v in values:
                    return 1, 1
                for value in values:
                    if value not in keyspass:
                        hm_t = self.hamming_distance(v, value)
                        if hm_t <= self.hm:
                            return 1, len(values)
                keyspass |= set(values)
        return 0, len(keyspass)

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
            if tot >self.hm:
                return tot
        return tot

    def imports(self, fin):
        """
        装载values文件
        :param f:
        :return:
        """
        f = open(fin, 'rb')
        f.seek(0)
        self.values = pickle.load(f)
        f.close()

    def exports(self, fout):
        """
        保存values到文件
        :param f:
        :return:
        """
        fileout = open(fout, 'wb')
        pickle.dump(self.values, fileout, -1)
        fileout.close()


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

    def process(fins, fout, fmodel, famodel):
        if fmodel is not None:
            """
            用已有数据验证输入数据是否存在
            """
            shb.imports(fmodel)
            for fin in fins:
                f = open(fin)
                lines = f.readlines()[-10000:]
                f.close()
                print(fin)
                c = len(lines)
                tc = 0
                zc = 0
                start = datetime.datetime.now()
                for l in range(c):
                    s = Simhash(lines[l])
                    r = shb.find(s.value)
                    tc += r[0]
                    zc += r[1]
                    if l % 1000 == 0:
                        print(l,end=',')
                print('')
                end = datetime.datetime.now()
                print('共 ', c, '条数据，', tc, '找到，', c - tc, '没找到，共', zc, '循环查找，平均每次查找', zc / c, '循环，共耗时 ',
                      (end - start).total_seconds(), ' 秒')
        elif famodel is not None:
            """
            用输入数据追加到现在数据集上
            """
            shb.imports(famodel)
            for fin in fins:
                f = open(fin)
                lines = f.readlines()
                f.close()
                print(fin)
                start = datetime.datetime.now()
                c = 0
                for l in range(len(lines)):
                    s = Simhash(lines[l])
                    if not shb.find(s.value)[0]:
                        c += 1
                        shb.save(s.value)
                        if l %1000 == 0:
                            print(l)
                end = datetime.datetime.now()
                print('开始: ', start, ' 结束: ', end, '共', c, '数据， 共耗时 ', (end - start).total_seconds(), '秒')
                shb.exports(famodel)
        elif fout is not None:
            """
            用输入数据新建数据集合
            """
            for fin in fins:
                f = open(fin)
                lines = f.readlines()
                f.close()
                print(fin)
                start = datetime.datetime.now()
                c=0
                for l in range(len(lines)):
                    s = Simhash(lines[l])
                    if not shb.find(s.value)[0]:
                        c+=1
                        shb.save(s.value)
                        if l %1000 == 0:
                            print(l)
                end = datetime.datetime.now()
                print('开始: ', start, ' 结束: ', end, '共',c,'数据， 共耗时 ', (end - start).total_seconds(), '秒')
                shb.exports(fout)

    shb = SimhashBig()
    start = datetime.datetime.now()
    if fin:
        process([fin], fout, fmodel, famodel)
    elif dir:
        files = os.listdir(dir)
        files = [dir+f for f in files]
        process(files, fout, fmodel, famodel)
    end = datetime.datetime.now()
    print('开始: ',start, ' 结束: ', end, '共耗时 ',(end-start).total_seconds(),'秒')

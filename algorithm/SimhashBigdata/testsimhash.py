# -*- coding: utf-8 -*-
# @创建时间 : 28/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

# 随机生成海量64位数
import datetime
import pickle
import random

from simhash import Simhash

from simhashbig import SimhashBig


def random_seed(n=256):
    """
    生成n多个随机种子数
    """
    return set([int(round(random.random(), 19) * 10 ** 19) for _ in range(n ** 2 * 100)])


def save_result(fout, v):
    fileout = open(fout, 'wb')
    pickle.dump(v, fileout, -1)
    fileout.close()


def load_result(fin):
    """
    装载values
    """
    f = open(fin, 'rb')
    f.seek(0)
    v = pickle.load(f)
    f.close()
    return v


if __name__ == '__main__':

    shb = SimhashBig()
    fin = 'sohu.simhash'
    shb.imports(fin)
    seeds=[]
    for i in shb.values[-1]:
        seeds.extend([i>>r for r in range(1,8)])
    ff = list(set(seeds)-shb.values[-1])

    c = 0
    zc = 0
    tf = set()
    result = {0: [0, 0], 1: [0, 0]}
    start = datetime.datetime.now()
    for z in ff:
        r = shb.find(z)
        result[r[0]][0] += 1
        result[r[0]][1] += r[1]
        if r[0] == 0:
            tf.add(z)
    end = datetime.datetime.now()
    ct = len(ff)
    print('共 ', ct, '条数据，', result[1][0], '找到，', result[1][1], '循环查找，', result[0][0], '没找到，', result[0][1],
          '循环查找，单次',0 if result[0][0] == 0 else result[0][1]/result[0][0],'循环查找, 共耗时 ',(end - start).total_seconds(), ' 秒')
    if len(tf):
        for f in tf:
            shb.save(f)
        shb.exports('sohu.simhash')



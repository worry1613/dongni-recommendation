# -*- coding: UTF-8 -*-
"""
    userlog.py
    write by worry1613
    2015-10-01
    处理用户行为日志，生成数据并保存。

"""
import math
import json
from configparser import ConfigParser
from operator import itemgetter
import getopt
import numpy as np
import pandas as pd
import datetime
import sys
import redis        #一定要安装hiredis不然操作redis会很慢

host = 0
port = 0
user = 0
pwd  = 0

def savetoredis(a):
    """
    保存到redis
    :param a:  user_itme数组
    :param c:  redis连接
    :param t:  act行为日志,rating打分日志
    :return:   null
    """
    rc = redis.StrictRedis(host=host, port=int(port))
    p = rc.pipeline()
    for log in a:
        p.set('%s:act%d:u%d:i%d'%(datetime.datetime.today().date().strftime('%Y-%m-%d'),log[2],log[0],log[1]),1)
        p.lpush('%s:act%d:u%d'%(datetime.datetime.today().date().strftime('%Y-%m-%d'),log[2],log[0]),log[1])
        p.lpush('%s:act%d:i%d'%(datetime.datetime.today().date().strftime('%Y-%m-%d'),log[2],log[1]),log[0])
        # p.set('%s:act%d:u%d:i%d'%(datetime.datetime.today().date().strftime('%Y-%m-%d'),log[2],log[0],log[1]),1)
    p.execute()
    return 'OK'

def savetohbase(a,c,t):
    """
    保存到hbase
    :param a:  user_itme数组
    :param c:  hbase连接
    :param t:  act行为日志,rating打分日志
    :return:   null
    """
    return

def process_action(f,o=None,t=None,c=savetoredis):
    """
    处理用户行为日志
    :param f:  日志文件
    :param o:  输出文件
    :param t:  输出类型,file,redis,hbase
    :param c:  输出函数
    :return:
    日志格式
    user_id::item_id::action_type::time
    使用ml-1m数据集中的ratings.dat 做测试，实际开发中格式会有同，请自行个性代码适配。
    读日志文件，解析，每种动作生成一个矩阵，保存。
    """
    actions = []
    fa = np.array(pd.read_csv(f,sep="::",engine='python'))
    act = fa[:,2:3].reshape(fa.shape[0])
    # 用户总量，物品总量
    userc = np.max(fa[:,:1])+1
    itemc = np.max(fa[:,1:2])+1
    # 行为动作类型
    unique_act = np.unique(act)
    if f is not None and o is not None:
        # n个动作，每个动作成生一个user_item数组
        for a in unique_act:
            actlog = fa[act==a][:,:2]
            users_items = np.zeros((userc,itemc))
            for log in actlog:
                users_items[log[0]][log[1]] = 1
            actions.append(users_items)
        np.save(o, actions)
    else:
        c(fa)
    return 'OK'

def process_rating(f):
    """
    处理打分行为日志
    :param argv:  日志文件
    :return:
    日志格式
    user_id::item_id::rating::time
    使用ml-1m数据集中的ratings.dat 做测试，实际开发中格式会有同，请自行个性代码适配。
    读日志文件，解析，生成一个矩阵，保存。
    """
    fa = np.array(pd.read_csv(f,sep="::",engine='python'))
    # 用户总量，物品总量
    userc = np.max(fa[:, :1]) + 1
    itemc = np.max(fa[:, 1:2]) + 1
    users_itemsrating = np.zeros((userc, itemc))
    for a in fa:
        users_itemsrating[a[0]][a[1]] = a[2]
    return users_itemsrating


if __name__ == '__main__':
    usage = """
    -i file         读日志文件
    -o file         保存成文件，不写文件名用默认文件名
    -r profile      指定redis配置文件，并保存
    -h profile      指定hkbase配置文件，并保存
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:h:i:o:",["redis=","hbase=","in=","out="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts)==0:
        print(usage)
        exit()
    infile = 0
    outfile = 0
    r = 0
    h = 0
    dbprofile=0
    for k,v in opts:
        if k in ('-o','--out'):
            if v == '':
                outfile = 'user_log.%s'%(datetime.datetime.today().date().strftime('%Y-%m-%d'),)
            else:
                outfile = v
        elif k in ('-i', '--in'):
            infile = v
        elif k in ('-r','--redis'):
            r =1
            dbprofile = v
        elif k in ('-h','--hbase'):
            h = 1
            dbprofile = v
        elif k in ('-h','--help'):
            print(usage)

    cf = ConfigParser()
    if infile is not 0 and outfile is not 0:
        ret = process_action(infile,outfile)
        print(ret)

        exit()
    elif infile is not 0 and r is not 0 and dbprofile is not 0:
        cf.read(sys.path[0]+'/'+dbprofile)
        host = cf.get('redis','host')
        port = cf.get('redis','port')
        user = cf.get('redis','user')
        pwd = cf.get('redis','pwd')
        ret = process_action(sys.path[0]+'/'+infile,t='redis',c=savetoredis)
        print(ret)
    elif infile is not 0 and h is not 0 and dbprofile is not 0:
        exit()





    # arracts = process_action(sys.argv)
    # filename = 'user_act.%s'%(datetime.datetime.today().date().strftime('%Y-%m-%d'),)
    # print(filename)
    # np.save(filename,arracts)
    #
    # arrrating = process_rating(sys.argv)
    # filename = 'user_itemrating.%s' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),)
    # print(filename)
    # np.save(filename, arrrating)



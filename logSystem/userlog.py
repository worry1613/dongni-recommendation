# -*- coding: UTF-8 -*-
"""
    userlog.py
    write by worry1613
    2015-10-01
    处理用户行为日志，生成数据并保存。


    日志格式
    user_id::item_id::rating::time


    使用
    不同类型，保存成文件，供numpy使用
    python userlog.py -i useractlog.2015-10-20.log -t act -o useractlog.2015-10-20
    python userlog.py -i useractlog.2015-10-20.log -t rate -o useractlog.2015-10-20

    不同类型，保存进入数据库(redis或hbase)，可以改成任何自己想要的数据库系统，mongodb,mysql,pgsql,hadoop都行
    python userlog.py -i useractlog.2015-10-20.log -t act -r redis.conf
    python userlog.py -i useractlog.2015-10-20.log -t rate -h hbase.conf

    -i file         读日志文件
    -o file         保存成文件，不写文件名用默认文件名
    -r profile      指定redis配置文件，并保存
    -h profile      指定hkbase配置文件，并保存
    -t type         act或rate，默认是act

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
import redis  # 一定要安装hiredis不然操作redis会很慢

SUCCESS = 1
host = 0
port = 0
user = 0
pwd = 0

actlogfeture = {'user': 0, 'item': 1, 'acttype': 2, 'time': 3, 'rate': 2}


def savetoredis(a, t='act'):
    """
    保存到redis
    :param a:  user_itme数组
    :param t:  act行为日志,rating打分日志
    :return:   null
    """
    rc = redis.StrictRedis(host=host, port=int(port))
    if t == 'act':
        saveredisact(a, rc)

    elif t == 'ratings':
        saveredisrating(a, rc)
    return 'OK'


def saveredisact(a, rc):
    """
    用户行为日志保存到redis
    :param a:  data
    :param rc:  redis
    :return:
    redis数据缓存，方便快读数据
    2015-11-01:act2      :u4454   :i3598
    日期       用户行为类型 用户标识   物品标识
    每天每个行为每个用户对每个物品记录1，快速定位，有行为返回1，没有行业返回NULL

    2015-11-01:act2      :u4454
    日期       用户行为类型 用户标识
    每天每个行为每个用户对所有物品记录，列表行式，返回所有物品的列表

    2015-11-01:act2      :i3598
    日期       用户行为类型 物品标识
    每天每个行为所有用户对每个物品记录，列表行式，返回所有有行为记录的用户的列表

    2015-11-01:act2      :items
    日期       用户行为类型
    每天每个行为所有用户对所有物品记录，列表行式，返回所有有行为记录的物品的列表

    2015-11-01:act2      :users
    日期       用户行为类型
    每天每个行为所有用户记录，列表行式，返回所有有行为记录的用户的列表
    """
    r = rc.pipeline()
    for log in a:
        r.set('%s:act%d:u%d:i%d' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                    log[actlogfeture['acttype']],
                                    log[actlogfeture['user']],
                                    log[actlogfeture['item']]), 1)
        r.lpush('%s:act%d:u%d' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                  log[actlogfeture['acttype']],
                                  log[actlogfeture['user']]),
                log[actlogfeture['item']])
        r.lpush('%s:act%d:i%d' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                  log[actlogfeture['acttype']],
                                  log[actlogfeture['item']]), log[actlogfeture['user']])
        r.lpush('%s:act%d:items' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                    log[actlogfeture['acttype']]),
                log[actlogfeture['item']])
        r.lpush('%s:act%d:users' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                    log[actlogfeture['acttype']]),
                log[actlogfeture['user']])
    r.execute()
    return SUCCESS


def saveredisrating(a, rc):
    """
    用户打分日志保存到redis
    :param a:  data
    :param rc:  redis
    :return:
    redis数据缓存，方便快读数据
    2015-11-01:act2      :u4454   :i3598
    日期       用户行为类型 用户标识   物品标识
    每天每个行为每个用户对每个物品记录rate，快速定位，有行为返回rate，没有行业返回NULL

    2015-11-01:act2      :u4454
    日期       用户行为类型 用户标识
    每天每个行为每个用户对所有物品记录，列表行式，返回所有[物品:rate]的列表

    2015-11-01:act2      :i3598
    日期       用户行为类型 物品标识
    每天每个行为所有用户对每个物品记录，列表行式，返回所有有行为记录的[用户:rate]的列表

    2015-11-01:act2      :items
    日期       用户行为类型
    每天每个行为所有用户对所有物品记录，列表行式，返回所有有行为记录的[物品:用户:rate]的列表

    2015-11-01:act2      :users
    日期       用户行为类型
    每天每个行为所有用户记录，列表行式，返回所有有行为记录的[用户:物品:rate]的列表
    """
    r = rc.pipeline()
    for log in a:
        r.set('%s:act%d:u%d:i%d' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                    log[actlogfeture['acttype']],
                                    log[actlogfeture['user']],
                                    log[actlogfeture['item']]), log[actlogfeture['rate']])

        r.lpush('%s:act%d:u%d' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                  log[actlogfeture['acttype']],
                                  log[actlogfeture['user']]),
                'i%d:%d' % (log[actlogfeture['item']], log[actlogfeture['rate']]))

        r.lpush('%s:act%d:i%d' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                  log[actlogfeture['acttype']],
                                  log[actlogfeture['item']]),
                'u%d:%d' % (log[actlogfeture['user']], log[actlogfeture['rate']]))

        r.lpush('%s:act%d:items' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                    log[actlogfeture['acttype']]),

                'i%d:u%d:%d' % (log[actlogfeture['item']],
                                log[actlogfeture['user']],
                                log[actlogfeture['rate']]))

        r.lpush('%s:act%d:users' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),
                                    log[actlogfeture['acttype']]),
                'u%d:i%d:%d' % (log[actlogfeture['user']],
                                log[actlogfeture['item']],
                                log[actlogfeture['rate']]))
    r.execute()
    return SUCCESS


def savetohbase(a, c, t):
    """
    保存到hbase
    :param a:  user_itme数组
    :param c:  hbase连接
    :param t:  act行为日志,rating打分日志
    :return:   null
    """
    return


def process_action(f, o=None, t=None, c=savetoredis):
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
    fa = np.array(pd.read_csv(f, sep="::", engine='python'))
    if t == 'file' and f is not None and o is not None:
        act = fa[:, 2:3].reshape(fa.shape[0])
        # 用户总量，物品总量
        userc = np.max(fa[:, :1]) + 1
        itemc = np.max(fa[:, 1:2]) + 1
        # 行为动作类型
        unique_act = np.unique(act)

        # n个动作，每个动作成生一个user_item数组
        for a in unique_act:
            actlog = fa[act == a][:, :2]
            users_items = np.zeros((userc, itemc))
            for log in actlog:
                users_items[log[0]][log[1]] = 1
            actions.append(users_items)
        np.save(o, actions)
    elif t in ['redis', 'hbase']:
        c(fa)
    else:
        # f o 有甚少一个是空的
        return 'FILE IS NULL'
    return SUCCESS


def process_rating(f, o=None, t=None, c=savetoredis):
    """
    处理用户打分日志
    :param f:  日志文件
    :param o:  输出文件
    :param t:  输出类型,file,redis,hbase
    :param c:  输出函数
    :return:
    日志格式
    user_id::item_id::rating::time
    使用ml-1m数据集中的ratings.dat 做测试，实际开发中格式会有同，请自行个性代码适配。
    读日志文件，解析，生成一个矩阵，保存。
    """
    fa = np.array(pd.read_csv(f, sep="::", engine='python'))
    if t == 'file' and f is not None and o is not None:
        # 用户总量，物品总量
        userc = np.max(fa[:, :1]) + 1
        itemc = np.max(fa[:, 1:2]) + 1
        users_itemsrating = np.zeros((userc, itemc))
        for a in fa:
            users_itemsrating[a[0]][a[1]] = a[2]
        np.save(o, users_itemsrating)

    elif t in ['redis', 'hbase']:
        c(fa)
    else:
        # f o 有甚少一个是空的
        return 'FILE IS NULL'
    return SUCCESS


if __name__ == '__main__':
    usage = """
    -i file         读日志文件
    -o file         保存成文件，不写文件名用默认文件名
    -r profile      指定redis配置文件，并保存
    -h profile      指定hkbase配置文件，并保存
    -t type         act或rate
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:h:i:o:t:", ["redis=", "hbase=", "in=", "out=", "type="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()
    infile = 0
    outfile = 0
    r = 0
    h = 0
    dbprofile = 0
    type = 'act'
    for k, v in opts:
        if k in ('-o', '--out'):
            if v == '':
                outfile = 'user_log.%s' % (datetime.datetime.today().date().strftime('%Y-%m-%d'),)
            else:
                outfile = v
        elif k in ('-i', '--in'):
            infile = v
        elif k in ('-r', '--redis'):
            r = 1
            dbprofile = v
        elif k in ('-h', '--hbase'):
            h = 1
            dbprofile = v
        elif k in ('-h', '--help'):
            print(usage)
        elif k in ('-t', '--type'):
            if v == 'act':
                type = 'act'
            elif v == 'rate':
                type = 'rate'
            else:
                type = 'act'
    cf = ConfigParser()
    if infile is not 0 and outfile is not 0:
        if type == 'act':
            ret = process_action(infile, outfile)
        else:
            ret = process_rating(infile, outfile)
        print(ret)
    elif infile is not 0 and r is not 0 and dbprofile is not 0:
        cf.read(sys.path[0] + '/' + dbprofile)
        host = cf.get('redis', 'host')
        port = cf.get('redis', 'port')
        user = cf.get('redis', 'user')
        pwd = cf.get('redis', 'pwd')
        if type == 'act':
            ret = process_action(sys.path[0] + '/' + infile, t='redis', c=savetoredis)
        else:
            ret = process_rating(sys.path[0] + '/' + infile, t='redis', c=savetoredis)
        print(ret)
    elif infile is not 0 and h is not 0 and dbprofile is not 0:
        pass


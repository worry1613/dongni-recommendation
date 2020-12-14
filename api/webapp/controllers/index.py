import json
import random
import urllib.parse

from flask import Blueprint
from flask import request
from flask import jsonify
import datetime
import numpy as np
import sys

from webapp.basemodels import DBcahace
from webapp.helpers.web_log import logger
from config import KAFKA_SERVERS,KAFKA_TOPIC_ACTION,KAFKA_TOPIC_FEEDS
from kafka import KafkaProducer

db = DBcahace('toutiao')
index = Blueprint('index', __name__)

KafkaProducer = KafkaProducer(bootstrap_servers=KAFKA_SERVERS)

# /feed?uid=xx&from=xx&size=10&category=xxx&algo=xxx
@index.route('/feed', methods=['GET'])
def feed():
    """
    feed流数据拉取
    :return:
    """
    size = 10
    category = None
    algo = 'cs:bandit'

    ret_dict = {}
    uidstr = request.args.get('uid', '')
    if uidstr == '':
        ret_dict = {'message': '缺少用户id', 'showtime': int(datetime.datetime.now().timestamp())}
        return jsonify(ret_dict)
    else:

        fsize = request.args.get('size', size)
        category = request.args.get('category', category)
        algo = request.args.get('algo', algo)

        # 历史数据 idhis
        uid =int(uidstr)
        idhis = gethistory(uid)

        # recall 召回
        ids, c = recall(uid, fsize, category, algo, idhis)

        # duplicate removal 去重
        ids = duplremove(uid, fsize, ids, idhis)

        # sort 排序
        retsort = itemsort(ids)

        # ret = itemcontent(ret, c, uid)
        ret = db.getidlist(retsort, c, uid)

        #
        ret_dict = {'code': 0,
                    'message': '',
                    'showtime': int(datetime.datetime.now().timestamp()),
                    'algo': algo + ':' + str(c),
                    'rec_id': 'rec_xxxx_yyyy',
                    'asize': len(ret),
                    'feeds': ret
                    }
        msg = {'user':uid,'algo':algo + ':' + str(c),'ids':[bytes.decode(r) for r in retsort]}
        logger.debug(json.dumps(msg))
        KafkaSendLog(KafkaProducer,KAFKA_TOPIC_FEEDS,msg)

        logger.debug('event: feed,user:%d, algo:%s, ids: %s' % (uid,
                                                                algo + ':' + str(c),
                                                                ','.join([r for r in retsort])))

    return jsonify(ret_dict)


# item-xxxx?act=1,2,4&from=xxxx&pos=1,10
@index.route('/item-<cid>', methods=['GET'])
def item(cid):
    """
    内容查看
    :param cid: item id
    :return:   实例后的内容数据
    """
    ret_dict = {}
    # act = None
    # from = None
    # pos = None
    uidstr = request.args.get('uid', '')
    if uidstr == '':
        ret_dict = {'message': '缺少用户id', 'showtime': int(datetime.datetime.now().timestamp())}
        return jsonify(ret_dict)
    else:
        uid = int(uidstr)
        # act 1,view,2,fav,3,share,动作的分值
        act = request.args.get('act', 1)
        fromid = request.args.get('from', '')
        choicestr = request.args.get('choice', '')
        idsstr = request.args.get('ids', '')

        choice = int(choicestr) if choicestr else 9999
        # ids =idsstr.split(',')
        ret_dict = db.getcontentbyid(cid, idsstr, choice, uid)
        # redis更新wins,
        # #### redis数据更新
        p, wins, trials, current, beta = db.getuserpwtcb(uid)
        wins[int(choice)] += 1
        vardict = {'wins': wins}
        db.updateuserwtc(u=uid, vardict=vardict)
        # ####
        msg={'user':uid,'cid':cid,'ids':idsstr}
        KafkaSendLog(KafkaProducer, KAFKA_TOPIC_ACTION, msg)
        logger.debug('event:click, user:%d, cid:%s ,ids:%s' % (uid, cid, idsstr))
        return jsonify(ret_dict)


def recall(uid, size, category, algo, his):
    """
    内容召回

    :param uid: 用户id, 1029384
    :param size:  内容返回个数, 5,10
    :param category: 内容类别, 0,1,2,3,4,5,6,7
    :param algo: 算法类形, cs:bindit
    :param his: 历史数据
    :return:   size个内容
    """
    return eval(algo.split(':')[-1])(uid, size, category, algo, his)


def duplremove(u, s, r, h):
    """
    去重
    :param u: 用户id
    :param s: item数量
    :param r: 召回，还未去重的ID LIST
    :param h: 历史
    :return: 去重后的id list
    """
    if len(h):
        ret = list(set(r) - set(h))[:s]
    else:
        ret = r[:s]
    savehistory(u, ret)
    return ret


def itemsort(r):
    """
    内容排序
    :param r: 召回数据
    :return: 排序后的数据
    """
    return sorted(r)


def itemcontent(rs, c, u):
    """
    id list to item content list
    :param rs:  id list
    :param c:  choice
    :param u:  uid
    :return: item content list
    """
    idstr = ','.join([str(r) for r in rs])
    ret = [{'tittle': '这是' + str(r) + '的标题',
            'url': 'http://localhost:9876/item-' + str(r) + '?ids=' + idstr + '&choice=' + str(c) + '&uid=' + str(
                u) + '&pos=' + str(
                k), 'id': r, 'viewed': random.randint(10, 10000),
            'comments': random.randint(10, 10000), 'digg': random.randint(10, 10000)} for k, r in enumerate(rs)]
    return ret


def gethistory(u):
    """
    取用户访问历史数据ID
    :param u: 用户id
    :return: set类型 ids
    """
    return db.getalgohistory(u)


def savehistory(u, ids):
    """
    保存用户访问历史数据ID
    :param u: 用户id
    :param ids: 内容id列表
    :return:
    """
    db.updatealgohistory(u, ids)
    return


def bandit(u, s, c, a, h):
    """
    bindit算法，汤普森采样
    :param u: 用户id
    :param s:  内容返回个数
    :param c: 内容类别
    :param a: 算法类形, cs:bindit
    :param h: 历史数据
    :return:   size个内容, choice
    """
    # #### redis数据初始化
    p, wins, trials, current, beta = db.getuserpwtcb(u)
    # beta = np.zeros(5)
    # ####汤普森采样, 核心算法
    beta[current] = np.random.beta(wins[current] + 1, trials[current] - wins[current] + 1)
    choice = np.argmax(beta)
    trials[choice] += 1

    if a.split(':')[-1] == 'bandit':
        ids = db.getbanditdata(u, choice, h, s)
    else:
        pass

    # #### redis数据更新
    vardict = {'trials': trials, 'current': choice, 'beta': beta}
    db.updateuserwtc(u=u, vardict=vardict)

    # his观看历史记录
    # ids = hbase select a.choice from content where uid=u ,size=his+s
    # 取redis 中 ids 内容，连接中加入choice
    # 更新redis中的wins，trials,current
    # 返回ids 中的内容
    return ids, choice

def KafkaSendLog(kafka, topic, log):
    """
    kafka发送分布式日志信息
    :param kafka:
    :param topic:
    :param log:
    :return:
    """
    msg = json.dumps(log)
    kafka.send(topic, str.encode(msg))

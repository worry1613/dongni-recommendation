# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.exc import SQLAlchemyError
import random
import time

from config import REDIS_DB, REDIS_HOST, REDIS_PORT, HBASE_HOST, HBASE_PORT, HBASE_TABLE_PREFIX
# db = SQLAlchemy()
import redis, happybase
import numpy as np


# from happybase import
#
class DBcahace(object):
    """
    数据访问类,redis ,hbase
    """

    def __init__(self, tablename):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.hbase = happybase.Connection(host=HBASE_HOST)
        self.table = self.hbase.table(tablename)
        # self.bindit
        bindits = self.redis.keys('bandit:*')
        self.bindit = dict(
            [[int(bytes.decode(b).replace('bandit:', '')), [bytes.decode(r) for r in self.redis.lrange(b, 0, -1)]] for b
             in bindits])
        self.p = [float(p) for p in bytes.decode(self.redis.get('userallp')).split(',')]

    def getidlist(self, ids, c, u):
        """
        ids to contents 数据实例化时用到
        :param ids:
        :param c:  choice
        :param u:  uid
        :return:
        """
        # c:xxxx 内容缓存
        contents = self.redis.mget(['c:%s' % (_id,) for _id in ids])
        # 处理无缓存的数据
        cachenolist = [[k, ids[k]] for k, v in enumerate(contents) if v is None]
        if cachenolist is not None:
            # 未缓存的数据
            # cachenonus = list(np.array(cachenolist).T[0])  # 序号[0,2,3,4]
            cachenoids = list(np.array(cachenolist).T[-1])  # ids
            ret = dict(self.table.rows(cachenoids))
            for nus in cachenolist:
                # 更新缓存
                content = bytes.decode(ret[str.encode(cachenolist[nus[0]][-1])][b'content:title'])
                contents[nus[0]] = content
                self.redis.set('c:%s' % (cachenolist[nus[0]][-1],),
                               content)
        idstr = ','.join([_id for _id in ids])

        ret = [{'tittle': r[-1],
                'url': 'http://localhost:9876/item-%s?ids=%s&choice=%d&uid=%d' % (
                r[0], idstr, c, u),
                'id': int(r[0])}
               for r in zip(ids, contents)]
        return ret

    def getcontentbyid(self, cid, idsstr, c, u):
        """
        item内容
        :param i: content id
        :param idsstr:
        :param c:  choice
        :param u:  uid
        :return:
        """
        content = self.redis.get('c:%s' % (cid,))

        return {'itemid': cid,
                'title': bytes.decode(content), 'content': bytes.decode(content), 'fromid': '',
                'ids': idsstr, 'choice': c, 'uid': u, 'message': ''
                }

    def getuserpwtcb(self, u):
        """
        取用户的p, wins,trials,current bindit类， beta, bindit算法用
        :param u:
        :return:  p, wins, trials, current bindit类
        """
        l = ['u:%s:w' % (u,), 'u:%s:t' % (u,), 'u:%s:c' % (u,), 'u:%s:beta' % (u,)]
        w, t, c, b = self.redis.mget(l)
        wins = np.array([float(i) for i in bytes.decode(w).split(',')])
        trials = np.array([float(i) for i in bytes.decode(t).split(',')])
        beta = np.array([float(i) for i in bytes.decode(b).split(',')])
        current = int(c) % len(trials)

        return self.p, wins, trials, current, beta

    def updateuserwtc(self, u, vardict):
        """
        更新用户的wins, trials, current bindit类
        :param u: uid
        :param w: wins
        :param t: trials
        :param c: current bindit类
        :return:
        """
        d = dict()
        if 'wins' in vardict.keys():
            d['u:%s:w' % (u,)] = ','.join([str(i) for i in vardict['wins']])
        if 'trials' in vardict.keys():
            d['u:%s:t' % (u,)] = ','.join([str(i) for i in vardict['trials']])
        if 'current' in vardict.keys():
            d['u:%s:c' % (u,)] = str(vardict['current'])
        if 'beta' in vardict.keys():
            d['u:%s:beta' % (u,)] = ','.join([str(i) for i in vardict['beta']])

        self.redis.mset(d)
        return

    def getbanditdata(self, u, c, h, s):
        """
        bindit算法取数据
        :param u:  uid
        :param c:  choice, int
        :param h:  history
        :param s:  size
        :return:  id list
        """
        return random.sample(list(set(self.bindit[c])), s + len(h))

    def getalgohistory(self, u):
        """
        取用户算法历史的列表，只要显示，不管看不看。看了，是用户查看的历史列表
        :param u: uid
        :return:
        """
        return [bytes.decode(h) for h in self.redis.zrange('u:%s:algo:h' % (u,), 0, -1)]

    def updatealgohistory(self, u, ids):
        """

        :param u:
        :param ids:
        :return:
        """

        t = time.time()
        varmap = {_id: t for _id in ids}
        self.redis.zadd('u:%s:algo:h' % (u,), varmap)
        return

    def getuserhistory(self, u):
        pass

    def updateuserhistory(self, u, ids):
        pass

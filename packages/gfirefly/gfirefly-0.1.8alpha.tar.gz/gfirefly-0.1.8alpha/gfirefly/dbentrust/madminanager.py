#coding:utf8
'''
Created on 2013-5-22

@author: lan (www.9miao.com)
'''
from gfirefly.utils.singleton import Singleton
from gevent_zeromq import zmq 
import gevent
from util import excuteSQL
import marshal

class MAdminManager:
    """一个单例管理器。作为所有madmin的管理者
    """
    __metaclass__ = Singleton
    
    def __init__(self):
        """初始化所有管理的的madmin的集合，放在self.admins中
        """
        context = zmq.Context()
        self.sock = context.socket(zmq.SUB)
        self.isStart = False
        
    def registe(self,admin):
        """注册一个madmin对象到管理中.
        >>> madmin = MAdmin('tb_registe','characterId',incrkey='id')
        >>> MAdminManager().registe(madmin)
        """
        pass
#         self.admins[admin._name] = admin

    def _run(self):
        """执行协议
        """
        while True: 
            msg = self.sock.recv()
            tablename,sql = marshal.loads(msg)
            excuteSQL(tablename, sql)
            print "excuteSQL",sql
    
    def checkAdmins(self):
        """遍历所有的madmin，与数据库进行同步。

        >>>MAdminManager().checkAdmins()
        """
        if self.isStart:
            return
        self.isStart=True
        from util import M2DB_PORT
        port = M2DB_PORT
        address = 'tcp://*:%s'%port
        self.sock.bind(address)
        self.sock.setsockopt(zmq.SUBSCRIBE, "")
        gevent.spawn(self._run)
        

        
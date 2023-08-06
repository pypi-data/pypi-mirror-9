#coding:utf8
'''
Created on 2015-1-3

@author: root
'''

from memclient import memcached_connect
from datetime import date
memcached_connect(["127.0.0.1:11222"])
from memclient import mclient

print "mc get",mclient.get("tb_role_info:1:data")
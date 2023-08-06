'''
Created on 2014-12-31

@author: root
'''
from memclient import memcached_connect
memcached_connect(["127.0.0.1:11211"])
from memobject import MemObject
from memclient import mclient


class Mcharacter(MemObject):
    
    def __init__(self,pid,name,mc):
        MemObject.__init__(self, name, mc)
        self.id = pid
        self.level = 0
        self.profession = 0
        self.nickname = u''
        self.guanqia = 1000
        
mcharacter = Mcharacter(1,'character:1',mclient)
mcharacter.nickname='lan'
mcharacter.insert()


mc_other = Mcharacter(1,'character:1',mclient)
print mc_other.get('nickname')










    
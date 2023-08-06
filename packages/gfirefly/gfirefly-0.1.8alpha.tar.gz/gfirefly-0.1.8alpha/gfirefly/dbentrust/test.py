'''
Created on 2014-12-30

@author: root
'''

data = {"name:a":1,"name:b":2,"name:c":3,
        "hehe:a":10,"hehe:b":20,"hehe:c":30,}



class MemFiled(object):
    
    def __init__(self,name):
        self.name = name
        self.value = None
    
    def getValue(self):
        if not self.value:
            self.value = data.get(self.name)
        return self.value
    
    def refreshValue(self):
        self.value = data.get(self.name)
        return self.value
        
    
    def setValue(self,value):
        self.value = value
        data[self.name]=value
        
    
class A(object):
    
    
    def __init__(self,name):
        self.a = MemFiled("%s:a"%name)
        self.b = MemFiled("%s:b"%name)
        self.c = MemFiled("%s:c"%name)
        
    def __getattribute__(self,attr):
        value = object.__getattribute__(self,attr)
        if isinstance(value, MemFiled):
            return value.getValue()
        return value
    
    def __setattr__(self, attr,value):
        if self.__dict__.has_key(attr):
            _value = object.__getattribute__(self,attr)
            if isinstance(_value, MemFiled):
                return _value.setValue(value)
            else:
                return object.__setattr__(self, attr,value)
        else:
            return object.__setattr__(self, attr,value)
        
    def geta(self):
        print self.a
        
        


a = A("name")
b = A("hehe")
b.c = {"a":123,"b":234,"c":345}
print b.c
b.geta()
print data
b.c['b']=0
print b.c
print data
s = b.c
s["c"]=0
print b.c
print data




        
        

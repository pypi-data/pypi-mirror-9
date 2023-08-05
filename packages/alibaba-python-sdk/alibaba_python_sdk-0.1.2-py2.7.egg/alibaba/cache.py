# -*- coding:utf-8 -*-

import time,json
from os.path import abspath, dirname

class Cache(object):
    def __init__(self,*args,**kw):
        self.init_cache()

    def init_cache(self):
        try:
            with open(dirname(abspath(__file__)) + "/tmp/tmp_cache","r") as f:
                body = f.read()
                self.cache = json.loads(body) if body else {}
        except:
            self.cache = {}
        self.time_cache = self.cache.get("self.time_cache.key",{})

    def flush(self):
        self.cache["self.time_cache.key"] = self.time_cache
        with open(dirname(abspath(__file__)) + "/tmp/tmp_cache","w") as f:
            f.write(json.dumps(self.cache))

    def get(self,key):
        self.init_cache()
        if self.time_cache.has_key(key):
            if self.time_cache.get(key,0) > time.time():
                return self.cache.get(key)
            else:
                del self.time_cache[key]
                del self.cache[key]
                return
        return self.cache.get(key)

    def get_multi(self,keys):
        self.init_cache()
        d = {}
        for key in keys:
            v = self.get(key)
            if v:
                d.setdefault(key,v)
        return d

    def set(self,key,value,expire=0):
        try:
            if expire and isinstance(expire,int):
                self.time_cache[key] = time.time() + expire
            self.cache[key] = value
            self.flush()
            return True
        except:
            return False

    def set_multi(self, mappings, expire=0):
        if isinstance(mappings,dict):
            for k,v in mappings.items():
                self.set(k,v,expire)
            self.flush()
            return True
        return False

    def add(self, key, value, expire=0):
        if self.cache.has_key(key):
            return False
        else:
            return self.set(key,value,expire)

    def replace(self, key, value, expire=0):
        if not self.cache.has_key(key):
            return False
        else:
            return self.set(key,value,expire)

    def delete(self,key):
        try:
            del self.cache[key]
            self.flush()
            return True
        except:
            return False


    def incr(self, key, delta=1):
        v = self.get(key)
        if str(v).isdigit() and isinstance(delta,int):
            self.set(key,int(v)+delta)
            return int(v)+delta

    def decr(self, key, delta=1):
        v = self.get(key)
        if str(v).isdigit() and isinstance(delta,int):
            nv = int(v) - delta if int(v) > delta else 0
            self.set(key,nv)
            return nv
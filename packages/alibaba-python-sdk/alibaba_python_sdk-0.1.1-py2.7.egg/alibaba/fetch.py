# -*- coding:utf-8 -*-


import urllib2,urllib


class Fetch(object):
    def __init__(self,*args,**kw):
        self.build_opener()

    def build_opener(self):
        try:
            self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        except Exception,e:
            return

    def get(self,url):
        if not url:
            return
        try:
            return self.opener.open(url).read()
        except:
            return

    def post(self,url,data={}):
        if not url:
            return
        try:
            req = urllib2.Request(url,urllib.urlencode(data))
            response = self.opener.open(req)
            return response.read()
        except:
            return

if __name__ == "__main__":
    f = Fetch()
    print f.get("http://www.163.com")

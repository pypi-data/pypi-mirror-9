# -*- coding:utf-8 -*-

import os,hashlib,shutil
from os.path import abspath, dirname

class Storage(object):
    def __init__(self,*args,**kw):
        self.set_path()

    def save_text(self,path,content):
        try:
            with open(self.path_to_name(path),"w") as f:
                f.write(content)
            return True
        except:
            return False

    def save_file(self,path,_file):
        try:
            shutil.copyfile(_file,self.path_to_name(path))
            return True
        except:
            return False

    def get(self,path,_to=None):
        if path and _to:
            try:
                if os.path.exists(self.path_to_name(path)):
                    shutil.copyfile(self.path_to_name(path),_to)
                    return True
                else:
                    return False
            except:
                return False
        else:
            try:
                with open(self.path_to_name(path)) as f:
                    return f.read()
            except:
                return ""


    def delete(self,path):
        try:
            os.remove(self.path_to_name(path))
            return True
        except:
            return False

    def is_exist(self,path):
        return os.path.exists(self.path_to_name(path))

    def move(self,_from,_to):
        try:
            os.rename(self.path_to_name(_from),self.path_to_name(_to))
            return True
        except:
            return False

    def copy(self,_from,_to):
        try:
            if _from and _to and self.is_exist(_from):
                shutil.copyfile(self.path_to_name(_from),self.path_to_name(_to))
                return True
            else:
                return False
        except:
            return False

    def set_path(self):
        tmp_dir = os.environ.get("TMPDIR","") if os.environ.get("TMPDIR","") else os.environ.get("TMP","")
        if not os.path.exists(tmp_dir):
            tmp_dir = dirname(abspath(__file__))+"/tmp"
        os.chdir(tmp_dir)
        if not os.path.exists("storage_tmp"):
            os.mkdir("storage_tmp")
        os.chdir("storage_tmp")

    def path_to_name(self,path):
        return hashlib.md5(path).hexdigest()


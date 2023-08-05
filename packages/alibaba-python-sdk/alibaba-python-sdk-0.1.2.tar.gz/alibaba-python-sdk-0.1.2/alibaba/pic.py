# -*- coding:utf-8 -*-
#!/usr/bin/env python
""" generated source for module PicServiceImpl """

#
#  * User: chenqiu
#  * Date: 14-7-29
#  * Time: 11:48
#  * To change this template use File | Settings | File Templates.
#


import logging,json
from datetime import datetime
from os.path import abspath, dirname

logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filemode='w')

class PicService():
    """ generated source for class PicServiceImpl """

    def __init__(self):
        self.logger = logging.getLogger("pic_service")
        self.init_ps()

    def init_ps(self):
        try:
            with open(dirname(abspath(__file__)) + "/tmp/tmp_dir","r") as f:
                body = f.read()
                self.cache_dir = json.loads(body) if body else {}
            with open(dirname(abspath(__file__)) + "/tmp/tmp_pic","r") as f:
                body = f.read()
                self.cache_pic = json.loads(body) if body else {}
        except:
            self.cache_pic = {}
            self.cache_dir = {"/":{}}


    def flush(self):
        try:
            with open(dirname(abspath(__file__)) + "/tmp/tmp_dir","w") as f:
                f.write(json.dumps(self.cache_dir))
            with open(dirname(abspath(__file__)) + "/tmp/tmp_pic","w") as f:
                f.write(json.dumps(self.cache_pic))
        except Exception as t:
            self.logger.error("flush"+t.message)

    def savePic(self, dirpath, filename, content):
        """ generated source for method savePic """
        try:
            if not content:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "image content empty")
            dirpath = normailizeDirpath(dirpath)
            validateDirpath(dirpath)
            validateFilename(filename)
            if not self.isDirExist(dirpath).get("result"):
                self.createDir(dirpath)
            pic = convertPic(filename,len(content))
            pic.dirpath = dirpath
            if self.cache_pic.get(get_pic_key(dirpath,filename)):
                raise PicException(ResponseStatus.FILE_NAME_DUPLICATE,"file name duplicate")
            self.cache_pic[get_pic_key(dirpath,filename)] = pic.to_json()
            self.flush()
            return {"status":200,"result":pic.to_json()}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("savePic"+t.message)
            return getSysErrorResponse()

    def getPic(self, dirpath, filename):
        """ generated source for method getPic """
        try:
            assertNull(filename, "filename")
            dirpath = normailizeDirpath(dirpath)
            if not self.isDirExist(dirpath).get("result"):
                raise PicException(ResponseStatus.DIR_NOT_FOUND, "directory not found:" + dirpath)
            pic = self.cache_pic.get(get_pic_key(dirpath,filename))
            if not pic:
                raise PicException(ResponseStatus.FILE_NOT_FOUND, "file not found:" + dirpath + "/" + filename)
            return {"status":200,"result":pic}
        except Exception as t:
            self.logger.error("createDir"+t.message)
            return getSysErrorResponse()

    def deletePic(self, dirpath, filename):
        """ generated source for method deletePic """
        try:
            assertNull(filename, "filename")
            dirpath = normailizeDirpath(dirpath)
            if not self.isDirExist(dirpath):
                raise PicException(ResponseStatus.DIR_NOT_FOUND, "directory not found:" + dirpath)
            pic = self.cache_pic.get(get_pic_key(dirpath,filename))
            if not pic:
                raise PicException(ResponseStatus.FILE_NOT_FOUND, "file not found:" + dirpath + "/" + filename)
            self.cache_pic.pop(get_pic_key(dirpath,filename))
            self.flush()
            return {"status":200,"result":True}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("deletePic"+t.message)
            return getSysErrorResponse()

    def getPicList(self, dirpath, currentPage=1, pageSize=40):
        """ generated source for method getPicList_0 """
        try:
            dirpath = normailizeDirpath(dirpath)
            if not self.isDirExist(dirpath).get("result"):
                raise PicException(ResponseStatus.DIR_NOT_FOUND, "directory not found:" + dirpath)
            if currentPage <= 0:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "currentPage must greater than or equal  1")
            if pageSize <= 0:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "pageSize must greater than 0 ")
            if pageSize > 100:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "pageSize must less than or equal  100")
            result = []
            for k in self.cache_pic.keys():
                if k.split("|||")[0] == dirpath:
                    result.append(self.cache_pic.get(k))
            return {"status":200,"result":result}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("getPicList"+t.message)
            return getSysErrorResponse()

    def createDir(self, dirpath):
        """ generated source for method createDir """
        try:
            assertNull(dirpath, "dirpath")
            dirpath = normailizeDirpath(dirpath)
            if "/" == dirpath:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "root directory can't create")
            validateDirpath(dirpath)
            if self.isDirExist(dirpath).get("result"):
                raise PicException(ResponseStatus.DIR_NAME_DUPLICATE, "dir name duplicate :" + dirpath)
            self.cache_dir = mkdir(self.cache_dir,dirpath)
            self.flush()
            return {"status":200,"result":True}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("createDir"+t.message)
            return getSysErrorResponse()

    def deleteDir(self, dirpath):
        """ generated source for method deleteDir """
        try:
            assertNull(dirpath, "dirpath")
            dirpath = normailizeDirpath(dirpath)
            if "/" == dirpath:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "root directory can't delete")
            if not self.isDirExist(dirpath).get("result"):
                raise PicException(ResponseStatus.DIR_NOT_FOUND, "directory not found:" + dirpath)
            dirs = dirpath.split("/")[1:]
            parent = self.cache_dir.get("/")
            for dir in dirs[:-1]:
                parent = parent.get(dir)
            parent.pop(dirs[-1])
            self.flush()
            return {"status":200,"result":True}
        except PicException as e:
            self.logger.error("deleteDir"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("deleteDir"+t.message)
            return getSysErrorResponse()

    def getDirList(self, dirpath):
        """ generated source for method getDirList """
        try:
            dirpath = normailizeDirpath(dirpath)
            dirs = dirpath.split("/")[1:]
            parent = self.cache_dir.get("/")
            if not self.isDirExist(dirpath).get("result"):
                raise PicException(ResponseStatus.DIR_NOT_FOUND, "directory not found:" + dirpath)
            for dir in dirs:
                parent = parent.get(dir)
            return {"status":200,"result":parent.keys()}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("getDirList"+t.message)
            return getSysErrorResponse()

    def isFileExist(self, dirpath, filename):
        """ generated source for method isFileExist """
        try:
            assertNull(filename, "filename")
            dirpath = normailizeDirpath(dirpath)
            return {"status":200,"result":self.cache_pic.has_key(get_pic_key(dirpath,filename))}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("isFileExist"+t.message)
            return getSysErrorResponse()

    def isDirExist(self, dirpath):
        """ generated source for method isDirExist """
        try:
            dirpath = normailizeDirpath(dirpath)
            dirs = dirpath.split("/")[1:]
            parent = self.cache_dir.get("/")
            if len(dirs)==1 and parent.has_key(dirs[0]):
                return {"status":200,"result":True}
            result = False
            for dir in dirs[:-1]:
                if not parent.has_key(dir):
                    break
                parent = parent.get(dir)
            if parent:
                result = bool(parent.has_key(dirs[-1]))
            return {"status":200,"result":result}
        except PicException as e:
            self.logger.error("deletePic"+e.message)
            return getErrorResponse(e)
        except Exception as t:
            self.logger.error("isDirExist"+t.message)
            return getSysErrorResponse()

    def get_cdn_url(self,full_url, width, height):
        """ generated source for method getCDNFullUrl """
        return full_url + "_" + width + "x" + height + ".jpg"

def getErrorResponse(e):
    """ generated source for method getErrorResponse """
    response = {"status":e.getStatus(),"error_msg":e.message}
    return response

def getSysErrorResponse():
    """ generated source for method getSysErrorResponse """
    response = {"status":ResponseStatus.SYS_ERROR,"error_msg":"sys_error"}
    return response


def normailizeDirpath(dirpath):
    """ generated source for method normailizeDirpath """
    if not dirpath:
        return "/"
    dirpath = dirpath.replace("\\\\", "/")
    if not dirpath.startswith("/"):
        dirpath = "/" + dirpath
    return dirpath

def assertNull(dirpath, paramName):
    """ generated source for method assertNull """
    if not dirpath:
        raise PicException(ResponseStatus.INVALID_PARAMETER, paramName + " is required")


def validateFilename(name):
    """ generated source for method validateFilename """
    if not name:
        return
    for r in "\\/:*?\"<>|;":
        if r in name:
            raise PicException(ResponseStatus.INVALID_PARAMETER, "filename has special word:   \\ / : * ? \" < > | ;")

def validateDirpath(dirpath):
    """ generated source for method validateDirpath """
    if not dirpath:
        return
    for dir in dirpath.split("/"):
        if not dir:
            continue
        if len(dir) >20:
            raise PicException(ResponseStatus.INVALID_PARAMETER, "directory name  (" + dir + ") length greater than 20")
        for r in ":*?\"<>|;":
            if r in dir:
                raise PicException(ResponseStatus.INVALID_PARAMETER, "directory name (" + dir + ")  has special word: : * ? \" < > | ;")

class PicException(Exception):
    """ generated source for class PicException """

    def __init__(self, status, message):
        """ generated source for method __init__ """
        super(PicException, self).__init__(message)
        self.status = status


    def getStatus(self):
        """ generated source for method getStatus """
        return self.status


class ResponseStatus(object):
    """ generated source for class ResponseStatus """
    SUCESS = 200
    INVALID_PARAMETER = 400
    FILE_NOT_FOUND = 404
    DIR_NOT_FOUND = 405
    FILE_NAME_DUPLICATE = 406
    DIR_NAME_DUPLICATE = 407
    REQ_TIMEOUT = 408
    FILE_SIZE_EXCEED = 409
    HAS_DIR_OR_FILE = 410
    DIR_IS_EXCEED = 411
    USER_CAPACITY_EXCEED = 412
    FILE_ADD_FILE_NUM_EXCEED = 413
    ILLEGAL_FILE_TYPE = 414
    SYS_ERROR = 500

class Pic(object):
    """ generated source for class Pic """

    def __init__(self):
        self.filename = None
        self.dirpath = None
        self.size = None
        self.type_ = 0
        self.fileModified = datetime.now()
        self.deleted = 0
        self.full_url = None

    def getCDNFullUrl(self, width, height):
        """ generated source for method getCDNFullUrl """
        return self.full_url + "_" + width + "x" + height + ".jpg"

    def to_json(self):
        return {"filename":self.filename,"dirpath":self.dirpath,"size":self.size,"fileModified":self.fileModified,"deleted":self.deleted,"full_url":self.full_url}

def convertPic(name,size):
    """ generated source for method convertPic """
    pic = Pic()
    pic.filename = name
    pic.size = size
    pic.fileModified = datetime.now().strftime("%Y-%m-%d %X")
    pic.full_url = "http://xxx.xxx.jpg"
    pic.deleted = 0
    return pic

def get_pic_key(dirpath,filename):
    return dirpath+"|||"+filename

def mkdir(dir_dict,dirpath):
    dirs = dirpath.split("/")[1:]
    parent = dir_dict.get("/")
    for dir in dirs:
        parent[dir] = parent.get(dir,{})
        parent = parent.get(dir)
    return dir_dict
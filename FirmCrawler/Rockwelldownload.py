#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import urllib2
import sys
import time

import pymongo
import hashlib


reload(sys)
sys.setdefaultencoding('utf-8')
from mycrawler.settings import firmlist_fc, MONGO_URI,dirs_root,MONGO_DATABASE,MONGO_COLLECTION,file_size

import multiprocessing



conn = pymongo.MongoClient(MONGO_URI)
print "################"
db = conn.get_database(MONGO_DATABASE)  # 使用数据库名为firmware

#print type(db)
#print type(MONGO_DATABASE)
#collection = db.scrapy_items  # 使用集合scrapy_items
collection = db.get_collection(MONGO_COLLECTION)
#collectionB = db.firmware_info  # 使用集合firmware_innfo

#dirs_root = "/home/byfeelus/firmware/Druid/"
#file_size = 104857600  # 默认文件大小是100m
# 加header，模拟浏览器
header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}





def has_keys(_dict, _iter):
    _l = []
    for x in _iter:
        _l.append(_dict.has_key(x))
    return all(_l)


def download_url(cur):
    if not has_keys(cur, ['URL', 'Manufacturer', 'FirmwareName']):
        collection.update(
            {"_id": cur['_id']}, {"$set": {'Status': 3}})

        print "no Link or Firm or Filename"
        return

    name = cur['FirmwareName']  # 把文件名赋值给name
    mylink = cur['URL']  # 把link赋值给mylink
    firm = cur['Manufacturer']  # 把firm赋值给firmname
    #fileclass = cur["ProductClass"]

    dirs1 = os.path.join(dirs_root, firm)  # 在FIRMWARE下根据厂商名建立新文件夹
    if not os.path.exists(dirs1):
        os.makedirs(dirs1)

    #dirs = os.path.join(dirs1,fileclass)
    #if not os.path.exists(dirs):
     #   os.makedirs(dirs)

    m = hashlib.md5()
    m.update(mylink)
    a = m.hexdigest()
    #b =  a[0] +a[1] +a[2]

    name1 = a + name
    filename = os.path.join(dirs1, name1)   # 定义文件的绝对路径

    # 判断文件是否已经存在，若不存在，继续下载，若存在，输出路径不下载
    if cur.has_key("Path") and cur["Path"] == filename:

        if os.path.exists(filename) and os.path.getsize(filename) > 1:
            print filename, '已经存在'  # 已经下载过的文件，修改status值

            collection.update({'_id': cur["_id"]}, {"$set": {'Status': 0}})
            return

    print "download", mylink
    trytime = 3
    z=0
    while trytime > 0:
        try:
            res = urllib2.urlopen(urllib2.Request(
                mylink, None, header), timeout=30)  # 15

            try:
                fsize = res.headers["content-length"]
                print fsize
                print "#################################"
                fsize = int(fsize)
                if fsize < 100000000:
                    with open(filename, 'wb') as f:
                        print "开始将数据写到文件中"
                        f.write(res.read())
                        f.close()
                        print"数据已经被写进文件中"

                        model = '%Y-%m-%d %X'
                        #date = time.strftime(model,time.localtime())
                        print" 已经走到这一步了"

                        collection.update({'_id': cur['_id']}, {
                            "$set": {
                                'Path': filename,
                                'Status': 0,
                                'Firmtype': 'FactoryControl' if firm in firmlist_fc else 'Not_FactoryControl',
                                'Size': os.path.getsize(filename),  # 　取大小
                                'Down_date': time.strftime(model, time.localtime())}})  # 取时间
                        print"第一次修改成功"
                        '''
                        collectionB.update({'Par_path': filename}, {
                            "$set": {
                                "Filename": cur.get("Filename"),

                                "Model": cur.get("Info").get("Model"),
                                # "Series": cur.get("Info").get("Series"),
                                "Version": cur.get("Info").get("Version"),
                                "Published": cur.get("Published"),
                                "Firm": cur.get("Firm"),
                                "Status": 1, "Flag": 0,
                                "Size":fsize,
                                "Descr": cur.get("Descr")}}, True)
                        print "插入新数据库成功"
                        '''
                        # "Firmname":cur["Filename"]}})
                        # "Class": cur.get("Info").get("Class"),
                        # 'Firmtype': 'FactoryControl' if firm in firmlist_fc else 'Not_FactoryControl'}}, True)

                        #print "插入完成"
                    break
                else:
                    collection.remove({"_id":cur["_id"]})


                    print "remove  success!"
            except Exception,e:
                print e
        except Exception, e:
            print e
            trytime -= 1
    else:
        print "status3"
        collection.update(
            {"_id": cur['_id']}, {"$set": {'Status': 3}})
        return

    print "download over........."


def download1():
    while 1:
        try:
            print "dao1111"



            if collection.find({'Status': 2}).count() > 0:  # !!!!!!!!!!!!!!!!!!! 应该是大于
                print "dao1112"
                print "Status:2\n\n\n\n"

                r_d = list(collection.find({'Status': 2}))[:7]
                if len(r_d) < 7:
                    download_url(r_d[-1])
                else:
                    print "dao1113"
                    for r in r_d[:5]:
                        #print '数量不足七个'
                        multiprocessing.Process(
                            target=download_url, args=(r,)).start()
                    download_url(r_d[-1])
                    download_url(r_d[-2])

            else:
                print "dao1114"
                if collection.find({'Status': 1,'Manufacturer':"Rockwell"}).count() > 0:
                    print "下载状态值为１的"
                    r_d = list(collection.find(
                        {'Status': 1,'Manufacturer':"Rockwell"}))[:7]
                    if len(r_d) < 7:
                        download_url(r_d[-1])
                    else:
                        for r in r_d[:5]:
                            #print '数量不足七个'

                            multiprocessing.Process(
                                target=download_url, args=(r,)).start()
                        download_url(r_d[-1])
                        download_url(r_d[-2])
                else:
                    return
        except Exception, e:
            print e






download1()


#!/usr/bin/python
#coding:utf-8
"""
clone memcache-server1 data to memcache-server2
Usage Example::
    from memcache_clone import memcache
    s = memcache('127.0.0.1',11211)
    s.con()
    #set(key,value,len,flags,express)
    s.set("key","value",5,0,0)
    #get(key) return list : list[value,value_len,flags]
    s.get("key")[0]
    #clone
    s.clone('127.0.0.1',11212)
"""
import socket
import os
import re
import sys
import time
class memcache(object):
    def __init__(self,address,port):
        self.address = address
        self.port = port
    def con(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.address,self.port))
    def get(self,key):
        get_command = "get %s\r\n" % key
        self.sock.send(get_command)
        buf = self.sock.recv(1024)
        tmp = ''
        data = ''
        while buf>0:
            data = data+buf
            if re.search('END\r\n',tmp+buf):
                break
            else:
                tmp = buf
                buf = self.sock.recv(1024)
        if data:
            data_list = data.split('\r\n')
            key_value = data_list[1]
            key_flags = data_list[0].split()[2]
            value_len = data_list[0].split()[3]
            key_data = [key_value,value_len,key_flags]
            return key_data
    def set(self,key,value,value_len,flags=0,express=0):
        key_len = len(key)
        get_command = "set %s %s %s %s\r\n%s\r\n" % (key,flags,express,value_len,value)
        self.sock.send(get_command)
        buf = self.sock.recv(1024)
        if buf != 'STORED\r\n':
            raise IndexError("store failed")
    def clone(self,c_addr,c_port):
        c = memcache(c_addr,c_port)
        c.con()
        now = int(time.time())
        self.sock.send("stats items\n")
        items_all = ''
        while True:
            items_all =  items_all+self.sock.recv(1024)
            if re.search('END',items_all):
                break
        result = re.search("STAT items:(\d+):.*?\nEND",items_all,re.M)
        if result:
            id_max = result.group(1)
            for id in range(1,int(id_max)+1):
                commond = "stats cachedump "+str(id)+" 0"+"\n"
                self.sock.send(commond)
                items = ''
                while True:
                    items =  items+self.sock.recv(1024)
                    if re.search('END',items):
                        break
                items = items.split('\r\n')
                for item in  items:
                    if re.search('ITEM ',item):
                        item_list = item.split(" ")
                        if len(item_list) == 6:
                            key = item_list[1]
                            value_len = item_list[2].replace('[','')
                            express_timestamp  = int(item_list[4])
                            if express_timestamp  < now:
                                express = "0"
                            else:
                                express = str(express_timestamp)
                            try:
                                line = [key,self.get(key),express]
                            except:
                                pass
                            else:
                                c.set(line[0],line[1][0],line[1][1],line[1][2],line[2])
                        else:
                            pass
        else:
            raise IndexError("no end")

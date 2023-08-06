#!/usr/bin/env python
# -*- coding:utf-8 -*-
import hashlib
import time
import os
import urllib
import socket

def send_sms(mobile_numbers=None,content=None):
    '''
    send SMS
    @param:
        mobile_numbers: the mobile phone,seperate by , in multi phones
        content: the SMS content
    '''
    url='http://www.haodou.com/api/sms_send_api.php'
    #post "time=1370243138&number=18684675581&content=test&from=sa
    unix_time=int(time.time())
    m = hashlib.md5()
    m.update("%sBell" % (str(unix_time)))
    phash = m.hexdigest()
    payload = {'hash':phash,'time':unix_time,'number':mobile_numbers,'content':content,'from':'sa'}
    try:
       import requests
       r = requests.post(url,data=payload)
       if  not r.status_code == requests.codes.ok:
            return (False,r.status_code)
       else:
            return (True,0)
    except Exception,err:
        return (False,-1)
"""
check the file wether expire or not
if the file's modify time is older than 7 day,return True,else return false
@params:
@filepath: filepath
@delta: the differ between two unix_time,at current,it's a constant
@returns: True if expired ,otherwise False
"""
def __expire(filepath,delta=604800):
    #delta=604800 #7 * 24 * 60 * 60
    current_time = time.time()
    modify_time = os.stat(filepath).st_mtime
    if current_time - modify_time >= delta:
        return True
    else:
        return False
    
"""
get all node list from current machine room
each machine room has a zabbix server
zabbix server scan all agent ,and get node' information,incuding hostname,ip address etc.
Parameters:
@machineroom: the abbr of machine room,at current bj means beijing ,tj means tianjin ,bj is default
@returns: return a list includeing node hostname,None if find any nodes
"""
def get_nodes(machineroom='bj'):

    if (not machineroom or machineroom not in ('tj','bj')):
        machineroom='bj'
  
    if machineroom == 'tj':
      #tianjin machine room NOT longer add new machine ,so simply use statis list
        return ['haodou50','haodou60','haodou61','haodou70','haodou71','haodou80','haodou81','haodou90']
        
    if machineroom == 'bj':
        url = 'http://haodou83.hd.com/hosts.txt'
     
      
    #first get it from local cache
    localfile=os.path.expanduser("~/.hosts.%s" % machineroom)
    if (os.path.exists(localfile) and not __expire(localfile)):
        return open(localfile).read().split('\n')[:-1] #remove trial blank item
    else:
        #create or update localfile    
        hosts = urllib.urlopen(url).read()
        #write to local cache
        open(localfile,'w').write(hosts)
        return hosts.split('\n')[:-1] #remove trial blank item
"""
convert ip address to hex-digigtal style
@returns: hexdecimal string
example:
127.0.0.1 --> 0x7f000001
"""    
def ip2int(ip):
    return "0x%s" % socket.inet_aton(ip).encode('hex')
    
"""
convert number-format ip address to string-format ipaddress
the number maybe decimal or hexdecimal
@returns: ip address string
example:
133169153 -> 127.0.0.1
0x7f000001 -> 127.0.0.1
"""
def int2ip(ip):
    #convert int to hexdecimal whether it is or not
    ipint=hex(ip)
    return socket.inet_ntoa(ipint[2:].zfill(8).decode('hex'))

       
    

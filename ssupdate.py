#!/usr/bin/env python
# coding: utf-8
import sys
import re
import os
import subprocess
import json
import copy
import getopt
import base64
import urllib.request

regRssaddr = '^http[s]{0,1}:\/\/\S*=\d{1}$'
regssrbase = '^ssr:\/\/\S*'
regssraddr = '^\S*:\d{0,5}:\S*:\S*:.*'

confpath = '/etc/shadowsocksr/rss/'
ssrpath = '/etc/shadowsocksr/'
version = 'ssrupdate version 0.1'


def usage():
    print("this a usage")
    pass


def base_adjust(basecode):
    basecode = basecode.replace(b'-', b'+')
    basecode = basecode.replace(b'_', b'/')
    s = len(basecode) % 4
    if (s != 0):
        basecode += b'=' * (4-s)
        pass
    return basecode


def parser_ssr_list(Rss):
    print(Rss)
    try:
        date = urllib.request.urlopen(Rss)
        ss = date.read()
    except InterruptedError:
        print("recvire data error")
        pass
    ssr_data = base64.b64decode(base_adjust(ss))
    return ssr_data.split(b'\n')


def load_default_config():
    if not os.path.exists(ssrpath+'config_def.json'):
        conf = json.load(open(ssrpath+'config.json', 'r'))
        json.dump(conf, open(ssrpath+'config_def.json', 'w'), ensure_ascii=False, indent=4)
    else:
        conf = json.load(open(ssrpath+'config_def.json', 'r'))
    return conf


def parser_ssr_addr(jsondata, ssraddr):
    if (re.match(regssrbase, str(ssraddr, encoding='utf-8'))):
        data = base_adjust(ssraddr[6:])
        data = base64.b64decode(data)
        if (data.find(b'/?')):
            data = data.split(b'/?')
            data1 = data[0].split(b':')
            jsondata['server'] = str(data1[0], encoding='utf-8')
            jsondata['server_port'] = int(data1[1])
            jsondata['protocol'] = str(data1[2], encoding='utf-8')
            jsondata['method'] = str(data1[3], encoding='utf-8')
            jsondata['obfs'] = str(data1[4], encoding='utf-8')
            jsondata['password'] = str(base64.b64decode(base_adjust(data1[5])),\
                                       encoding='utf-8')
            data2 = data[1].split(b'&')

            tmp = data2[0].split(b'=')
            if(len(tmp[1]) != 0):
                jsondata['obfs_param'] = str(base64.b64decode(base_adjust(tmp[1])), encoding='utf-8')

            tmp = data2[1].split(b'=')
            if(len(tmp[1]) != 0):
                jsondata['protocol_param'] = str(base64.b64decode(base_adjust(tmp[1])), encoding='utf-8')

            tmp = data2[2].split(b'=')
            if(len(tmp) != 0):
                jsondata['remarks'] = str(base64.b64decode(base_adjust(tmp[1])), encoding='utf-8')

            tmp = data2[3].split(b'=')
            if(len(tmp) != 0):
                jsondata['group'] = str(base64.b64decode(base_adjust(tmp[1])), encoding='utf-8')
                pass
        return jsondata


def write_ssr_config_file(ssr):
    ssrdata = load_default_config()

    ssrdata = parser_ssr_addr(ssrdata, ssr)

    group = 'defaults'
    if 'group' in ssrdata:
        group = ssrdata['group']
        del ssrdata['group']
        pass

    ssrgrp = {}
    if os.path.exists(confpath+group+'.json'):
        ssrgrp = json.load(open(confpath+group+'.json', 'r'))
        pass

    ssrgrp[str(len(ssrgrp)+1)] = ssrdata

    json.dump(ssrgrp, open(confpath+group+'.json', 'w'), ensure_ascii=False, indent=4)
    return True


def update_rss(ssrsite):
    data = parser_ssr_list(ssrsite)[2:]
    for x in range(len(data)-1):
        write_ssr_config_file(data[x])
        pass
    print('Completed!')
    pass


def ping_test(server):
    cmd = 'ping -W 1 -c 2 ' + server
    res = subprocess.getstatusoutput(cmd)
    if (res[0] == 0):
        res = re.findall("time=.*ms", res[1])
        return res[1]
    return "faile"


def server_speed(group, cid):
    if os.path.exists(confpath + group + '.json'):
        data = json.load(open(confpath+group+'.json', 'r'))
        s = ping_test(data[cid]['server'])
        remark = ''
        if 'remarks' in data[cid]:
            remark = data[cid]['remarks']
        print('id:'+cid+' server://'+data[cid]['server']+' '+s+' '+remark)
        return True


def server_speed_group(group):
    pass


def group_list():
    grp = os.listdir(confpath)
    for e in grp:
        d = json.load(open(confpath+e, 'r'))
        print('[Group: '+e.split('.')[0]+'] [Range: 1~'+str(len(d))+']')
    pass


def show_group(grp):
    if os.path.exists(confpath+grp+'.json'):
        data = json.load(open(confpath+grp+'.json', 'r'))
        for v in data:
            remark = ''
            if 'remarks' in data[v]:
                remark = data[v]['remarks']
                pass
            print('id:'+v+' '+data[v]['server']+' '+remark)
            pass
        pass
    else:
        print('group is not exists')
    pass


def delete_group(grp):
    if os.path.exists(confpath+grp+'.json'):
        os.remove(confpath+grp+'.json')
        pass
    pass


def switch_config(grp, id):
    print(grp)
    if os.path.exists(confpath+grp+'.json'):
        data = json.load(open(confpath+grp+'.json', 'r'))
        if id in data:
            new_config = copy.copy(data[id])
            del new_config['remarks']
            json.dump(new_config, open(ssrpath+'config.json', 'w'), ensure_ascii=False, indent=4)
            ret = subprocess.getstatusoutput('systemctl is-active shadowsocksr@config')
            if ret[1] == 'active':
                os.system('systemctl restart shadowsocksr@config')
                print('restart shadowsocksr@config')
                pass
            print('completed')
            pass
        else:
            print('id is not exists')
        pass
    else:
        print('group is not exists')
    pass


def main(argv):

    if not os.path.exists(confpath):
        os.mkdir(confpath)

    try:
        opt, arg = getopt.getopt(argv[1:], "hvgu:t:s:d:c:",\
                                 ["help", "version", "rss=", "ssr="])
    except IOError:
        print("error")
        pass
    for n, v in opt:
        if n in ['-v', '-version']:
            print(version)
            pass
        elif n in ('-h', '--help'):
            usage()
            pass
        elif n == '-t':
            s = v.split('/')
            server_speed(s[0], s[1])
        elif (n == '-g'):
            group_list()
        elif n == '--rss':
            update_rss(v)
        elif n == '-s':
            show_group(v)
        elif n == '-c':
            s = v.split('/')
            switch_config(s[0], s[1])
        pass
    pass


if __name__ == '__main__':
    if (os.name == 'posix') and os.path.isdir('/etc/shadowsocksr'):
        main(sys.argv)
        pass
    else:
        print('not support os platrom or ssr not installed')
    pass

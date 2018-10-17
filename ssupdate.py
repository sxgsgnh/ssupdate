#!/usr/bin/env python
# coding: utf-8
import sys
import re
import json
import copy
import getopt
import base64
import urllib.request

test = b"ssr://Y24wMi5oa2JuLm1sOjQ1MzU3Om9yaWdpbjphZXMtMjU2LWNmYjpwbGFpbjpiMWhtU1hRMS8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPU1TRG10N0hsbkxQcG1MX3BoNHprdXBIa3VLM292YXdnTlRBd1RXSndjeUF5NVlDTklPaW5odW1pa2VXa3AtYTFnZW1Iai1pS2d1ZUN1U0FnNXJpNDVvaVA1NVNvNW9pMzZLLTM1TDJfNTVTbzVMaUw2WjJpNmFhWjVyaXY1TGlUNTdxX0lDMGc2YWFaNXJpdlNFdFVNREVnTVVkaWNITWdNQzQ0NVlDTklFNWxkR1pzYVhnZ1NFSlBJRlJXUWcmZ3JvdXA9YzNOeVkyeHZkV1E"
ssrsite = 'https://www.coit.ml/link/gvEUn6gIN6IKOX7I?mu=0'
regRssaddr = '^http[s]{0,1}:\/\/\S*=\d{1}$'
regssrbase = '^ssr:\/\/\S*'
regssraddr = '^\S*:\d{0,5}:\S*:\S*:.*'


def base_adjust(basecode):
    basecode = basecode.replace(b'-', b'+')
    basecode = basecode.replace(b'_', b'/')
    s = len(basecode) % 4
    if (s != 0):
        basecode += b'=' * (4-s)
        pass
    return basecode


def parser_ssr_list(Rss):
    try:
        date = urllib.request.urlopen(ssrsite)
        ss = date.read()
    except InterruptedError:
        print("recvire data error")
        pass
    ssr_data = base64.b64decode(base_adjust(ss))
    return ssr_data.split(b'\n')


def load_default_config():
    try:
        ss = json.load(open("/etc/shadowsocksr/config.json", 'r'))
    except IOError:
        print("default confige not exist , plase check shadowsocksr is installed")
    return ss

def parser_ssr_addr(jsondata, ssraddr):
    if (re.match(regssrbase, str(ssraddr, encoding='utf-8'))):
        data = base_adjust(ssraddr[6:])
        data = base64.b64decode(data)
        if (data.find(b'/?')):
            data = data.split(b'/?')
            data1 = data[0].split(b':')
            jsondata['server'] = str(data1[0], encoding='utf-8')
            jsondata['server_port'] = str(data1[1], encoding='utf-8')
            jsondata['protocol'] = str(data1[2], encoding='utf-8')
            jsondata['method'] = str(data1[3], encoding='utf-8')
            jsondata['obfs'] = str(data1[4], encoding='utf-8')
            jsondata['password'] = str(base64.b64decode(base_adjust(data1[5])), encoding='utf-8')
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
            return jsondata
    pass

print(parser_ssr_addr(load_default_config(), test))

def main(argv):
    try:
        arg = getopt.getopt(argv[1:],"hv",["help","version"])
    except IOError:
        print("error")
        pass
    print(arg)
    pass


if __name__ == '__main__':
    #main(sys.argv)
    pass

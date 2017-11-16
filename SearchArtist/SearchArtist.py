# coding:utf-8

import requests
import re
import base64
from Crypto.Cipher import AES
import os
import json
import xlwt
import xlrd
from xlutils.copy import copy
import time
import datetime
from concurrent import futures
import logging


def searchBaidu(artist, alias):
    try:
        logging.info('search Baidu,artist:%s\talias:%s' % (artist, alias))
        for i in range(3):
            if searchBaiduByPage(artist, alias, i):
                return True
                exit
        return False
    except Exception as e:
        logging.error(e)


def searchBaiduByPage(artist, alias, page):
    try:
        page = page * 20
        r = requests.get('http://music.baidu.com/search/artist?key=%s&start=%d&size=20&third_type=0' % (alias, page))
        r.encoding = 'utf-8'
        artist_re = re.compile("artist = '(.*)' target='_blank'>")
        m = re.findall(artist_re, r.text)
        if artist in m:
            return True
        else:
            return False
    except Exception as e:
        logging.error(e)

# 由于网易云音乐歌曲评论采取AJAX填充的方式所以在HTML上爬不到，需要调用评论API，而API进行了加密处理，下面是相关解决的方法


def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]


def search163(artist, alias):
    try:
        logging.info('search 163,artist:%s\talias:%s' % (artist, alias))
        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        headers = {'Cookie': 'appver=1.5.0.75771;', 'Referer': 'http://music.163.com/'}
        text = {'type': '100', 's': alias, 'offset': '0', 'total': 'true', 'limit': '100'}
        modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        nonce = '0CoJUm6Qyw8W8jud'
        pubKey = '010001'
        text = json.dumps(text)
        secKey = createSecretKey(16)
        encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
        encSecKey = rsaEncrypt(secKey, pubKey, modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        res = requests.post(url, headers=headers, data=data).json()['result']
        if res['artistCount'] > 0:
            for j in res['artists']:
                if j['name'] == artist:
                    return True
                    exit
        return False
    except Exception as e:
        logging.error(e)


def searchQQ(artist, alias):
    try:
        logging.info('search QQ,artist:%s\talias:%s' % (artist, alias))
        for i in range(3):
            if searchQQByPage(artist, alias, i):
                return True
                exit
        return False
    except Exception as e:
        logging.error(e)


def searchQQByPage(artist, alias, page):
    try:
        res = requests.get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp?&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=%d&n=20&w=%s' % (page + 1, alias))
        for song in json.loads(res.text.strip('callback()'))['data']['song']['list']:
            # 依次从songlist中校验歌曲的歌手
            if song['singer'][0]['name'] == artist:
                return True
                exit
        return False
    except Exception as e:
        print e
        logging.error(e)


def searchArtist(artist, aliasList):
    try:
        logging.info('begin search artist:%s\talias:%s' % (artist, aliasList))
        aliasResult = []
        for alias in aliasList.split('|'):
            if searchBaidu(artist, alias) or search163(artist, alias) or searchQQ(artist, alias):
                logging.info('%s\tmatch\t%s' % (alias, artist))
                aliasResult.append(alias)
            else:
                logging.warn('%s\tnot match\t%s' % (alias, artist))
        aliasResult = '|'.join(aliasResult)
        logging.info('end search artist:%s\talias:%s' % (artist, aliasResult))
        return artist, aliasResult

    except Exception as e:
        logging.error(e)


def readAliasFromExcel(aliasFile):
    try:
        logging.info('begin read:\t%s' % aliasFile)
        res = {}
        rb = xlrd.open_workbook(aliasFile)
        rs = rb.sheets()[0]
        nrows = rs.nrows
        for i in range(1, nrows):
            artist = rs.cell(i, 2).value
            aliasList = rs.cell(i, 3).value

            # float数字处理
            if isinstance(aliasList, float):
                if aliasList == int(aliasList):
                    aliasList = str(int(aliasList))
                else:
                    aliasList = str(aliasList)
            res[artist] = aliasList
        logging.info('end read:\t%s' % aliasFile)
        return res

    except Exception as e:
        logging.error(e)


def writeAliasToExcel(aliasFile, aliasResultFile, artistAliasResult):
    try:
        logging.info('begin write:\t%s' % aliasResultFile)
        rb = xlrd.open_workbook(aliasFile)
        rs = rb.sheets()[0]
        wb = copy(rb)
        ws = wb.get_sheet(0)
        nrows = rs.nrows
        for i in range(1, nrows):
            artist = rs.cell(i, 2).value
            ws.write(i, 4, artistAliasResult[artist])
        wb.save(aliasResultFile)
        logging.info('end write:\t%s' % aliasResultFile)
    except Exception as e:
        logging.error(e)


def mutiSearch(max_workers=4):
    try:
        # max_workers并发数，默认4
        # with futures.ProcessPoolExecutor(max_workers=max_workers) as executor:  #多进程
        with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:  # 多线程
            for artist, aliasResult in executor.map(searchArtist, artistAliasDict.keys(), artistAliasDict.values()):
                artistAliasResult[artist] = aliasResult
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    # 文本日志配置
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] [%(filename)s][line:%(lineno)d] [%(levelname)s] %(message)s',
                        filename='%s.log' % datetime.datetime.now().strftime('%Y-%m-%d'),
                        filemode='w')  # 文件写入模式，a为追加写入，w为重新写入

    # 控制台日志配置
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(filename)s][line:%(lineno)d] [%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    aliasFile = u'歌手别名.xlsx'  # 原始歌手、别名excel文件
    aliasResultFile = 'Result_%s.xls' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')  # 歌手、别名搜索结果文件
    artistAliasDict = readAliasFromExcel(aliasFile)  # 读取搜索歌手、别名dict
    artistAliasResult = {}  # 歌手、别名搜索结果dict
    mutiSearch()  # 多进程/线程并发搜索
    writeAliasToExcel(aliasFile, aliasResultFile, artistAliasResult)  # 写入歌手、别名信息

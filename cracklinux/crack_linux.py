#!/usr/bin/env python
# coding: utf8

import sys
import os
import crypt


def test_pass(crypt_passwd, dict_list):
    """
    @crypt_passwd: encrypted password
    @dict_list: password list
    """
    salt = crypt_passwd[:12]
    for word in dict_list:
        crypt_word = crypt.crypt(word.strip(), salt)
        if crypt_passwd == crypt_word:
            print '[+] Found Password: %s' % word
            return
    print '[-] Password Not Found.'


def main(passwd_file, dict_file):
    """
    @passwd_file: to crack the account password file
    @dict_file: password dictionary
    """
    with open(dict_file) as d_fp:
        dict_list = d_fp.readlines()

    with open(passwd_file) as fp:
        for line in fp.readlines():
            if not line.startswith('#') and ':' in line:
                user = line.split(':')[0]
                crypt_passwd = line.split(':')[1].strip()
                if not crypt_passwd.startswith('$'):
                    print '[*] Password Format Bad!'
                    continue
                print '[*] Cracking Password For: %s' % user
                test_pass(crypt_passwd.strip(), dict_list)


if __name__ == '__main__':
    platform = sys.platform
    if not platform.startswith('linux'):
        print 'Need linux system run.'
        exit(0)
    if len(sys.argv) != 3:
        print 'Usage: %s <password.txt> <dictionary.txt>' % sys.argv[0]
        exit(0)
    if not os.path.isfile(sys.argv[1]):
        print '"%s" file does not exist!!!' % sys.argv[1]
        exit(0)
    if not os.path.isfile(sys.argv[2]):
        print '"%s" file does not exist!!!' % sys.argv[2]
        exit(0)
    main(sys.argv[1], sys.argv[2])

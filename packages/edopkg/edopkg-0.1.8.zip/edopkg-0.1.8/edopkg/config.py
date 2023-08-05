# encoding: utf-8

import os
import sys

VERSION = '0.1.8'

EDO_CONFIG_PATH = os.path.normpath(os.path.expanduser(r'~/.edopkgrc'))
SECTION = 'dev'
OC_API = r'https://oc-api.everydo.cn'
ACCOUNT='zopen'
INSTANCE = 'default'
USERNAME='admin'
CLIENT_ID = 'test'
CLIENT_SECRET = '022127e182a934dea7d69s10697s8ac2'
HELP_INFO = u'''
edopkg version  %(VERSION)s

使用edopkg，可以将文件系统中的软件包和易度系统中的软件包同步。
服务器配置文件位于 ''%(PATH)s''

可使用如下命令:
edopkg server: 查看和设置服务器配置
edopkg config: 添加和修改服务器配置
edopkg clone:  复制一个软件包
edopkg pull:   下载一个软件包
edopkg push:   上传一个软件包
''' % {'VERSION':VERSION, 'PATH':EDO_CONFIG_PATH}

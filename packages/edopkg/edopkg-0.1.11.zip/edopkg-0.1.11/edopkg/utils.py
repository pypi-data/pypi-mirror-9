# encoding: utf-8

import urllib

def parse_ocapi(oc_api):
    try:
        scheme, rest = urllib.splittype(oc_api)
        host = urllib.splithost(rest)[0]
        h3, port = urllib.splitport(host)
        h2 = '.'.join(h3.split('.')[-2:])
        online = ['everydo.cn', 'easydo.cn', 'everydo.com']
        host = 'oc-api.' + h2 if h2 in online else host + '/oc_api'
        return scheme + '://' + host
    except e:
        raise e

def complie_script(script):
   # 组装为函数
    lines = []
    for line in script.splitlines():
        lines.append('   ' + line)
    code = """def complie_script(s):
%s"""   % ('\n'.join(lines))
    compile(code, '', 'exec')

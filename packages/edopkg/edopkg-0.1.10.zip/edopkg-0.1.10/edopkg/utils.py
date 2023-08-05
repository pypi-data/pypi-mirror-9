# encoding: utf-8

from urlparse import urlparse

def parse_ocapi(oc_api):
    scheme, host, path = urlparse(oc_api)[:3]
    short = '.'.join(''.join(host.split(':')[:1]).split('.')[1:])
    if short in ['everydo.cn', 'easydo.cn', 'everydo.com']:
        host = 'oc-api.' + short
    else:
        host = host + '/oc_api'
    print scheme + '://' + host
    return scheme + '://' + host

def complie_script(script):
   # 组装为函数
    lines = []
    for line in script.splitlines():
        lines.append('   ' + line)
    code = """def complie_script(s):
%s"""   % ('\n'.join(lines))
    compile(code, '', 'exec')

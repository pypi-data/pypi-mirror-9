# encoding: utf-8
import os
import sys
import ConfigParser
import yaml
import getpass
from edopkg import config, pyaml
from config import EDO_CONFIG_PATH, OC_API, SECTION, ACCOUNT, INSTANCE, \
USERNAME, CLIENT_ID, CLIENT_SECRET, HELP_INFO
from utils import get_wo_client
from package import EdoPackage

reload(sys)
sys.setdefaultencoding('utf-8')

PKG_COMMAND = ['clone', 'push', 'pull', 'server', 'config']

def main():

    # 命令解析
    cmd = ''.join(sys.argv[1:2])
    if cmd == '':
        print HELP_INFO
    elif cmd == 'server':
        section = ''.join(sys.argv[2:3])
    elif cmd == 'clone':
        pkg_name = sys.argv[2]
    else:
        path_filter = ''.join(sys.argv[2:3])

    #  获取配置对象
    edo_configparse = ConfigParser.ConfigParser()
    if not os.path.exists(EDO_CONFIG_PATH):
        #  初始化配置文件
        section= read_init_section(SECTION)
        oc_api, account, instance, username, password = read_detail_inputs()
        edo_configparse.add_section('edopkg')
        edo_configparse.set('edopkg', 'server', section)
        save_config(edo_configparse, EDO_CONFIG_PATH, section, oc_api, account,
                    instance, username, password)
    edo_configparse.read(EDO_CONFIG_PATH)

    #  执行非同步命令
    if cmd == '':
        return
    elif cmd not in PKG_COMMAND:
        print 'command error'
        return
    elif cmd == 'server':
        if section:
            # 重新设置服务器配置
            edo_configparse.set('edopkg', 'server', section)
            edo_configparse.write(open(EDO_CONFIG_PATH, 'w'))
            print u' 默认配置已经修改为：' + section
        else:
            #  显示当前服务器配置
            print_server_config(edo_configparse)
        return
    elif cmd == 'config':
        print_server_config(edo_configparse)
        section, action = read_section_input(edo_configparse)
        if action == 'modify':
            edo_config = dict(edo_configparse.items(section))
            oc_api, account, instance, username, password = read_detail_inputs(
                oc_api=edo_config['oc_api'],
                account=edo_config['account'],
                instance=edo_config['instance'],
                username=edo_config['username']
            )
        else:
            oc_api, account, instance, username, password = read_detail_inputs()
        save_config(edo_configparse, EDO_CONFIG_PATH, section, oc_api, account,
                    instance, username, password)
        return

    #  确认同步操作
    if cmd in ['push', 'pull'] and not confirm_cmd(cmd):
        print u'同步被取消'
        return

    #  计算local_root
    if cmd == 'clone':
        local_root = os.path.abspath(pkg_name)
        if os.path.exists(local_root):
            print 'package already exited'
            return
    else:
        local_root = find_package_root()
        if not local_root:
            print 'can not find the package'
            return
        # 相对路径转换: 计算path_filter相对于local_root的子路径
        abspath = os.path.abspath(path_filter) if path_filter else local_root
        path_filter = '' if abspath == local_root else os.path.relpath(abspath, local_root)

    # 生成服务端连接
    section = edo_configparse.get('edopkg', 'server')
    edo_config = dict(edo_configparse.items(section))
    wo_client = get_wo_client(  edo_config['oc_api'],
                                edo_config['client_id'],
                                edo_config['client_secret'],
                                edo_config['account'],
                                edo_config['instance'],
                                edo_config['username'],
                                edo_config['password'])

    # 初始化包管理器
    edo_pkg = EdoPackage(wo_client, local_root)

    # 执行同步命令
    if cmd == 'pull':
        edo_pkg.pull(path_filter)
    elif cmd == 'push':
        edo_pkg.push(path_filter)
    elif cmd == 'clone':
        edo_pkg.clone()

def print_server_config(edo_configparse):
    active_section = edo_configparse.get('edopkg', 'server')
    info_template = u'%s, 账号 %s, 站点 %s '
    for section in edo_configparse.sections():
        if section == 'edopkg':
            continue
        oc_api = edo_configparse.get(section, 'oc_api')
        account = edo_configparse.get(section, 'account')
        instance = edo_configparse.get(section, 'instance')
        if section == active_section:
            head = u'  * %s:' % section
        else:
            head = u'    %s:' % section
        print ''.join([head.ljust(20), info_template % (oc_api, account, instance)])

def save_config(edo_configparse, path, section, oc_api, account, instance, username, password):
    if section not in edo_configparse.sections():
        edo_configparse.add_section(section)
    edo_configparse.set(section, 'client_id', CLIENT_ID)
    edo_configparse.set(section, 'client_secret', CLIENT_SECRET)
    edo_configparse.set(section, 'oc_api', oc_api)
    edo_configparse.set(section, 'account', account)
    edo_configparse.set(section, 'instance', instance)
    edo_configparse.set(section, 'username', username)
    edo_configparse.set(section, 'password', password)
    edo_configparse.write(open(path, 'w'))
    print u' 配置文件已保存到：%s ' % path

def confirm_cmd(cmd):
    print u'%s 命令会删除不存在的内容，您确定要继续么？' % cmd
    sys.stdout.write(u'您的选择[y/n](y:继续 | n:取消):')
    return raw_input().lower() == 'y'

def read_section_input(edo_configparse):
    print u'''您可以选择：
    1.修改已存在的配置
    2.新建一个配置
    '''
    sys.stdout.write(u'您的选择[1/2](或输入其他命令退出)：')
    num = raw_input()
    if num not in ['1', '2']:
        sys.exit(0)
    # 检查用户输入的配置名
    if num == '1':
        while True:
            sys.stdout.write(u'请输入要修改的配置:')
            section = raw_input()
            if section not in edo_configparse.sections():
                print u'不存在此配置，请确认后重新输入'
            else:
                break
    else:
        while True:
            sys.stdout.write(u'请输入配置名：')
            section = raw_input()
            if section in edo_configparse.sections():
                print u'配置已存在，请确认后重新输入'
            else:
                break
    action = 'modify' if num == '1' else 'add'
    return section, action

def read_init_section(section):
    print u'''
 -----------------------------
 需要输入配置信息以进行初始化
 -----------------------------'''
    section = get_input(u'请输入配置名', default=section)
    return section

def read_detail_inputs(oc_api=OC_API, account=ACCOUNT,instance=INSTANCE,
                       username=USERNAME):
    print u'''
 -----------------------------
 请输入具体的配置数据
 -----------------------------
 字段的具体含义：

 oc_api: oc服务地址
 account: 公司(子域名)名称
 instance: 站点实例， 只有一个站点时为default
 username: 用户名
 password: 密码
 -----------------------------
 请输入数据：
 '''
    while True:
        oc_api = get_input('oc_api', default=oc_api)
        account = get_input('account', default=account)
        instance = get_input('instance', default=instance)
        username = get_input('username', default=username)

        print u'''
 -----------------------------
 您的输入：
 -----------------------------'''
        print ' oc_api: %s' % oc_api
        print ' account: %s' % account
        print ' instance: %s' % instance
        print ' username: %s' % username
        print u'''
 -----------------------------
 您确认要输入的是以上的数据么？[y/n]（确认：y | 重新输入：n）：'''
        if raw_input().lower() == 'y':
            break
        else:
            print u'请重新输入数据:'

    while True:
        password = getpass.getpass('password: ')
        confirm_pwd = getpass.getpass('confirm password: ')
        if password == confirm_pwd:
            break
        else:
            print u'两次输入的密码不一致,  请重新输入'
    return oc_api, account, instance, username, password

def get_input(msg, default =''):
    msg = ' %s[%s]: ' % (msg, default)
    sys.stdout.write(msg)
    input_info = raw_input()
    return input_info if input_info else default

def find_package_root():
    # 优先在当前目录下查找
    base_path = os.getcwd()
    config_path = os.path.join(base_path, 'config.yaml')
    # 不存在时往上级查找
    while not os.path.exists(config_path):
        if base_path != os.path.dirname(base_path):
            base_path = os.path.dirname(base_path)
            config_path = os.path.join(base_path, 'config.yaml')
        else:
            # 到达根时退出
            return False
    return base_path

if __name__ == '__main__':
    main()

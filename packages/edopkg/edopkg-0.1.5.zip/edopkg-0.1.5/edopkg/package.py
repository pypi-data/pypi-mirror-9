# encoding: utf-8
import os
import sys
import shutil
import yaml
import traceback
from edopkg import pyaml
from utils import complie_script

# 优先检测代码并上传， 最后上传form
OBJ_CATS = ['script', 'workflow', 'mdset', 'rule', 'template',
        'stage','skin', 'resource', 'form']

class EdoPackage:

    def __init__(self, wo_client, local_root):
        self.remote_pkg = wo_client.package
        self.local_root = local_root
        self.pkg_name = os.path.basename(local_root)

    def pull(self, path_filter=''):
        sys.stdout.write('\rpulling...')
        if not path_filter or path_filter == 'config.yaml':
            pkg_info = self.remote_pkg.get(self.pkg_name, detail=False)
            self.write_yaml('config.yaml', pkg_info)

        # 写入软件包对象
        for obj_cat in OBJ_CATS:
            obj_folder = obj_cat + 's'

            # 过滤
            if path_filter and not path_filter.startswith(obj_folder):
                continue

            # 计算文件的过滤条件
            filename_filter = path_filter[len(obj_folder) + 1:]

            #  删除同步：清空本地文件夹
            if not filename_filter:
                abs_folder_path = os.path.join(self.local_root, obj_folder)
                if os.path.exists(abs_folder_path):
                    shutil.rmtree(abs_folder_path)

            # 逐个对象同步
            for obj_name in getattr(self.remote_pkg, 'list_' + obj_folder)(self.pkg_name):
                self.pull_obj(obj_cat, obj_name, obj_folder, filename_filter)

        print '\rpull successful'.ljust(60)

    def push(self, path_filter=''):
        sys.stdout.write('\rpushing...')

        if not path_filter or path_filter == 'config.yaml':
            pkg_info = self.read_yaml('config.yaml')
            pkg_list = self.remote_pkg.list()
            if self.pkg_name not in pkg_list:
                status = self.remote_pkg.new(self.pkg_name, pkg_info)
            status = self.remote_pkg.set(self.pkg_name, pkg_info)

        # 读取软件包对象
        for obj_cat in OBJ_CATS:
            obj_folder = obj_cat + 's'
            # 过滤
            if path_filter and not path_filter.startswith(obj_folder):
                continue
            filename_filter = path_filter[len(obj_folder) + 1:]


            # 删除同步：删除远程的对象
            if not filename_filter:
                for obj_name in getattr(self.remote_pkg, 'list_' + obj_folder)(self.pkg_name):
                    if obj_cat == 'resource':
                        self.remote_pkg.remove_resource(self.pkg_name, obj_name)
                    else:
                        getattr(self.remote_pkg, 'remove_' + obj_cat)(obj_name)

            # 判断是否存在文件夹
            cat_path = os.path.join(self.local_root, obj_folder)
            if not os.path.exists(cat_path):
                continue

            # 获取同步列表
            obj_list = os.listdir(cat_path)

            # 根据文件类型进行过滤
            obj_list = filter(lambda f:not f.startswith(('.', '~')), obj_list)
            obj_list = filter(lambda f:not f.endswith(('.bak', '~')), obj_list)
            if obj_cat == 'template':
                obj_list == filter(lambda f:f.endswith('.pt'), obj_list)
            elif obj_cat != 'resource':
                obj_list == filter(lambda f:f.endswith('.yaml'), obj_list)

            # 对于表单进行特殊处理
            if obj_cat == 'form':
                first_list, after_list = [], []
                for obj_filename in obj_list:
                    obj_data = self.read_yaml(os.path.join(self.local_root, cat_path, obj_filename))
                    # 优先上传类型为DataContainer的表单
                    if ''.join(obj_data['object_types']) == 'DataContainer':
                        first_list.append(obj_filename)
                    else:
                        after_list.append(obj_filename)
                # 合并列表
                obj_list = first_list + after_list

            # 逐个上传
            for obj_filename in obj_list:
                # 过滤
                if filename_filter and not obj_filename.startswith(filename_filter):
                    continue

                #  同步
                if os.path.isdir(os.path.join(self.local_root, obj_folder, obj_filename)):
                    self.push_folder(os.path.join(obj_folder, obj_filename))
                else:
                    self.push_obj(obj_cat, obj_folder, obj_filename)

        print '\rpush successful'.ljust(60)

    def push_folder(self, obj_folder, obj_cat='resource'):
        for obj_filename in os.listdir(os.path.join(self.local_root, obj_folder)):
            if os.path.isdir(os.path.join(self.local_root, obj_folder, obj_filename)):
                self.push_folder(os.path.join(obj_folder, obj_filename))
            else:
                self.push_obj(obj_cat, obj_folder, obj_filename)

    def pull_obj(self, obj_cat, obj_name, obj_folder, filename_filter):
        # 读取文件名
        if obj_cat == 'resource':
            obj_filename = os.path.normpath(obj_name)
        elif obj_cat == 'template':
           obj_filename = obj_name.split(':')[1] + '.pt'
        else:
           obj_filename = obj_name.split(':')[1] + '.yaml'

        # 过滤
        if filename_filter and not obj_filename.startswith(filename_filter):
            return

        # 更新提示
        sys.stdout.write('\rpulling ' + obj_name.ljust(60))

        # 下载数据
        if obj_cat == 'resource':
            obj_data = self.remote_pkg.get_resource(self.pkg_name, path = obj_name)
        else:
            obj_data = getattr(self.remote_pkg, 'get_' + obj_cat)(obj_name)

        # 写入数据
        obj_path = os.path.join(obj_folder, obj_filename)

        # 判断文件夹是否存在
        dirname = os.path.dirname(os.path.join(self.local_root, obj_path))
        if not os.path.exists( dirname):
            os.makedirs(dirname)

        if obj_cat == 'template':
            self.write_file(obj_path, obj_data['template'])
        elif obj_cat == 'resource':
            self.write_response(obj_path, obj_data)
        else:
            self.write_yaml(obj_path, obj_data)

    def push_obj(self, obj_cat, obj_folder, obj_filename):
        # 更新提示
        sys.stdout.write('\rpushing ' + obj_filename.ljust(60))

        obj_name = obj_filename.split('.')[0]
        # 读取数据
        obj_path = os.path.join(obj_folder, obj_filename)
        if obj_cat == 'template':
            obj_data = self.read_template(obj_name, obj_path)
        elif obj_cat == 'resource':
            obj_stream = self.read_stream(obj_path)
        else:
            obj_data = self.read_yaml(obj_path)

        # 代码检测
        if obj_cat == 'script':
            script = obj_data.get('script', '')
            try:
                complie_script(script)
            except:
                print u'\n脚本代码 %s 存在错误，以下是错误信息：' % obj_filename
                traceback.print_exc(0)
                print u'\n上传中止'
                sys.exit(2)

        # 上传数据
        if obj_cat == 'template':
            status = getattr(self.remote_pkg, 'register_' + obj_cat)(
                self.pkg_name, obj_data, overwrite = True)
        elif obj_cat == 'resource':
            remote_path = obj_filename.replace(os.sep, '/')
            status = self.remote_pkg.add_resource(
                self.pkg_name, remote_path, obj_stream, overwrite=True)
        else:
            status = getattr(self.remote_pkg, 'register_' + obj_cat)(
                self.pkg_name, obj_data, overwrite = True)

    def write_yaml(self, path, data):
        open(os.path.join(self.local_root, path), 'wb').write(pyaml.dump(data))

    def write_file(self, path, data='', response=''):
        open(os.path.join(self.local_root, path), 'wb').write(data)

    def write_response(self, response):
        with open(path, 'wb') as f:
            for block in response.iter_content(chunk_size=1024):
                if not block:
                    break
                f.write(block)
                f.flush()

    def read_yaml(self, path):
        return yaml.load(open(os.path.join(self.local_root, path)).read())

    def read_template(self, obj_name, path):
        data = open(os.path.join(self.local_root, path)).read()
        return {'name':obj_name, 'title':obj_name, 'template':data}

    def read_stream(self, path):
        return open(os.path.join(self.local_root, path))




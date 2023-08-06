========================
edopkg: 易度软件包同步
========================

用途
==========
``edopkg`` 是易度提供给开发者的一个命令行工具，
方便基于文件系统进行软件包开发。

这个工具，可以直接将易度软件包导入、导出到文件系统，进行代码同步。

安装
==========
使用python的pip命令进行安装::

    pip install edopkg

安装之后可以使用 ``edopkg`` 进行操作::

   # edopkg 
   使用edopkg，可以将文件系统中的软件包和易度系统中的软件包同步。
   服务器配置文件位于 ``~/.edopkgrc``

   可使用如下命令:

   edopkg server: 查看和设置服务器
   edopkg config: 设置服务器配置
   edopkg clone:  复制一个软件包
   edopkg pull:   下载一个软件包
   edopkg push:   上传一个软件包

使用方法
===========
需要配置服务器连接信息才能使用，详细见最后一节。
如果没有配置，会自动交互配置。

另外，必须拥有软件包的开发权限，才能进行软件包的同步操作。

clone: 复制一个软件包
-----------------------
从线上下载一个名为zopen.plans的软件包::

  edopkg clone zopen.plans

执行后将会在使用默认配置，在当前文件夹下创建zopen.plans文件夹，并下载软件包数据

或者通过‘-s 选项指定要使用的配置，其余同步命令均支持此用法::

  edopkg clone zopen.plans -s dev

pull: 下载
-------------------------------

更新整个软件包::

  edopkg pull zopen.plans

或者进入到软件包目录内::

  edopkg pull

执行后程序会自动识别出省略的软件包名，除clone外的同步命令均支持省略软件包名的用法

更新全部表单::

  edopkg pull zopen.plans/forms

仅仅更新一个表单定义::

  edopkg pull zopen.plans/forms/plans.yaml

注意：下载软件包的时候，会覆盖本地的修改。 

push: 上传
---------------------

提交整个软件包：:

  edopkg push zopen.plans

提交全部表单::

  edopkg push zopen.plans/forms

仅仅提交一个表单定义::

  edopkg push zopen.plans/forms/plans.yaml

注意：上次软件包的时候，服务器上的修改会被删除。

server 设置当前服务器
----------------------------
查看当前的设置::

  # edopkg server

  当前配置了如下服务器，星标的是当前的服务器，可在 ~/.edopkgrc 里面调整配置.

  * test:        https://oc-api.everydo.cn, 账号zopen, 站点default
    production:  https://oc-api.easydo.cn, 账号zopen, 站点default

把当前服务器设置为 ``production`` 配置::

  edopkg server production

config 配置服务器
----------------------------
运行 ``edopkg config`` 可以设置一个新的服务器:

会显示当前的服务器配置信息，用户输入一个配置，进行调整。

配置文件
===============

配置文件位于 ~/.edopkgrc. 
首次使用会自动进行配置

格式：
----------
配置文件的一个具体例子, 配置了测试服务器(test)和正式服务器(production)，当前使用test服务器::

    [edopkg]
    server=test

    [test]
    oc_api = https://oc-api.everydo.cn	
    account = zopen	
    instance = default	
    username = xxx	
    password = xxx	
    client_id = test	
    client_secret = 022127e182a934dea7d69s10697s8ac2	

    [production]
    oc_api = https://oc-api.easydo.cn	
    account = zopen	
    instance = default	
    username = xxx	
    password = xxx	
    client_id = test	
    client_secret = 022127e182a934dea7d69s10697s8ac2	

字段的含义：

- oc_api: oc服务地址
- account: 公司(子域名)名称
- instance: 站点实例名称，默认为'default'
- username: 用户名
- password: 密码
- client_id:应用的ID
- client_secret:应用的密钥

更多具体的信息，可参照：
https://zopen.everydo.cn/platform/docs/auth/开放API概览.rst/@zopen.cms:view


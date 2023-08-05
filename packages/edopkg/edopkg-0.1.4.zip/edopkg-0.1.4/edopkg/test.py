# -*- coding: utf-8 -*-
from edo_client import OcClient, WoClient
# --
oc_arg = [
         'https://oc-api.everydo.cn',
         'test',
         '022127e182a934dea7d69s10697s8ac2',
         'everydo'
        ]
oc_client = OcClient(*oc_arg)
print 'get client '
# --
auth_kw = dict(
        username = 'xhy1991',
        password = 'xhy123',
        account = 'everydo'
        )
oc_client.auth_with_password(**auth_kw)
print 'auth ok'
# --
instance_kw = dict(
        account = 'everydo',
        application = 'workonline',
        instance = 'default'
        )
wo_instance = oc_client.account.get_instance(**instance_kw)
print 'get wo_instance'
# --
wo_arg = [
        wo_instance['api_url'],
        'test',
        '022127e182a934dea7d69s10697s8ac2',
        ]
wo_kw = dict(
        account = 'everydo',
        instance = 'default'
        )
wo_client = WoClient(*wo_arg, **wo_kw)

print 'get wo_client'
# --
wo_client.auth_with_token(oc_client.access_token)

print wo_client.package.get('zopen.plans')
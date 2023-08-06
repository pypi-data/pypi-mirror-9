from sfa.util.sfalogging import logger
from keystoneclient.v2_0 import client as keystone_client
from glance import client as glance_client
from novaclient.v1_1 import client as nova_client
from sfa.util.config import Config


def parse_novarc(filename):
    opts = {}
    f = open(filename, 'r')
    for line in f:
        try:
            line = line.replace('export', '').strip()
            parts = line.split('=')
            if len(parts) > 1:
                value = parts[1].replace("\'", "")
                value = value.replace('\"', '') 
                opts[parts[0]] = value
        except:
            pass
    f.close()
    return opts


class KeystoneClient:
    def __init__(self, username=None, password=None, tenant=None, url=None, config=None):
        if not config:
            config = Config()
        opts = parse_novarc(config.SFA_NOVA_NOVARC)
        if username:
            opts['OS_USERNAME'] = username
        if password:
            opts['OS_PASSWORD'] = password
        if tenant:
            opts['OS_TENANT_NAME'] = tenant
        if url:
            opts['OS_AUTH_URL'] = url
        self.opts = opts 
        self.client = keystone_client.Client(username=opts.get('OS_USERNAME'),
                                             password=opts.get('OS_PASSWORD'),
                                             tenant_name=opts.get('OS_TENANT_NAME'),
                                             auth_url=opts.get('OS_AUTH_URL'))

    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)
   
    def __getattr__(self, name):
        return getattr(self.client, name) 


class GlanceClient:
    def __init__(self, config=None):
        if not config:
            config = Config()
        opts = parse_novarc(config.SFA_NOVA_NOVARC)
        self.client = glance_client.get_client(host='0.0.0.0',
                                               username=opts.get('OS_USERNAME'),
                                               password=opts.get('OS_PASSWORD'),
                                               tenant=opts.get('OS_TENANT_NAME'),
                                               auth_url=opts.get('OS_AUTH_URL'))
    def __getattr__(self, name):
        return getattr(self.client, name)

class NovaClient:
    def __init__(self, username=None, password=None, tenant=None, url=None, config=None):
        if not config:
            config = Config()
        opts = parse_novarc(config.SFA_NOVA_NOVARC)
        if username:
            opts['OS_USERNAME'] = username
        if password:
            opts['OS_PASSWORD'] = password
        if tenant:
            opts['OS_TENANT_NAME'] = tenant
        if url:
            opts['OS_AUTH_URL'] = url
        self.opts = opts
        self.client = nova_client.Client(username=opts.get('OS_USERNAME'),
                                         api_key=opts.get('OS_PASSWORD'),
                                         project_id=opts.get('OS_TENANT_NAME'),
                                         auth_url=opts.get('OS_AUTH_URL'),
                                         region_name='',
                                         extensions=[],
                                         service_type='compute',
                                         service_name='',  
                                         )

    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)
                              
    def __getattr__(self, name):
        return getattr(self.client, name)        

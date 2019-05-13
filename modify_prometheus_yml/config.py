#enconding=utf-8

TEST_SERVICE_API_32 = {
    'REST_SERVER_URI': 'http://10.11.3.2:9186',
    'PROMETHEUS_URI': 'htttp://10.11.3.2:9091',
    'YARN_WEB_PORTAL_URI': 'http://10.11.3.2:8088',
    'GRAFANA_URI': 'http://10.11.3.2:3000',
    'LAUNCHER_WEBSERVICE_URI': 'http://10.11.3.2:9086',
    'HDFS_URI': 'hdfs://10.11.3.2:9000',
    'WEBHDFS_URI': 'http://10.11.2.5:50070',
    'ETCD_URI': 'http://10.11.3.2:4001',
    'K8S_DASHBOARD_URI': 'http://10.11.3.2:9090',
    'K8S_API_SERVER_URI': 'http://10.11.3.2:8080',
    'USER_CENTER':{
        'user_info': {"account": "admin", "password": "admin123456"},
        'server_url': "http://139.129.203.44:8180/leinao-operation-web"
    },
    'HOSTS_INFO':{
        'nodes_default_config':{
            "usr": "leinao",
            "passwd": "K&3hsU7D*t",
            "port": 22
        }
    },
    'CLUSTER_LOGIN':{
        'username': 'paictrlcenter@leinao.ai',
        'password': 'ughYCd74'
    },
    'DATA_BASE':{
        'dataset': {
            'db_host': '10.11.3.2',
            'db_user': 'root',
            'db_passwd': '12345678',
            'db_port': 3306,
        },
        'platform': {
            'db_host': '10.11.3.2',
            'db_user': 'root',
            'db_passwd': '12345678',
            'db_port': 3306
        }
    }
}


#获取rest-server api
def get_cluster_rest_server_uri():
    service_api = TEST_SERVICE_API_32
    return service_api['REST_SERVER_URI']


#暂时没有加密密码
def get_cluster_login_token():
    service_api = TEST_SERVICE_API_32
    return service_api['CLUSTER_LOGIN']


#获取节点ssh info
def get_node_ssh_config(node_id):
    service_api = TEST_SERVICE_API_32
    nodes_default_config = service_api['HOSTS_INFO']['nodes_default_config']
    host_config = dict(host = node_id, usr = nodes_default_config['usr'],
                      passwd = nodes_default_config['passwd'], port = nodes_default_config['port'])
    return host_config


#获取yarn api
def get_cluster_yarn_uri():
    service_api = TEST_SERVICE_API_32
    return service_api['YARN_WEB_PORTAL_URI']



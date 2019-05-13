#encoding=utf-8

TEST_SERVICE_API_35 = {
    'REST_SERVER_URI': 'http://10.12.3.5:9186',
    'PROMETHEUS_URI': 'htttp://10.12.3.5:9091',
    'YARN_WEB_PORTAL_URI': 'http://10.12.3.5:8088',
    'GRAFANA_URI': 'http://10.12.3.5:3000',
    'LAUNCHER_WEBSERVICE_URI': 'http://10.12.3.5:9086',
    'HDFS_URI': 'hdfs://10.12.3.5:9000',
    'WEBHDFS_URI': 'http://10.12.3.5:50070',
    'ETCD_URI': 'http://10.12.3.5:4001',
    'K8S_DASHBOARD_URI': 'http://10.12.3.5:9090',
    'K8S_API_SERVER_URI': 'http://10.12.3.5:8080',
    'CLUSTER_LOGIN':{
        'username': 'mengjiaxiang@leinao.ai',
        'password': 'K&3hsU7D*t'
    },
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
    'DATA_BASE':{
        'dataset': {
            'db_host': '10.12.3.5',
            'db_user': 'root',
            'db_passwd': '12345678',
            'db_port': '3306',
        },
        'platform': {
            'db_host': '10.12.3.5',
            'db_user': 'root',
            'db_passwd': '12345678',
            'db_port': 3306
        }
    }
}

TEST_SERVICE_API_32 = {
    'REST_SERVER_URI': 'http://10.12.3.2:9186',
    'PROMETHEUS_URI': 'htttp://10.12.3.2:9091',
    'YARN_WEB_PORTAL_URI': 'http://10.12.3.2:8088',
    'GRAFANA_URI': 'http://10.12.3.2:3000',
    'LAUNCHER_WEBSERVICE_URI': 'http://10.12.3.2:9086',
    'HDFS_URI': 'hdfs://10.12.3.2:9000',
    'WEBHDFS_URI': 'http://10.12.2.5:50070',
    'ETCD_URI': 'http://10.12.3.2:4001',
    'K8S_DASHBOARD_URI': 'http://10.12.3.2:9090',
    'K8S_API_SERVER_URI': 'http://10.12.3.2:8080',
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
        'username': 'mengjiaxiang@leinao.ai',
        'password': 'K&3hsU7D*t'
    },
    'DATA_BASE':{
        'dataset': {
            'db_host': '10.12.3.2',
            'db_user': 'root',
            'db_passwd': '12345678',
            'db_port': '3306',
        },
        'platform': {
            'db_host': '10.12.3.2',
            'db_user': 'root',
            'db_passwd': '12345678',
            'db_port': 3306
        }
    }
}

TEST_SERVICE_API_LISTS = {
    '10.11.3.5': TEST_SERVICE_API_35,
    '10.12.3.5': TEST_SERVICE_API_35,
    '10.11.3.2': TEST_SERVICE_API_32,
    '10.12.3.2': TEST_SERVICE_API_32,
}


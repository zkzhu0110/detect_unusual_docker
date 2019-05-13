#enconding=utf-8
import json
import common.kubenetes.kubenetes
import app.cluster.cluster
from common.log.log_config import logger
from .cluster_config_test import TEST_SERVICE_API_LISTS
#获取集群服务配置
def get_cluster_service_api(cluster_name):
    cluster_info = app.cluster.cluster.get_cluster_by_name(cluster_name)

    #测试用途
    if cluster_info['ip'] in TEST_SERVICE_API_LISTS.keys():
        return TEST_SERVICE_API_LISTS[cluster_info['ip']]

    config_map = common.kubenetes.kubenetes.get_k8s_configmap(cluster_info['uri'], 'default', 'service_api')
    service_api_str = list(config_map['data'].values())[0]
    service_api = json.loads(service_api_str)
    logger.info(service_api)

    return service_api

#获取rest-server api
def get_cluster_rest_server_uri(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['REST_SERVER_URI']

#获取promethues api
def get_cluster_prometheus_uri(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['PROMETHEUS_URI']

#获取yarn api
def get_cluster_yarn_uri(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['YARN_WEB_PORTAL_URI']

#获取launcher api
def get_cluster_launcher_uri(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['LAUNCHER_WEBSERVICE_URI']

#获取集群数据库配置
def get_cluster_database(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['DATA_BASE']

#获取集群节点信息
def get_cluster_host_config(cluster_name):
    cluster_info = app.cluster.cluster.get_cluster_by_name(cluster_name)
    config_map = common.kubenetes.kubenetes.get_k8s_configmap(cluster_info['uri'], 'default', 'host-info')
    host_info_str = list(config_map['data'].values())[0]
    host_info = json.loads(host_info_str)

    return  host_info

#暂时没有加密密码
def get_cluster_login_token(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['CLUSTER_LOGIN']

#获取用户中心配置
def get_user_center_config(cluster_name):
    service_api = get_cluster_service_api(cluster_name)
    return service_api['USER_CENTER']

#获取节点ssh info
def get_node_ssh_config(cluster_name, node_id):
    service_api = get_cluster_service_api(cluster_name)
    nodes_default_config = service_api['HOSTS_INFO']['nodes_default_config']

    host_config = dict(host = node_id, usr = nodes_default_config['usr'],
                      passwd = nodes_default_config['passwd'], port = nodes_default_config['port'])

    return host_config

if __name__ == '__main__':
    get_cluster_service_api('test35')

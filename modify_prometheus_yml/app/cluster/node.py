#encoding=utf-8
import requests
import pymysql
import app.cluster.cluster_config
import copy
import socket

from common.log.log_config import logger

#获取集群node-manager列表
def get_nodes_list(yarn_url):
    cluster_info = get_yarn_nodes_info(yarn_url)
    nodes_lists = []
    for node in cluster_info.get("nodes").get("node"):
        host_ip = node.get("nodeHostName")
        node_total_memory = node.get("usedMemoryMB") + node.get("availMemoryMB")
        node_total_cpu = node.get("usedVirtualCores") + node.get("availableVirtualCores")
        #resource manager 会显示已经剔除集群的节点，资源数全为0
        if node_total_memory > 0 and node_total_cpu > 0 :
            nodes_lists.append(host_ip)

    nodes_lists = sorted(nodes_lists, key= lambda item: socket.inet_aton(item))

    return nodes_lists

#获取节点gpu类型
def get_node_gpu_type(framework_url):
    try:
        response = requests.get(framework_url)
        return response.json()
    except Exception as err:
        logger.info("[get_node_gpu_type]: Get node GPU type error {}".format(err))
        return None

def get_yarn_nodes_info(url):
    try:
        response = requests.get(url)
        return response.json()
    except Exception as err:
        logger.info("[getClusterInfo]: Get cluster info error {}".format(err))
        return None

#获取被隔离的资源
def getUnavailableResourceFromMysql(cluster_name):
    try:
        data_base = app.cluster.cluster_config.get_cluster_database(cluster_name)['platform']
        db = pymysql.connect(host=data_base['db_host'], port=data_base['db_port'], user=data_base['db_user'],
                             passwd=data_base['db_passwd'], db="platform", charset='utf8')
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM node_attribute")
        data = cursor.fetchall()
        logger.info("get unavailable resource from sql: {}".format(data))
        cursor.close()
        db.close()
        return data
    except Exception as err:
        logger.info(err)
        raise


#获取节点资源使用信息
def statistic_node_resource(yarn_url):
    cluster_info = get_yarn_nodes_info(yarn_url)

    if not cluster_info:
        logger.info("[statistic_node_resource]: cluster_info is None")
        return None

    nodes_resource = {}
    default_resouce = {"gpu":{"total":0, "left": 0, 'unavailable': ''}, "mem":{"total":0, "left": 0}, "cpu":{"total":0, "left": 0}}

    for node in cluster_info.get("nodes").get("node"):
        node_total_memory = node.get("usedMemoryMB") + node.get("availMemoryMB")
        node_total_cpu = node.get("usedVirtualCores") + node.get("availableVirtualCores")
        if node_total_cpu <= 0 or node_total_memory <= 0:
            continue
        host_ip = node.get("nodeHostName")
        nodes_resource.setdefault(host_ip, copy.deepcopy(default_resouce))
        nodes_resource[host_ip]["gpu"]["left"] += node.get("availableGPUs")
        nodes_resource[host_ip]["gpu"]["total"] += node.get("usedGPUs") + node.get("availableGPUs")
        nodes_resource[host_ip]["mem"]["left"] += node.get("availMemoryMB")
        nodes_resource[host_ip]["mem"]["total"] += node.get("usedMemoryMB") + node.get("availMemoryMB")
        nodes_resource[host_ip]["cpu"]["left"] += node.get("availableVirtualCores")
        nodes_resource[host_ip]["cpu"]["total"] += node.get("usedVirtualCores") + node.get("availableVirtualCores")

    logger.info("[statistic_node_resource]: get resource by gpu type: {}".format(nodes_resource))
    return nodes_resource


#获取节点gpu类型以及节点使用信息
def get_node_info(framework_url, yarn_url, cluster_name):
    nodes_resource = statistic_node_resource(yarn_url)
    node_gpu = get_node_gpu_type(framework_url)

    #添加gpu类型信息
    for host_ip in nodes_resource.keys():
        if host_ip in node_gpu['nodes']:
            nodes_resource[host_ip]['machineType'] = node_gpu['nodes'][host_ip]['gpuType']
        else:
            nodes_resource[host_ip]['machineType'] = 'machine-cpu'

    #添加被隔离资源的信息
    unavailable = getUnavailableResourceFromMysql(cluster_name)
    for data in unavailable:
        host_ip = data.get("node_id")
        if host_ip not in nodes_resource:
            continue
        unavailableGpus = data.get("unhealthy_gpu")
        gpuBits  = bin(unavailableGpus).replace('0b','')
        gpuStr = ''
        for n in range(len(gpuBits)):
            if (1<<n) & unavailableGpus:
                gpuStr += str(n)
        logger.info("{} {} ".format(host_ip,gpuStr))
        nodes_resource[host_ip]['gpu']['unavailable'] = gpuStr

    #按数值大小排序
    result = sorted(nodes_resource.items(), key= lambda item: socket.inet_aton(item[0]))
    nodes_resource_list = []
    for item in result:
        #转为数组，添加节点id
        item[1]['nodeId'] = item[0]
        nodes_resource_list.append(item[1])

    logger.info(nodes_resource_list)

    return nodes_resource_list

#根据集群名称获取节点资源信息
def get_nodes_resource_by_cluster_name(cluster_name):
    yarn_uri = app.cluster.cluster_config.get_cluster_yarn_uri(cluster_name)
    launcher_uri = app.cluster.cluster_config.get_cluster_launcher_uri(cluster_name)

    if not yarn_uri or not launcher_uri:
        logger.info('get cluster info of {} error', cluster_name)
        return None

    launcher_url = "{}/v1/LauncherRequest/ClusterConfiguration".format(launcher_uri)
    yarn_url = "{}/ws/v1/cluster/nodes".format(yarn_uri)

    logger.info("get_nodes_info_by_cluster_name {} {} {}".format(cluster_name, launcher_url, yarn_url))

    return  get_node_info(launcher_url, yarn_url, cluster_name)

if __name__ == '__main__':
    logger.info(get_nodes_resource_by_cluster_name('test'))


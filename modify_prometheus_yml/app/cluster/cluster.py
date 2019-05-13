#enconding=utf-8
import os
import json
import common.kubenetes.kubenetes
from common.log.log_config import logger

#从配置中获取cluster信息
#cluster: {'id':1, 'name':'cluster_test', 'uri':'10.10.8.1:8080'}
CLUSTER_ENV_KEY= 'clusters_info'

def get_clusters(config_type= 'FILE_JSON', config_path= 'clusters_info.json'):
    if config_type == 'FILE_JSON':
        if not os.path.exists(config_path):
            logger.info('{} does not exist'.format(config_path))
            return []
        with open(config_path, 'r') as config_path_fd:
            return json.loads(config_path_fd.read())

    return []

#获取指定集群信息
def get_cluster_by_name(cluster_name, config_type= 'FILE_JSON', config_path= 'clusters_info.json'):
    if config_type == 'FILE_JSON':
        if not os.path.exists(config_path):
            logger.info('[get_cluster_by_name] {} does not exist'.format(config_path))
            return None
        logger.info('[get_cluster_by_name] finding {} in path: {}'.format(cluster_name, config_path))
        with open(config_path, 'r') as config_path_fd:
            for cluster in json.loads(config_path_fd.read())[CLUSTER_ENV_KEY]:
                if cluster['name'] == cluster_name:
                    return cluster
    return None

#保存集群配置信息
def save_cluster(cluster_info, config_type= 'FILE_JSON', config_path= 'clusters_info.json'):
    logger.info('save_cluster',cluster_info, config_type, config_path )
    if config_type == 'FILE_JSON':
        if not os.path.exists(config_path):
            logger.info('creating cluster', cluster_info)
            #写入首个cluster信息
            with open(config_path, 'w') as config_path_fd:
                clusters_info = {CLUSTER_ENV_KEY: []}
                clusters_info[CLUSTER_ENV_KEY].append(cluster_info)
                logger.info(clusters_info)
                config_path_fd.write(json.dumps(clusters_info))

        #获取已经保存的集群信息
        with open(config_path, 'r') as config_path_fd:
            saved_clusters = json.loads(config_path_fd.read())

        #更新新添加的集群信息
        id_set = set()
        for cluster in saved_clusters[CLUSTER_ENV_KEY]:
            id_set.add(cluster['id'])
            if cluster['name'] == cluster_info['name']:
                logger.info('{} already existed in {}'.format(cluster, cluster_info))
                return True

        #寻找有效的ID
        for index in range(len(id_set)):

            if (index + 1) not in id_set:
                cluster_info['id'] = index + 1
                break
        if cluster_info['id'] in id_set:
            cluster_info['id'] = len(id_set)
        #不存在时新增
        saved_clusters[CLUSTER_ENV_KEY].append(cluster_info)

        with open(config_path, 'w') as config_path_fd:
            config_path_fd.write(json.dumps(saved_clusters))

        return True

    return False

#保存集群配置信息
def delete_cluster(cluster_name, config_type= 'FILE_JSON', config_path= 'clusters_info.json'):
    if config_type == 'FILE_JSON':
        if not os.path.exists(config_path):
            return True

        #获取已经保存的集群信息
        with open(config_path, 'r') as config_path_fd:
            saved_clusters = json.loads(config_path_fd.read())

        #找到并删除集群
        for cluster in saved_clusters[CLUSTER_ENV_KEY]:
            if cluster['name'] == cluster_name:
                logger.info('{} existed in {}, removing'.format(cluster, cluster_name))
                saved_clusters[CLUSTER_ENV_KEY].remove(cluster)

                #删除后集群为空
                if len(saved_clusters[CLUSTER_ENV_KEY]) == 0:
                    os.remove(config_path)
                    return True

                #更新集群配置文件
                with open(config_path, 'w') as config_path_fd:
                    config_path_fd.write(json.dumps(saved_clusters))

                return True

    return False

#根据集群名称获取集群节点信息
def get_cluster_nodes_by_name(cluster_name, config_type= 'FILE_JSON', config_path= 'clusters_info.json'):
    clusters_info = get_clusters(config_type, config_path)
    if not clusters_info:
        logger.info('clusters_info does not exist')
        return []

    global CLUSTER_ENV_KEY
    for cluster in clusters_info[CLUSTER_ENV_KEY]:
        if cluster_name == cluster['name']:
            return common.kubenetes.kubenetes.get_k8s_nodes(cluster['uri'])

    raise Exception("cluster:{} not found".format(cluster_name))

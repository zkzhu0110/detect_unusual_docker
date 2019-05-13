#encoding=utf-8
from flask import Blueprint, request
import json
import app.cluster.cluster
import app.cluster.node
from common.error_code.response import make_success_response, make_error_response, make_no_data_response
from common.log.log_config import logger

route_cluster = Blueprint('cluster', __name__)

#获取集群列表
@route_cluster.route('/', methods=['GET'])
def get_clusters():
    try:
        clusters_list = app.cluster.cluster.get_clusters()
        return make_success_response(clusters_list)
    except Exception as err:
        logger.info('[get_clusters] err {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

#获取指定集群的节点列表
@route_cluster.route('/<cluster_name>/nodes', methods=['GET'])
def get_cluster_nodes(cluster_name):
    try:
        nodes_list = app.cluster.cluster.get_cluster_nodes_by_name(cluster_name)
        return make_success_response(nodes_list)
    except Exception as err:
        logger.info('[get_cluster_nodes] {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

#获取指定集群node-manager节点资源信息
@route_cluster.route('/<cluster_name>/resources', methods=['GET'])
def get_cluster_resources(cluster_name):
    try:
        nodes_resources = app.cluster.node.get_nodes_resource_by_cluster_name(cluster_name)
        return make_success_response(nodes_resources)
    except Exception as err:
        logger.info('[get_cluster_resources] {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

#创建新cluster
#return {'status': 'OK'} {status': 'FAILED'}
@route_cluster.route('/register', methods=['POST'])
def add_cluster():
    try:
        logger.info('entering add_cluster')
        logger.info('add_cluster', request.get_data().decode('utf-8'))
        cluster_input = json.loads(request.get_data().decode('utf-8'))
        logger.info('add_cluster', cluster_input)
        #从前台获取参数
        cluster_name = cluster_input.get('cluster_name')
        k8s_master_ip = cluster_input.get('k8s_master_ip')
        k8s_master_port = cluster_input.get('k8s_master_port')

        cluster_info = dict(id=1, name=cluster_name, uri="{}:{}".
                            format(k8s_master_ip, k8s_master_port), ip=k8s_master_ip)
        logger.info(cluster_info)

        if app.cluster.cluster.save_cluster(cluster_info, 'FILE_JSON', 'clusters_info.json'):
            return make_no_data_response(status=200, code=0, message="SUCCESS")
        else:
            return make_error_response(status=200, code=500, message="FAILED")
    except Exception as err:
        logger.info('add_cluster {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

#删除集群
@route_cluster.route('/<cluster_name>', methods=['DELETE'])
def delete_cluster(cluster_name):
    try:
        if app.cluster.cluster.delete_cluster(cluster_name):
            return make_no_data_response(status=200, code=0, message="SUCCESS")
        else:
            return make_error_response(status=200, code=500, message="FAILED")
    except Exception as err:
        logger.info('delete_cluster error {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

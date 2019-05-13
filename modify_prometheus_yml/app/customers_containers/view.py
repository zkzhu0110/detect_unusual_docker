#encoding=utf-8
from flask import Blueprint
import app.customers_containers.containers
import app.cluster.cluster_config
import common.pai_job.PaiSingeJob
import app.cluster.node
import copy
import time
from common.error_code.response import make_success_response, make_error_response
from common.log.log_config import logger

route_containers = Blueprint('containers', __name__)

#任务可能有多个容器，获取指定容器运行时信息
def get_container_runtime(container_id, job_detail):
    for task_role_name in job_detail['taskRoles'].keys():
        for task_role in job_detail['taskRoles'][task_role_name]['taskStatuses']:
            logger.info("{}  {}".format(container_id, task_role["containerId"]))
            if container_id == task_role["containerId"]:
                return task_role_name, task_role

    return None

#获取单个节点上用户的容器
def get_single_node_zombies(cluster_name, node_id):
        #测试机器10.11网段不通，10.11网段转成10.10网段
        node_id = node_id.replace('10.11.', '10.10.')
        logger.info(node_id)

        restserver_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)
        ssh_config = app.cluster.cluster_config.get_node_ssh_config(cluster_name, node_id)
        containers = app.customers_containers.containers.get_node_containers(ssh_config, ['k8s', 'kubelet'])

        containers_info = []
        for container in containers:
            logger.info(container)
            job_name = app.customers_containers.containers.get_job_name_by_container(container)
            container_id = app.customers_containers.containers.get_container_id_by_container(container)
            job_instance = common.pai_job.PaiSingeJob.PaiJob(job_name, restserver_url, token_config)
            job_detail = job_instance.get_job_detail()
            job_config = job_instance.get_job_config()

            #获取任务状态
            job_status = job_detail['jobStatus']['state']
            
            if job_status  in ["RUNNING"]:
                continue

            #获取僵尸容器
            #获取该容器运行信息
            container_runtime_info = get_container_runtime(container_id, job_detail)

            timstamp_now = time.time()
            run_time = timstamp_now*1000 - job_detail['jobStatus']['appLaunchedTime']

            containers_info.append(dict(container_name = container,
                                        job_name = job_name,
                                        username = job_detail['jobStatus']['username'],
                                        job_status = job_status,
                                        container_gpu_info = container_runtime_info[1]['containerGpus'],
                                        container_ports = container_runtime_info[1]['containerPorts'],
                                        image_name = job_config['image'],
                                        gpu_type = job_config['gpuType'],
                                        run_time = run_time
                                        ))

            #logger.info("{} {}".format(timstamp_now, job_detail['jobStatus']['appLaunchedTime']))

        return containers_info

#获取单个节点上用户的容器
def get_single_node_containers(cluster_name, node_id):
        #测试机器10.11网段不通，10.11网段转成10.10网段
        node_id = node_id.replace('10.11.', '10.10.')
        logger.info(node_id)

        restserver_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)
        logger.info("{} {}".format(restserver_url, token_config))

        ssh_config = app.cluster.cluster_config.get_node_ssh_config(cluster_name, node_id)
        containers = app.customers_containers.containers.get_node_containers(ssh_config, ['k8s', 'kubelet'])

        containers_info = []
        for container in containers:
            logger.info(container)
            job_name = app.customers_containers.containers.get_job_name_by_container(container)
            container_id = app.customers_containers.containers.get_container_id_by_container(container)
            job_instance = common.pai_job.PaiSingeJob.PaiJob(job_name, restserver_url, token_config)
            job_detail = job_instance.get_job_detail()

            #获取任务状态
            job_status = job_detail['jobStatus']['state']
            #获取该容器运行信息
            container_runtime_info = get_container_runtime(container_id, job_detail)

            containers_info.append(dict(container_name = container, job_name = job_name,
                                        job_status = job_status,
                                        container_gpu_info = container_runtime_info[1]['containerGpus'],
                                        ))
        return containers_info

#获取用户容器所在节点列表
@route_containers.route('/<cluster_name>/nodeslist', methods=['GET'])
def get_node_manager_list(cluster_name):
    try:
        yarn_uri = app.cluster.cluster_config.get_cluster_yarn_uri(cluster_name)
        logger.info(yarn_uri)
        yarn_url = "{}/ws/v1/cluster/nodes".format(yarn_uri)
        nodes_list = app.cluster.node.get_nodes_list(yarn_url)
        logger.info(nodes_list)

        return make_success_response(nodes_list)

    except Exception as err:
        logger.info("error happened {}".format(err))
        return make_error_response(status=200, code=500, message=err)

#获取单个节点的僵尸容器
@route_containers.route('/<cluster_name>/zombies/<node_id>', methods=['GET'])
def get_cluster_node_zombies(cluster_name, node_id):
    try:
        cluster_zombies = {}
        containers_info = get_single_node_zombies(cluster_name, node_id)
        if containers_info:
            cluster_zombies[node_id] = containers_info

        return make_success_response(cluster_zombies)

    except Exception as err:
        logger.info("error happened {}".format(err))
        return make_error_response(status=200, code=500, message=err)

#获取集群所有的僵尸容器
@route_containers.route('/<cluster_name>/zombies', methods=['GET'])
def get_cluster_zombies(cluster_name):
    try:
        yarn_uri = app.cluster.cluster_config.get_cluster_yarn_uri(cluster_name)
        logger.info(yarn_uri)
        yarn_url = "{}/ws/v1/cluster/nodes".format(yarn_uri)
        nodes_list = app.cluster.node.get_nodes_list(yarn_url)
        logger.info(nodes_list)
        cluster_zombies = {}

        for node_id in nodes_list:
            containers_info = get_single_node_zombies(cluster_name, node_id)
            if containers_info:
                cluster_zombies[node_id] = containers_info

        return make_success_response(cluster_zombies)

    except Exception as err:
        logger.info("error happened {}".format(err))
        return make_error_response(status=200, code=500, message=err)


#获取特定节点的容器
@route_containers.route('/<cluster_name>/nodes/<node_id>', methods=['GET'])
def get_node_containers(cluster_name, node_id):
    try:
        containers_info = get_single_node_containers(cluster_name, node_id)
        return make_success_response(containers_info)

    except Exception as err:
        logger.info("error happened {}".format(err))
        return make_error_response(status=200, code=500, message=err)

#获取特定容器信息
@route_containers.route('/<cluster_name>/<container_name>', methods=['GET'])
def get_node_container_detail(cluster_name, container_name):
    try:
        restserver_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)
        logger.info(container_name)

        job_name = app.customers_containers.containers.get_job_name_by_container(container_name)
        container_id = app.customers_containers.containers.get_container_id_by_container(container_name)
        job_instance = common.pai_job.PaiSingeJob.PaiJob(job_name, restserver_url, token_config)
        job_detail = job_instance.get_job_detail()
        job_config = job_instance.get_job_config()

        #获取任务状态
        job_status = job_detail['jobStatus']['state']
        #获取该容器运行信息
        container_runtime_info = get_container_runtime(container_id, job_detail)

        #获取容器配置
        task_role_name = container_runtime_info[0]
        container_config = copy.deepcopy(job_config)
        del container_config['taskRoles']
        for config_task_role in job_config['taskRoles']:
            if task_role_name == config_task_role['name']:
                container_config['taskRole'] = config_task_role
                break

        containers_info =dict(container_name = container_name, job_name = job_name,
                                    job_status = job_status, container_runtime_info = container_runtime_info[1],
                                    container_config = container_config)

        return make_success_response(containers_info)

    except Exception as err:
        logger.info("error happened {}".format(err))
        return make_error_response(status=200, code=500, message=err)

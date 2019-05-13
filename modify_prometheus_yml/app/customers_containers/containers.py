#encoding=utf-8
import common.ssh.utils
import re
from common.log.log_config import logger

#返回符合条件的容器名称
def get_node_containers(host_config, ignore_list):
    ssh_connection = common.ssh.utils.SSHManager(host_config['host'], host_config['usr'],
                                                    host_config['passwd'], host_config['port'])
    #获取所有运行容器的名称
    cmd = r'sudo docker ps --format "{{ json .Names }}"'
    result = ssh_connection.ssh_exec_cmd(cmd, True)
    if result['status'] != 0:
        logger.warning('error happened in {} error is :{}'.format(cmd, result['stderr']))
        return []
    else:
        logger.info("cmd {} executed successfully".format(cmd))

    raw_containers_list = result['stdout'].split('\n')
    containers_list = []
    for line in raw_containers_list:
        #剔除指定的容器
        ifwrite = True
        for ignore in ignore_list:
            if ignore in line:
                ifwrite = False
                break
        if not ifwrite:
            continue

        #寻找任务容器
        job = re.search(r'^"(.*?)-container_.*"$', line)
        if not job:
            continue

        containers_list.append(line[1:-1])

    return containers_list

#获取容器对应任务的名称
def get_job_name_by_container(container_name):
    try:
        job = re.search(r'^(.*?)-container_.*$', container_name)
        if not job:
            logger.warning('container {} belong to no job'.format(container_name))
            return None

        #获取任务名字
        job_name = job.group(1)
        logger.info("container_name:{}, job_name:{}".format(container_name, job_name))
    except Exception as err:
        logger.info("error happened {}".format(err))
        return None

    return job_name

#获取容器对应任务的container_id
def get_container_id_by_container(container_name):
    try:
        job = re.search(r'^(.*?)-(container_.*)$', container_name)
        if not job:
            logger.warning('container {} belong to no container_id'.format(container_name))
            return None

        #获取任务名字
        container_id = job.group(2)
        logger.info("container_name:{}, container_id:{}".format(container_name, container_id))
    except Exception as err:
        logger.info("error happened {}".format(err))
        return None

    return container_id


if __name__ == "__main__":
    host_config = dict(host=r'10.10.8.1', usr= r'leinao', passwd= r'12345678', port=22)
    print(get_node_containers(host_config, ['k8s', 'kubelet']))



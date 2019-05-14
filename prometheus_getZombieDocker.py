import docker
import os
import json
import time
from prometheus_client import Gauge, start_http_server

dockerClient = docker.APIClient(base_url='unix://var/run/docker.sock')

PROMETHEUS_SERVER_PORT = 8000
TEST_PERIOD = 3600

unusual_container_count = Gauge('unusual_container_num', 'Number of detected unusual container')
c = Gauge('is_unusual_container', 'Whether current user container is an unusual container', ['container_name',
                                                                                             'created_time',
                                                                                             'container_pid',
                                                                                             'job_name',
                                                                                             'user_name',
                                                                                             'job_state',
                                                                                             'host_ip',
                                                                                             'used_gpus',
                                                                                             'ssh_port',
                                                                                             'exception_value'])


# 获取framework信息，用于获取任务在平台上运行的状态
def get_job_state(job_name):

    # 获取framework信息，存入job_info.json
    cmd = "curl -o job_info.json http://10.11.3.2:9086/v1/Frameworks/%s" % job_name
    os.system(cmd)

    # 将json文件解析出来，提取里面的任务状态信息
    with open('job_info.json', 'rt') as fin:
        job_info = json.load(fin)
    job_state = job_info["summarizedFrameworkInfo"]["frameworkState"]

    return job_state


# 获取容器占用的GPU资源（根据映射宿主机的设备来判断）
def get_used_gpu(container_id):

    container_inspect_info = dockerClient.inspect_container(container_id)
    devices_list = container_inspect_info.get("HostConfig").get("Devices")  # 映射了宿主机的哪些设备
    gpu_standard_num = 0  # 将GPU使用的情况形成二进制排布最后转成十进制数值

    for cur_device_info in devices_list:
        path_on_host = cur_device_info['PathOnHost']  # 映射的宿主机设备
        dev_name = path_on_host.split(sep='/')[2]  # 提取出/dev/之后的信息
        if dev_name == "nvidiactl" or dev_name == "nvidia-uvm":
            continue
        if dev_name.startswith("nvidia"):
            gpu_id = int(dev_name[6:len(dev_name)])  # 提取nvidia之后的序号，即使用了哪台GPU
            gpu_standard_num += pow(2, gpu_id)

    return gpu_standard_num


# 获取容器的基本信息
def get_container_info(container_id):

    # 聚合容器信息的字典变量
    container_info_dict = {}

    container_inspect_info = dockerClient.inspect_container(container_id)
    container_name = container_inspect_info.get("Name")    # 获取容器的名称（inspect中提取的一般会有前缀“/”）
    created_time = container_inspect_info.get("Created")   # 获取容器的创建时间
    container_pid = container_inspect_info.get("State").get("Pid")   # 获取容器的pid
    container_env_list = container_inspect_info.get("Config").get("Env")     # 获取容器的环境变量

    # 无法获取环境变量，说明不是用户的容器
    if container_env_list is None:
        return False, container_info_dict

    # 获取容器对应的任务名称、宿主机IP以及用户编号
    job_name = ""
    host_ip = ""
    user_name = ""
    ssh_port = ""
    for cur_env in container_env_list:
        if cur_env.startswith('FRAMEWORK_NAME='):
            job_name = cur_env.split(sep='FRAMEWORK_NAME=')[1]
        if cur_env.startswith('PAI_CONTAINER_HOST_IP='):
            host_ip = cur_env.split(sep='PAI_CONTAINER_HOST_IP=')[1]
        if cur_env.startswith('HADOOP_USER_NAME='):
            user_name = cur_env.split(sep='HADOOP_USER_NAME=')[1]
        if cur_env.startswith('PAI_CONTAINER_SSH_PORT='):
            ssh_port = cur_env.split(sep='PAI_CONTAINER_SSH_PORT=')[1]

    # job名称获取不了，说明不是用户的容器
    if job_name == "":
        return False, container_info_dict

    # 获取容器对应任务的平台运行状态
    job_state = get_job_state(job_name)

    # 获取占用的GPU资源
    used_gpus = get_used_gpu(container_id)

    container_info_dict = {
        'container_name': container_name,
        'created_time': created_time,
        'container_pid': container_pid,
        'job_name': job_name,
        'user_name': user_name,
        'job_state': job_state,
        'host_ip': host_ip,
        'used_gpus': used_gpus,
        'ssh_port': ssh_port
    }

    return True, container_info_dict


# 打印僵尸容器的信息
def print_unusual_container(container_info_dict, exception_type):
    print("")
    print("------Unusual Container------")
    print("Container Name : {}".format(container_info_dict['container_name']))
    print("Created Time : {}".format(container_info_dict['created_time']))
    print("Docker Pid : {}".format(container_info_dict['container_pid']))
    print("Job Name : {}".format(container_info_dict['job_name']))
    print("User Name : {}".format(container_info_dict['user_name']))
    print("Job State : {}".format(container_info_dict['job_state']))
    print("Host Node's IP : {}".format(container_info_dict['host_ip']))
    print("Used GPUs : {}".format(container_info_dict['used_gpus']))
    print("SSH Port : {}".format(container_info_dict['ssh_port']))
    print("Exception Value : {}".format(exception_type))
    print("")
    print("----------------------------")
    print("")


# 更新prometheus的相关标签值
def set_prometheus_value(container_info_dict, exception_type):

    if exception_type > 0:
        index_value = 1
    else:
        index_value = 0

    # 更新prometheus的label
    c.labels(container_name=container_info_dict['container_name'],
             created_time=container_info_dict['created_time'],
             container_pid=container_info_dict['container_pid'],
             job_name=container_info_dict['job_name'],
             user_name=container_info_dict['user_name'],
             job_state=container_info_dict['job_state'],
             host_ip=container_info_dict['host_ip'],
             used_gpus=container_info_dict['used_gpus'],
             ssh_port=container_info_dict['ssh_port'],
             exception_value=exception_type).set(index_value)

    # 如果index_value数值为1，则说明是异常容器
    if index_value == 1:
        unusual_container_count.inc()
        print_unusual_container(container_info_dict, exception_type)


# 检测出僵尸容器
def detect_unusual_containers():
    containers = dockerClient.containers()
    for i in containers:
        container_id = i.get("Id")

        # 获取容器基本信息
        is_user_container, container_info_dict = get_container_info(container_id)

        # 如果不是用户容器，则跳过，不属于我们考虑的范围
        if not is_user_container:
            continue

        '''
        检测异常容器：
            类型1 -- 如果容器对应的平台任务状态为“完成”，容器存在、不能够再进入（我们讨论的僵尸容器）。
            类型2 -- 如果容器对应的平台任务状态为“完成”，容器存在、还可以再进入。
            类型3 -- 如果容器对应的平台任务状态已丢失，容器存在、不能够再进入。
            类型4 -- 如果容器对应的平台任务状态已丢失，容器存在、还可以再进入。
        '''
        create_id = dockerClient.exec_create(container_id, "bash")
        exec_id = create_id.get("Id")
        if container_info_dict['job_state'] == "FRAMEWORK_COMPLETED":
            if b"exit status" in dockerClient.exec_start(exec_id):
                set_prometheus_value(container_info_dict, 1)
            else:
                set_prometheus_value(container_info_dict, 2)
        elif container_info_dict['job_state'] == "":
            if b"exit status" in dockerClient.exec_start(exec_id):
                set_prometheus_value(container_info_dict, 3)
            else:
                set_prometheus_value(container_info_dict, 4)
        else:
            set_prometheus_value(container_info_dict, 0)


if __name__ == "__main__":

    # Start up the server to expose the metrics.
    start_http_server(PROMETHEUS_SERVER_PORT)

    # Parameter unusual_container_count is set to 0
    unusual_container_count.set(0)

    # Detect unusual container continuously
    while True:
        print("Begin detecting...")
        detect_unusual_containers()
        print("Waiting...")
        time.sleep(TEST_PERIOD)

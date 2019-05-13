#encoding=utf-8

from config import get_cluster_yarn_uri
import app.cluster.node
import yaml

PROMETHEUS_SERVER_PORT = 8000

# 获取集群所有的僵尸容器
def main():
    # Acquire hosts' address
    try:
        yarn_uri = get_cluster_yarn_uri()
        yarn_url = "{}/ws/v1/cluster/nodes".format(yarn_uri)
        nodes_list = app.cluster.node.get_nodes_list(yarn_url)
    except Exception as err:
        print("error happened {}".format(err))
        return

    # Read original yaml file
    with open("prometheus.yml", "r") as yaml_file:
        yaml_obj = yaml.load(yaml_file.read(), Loader=yaml.FullLoader)

    # Add host addressed and ports
    for cur_node_ip in nodes_list:
        print('node ip : ', cur_node_ip)
        cur_target = '%s:%d' % (cur_node_ip, PROMETHEUS_SERVER_PORT)
        yaml_obj['scrape_configs'][0]['static_configs'][0]['targets'].append(cur_target)

    # Modify yaml file
    with open("prometheus.yml", "w") as yaml_file:
        yaml.dump(yaml_obj, yaml_file)


if __name__ == '__main__':
    main()


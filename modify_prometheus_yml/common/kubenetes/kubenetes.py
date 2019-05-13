#encoding=utf-8
import requests

#获取k8s节点名称
def get_k8s_nodes(uri):
    api_url = 'http://{}/api/v1/nodes'.format(uri)
    try:
        response = requests.get(api_url)
        nodes_list = []
        for node in response.json()['items']:
            nodes_list.append(node['metadata']['name'])
        return nodes_list
    except:
        print('get k8s node error {}'.format(api_url))
        return None

#获取conigmap
def get_k8s_configmap(uri, namesapce, configmap):
    api_url = 'http://{}/api/v1/namespaces/{}/configmaps/{}'.format(uri, namesapce, configmap)
    try:
        response = requests.get(api_url)
        return response.json()
    except:
        print('get_k8s_configmap error {} '.format(api_url))
        return None

#定制化的一个接口，暂时未实现，认为都在master节点上，返回master节点的IP
def get_k8s_pod_ip(api_url, pod_name_prefix):
    return api_url.split(':')[0]

if __name__ == '__main__':
    #get_k8s_nodes('10.10.8.5:8080')
    print(get_k8s_configmap('10.10.8.5:8080', 'default', 'prometheus-configmap')['data'].values())

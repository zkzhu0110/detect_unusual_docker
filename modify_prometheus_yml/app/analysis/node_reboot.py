import requests
import more_itertools as mit
from common.log.log_config import logger

#获取节点的down(up==0)的数据，间隔150s
def getNodeDownInfo(serverUrl, start, end):
    queryRangeServerUrl = serverUrl + '/api/v1/query_range?'
    nodeDownInfoUrl = queryRangeServerUrl + 'query=up==0&start=' + str(start) + '&end=' + str(end) + '&step=30s'
    logger.info(nodeDownInfoUrl)
    response = requests.get(nodeDownInfoUrl)
    return response.json()

#获取容器的信息
def getContainerDict(serverUrl, start, end):
    queryRangeServerUrl = serverUrl + '/api/v1/query_range?'
    containerInfoUrl = queryRangeServerUrl + 'query=container_BlockIn&start=' + str(start) +'&end=' + str(end) + '&step=30s'
    response = requests.get(containerInfoUrl)
    return response.json()

def getNodeDownIp(serverUrl, start, end):
    dictUp = getNodeDownInfo(serverUrl, start, end)
    metrics = dictUp['data']['result']
    listDown = []
    for metric in metrics:
        down = {}
        down['instance'] = metric['metric']['instance']
        down['rqtime'] = list(value[0] for value in metric['values'])
        listDown.append(down)
    return listDown

#过滤badinstances的节点数据
def checkNodes(listDown):
    #目前需要通过自定义方式
    badinstances =['10.11.3.4','10.11.2.28','10.11.2.6','10.11.2.35']
    checkedDown = []
    for down in listDown:
        if down['instance'] not in badinstances:
            checkedDown.append(down)
    return checkedDown

def findRanges(listDown):
    downInfos = []
    for down in listDown:
        rqtime = down['rqtime']
        rqtime = list(i // 30 for i in rqtime)
        for group in mit.consecutive_groups(rqtime):
            downinfo = {}
            downinfo['instance'] = down['instance']
            l = list(30 * i for i in list(group))
            downinfo['start'] = min(l)
            downinfo['end'] = max(l)
            downinfo['down'] = '1'
            downInfos.append(downinfo)
    return downInfos


def getContainerInfo(serverUrl, start, end):
    dictContaner = getContainerDict(serverUrl, start, end)
    metrics = dictContaner['data']['result']
    containerInfos = []
    for metric in metrics:
        containerInfo ={}
        values = list(value[0] for value in metric['values'])
        containerInfo['instance'] = metric['metric']['instance']
        containerInfo['jobname'] = metric['metric']['container_label_PAI_JOB_NAME']
        #containerInfo['rqtime'] = values
        containerInfo['start'] = min(values)
        containerInfo['end'] = max(values)
        containerInfo['usrname'] = metric['metric']['container_label_PAI_USER_NAME']
        containerInfo['hostname'] = metric['metric']['container_label_PAI_HOSTNAME']
        containerInfo['taskindex'] = metric['metric']['container_env_PAI_TASK_INDEX']
        containerInfo['taskrolename'] = metric['metric']['container_label_PAI_CURRENT_TASK_ROLE_NAME']
        containerInfos.append(containerInfo)
    return containerInfos

def checkContainerInfo(downInfos ,containerInfos):
    for downInfo in downInfos:
        containers = []
        for containerInfo in containerInfos:
            #print(containerInfo, downInfo)
            if containerInfo['instance']==downInfo['instance']\
                    and containerInfo['end']>=(downInfo['start']-5*60) \
                    and containerInfo['end']<=(downInfo['start']+5*60):
                containers.append(containerInfo)
        downInfo['containers'] = containers
    return downInfos

def findContainerInfo(serverUrl, start, end):
    logger.info("{} {} {}".format(serverUrl, start, end))
    listDown = getNodeDownIp(serverUrl, start, end)
    checkedDown = checkNodes(listDown)
    downInfos = findRanges(checkedDown)
    logger.info(downInfos)
    containerInfos = getContainerInfo(serverUrl, start, end)
    downContainerInfos = checkContainerInfo(downInfos, containerInfos)

    return downContainerInfos

def main():
    serverUrl = 'http://10.10.8.1:9091'
    start =1547134019.158
    end = 1547194019.158
    downContainerInfos = findContainerInfo(serverUrl, start, end)
    logger.info(downContainerInfos)

if __name__ == '__main__':
    main()



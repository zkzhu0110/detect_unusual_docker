#encoding=utf-8
import common.pai_job.PaiToken
import requests
import re
from common.log.log_config import logger

#获取任务列表
def get_jobs_list(token_config, server_url):
    job_server_url = server_url + '/api/v1/jobs'
    token_server_url = server_url + '/api/v1/token'
    logger.info("get_jobs_list {} {}".format(job_server_url, token_server_url))

    paiToken = common.pai_job.PaiToken.PaiToken(token_config, token_server_url)
    try:
        response = requests.get(
            job_server_url,
            headers={
                'Authorization': u'Bearer ' + paiToken.getToken(),
                # 'Content-type': u'application/json'
            }
        )

        return response.json()
    except Exception as err:
        logger.info("[get_jobs_list] err".format(err))
        raise

def filter_jobs_by_key(jobs_list, filter_key):
    searched_jobs = []
    for job in jobs_list:
        # 当前实现方式直接将job信息导成字符串，然后在字符串中搜索
        job_str = str(job)
        if re.search(filter_key, job_str, re.IGNORECASE):
            searched_jobs.append(job)
    return searched_jobs

#根据关键字筛选任务列表
def get_jobs_list_by_key(token_config, server_url, search_multi_key):
    job_server_url = server_url + '/api/v1/jobs'
    token_server_url = server_url + '/api/v1/token'

    paiToken = common.pai_job.PaiToken.PaiToken(token_config, token_server_url)
    try:
        response = requests.get(
            job_server_url,
            headers={
                'Authorization': u'Bearer ' + paiToken.getToken(),
                # 'Content-type': u'application/json'
            }
        )
        searched_jobs  = response.json()
        #遍历任务筛选符合条件的任务
        #通过逗号支持多个关键字
        search_key_list = search_multi_key.split(',')
        for search_key in search_key_list:
            searched_jobs = filter_jobs_by_key(searched_jobs, search_key)

        return searched_jobs
    except Exception as err:
        logger.info("[get_jobs_list_by_key] err".format(err))
        raise

#根据任务明停止任务
def stop_job(token_config, server_url, job_name):
    logger.info("stopping job:{0}".format(job_name))

    token_server_url = server_url + '/api/v1/token'
    paiToken = common.pai_job.PaiToken.PaiToken(token_config, token_server_url)

    job_server_url = server_url + '/api/v1/jobs'
    stop_job_url = "{0}/{1}/executionType".format(job_server_url, job_name)
    try:
        response = requests.put(
            stop_job_url,
            headers={
                'Authorization': u'Bearer ' + paiToken.getToken(),
                # 'Content-type': u'application/json'
            },
            data={'value': 'STOP'})
    except Exception as err:
        logger.info("stopping job:{0} error: {1}".format(job_name, err))

def get_job_detail(token_config, server_url, job_name):
    job_server_url = server_url + '/api/v1/jobs'
    token_server_url = server_url + '/api/v1/token'

    paiToken = common.pai_job.PaiToken.PaiToken(token_config, token_server_url)
    try:
        response = requests.get(
            job_server_url + '/{}'.format(job_name),
            headers={
                'Authorization': u'Bearer ' + paiToken.getToken(),
                # 'Content-type': u'application/json'
            }
        )

        job_detail =  response.json()

        response_config = requests.get(
            job_server_url + '/{}/config'.format(job_name),
            headers={
                'Authorization': u'Bearer ' + paiToken.getToken(),
                # 'Content-type': u'application/json'
            }
        )

        job_config = response_config.json()
        job_detail['jobConfig'] = job_config

        return job_detail

    except Exception as err:
        logger.info("[get_jobs_list] err".format(err))
        raise


if __name__ == '__main__':
    token_config = dict(username=r'test', password=r'test')
    server_url = 'http://10.10.8.1:9186'

    jobs_list = get_jobs_list(token_config, server_url)
    logger.info(jobs_list)

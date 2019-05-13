#encoding=utf-8
import common.pai_job.PaiToken
import requests
from common.log.log_config import logger

class PaiJob:
    def __init__(self, job_name, restserver_url, token_config):
        self.job_name = job_name
        self.token_config = token_config
        self.token_server_config =  restserver_url + '/api/v1/token'
        self.job_server_url = restserver_url + '/api/v1/jobs'
        self.pai_token = common.pai_job.PaiToken.PaiToken(self.token_config, self.token_server_config)

    #获取配置参数
    def get_job_config(self):
        try:
            response_config = requests.get(
                    self.job_server_url + '/{}/config'.format(self.job_name),
                    headers={
                        'Authorization': u'Bearer ' + self.pai_token.getToken(),
                        # 'Content-type': u'application/json'
                    }
                )
            return response_config.json()
        except Exception as err:
            logger.info("[get_job_config] err".format(err))
            raise

    #获取任务详情
    def get_job_detail(self):
        try:
            response = requests.get(
                self.job_server_url + '/{}'.format(self.job_name),
                headers={
                    'Authorization': u'Bearer ' + self.pai_token.getToken(),
                    # 'Content-type': u'application/json'
                }
            )
            return response.json()
        except Exception as err:
            logger.info("[get_jobs_list] err".format(err))
            raise

    #停止任务
    def stop_job(self):
        logger.info("stopping job:{0}".format(self.job_name))

        stop_job_url = "{0}/{1}/executionType".format(self.job_server_url, self.job_name)
        try:
            response = requests.put(
                stop_job_url,
                headers={
                    'Authorization': u'Bearer ' + self.pai_token.getToken(),
                    # 'Content-type': u'application/json'
                },
                data={'value': 'STOP'})
        except Exception as err:
            logger.info("stopping job:{0} error: {1}".format(self.job_name, err))

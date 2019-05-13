#encoding=utf-8
import requests
import app.cluster.cluster_config
from common.log.log_config import logger

token = ""
def get_user_center_token(cluster_name):
    try:
        user_center_config = app.cluster.cluster_config.get_user_center_config(cluster_name)
        response = requests.post(
            user_center_config['server_url'] + "/manager/login",
            headers={
                 'Content-type': u'application/x-www-form-urlencoded'
            },
            data=user_center_config['user_info']
        )
        return response.json()['result']['token']
    except Exception as error:
        logger.info("[get_user_center_token] {}".format(error))
        raise

def get_valid_user_token(cluster_name):
    global token
    #需要检验token是否过期
    if not token:
        return get_user_center_token(cluster_name)


def get_user_list_by_page(cluster_name, page=1, page_size=10,status="", is_limited="",  search_key=""):
    try:
        user_center_config = app.cluster.cluster_config.get_user_center_config(cluster_name)
        used_token = get_valid_user_token(cluster_name)
        user_list_url = "{}/user/getUserByPage?page={}&pageSize={}&status={}&isLimited={}&searchKey={}&token={}".format(
                user_center_config['server_url'], page, page_size, status, is_limited, search_key, used_token )
        logger.info(user_list_url)
        result = requests.get(user_list_url)
        return result.json()
    except Exception as err:
        logger.info(err)
        raise

if __name__ == '__main__':
    result = get_user_list_by_page()
    logger.info(result)

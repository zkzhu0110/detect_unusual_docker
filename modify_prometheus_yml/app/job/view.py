#encoding=utf-8
from flask import Blueprint, jsonify, request
import json
import app.cluster.cluster
import app.cluster.cluster_config
import app.job.job
from common.error_code.response import make_success_response, make_error_response
from common.log.log_config import logger

route_job = Blueprint('job', __name__)

#获取集群内的所有任务列表
@route_job.route('/<cluster_name>', methods=['GET'])
def get_cluster_jobs(cluster_name):
    try:
        server_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)

        jobs_list = app.job.job.get_jobs_list(token_config, server_url)
        if len(jobs_list) < 500:
            return make_success_response(jobs_list)
        else:
            return make_success_response(jobs_list[1:500])

    except Exception as err:
        logger.info('[get_cluster_jobs] err {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

#根据关键字查询集群内的任务
@route_job.route('/<cluster_name>/search/<search_multi_key>', methods=['GET'])
def get_cluster_jobs_by_key(cluster_name, search_multi_key):
    try:
        logger.info("get_cluster_jobs_by_key {} {}".format(cluster_name, search_multi_key))
        server_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)

        jobs_list = app.job.job.get_jobs_list_by_key(token_config, server_url, search_multi_key)
        return make_success_response(jobs_list)
    except Exception as err:
        logger.info('[get_cluster_jobs] err {}'.format(err))
        return make_error_response(status=200, code=500, message=err)

@route_job.route('/<cluster_name>/<job_name>/executionType', methods=['POST'])
def stop_cluster_job(cluster_name, job_name):
    try:
        data_str = request.get_data().decode('utf-8')
        action = json.loads(data_str)['value']

        if action != 'STOP':
            logger.info('[stop_cluster_job] stop job action should be STOP')
            return jsonify({"message": {"status": 200, "code": 500, "message": 'value should be STOP'}})

        server_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)

        app.job.job.stop_job(token_config,  server_url, job_name)
        return jsonify({"message": {"status": 200, "code": 0, "message": "success"}})
    except Exception as err:
        logger.info('[stop_cluster_job]', err)
        return make_error_response(status=200, code=500, message=err)

@route_job.route('/<cluster_name>/<job_name>', methods=['GET'])
def get_job_detail(cluster_name, job_name):
    try:
        server_url = app.cluster.cluster_config.get_cluster_rest_server_uri(cluster_name)
        token_config = app.cluster.cluster_config.get_cluster_login_token(cluster_name)

        job_detail = app.job.job.get_job_detail(token_config,  server_url, job_name)
        return make_success_response(job_detail)
    except Exception as err:
        logger.info('[get_job_detail]', err)
        return make_error_response(status=200, code=500, message=err)

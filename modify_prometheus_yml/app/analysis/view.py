#encoding=utf-8
from flask import Blueprint, request
import app.cluster.cluster
import app.analysis.node_reboot
from common.error_code.response import make_success_response, make_error_response
from common.log.log_config import logger

route_analysis = Blueprint('analysis', __name__)

#获取集群重启信息
@route_analysis.route('/node_reboot/<cluster_name>', methods = ['GET'])
def get_cluster_reboot_log(cluster_name):
    try:
        cluster_info = app.cluster.cluster.get_cluster_by_name(cluster_name)
        server_url = "http://{}:9091".format(cluster_info['ip'])
        start_time = request.args.get('start_time', type=float)
        end_time = request.args.get('end_time', type=float)
        logger.info("start_time:{} end_time:{}".format(start_time, end_time))
        #指定搜索范围
        if not start_time or not end_time:
            return make_error_response(status=200, code=500, message="need star_time and end_time")

        #前端传过来的是毫秒，prometheus需要秒
        start_time = start_time/1000
        end_time = end_time/1000

        result = app.analysis.node_reboot.findContainerInfo(server_url, start_time, end_time)
        return make_success_response(result)
    except Exception as err:
        logger.info("[get_cluster_reboot_log] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

#encoding=utf-8
from flask import Blueprint, jsonify, request
import app.user.user
from common.error_code.response import make_error_response
from common.log.log_config import logger

route_users = Blueprint('users', __name__)

#获取用户信息
@route_users.route('/<cluster_name>', methods=['GET'])
def get_cluster_users(cluster_name):
    try:
        logger.info("get_cluster_users cluster_name: {}".format(cluster_name))
        page = request.args.get('page')
        page_size = request.args.get('pageSize')
        status = request.args.get('status')
        is_limited = request.args.get('isLimited')
        search_key = request.args.get('searchKey')
        logger.info("[get_cluster_users] {} {} {} {} {}".format
                    (page, page_size, status, is_limited, search_key))

        user_lists = app.user.user.get_user_list_by_page(cluster_name,
                                                         page, page_size, status,
                                                         is_limited, search_key)
        #直接将社区返回的元结果返回
        return jsonify(user_lists)
    except Exception as err:
        logger.info(err)
        return make_error_response(status=200, code=500, message=err)




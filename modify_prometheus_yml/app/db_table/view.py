#encoding=utf-8
from flask import Blueprint, request,g
import json

from sqlalchemy import desc
from datetime import datetime
from app.cluster.db_config import get_cluster_database_session

from common.log.log_config import logger
from common.error_code.response import make_success_response, make_error_response, make_no_data_response
from app.db_table.gpu_resources.model import Node_Attribute, Resource_Action_Log
from app.db_table.datasets.model import DataSets
from app.db_table.images.model import Images

route_db_table = Blueprint('db_tables', __name__)

table_web_map = {'images_detail': Images,
                 'datasets_detail': DataSets,
                 'unavailable_resource': Node_Attribute,
                 'unavailable_res_log': Resource_Action_Log
                 }

#处理请求前操作
@route_db_table.before_request
def init_operate():
    g.db_session = {}

#处理请求后操作
@route_db_table.teardown_request
def clean_operate(ex):
    for session in g.db_session.keys():
        logger.info("closing {}".format(session))
        g.db_session[session].close()

#为了统计一次请求中所有的数据库session
def get_request_database_session(cluster_name, database_name):
    g.db_session[database_name] = get_cluster_database_session(cluster_name, database_name)()
    return g.db_session[database_name]

#根据表名称获取表全部记录
@route_db_table.route('/<cluster_name>/unavailable_resource', methods=['GET'])
def get_cluster_unavailable_resource(cluster_name):
    session_platform = get_request_database_session(cluster_name, 'platform')
    records = []
    results = session_platform.query(Node_Attribute).all()
    for record in results:
        records.append(record.get_data_info())

    return make_success_response(records)

#根据表名称获取表全部记录
@route_db_table.route('/<cluster_name>/unavailable_res_log', methods=['GET'])
def get_cluster_unavailable_res_log(cluster_name):
    session_platform = get_request_database_session(cluster_name, 'platform')
    records = []
    results = session_platform.query(Resource_Action_Log).all()
    for record in results:
        records.append(record.get_data_info())
    return make_success_response(records)

#根据表名称获取表全部记录
@route_db_table.route('/<cluster_name>/datasets_detail', methods=['GET'])
def get_cluster_datasets_detaile(cluster_name):
    #session_dataset = DBSession_DataSet()
    session_dataset = get_request_database_session(cluster_name, 'dataset')
    records = []
    results = session_dataset.query(DataSets).all()
    for record in results:
        records.append(record.get_data_info())

    return make_success_response(records)

#根据表名称获取表全部记录
@route_db_table.route('/<cluster_name>/images_detail', methods=['GET'])
def get_cluster_images_detail(cluster_name):
    session_dataset = get_request_database_session(cluster_name, 'dataset')
    records = []
    results = session_dataset.query(Images).all()
    for record in results:
        records.append(record.get_data_info())

    return make_success_response(records)


#根据家磊建议 不在view层做更多的封装
#筛选表unavailable_res_log记录
@route_db_table.route('/<cluster_name>/unavailable_res_log/search', methods=['GET'])
def get_cluster_table_records_by_key(cluster_name):
    try:
        node_id = request.args.get('node_id', type=str)
        logger.info("node_id is {}".format(node_id))
        if not node_id:
            return make_error_response(status=200, code=500, message="query parameter node_id does not exist")

        #按照时间逆序
        session_platform = get_request_database_session(cluster_name, 'platform')
        results = session_platform.query(Resource_Action_Log)\
                    .filter_by(node_id = node_id)\
                    .order_by(desc(Resource_Action_Log.action_time))
        #组装字典
        records = []
        for record in results:
            records.append(record.get_data_info())
        logger.info(records)

        return make_success_response(records)
    except Exception as err:
        logger.info("[get_cluster_table_records_by_key] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

"""
请求数据格式
{'action': 'ADD', 'record':{'id':'10001'...}}
{'action': 'UPDATE', 'record':{ primary:{name:key_name, value: key_value}, content:{}}}
{'action': 'DELETE', 'record':{'id':'10001'...}}
"""

def update_table(session, action, module, record_content, commit = True):
    logger.info("{} {} {}".format(action, module, record_content))
    if action == "ADD":
        logger.info(module(**record_content))
        session.add(module(**record_content))

    if action == "UPDATE":
        filter_condition = {}
        #过滤条件
        filter_condition[record_content['primary']['name']] = record_content['primary']['value']
        session.query(module)\
            .filter_by(**filter_condition)\
            .update(record_content['content'], synchronize_session='fetch')

    if action == "DELETE":
        session.query(module)\
            .filter_by(**record_content)\
            .delete(synchronize_session='fetch')

    #考虑操作多张表时统一提交
    if commit:
        session.commit()

@route_db_table.route('/<cluster_name>/unavailable_resource', methods=['POST'])
def update_cluster_unavailable_resource(cluster_name):
    #解析用户请求
    try:
        request_data = json.loads(request.get_data().decode('utf-8'))
        action = request_data["action"]
        record_content = request_data['record']
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

    #校验用户请求类型
    valid_action = ["ADD", "UPDATE", "DELETE"]
    if action not in valid_action:
        error = "invalid action of table {} ,allowed action is {}".format()
        logger.info("update_cluster_tale_record {}".foramt(error))
        return make_error_response(status=200, code=500, message=error)

    logger.info(record_content)
    #处理符合要求的请求
    try:
        session_platform = get_request_database_session(cluster_name, 'platform')
        update_table(session_platform, action, Node_Attribute, record_content)
        return make_no_data_response(status=200, code=0, message="success")
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

@route_db_table.route('/<cluster_name>/unavailable_res_log', methods=['POST'])
def update_cluster_unavailable_res_log(cluster_name):
    #解析用户请求
    try:
        request_data = json.loads(request.get_data().decode('utf-8'))
        action = request_data["action"]
        record_content = request_data['record']
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

    #校验用户请求类型
    valid_action = ["ADD", "UPDATE", "DELETE"]
    if action not in valid_action:
        error = "invalid action of table {} ,allowed action is {}".format()
        logger.info("update_cluster_tale_record {}".foramt(error))
        return make_error_response(status=200, code=500, message=error)

    logger.info(record_content)
    #处理符合要求的请求
    try:
        session_platform = get_request_database_session(cluster_name, 'platform')
        update_table(session_platform, action, Resource_Action_Log, record_content)
        return make_no_data_response(status=200, code=0, message="success")
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

@route_db_table.route('/<cluster_name>/datasets_detail', methods=['POST'])
def update_cluster_datasets_detail(cluster_name):
    #解析用户请求
    try:
        request_data = json.loads(request.get_data().decode('utf-8'))
        action = request_data["action"]
        record_content = request_data['record']
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

    #校验用户请求类型
    valid_action = ["ADD", "UPDATE", "DELETE"]
    if action not in valid_action:
        error = "invalid action of table {} ,allowed action is {}".format()
        logger.info("update_cluster_tale_record {}".foramt(error))
        return make_error_response(status=200, code=500, message=error)

    logger.info(record_content)
    #处理符合要求的请求
    try:
        if  'createtime' in record_content:
            logger.info(int(record_content['createtime']))
            record_content['createtime'] = datetime.utcfromtimestamp(
                record_content['createtime']/1000).strftime('%Y-%m-%d %H:%M:%S')
        session_dataset = get_request_database_session(cluster_name, 'dataset')
        update_table(session_dataset, action, DataSets, record_content)
        return make_no_data_response(status=200, code=0, message="success")
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

@route_db_table.route('/<cluster_name>/images_detail', methods=['POST'])
def update_cluster_images_detail(cluster_name):
    #解析用户请求
    try:
        request_data = json.loads(request.get_data().decode('utf-8'))
        action = request_data["action"]
        record_content = request_data['record']
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

    #校验用户请求类型
    valid_action = ["ADD", "UPDATE", "DELETE"]
    if action not in valid_action:
        error = "invalid action of table {} ,allowed action is {}".format()
        logger.info("update_cluster_tale_record {}".foramt(error))
        return make_error_response(status=200, code=500, message=error)

    logger.info(record_content)
    #处理符合要求的请求
    try:
        session_dataset = get_request_database_session(cluster_name, 'dataset')
        update_table(session_dataset, action, Images, record_content, commit= True)
        return make_no_data_response(status=200, code=0, message="success")
    except Exception as err:
        logger.info("[update_cluster_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

"""
请求数据格式
{'action': 'ADD', 'record':{'id':'10001'...}}
{'action': 'UPDATE', 'record':{ primary:{name:key_name, value: key_value}, content:{}}}
{'action': 'DELETE', 'record':{'id':'10001'...}}
"""
@route_db_table.route('/<cluster_name>/multiple_tables', methods=['POST'])
def update_cluster_multi_tale_record(cluster_name):
    #解析用户请求
    try:
        request_data = json.loads(request.get_data().decode('utf-8'))
    except Exception as err:
        logger.info("[update_cluster_multi_tale_record] err:{}".format(err))
        return make_error_response(status=200, code=500, message=err)

    try:
        #可能表处理顺序有要求
        for table_name_origin in request_data.keys():
            #检验前台表名称
            if table_name_origin not in table_web_map:
                error = "{} not configured, please check".format(table_name_origin)
                logger.info('operate_multi_table err:{}'.format(error))
                return make_error_response(status=200, code=500, message=error)

            #转换表名称
            module = table_web_map[table_name_origin]
            action = request_data[table_name_origin]['action']
            record_content = request_data[table_name_origin]['record']

            #临时处理
            conver_list = ['value_before', 'value_after']
            for item in conver_list:
                if item in record_content:
                    if record_content[item] == '':
                        record_content[item] = 0

            #更新数据库
            session_platform = get_request_database_session(cluster_name, 'platform')
            update_table(session_platform, action, module, record_content, False)

        #不成功则回滚
        try:
            session_platform.commit()
        except Exception as err:
            session_platform.rollback()
            logger.info(err)
            return make_error_response(status=200, code=500, message=err)

    except Exception as err:
        logger.info(err)
        return make_error_response(status=200, code=500, message=err)

    return make_no_data_response(status=200, code=0, message="success")

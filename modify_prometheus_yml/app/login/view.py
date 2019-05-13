#encoding=utf-8
from flask import Blueprint
from common.error_code.response import make_success_response, make_error_response, make_no_data_response
from app.login.auth import auth, token_auth
import app.login.User
from common.log.log_config import logger

route_auth = Blueprint('auth', __name__)

@route_auth.route('/api/v1/token', methods=['GET', 'POST'])
@auth.login_required
def get_token():
    try:
        auth_request = auth.get_auth()
        logger.info("[get_token] {}".format(auth_request.username))
        token_str = app.login.User.generate_auth_token(auth_request.username)
        return make_success_response(dict(token = str(token_str), username = auth_request.username))
    except Exception as err:
        logger.info("[get_token] {}".format(err))
        return make_error_response(status=200, code=500, message=err)

@route_auth.route('/api/v1/token', methods=['DELETE'])
@token_auth.login_required
def invalidate_toke():
    #此处需要将token设置为无效，暂时未实现
    return make_no_data_response(status=200, code=500, message="logout successfully")

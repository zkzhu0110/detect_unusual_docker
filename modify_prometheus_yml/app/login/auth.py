#encoding=utf-8
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.datastructures import Authorization
from flask import request, g
import json
import app.login.User
import app.login.config
from common.log.log_config import logger

from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import create_engine

# 初始化数据库连接:
engine_user = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
                            app.login.config.db_config['db_user'],
                            app.login.config.db_config['db_pwd'],
                            app.login.config.db_config['db_host'],
                            app.login.config.db_config['db_port'],
                            app.login.config.db_config['database'],
                            ),
                            pool_size=50, max_overflow=100)
# 创建DBSession类型:
DBSession_user = scoped_session(sessionmaker(bind=engine_user, autoflush=False),
                                    scopefunc=g._get_current_object)

class HttpPostAuth(HTTPBasicAuth):
    def get_auth(self):
        try:
            data_str = request.get_data().decode('utf-8')
            logger.info("get_auth {}".format(data_str))
            usrname  = json.loads(data_str)['username']
            password  = json.loads(data_str)['password']
            auth = Authorization(None, {'username': usrname, 'password': password})
        except Exception as err:
            logger.info(err)
            auth = None

        if auth is None and 'Authorization' in request.headers:
            # Flask/Werkzeug do not recognize any authentication types
            # other than Basic or Digest, so here we parse the header by
            # hand
            try:
                auth_type, token = request.headers['Authorization'].split(
                    None, 1)
                auth = Authorization(auth_type, {'token': token})
            except ValueError:
                # The Authorization header is either empty or has no token
                pass

        # if the auth type does not match, we act as if there is no auth
        # this is better than failing directly, as it allows the callback
        # to handle special cases, like supporting multiple auth types
        #if auth is not None and auth.type.lower() != self.scheme.lower():
        #   auth = None
        return auth

auth = HttpPostAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    logger.info("[verify_password] {}".format(username_or_token))
    #user = app.login.User.verify_auth_token(username_or_token)
    # try to authenticate with username/password
    hash_passwd = app.login.User.get_user_passwd(DBSession_user(), username_or_token)
    logger.info("[verify_password] {} ".format(hash_passwd))
    if not hash_passwd or not app.login.User.verify_password(hash_passwd, password):
        return False

    return True

@auth.error_handler
def verify_passwd_error_hand():
    logger.info("[verify_passwd_error_hand] entering")
    return json.dumps(dict(message = dict(status=401, code=-2, message="password is not correct")))

token_auth = HTTPTokenAuth()

@token_auth.verify_token
def verify_token(token):
    # first try to authenticate by token
    logger.info("[verify_token] {}".format(token))
    user = app.login.User.verify_auth_token(token)
    logger.info("[verify_token] user: {}".format(user))
    if not user:
            return False
    return True

@token_auth.error_handler
def verify_token_error_hand():
    logger.info("[verify_token_error_hand] entering")
    return json.dumps(dict(message = dict(status=401, code=-2, message="token is not correct")))

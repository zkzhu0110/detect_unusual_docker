#encoding=utf-8
from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from app.login import  config
import common.sql.mysql
from common.log.log_config import logger

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()

#运维用户
class Management_User(Base):
    __tablename__ = 'management_user'
    user_name = Column(String(40), primary_key=True, nullable=False)
    user_passwd = Column(String(300), nullable=False)
    user_role = Column(String(10))

    def get_data_info(self):
        return dict(user_name = self.user_name, user_passwd = self.user_passwd, user_role = self.user_role)

    def __str__(self):
        return "{}".format(self.get_data_info())

    def __repr__(self):
        return "{}".format(self.get_data_info())

db_instance = common.sql.mysql.MySQL(config.db_config['db_host'], config.db_config['db_port'],
            config.db_config['db_user'], config.db_config['db_pwd'], config.db_config['database'])

# 密码加密
def hash_password(password):
    return custom_app_context.encrypt(password)

# 密码解析
def verify_password(hash_password, password):
    return custom_app_context.verify(password, hash_password)

# 获取token，有效时间10min
def generate_auth_token(username, expiration = 60*60*24):
    s = Serializer(config.SECRET_KEY, expires_in = expiration)
    return s.dumps({ 'username': username }).decode('utf-8')

def get_user_passwd(session, user_name):
    result = session.query(Management_User)\
                    .filter_by(user_name = user_name).first()
    return result.get_data_info()['user_passwd']

def add_user(session, username, passwd, role):
    passwd = hash_password(passwd)
    session.add(Management_User(user_name = username, user_passwd = passwd, user_role = role))
    session.commit()
    return True

# 解析token，确认登录的用户身份
def verify_auth_token(token):
    token = bytes(token, encoding='utf-8')
    logger.info('token: {}'.format(token))
    s = Serializer(config.SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None # valid token, but expired
    except BadSignature:
        return None # invalid token

    return data['username']

if __name__ == '__main__':
    #add_user('admin', 'admin123', 'admin')
    #logger.info(generate_auth_token('admin'))
    #logger.info(verify_auth_token(generate_auth_token('admin')))
    #add_user('caoyue', 'leinao123', 'admin')
    # 初始化数据库连接:
    engine_user = create_engine('mysql+pymysql://root:12345678@10.10.8.1:3306/management')
    # 创建DBSession类型:
    DBSession_user = sessionmaker(bind=engine_user, autoflush=False)
    #add_user(DBSession_user(), 'changfeng', 'leinao123', 'admin')
    print(get_user_passwd(DBSession_user(), 'yaosheng'))


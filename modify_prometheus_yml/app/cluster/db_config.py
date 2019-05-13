#encoding=utf-8
from flask import g
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import create_engine
import app.cluster.cluster_config
from common.log.log_config import logger

cluster_database = {}

#获取集群数据库session
def get_cluster_database_session(cluster_name, database_name):
    database_config = app.cluster.cluster_config.get_cluster_database(cluster_name)
    #数据库未配置
    if not database_name in database_config.keys():
        logger.info("{} not in {}".format(database_name, database_config))
        return None
    global  cluster_database

    #判读集群名称
    if cluster_name not in cluster_database:
        cluster_database[cluster_name] = {}

    #判断仓库名称
    if database_name not in cluster_database[cluster_name]:
        database = database_config[database_name]
        sql_path = "mysql+pymysql://{}:{}@{}:{}/{}".format(
                            database['db_user'],
                            database['db_passwd'],
                            database['db_host'],
                            database['db_port'],
                            database_name)
        logger.info('sql_path: {}'.format(sql_path))
        # 初始化数据库连接:
        engine = create_engine(sql_path, pool_size=50, max_overflow=100)
        # 创建DBSession类型:
        session = scoped_session(sessionmaker(bind=engine, autoflush=False),
                                 scopefunc=g._get_current_object)

        cluster_database[cluster_name][database_name] = session

    return cluster_database[cluster_name][database_name]

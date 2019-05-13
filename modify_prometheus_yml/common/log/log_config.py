#coding=utf8
import logging
import logging.config
import yaml
import os

def load_yaml_config(config_path):

    with open(config_path, "r") as f:
        cluster_data = yaml.load(f, Loader=yaml.FullLoader)

    return cluster_data

def setup_logging():
    """
    Setup logging configuration.
    """
    dir = os.path.dirname(__file__)
    configuration_path = "{}/logging.yaml".format(dir)

    logging_configuration = load_yaml_config(configuration_path)

    logging.config.dictConfig(logging_configuration)

# 创建一个logger
logger = logging.getLogger(__name__)

setup_logging()

if __name__ == '__main__':
    # 记录一条日志
    logger.info('test')

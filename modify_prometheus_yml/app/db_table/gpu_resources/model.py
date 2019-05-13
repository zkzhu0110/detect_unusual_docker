#encoding=utf-8
from sqlalchemy import create_engine, Column, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# 创建对象的基类:
Base = declarative_base()

#被隔离的GPU
class Node_Attribute(Base):
    __tablename__ = 'node_attribute'
    node_id = Column(String(40), primary_key=True)
    unhealthy_gpu = Column(BigInteger)

    def get_data_info(self):
        return dict(node_id = self.node_id, unhealthy_gpu = self.unhealthy_gpu)

    def __str__(self):
        return "{}".format(self.get_data_info())

    def __repr__(self):
        return "{}".format(self.get_data_info())

#隔离操作日志
class Resource_Action_Log(Base):
    __tablename__ = 'resource_action_log'
    id = Column(BigInteger, primary_key=True)
    node_id = Column(String(40))
    value_before = Column(BigInteger)
    value_after = Column(BigInteger)
    action = Column(String(10))
    action_time = Column(DateTime, default =func.now())
    resource_type = Column(String(10), default='gpu')
    operator = Column(String(20))
    remark = Column(String(1000))

    def get_data_info(self):
        return dict(id = self.id, node_id = self.node_id, value_before = self.value_before,
                    value_after = self.value_after, action = self.action, action_time = self.action_time,
                    resource_type = self.resource_type, operator = self.operator, remark = self.remark)

    def __str__(self):
        return "{}".format(self.get_data_info())

    def __repr__(self):
        return "{}".format(self.get_data_info())

if __name__ == '__main__':
    # 初始化数据库连接:
    engine = create_engine('mysql+pymysql://root:12345678@10.12.3.2:3306/platform')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    print(session.query(Node_Attribute).all())
    for item in (session.query(Resource_Action_Log).filter_by(node_id = '10.11.0.12')):
        print(item)

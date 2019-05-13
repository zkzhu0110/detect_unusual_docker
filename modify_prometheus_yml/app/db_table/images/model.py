#encoding=utf-8
from sqlalchemy import create_engine, Column, String, TEXT, DATETIME
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()

#数据集合
class Images(Base):
    __tablename__ = 'images'
    id = Column(String(100), primary_key=True, index= True, unique= True, nullable= False)
    name = Column(String(40), nullable= False)
    type = Column(String(10))
    file_type = Column(String(10))
    place = Column(String(512))
    description = Column(LONGTEXT)
    provider = Column(String(40))
    createtime = Column(DATETIME)
    remark = Column(String(40))

    def get_data_info(self):
        return dict(id = self.id, name = self.name, type = self.type,
                    file_type = self.file_type, place = self.place,
                    description = self.description, provider = self.provider,
                    createtime = self.createtime, remark = self.remark)

    def __str__(self):
        return "{}".format(self.get_data_info())

    def __repr__(self):
        return "{}".format(self.get_data_info())

if __name__ == '__main__':
    # 初始化数据库连接:
    engine = create_engine('mysql+pymysql://root:12345678@10.12.3.2:3306/dataset')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    print(session.query(Images).all())

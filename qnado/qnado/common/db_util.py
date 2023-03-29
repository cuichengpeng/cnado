from qnado import settings
from pymongo import MongoClient
from bson import ObjectId


class DBHelerFactory:
    """ 数据库交互类的简单工厂。 """
    def __init__(self, db_url) -> None:
        """
        db_url 示例：
            - mongodb: mongodb://username:password@127.0.0.1:27017

        """
        self.db = None
        self.db_type = db_url.split(':')[0]

        if self.db_type == 'mongodb':
            self.db = DBHelperMongodb(db_url)
        elif self.db_type == 'mysql':
            pass
        else:
            # 不支持的情况
            raise ValueError('目前不支持该数据库：', self.db_type)

    def get_db(self):
        return self.db


class DBHelperBase:
    """ 具体数据库交互类的基类。"""
    def __init__(self, db_url) -> None:
        self.db = None
        self.db_url = db_url

    def insert(self, tablename, data):
        """ 插入数据，支持单条和多条。"""
        raise NotImplementedError("该方法需要在子类实现。")


class DBHelperMongodb(DBHelperBase):
    def __init__(self, db_url) -> None:
        super().__init__(db_url)
        client = MongoClient(self.db_url, connect=False)
        self.db = client[settings.DB_NAME]

    def find_one(self, tablename, cond):
        return self.db[tablename].find_one(cond)

    def insert(self, tablename, data):
        self.db[tablename].insert_one(data)
        oid = data.pop('_id')
        return oid

    def update(self, tablename, cond, data):
        self.db[tablename].update_one(cond, {'$set': data})


# db 操作统一从此处导入
db = DBHelerFactory(db_url=settings.DB_URL).get_db()

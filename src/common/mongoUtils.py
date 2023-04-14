import pymongo


class MongoUtils(object):
    HOST_CONF = {
        "local": ["127.0.0.1", 27017],
    }

    def __init__(self):
        pass

    __CLIENT__CACHE = {}

    def get_client(self, host_name):
        client = self.__CLIENT__CACHE.get(host_name)
        if client:
            return client

        [host, port] = self.HOST_CONF[host_name]
        client = pymongo.MongoClient(host=host, port=port, unicode_decode_error_handler='ignore')
        self.__CLIENT__CACHE.update({host_name: client})

        return client

    __TABLE_CACHE = {}

    # table 表名 "host_name/db/collection"
    def get_table(self, table: str):
        args = table.split("/")
        if len(args) < 2:
            raise Exception("获取表参数错误")
        if len(args) == 2:
            args = ["growth", *args]

        table = "/".join(args)
        if MongoUtils.__TABLE_CACHE.get(table):
            return MongoUtils.__TABLE_CACHE.get(table)

        host, db, tb = args
        client = self.get_client(host)
        instance = client[db][tb]
        MongoUtils.__TABLE_CACHE.update({
            table: instance
        })
        return instance

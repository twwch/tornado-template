import os
import json
import argparse
from copy import deepcopy
from pymongo import ReadPreference
from .log import load_logger

MONGODB = {}
REDIS = {}
MYSQLDB = {}


def load_conf():
    """
    解析环境变量(CONFIG_FILE)或命令行参数(-c), 获取配置文件
    manage.py运行的脚本不能通过命令行参数传入配置文件, 规范统一从环境变量中获取配置文件
    需要优先解析环境变量, 因为脚本可能会用-c参数代表其他参数(如数据库表)
    """
    config_file = os.getenv("CONFIG_FILE")
    if not config_file:
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', metavar='ConfigFile', type=str, help='config file')
        args, _ = parser.parse_known_args()
        config_file = os.path.abspath(args.c)
    if not config_file:
        print('no config file provided')
        exit(1)
    with open(config_file, encoding='utf-8') as f:
        env = json.load(f)
    return env


def load_mongodb(mongos_env):
    for db_name, _db_conf in mongos_env.items():
        db_conf = deepcopy(_db_conf)
        read_preference = db_conf.get("read_preference")
        if read_preference == "primary":
            db_conf["read_preference"] = ReadPreference.PRIMARY
        elif read_preference == "primary_preferred":
            db_conf["read_preference"] = ReadPreference.PRIMARY_PREFERRED
        elif read_preference == "secondary":
            db_conf["read_preference"] = ReadPreference.SECONDARY
        else:
            db_conf["read_preference"] = ReadPreference.SECONDARY_PREFERRED
        MONGODB[db_name] = db_conf


env = load_conf()
load_mongodb(env["mongodb"])
load_logger(env["log"], env["service_name"])

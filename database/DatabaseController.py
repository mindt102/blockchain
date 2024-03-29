import json
import os
import sqlite3

import yaml

import utils


class DatabaseController:
    __logger = utils.get_logger(__name__)

    def __init__(self):
        # config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        self.db_name = utils.config["db"]["name"]
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute(self, command, params=()):
        try:
            self.cursor.execute(command, params)
            self.conn.commit()
        except Exception:
            self.__logger.exception(command)
            raise
        return self.cursor.lastrowid

    def fetchOne(self, command, params=()):
        self.cursor.execute(command, params)
        return self.cursor.fetchone()

    def fetchAll(self, command, params=()):
        self.cursor.execute(command, params)
        return self.cursor.fetchall()

    def selectOne(self, table_name, where="1", field="*", params=()):
        return self.fetchOne(f'SELECT {field} FROM {table_name} WHERE ({where})=({"?,"*(len(params)-1)}?)', params)

    def selectAll(self, table_name, where="1", field="*", sortby="id", params=()):
        return self.fetchAll(f'SELECT {field} FROM {table_name} WHERE ({where})=({"?,"*(len(params)-1)}?) ORDER BY {sortby}', params)

    def insert(self, tableName, tableCol, values):
        return self.execute(
            f'INSERT INTO {tableName} ({",".join(tableCol)}) VALUES ({"?,"*(len(values)-1)}?)', values)


def query_func(func):
    def wrapper(*args, **kwargs):
        # print(f"args = {args}, kwargs = {kwargs}")
        db = None
        if "db" not in kwargs or not kwargs["db"]:
            db = DatabaseController()
            kwargs["db"] = db

        result = func(*args, **kwargs)
        if db:
            db.close()
        return result
    return wrapper

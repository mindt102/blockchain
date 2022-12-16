import sqlite3
import yaml


class DatabaseController:
    def __init__(self):
        config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
        self.db_name = config["db"]["name"]
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute(self, command, params=()):
        self.cursor.execute(command, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def fetchOne(self, command, params=()):
        self.cursor.execute(command, params)
        return self.cursor.fetchone()

    def selectOne(self, tableName, where="1", field="*", values=()):
        return self.fetchOne(f'SELECT {field} FROM {tableName} WHERE ({where})=({"?,"*(len(values)-1)}?)', values)

    def insert(self, tableName, tableCol, values):
        return self.execute(
            f'INSERT INTO {tableName} ({",".join(tableCol)}) VALUES ({"?,"*(len(values)-1)}?)', values)

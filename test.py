# import socketio

# sio = socketio.Client()


# # @sio.event
# # def connect():


# @sio.event
# def message(data):
#     print(f"Received message: {data}")


# @sio.event
# def mempool(data):
#     print(f"Received mempool: {data}")


# @sio.event
# def block(data):
#     print(f"Received block: {data}")


# sio.connect('http://localhost:3000')
# sio.wait()

class GenerateQuery(object):
    def __init__(self, tableName, tableCol):
        self.tableName = tableName
        self.tableCol = tableCol

    def __fieldStringGen(self):
        fieldString = []
        for field in self.tableCol:
            typeCol = "{}{}".format(
                field['type'], "({})".format(field['length']) if 'length' in field else '')
            primaryKey = "{}".format("constraint {}_pk primary key {}".format(
                self.tableName, "autoincrement" if "AI" in field else '') if 'primaryKey' in field else '')
            foreignKey = "{}".format(
                "constraint {}_{}_fk references {} ({})".format(self.tableName, field['refTable'], field['refTable'], field['refCol']) if 'foreignKey' in field else '')

            nullCol = "null" if field['null'] else 'not null'
            fieldString.append("{} {} {} {} {}".format(
                field['name'], typeCol, nullCol, primaryKey, foreignKey))
        return ", ".join(fieldString)

    def __str__(self):
        return "create table {} ({})".format(self.tableName, self.__fieldStringGen())

from utils import config
# from databas?e import GenerateQuery
import json

with open(config["db"]["sample"]) as f:
    tables_config = json.loads(f.read())
    create_queries = map(
        lambda conf: GenerateQuery(**conf), tables_config)
    for query in create_queries:
        print(str(query))

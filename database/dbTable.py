import json
import os

from database.DatabaseController import DatabaseController
from database.GenerateQuery import GenerateQuery


def createDb(dbName: str, dbSample: str, isDebug: bool = True):
    # Check file exist and delete
    if isDebug:
        if os.path.exists(dbName):
            os.remove(dbName)
    # Create table
        f = open(dbSample, 'r')
        db = DatabaseController()
        js = f.read()
        j = json.loads(js)
        tableList = map(lambda x: GenerateQuery(**x), j)
        for table in tableList:
            db.execute(str(table))
        db.close()

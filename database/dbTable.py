from database.db import db
from database.generateQuery import GenerateQuery
import os
import json


def createDb():
    # Check file exist and delete
    # if os.path.exists('bc.db'):
    #     os.remove('bc.db')
    # Create table
    f = open('database/db.json', 'r')
    js = f.read()
    j = json.loads(js)
    tableList = map(lambda x: GenerateQuery(**x), j)
    for table in tableList:
        db.execute(str(table))

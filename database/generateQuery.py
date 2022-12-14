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

import sqlite3


class DatabaseController:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute(self, command):
        self.cursor.execute(command)
        self.conn.commit()


db = DatabaseController('bc.db')

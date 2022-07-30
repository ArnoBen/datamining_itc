import pymysql
import os
from dotenv import load_dotenv
load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.connection = pymysql.connect(user=os.environ["MYSQL_USER"],
                                          password=os.environ["MYSQL_PASSWORD"],
                                          db="datamining_itc_music")
        self.cursor = self.connection.cursor()


if __name__ == "__main__":
    dbmanager = DatabaseManager()
    print(dbmanager)
import os
import pymysql
from dotenv import load_dotenv

class MySQL():
    def __init__(self):
        load_dotenv()
        self.db = None
        self.cursor = None

    def connect(self):
        self.db = pymysql.connect(host='common-write.db.service',
                            port=3306,
                            user='wblmysql',
                            passwd='D12vmaria010',
                            db='ledger',
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
        return self.db
        
    def test(self):
        try:
            self.cursor = self.db.cursor()
            self.sql = 'SHOW DATABASES'
            self.cursor.execute(self.sql)
            self.results = self.cursor.fetchall()
            return self.results
        except Exception as e:
            print(e)
            return 'Connect First!!'
    def close(self):
        self.db.close()

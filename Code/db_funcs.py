import numpy as np
import psycopg2

class DBFunctions:
    cursor = None
    conn = None
    dbname = ""

    def __init__(self, dbname="OCRData", hostname="localhost", portno="5432", usr="postgres", pwd="a250695postgres"):
        try:
            self.conn = psycopg2.connect(host=hostname, port=portno, database=dbname, user=usr, password=pwd)
            self.cursor = self.conn.cursor()
            self.dbname = dbname
        except (Exception, psycopg2.Error, psycopg2.DatabaseError) as e:
            print(e)

    def createTable(self, tableName, definition):
        try:
            self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (tableName,))
            if not self.cursor.fetchone()[0]:
                self.cursor.execute("CREATE TABLE " + tableName + " ( " + definition + " ) ")
                print("Table created")
            else:
                self.cursor.execute("TRUNCATE TABLE " + tableName)
                print("Table exists already")
            self.commitChanges()
        except (Exception, psycopg2.Error, psycopg2.DatabaseError) as e:
            print(e)

    def insertLine(self, tableName, description, units, price):
        try:
            self.cursor.execute("INSERT INTO " + tableName + " (Description, Units, Price) VALUES (%s, %s, %s)", (description, units, price))
        except (Exception, psycopg2.Error, psycopg2.DatabaseError) as e:
            print(e)

    def commitChanges(self):
        self.conn.commit()

    def closeConnection(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


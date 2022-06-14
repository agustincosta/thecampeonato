from ast import If
import numpy as np
import psycopg2
#import pandas
import matplotlib.pyplot as plt
#from sqlalchemy import create_engine
import categorization_funcs
import datetime

class DBFunctions:
    cursor = None
    conn = None
    dbname = ""

    def __init__(self, dbname="expense_tracking", hostname="localhost", portno="5432", usr="postgres", pwd="a250695postgres"):
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

    def getSinglePurchaseInfo(self, purchase_id):
        select_query = ("SELECT * FROM general_table WHERE purchase_id = " + purchase_id)
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def getUserPurchaseInfo(self, user_id):
        select_query = "SELECT * FROM general_table WHERE user_id = " + user_id
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def purchaseAnalysis(self, purchase_id):
        select_query = ("SELECT * FROM details_table WHERE purchase_number = " + purchase_id)
        self.cursor.execute(select_query)
        purchase_detail = np.array(self.cursor.fetchall())

        labels = purchase_detail[:,2] 

        select_query = ("SELECT * FROM general_table WHERE purchase_id = " + purchase_id)
        self.cursor.execute(select_query)
        general = np.array(self.cursor.fetchall())

        user = general[0,1]
        purchase_date = general[0,3]
        total = general[0,4]
        normalized_amounts = purchase_detail[:,5]

        select_query = ("SELECT * FROM users_table WHERE user_id = " + str(user))
        self.cursor.execute(select_query)
        users_data = np.array(self.cursor.fetchall())

        user_name = users_data[0,1]
    
        cat = categorization_funcs.categorization("../Dataset/categorias.csv")
        categories = cat.categorizeItems(labels, cutoff=0.4)
        uniqueCats, uniqueAmts = cat.addCategoriesTotal(categories, normalized_amounts)

        fig1, ax1 = plt.subplots()
        ax1.pie(uniqueAmts, labels=uniqueCats, autopct='%1.1f%%', shadow=False, startangle=90)
        ax1.axis('equal')
        plt.title('Compra de ' + user_name + ' el día ' + purchase_date.strftime("%d %b %Y"))
        plt.show()

    def getLastPurchases(self, n=5):
        select_query = "SELECT purchase_id FROM general_table ORDER BY timestamp DESC"
        self.cursor.execute(select_query)
        pid = np.zeros(n, dtype=int)
        for i in range (n):
            pid[i] = int(self.cursor.fetchone()[0])
        return pid

    def getUserMonthlyPurchases(self, user_id, month, year):
        select_query = ("SELECT * FROM general_table WHERE user_id = " + str(user_id) + " AND (timestamp BETWEEN '" + str(year) + "-" + str(month) + "-1' AND '" + str(year) + "-" + str(month) + "-31')")
        self.cursor.execute(select_query)
        user_mthly_general = np.array(self.cursor.fetchall())

        user_mthly_pids = user_mthly_general[:,0]
        user_mthly_totals = user_mthly_general[:,3]

        user_mthly_labels = []
        user_mthly_amts = np.zeros(1)

        for i in range(len(user_mthly_pids)):
            select_query = ("SELECT * FROM details_table WHERE purchase_number = " + str(user_mthly_pids[i]))
            self.cursor.execute(select_query)
            purchase_detail = np.array(self.cursor.fetchall())

            user_mthly_labels.append(purchase_detail[:,2])
            user_mthly_amts = np.append(user_mthly_amts, purchase_detail[:,5])
   
        cat = categorization_funcs.categorization("../Dataset/categorias.csv")
        categories = cat.categorizeItems(user_mthly_labels, cutoff=0.4)    
        uniqueMthlyCats, uniqueMthlyAmts = cat.addCategoriesTotal(categories, user_mthly_amts)

        select_query = ("SELECT * FROM users_table WHERE user_id = " + str(user_id))
        self.cursor.execute(select_query)
        users_data = np.array(self.cursor.fetchall())

        user_name = users_data[0,1]

        titulo = 'Desglose mensual de ' + user_name + ' del mes ' + str(month) + '/' + str(year)
        self.plotPieChart(uniqueMthlyAmts, uniqueMthlyCats, titulo)

    def plotPieChart(self, amounts, categories, plotTitle):
        fig1, ax1 = plt.subplots()
        exp = np.ones_like(amounts)/50
        ax1.pie(amounts, labels=categories, autopct='%1.1f%%', shadow=False, startangle=90, explode=exp)
        ax1.axis('equal')
        plt.title(plotTitle, y=1.08)
        plt.show()

    def closeConnection(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    db = DBFunctions()
    #print(db.getSinglePurchaseInfo("10"))
    #print(db.getUserPurchaseInfo("3"))
    #print(db.purchaseAnalysis("1"))
    #db.purchaseAnalysis("12")
    # last_pid = db.getLastPurchases()
    # for pid in last_pid:
    #     db.purchaseAnalysis(str(pid))
    db.getUserMonthlyPurchases(3,5,2021)